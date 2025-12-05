# sacco_core/aml/dashboard.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Tuple
import pandas as pd

from sacco_core.db import query

# --- Config constants (align to your configs/aml_config.yml) ---
CTR_THRESHOLD_KES = 1_900_000  # cash threshold (≈USD 15k)
STR_DEADLINE_DAYS = 2

@dataclass
class OverviewKPIs:
    members: int
    txns_period: int
    high_risk_members: int
    pep_records: int
    sanctions_records: int
    ctr_hits_alltime: int

# ---------- Overview ----------
def get_overview_kpis(where_sql: str, params: list) -> OverviewKPIs:
    def val(sql: str, p=None, col="c", default=0):
        try: return query(sql, p)[col].iloc[0]
        except Exception: return default

    members_cnt = val("select count(*) c from members")
    txns_cnt = val(f"select count(*) c from transactions{where_sql}", params)
    high_risk_cnt = val("select count(*) c from members where risk_band='HIGH'")
    pep_cnt = val("select count(*) c from pep_list")
    sanc_cnt = val("select count(*) c from sanctions_list")
    ctr_hits = val("select count(*) c from transactions where channel='CASH' and amount>=?", [CTR_THRESHOLD_KES])

    return OverviewKPIs(
        members=members_cnt,
        txns_period=txns_cnt,
        high_risk_members=high_risk_cnt,
        pep_records=pep_cnt,
        sanctions_records=sanc_cnt,
        ctr_hits_alltime=ctr_hits,
    )

def inflow_outflow_trend(where_sql: str, params: list) -> pd.DataFrame:
    sql = f"""
        select ts::date as d,
               sum(case when amount>0 then amount else 0 end) as inflow,
               sum(case when amount<0 then -amount else 0 end) as outflow
        from transactions
        {where_sql}
        group by 1
        order by 1
    """
    try:
        df = query(sql, params)
        return df
    except Exception:
        return pd.DataFrame(columns=["d","inflow","outflow"])

# ---------- Compliance metrics ----------
def compliance_snapshot(where_sql: str, params: list) -> Dict[str, str]:
    """
    Lightweight KPIs to show health against deadlines.
    Approximations until full filings registry is wired.
    """
    # CTR weekly compliance proxy: weeks that have >=1 CTR cash hit
    try:
        ctr_weeks = query(
            f"""
            with cash_hits as (
                select ts::date d
                from transactions
                where channel='CASH' and amount >= {CTR_THRESHOLD_KES}
            ),
            weeks as (
                select date_trunc('week', d) as week_start, count(*) c
                from cash_hits
                group by 1
            )
            select count(*) c from weeks
            """
        )["c"].iloc[0]
    except Exception:
        ctr_weeks = 0

    # STR SLA proxy: alerts older than 2 days and still "OPEN"
    try:
        str_breaches = query(
            f"""
            select count(*) c
            from alerts
            where severity in ('HIGH','CRITICAL')
              and status in ('OPEN','PENDING')
              and created_at <= (now() - interval '{STR_DEADLINE_DAYS} day')
            """
        )["c"].iloc[0]
    except Exception:
        str_breaches = 0

    # Record retention (assume policy is 7 years) – proxy is “OK”
    retention = "Compliant"

    return {
        "ctr_weeks_with_hits": f"{ctr_weeks}",
        "str_sla_status": "Breaches" if str_breaches > 0 else "On Track",
        "str_breaches": f"{str_breaches}",
        "retention": retention,
    }

# ---------- Alerts feed ----------
def realtime_alerts(limit: int = 50, where_sql: str | None = None, params: list | None = None) -> pd.DataFrame:
    """
    Pull latest alerts if `alerts` exists; otherwise synthesize from `transactions`.
    Adapts to your schema (member_id/customer_id optional; channel/product/branch optional).
    Uses string concatenation for JSON (avoids format/printf issues).
    """
    # 1) Try native alerts table
    try:
        df = query(
            """
            select id, rule_id, severity, created_at, status, owner, linked_entities, narrative
            from alerts
            order by created_at desc
            limit ?
            """,
            [limit],
        )
        if not df.empty:
            return df
    except Exception:
        pass

    # 2) Inspect transactions schema
    try:
        tx_cols = query("PRAGMA table_info(transactions)")["name"].str.lower().tolist()
    except Exception:
        tx_cols = []

    has_member   = "member_id" in tx_cols
    has_customer = "customer_id" in tx_cols
    id_col       = "member_id" if has_member else ("customer_id" if has_customer else None)

    has_channel  = "channel" in tx_cols
    has_product  = "product" in tx_cols
    has_branch   = "branch"  in tx_cols
    has_ts       = "ts"      in tx_cols
    has_amount   = "amount"  in tx_cols

    if not (has_ts and has_amount):
        # Need at least ts & amount to produce any alert
        return pd.DataFrame(columns=["id","rule_id","severity","created_at","status","owner","linked_entities","narrative"])

    # 3) Build selector and predicates
    sel_cols = ["row_number() over() as txn_id", "ts", "amount"]
    if id_col:      sel_cols.append(f"{id_col}")
    if has_channel: sel_cols.append("channel")
    if has_product: sel_cols.append("product")
    if has_branch:  sel_cols.append("branch")

    if where_sql is None:
        where_sql, params = " where ts is not null", []

    ctr_pred = f"(channel='CASH' and amount >= {CTR_THRESHOLD_KES})" if has_channel else f"(amount >= {CTR_THRESHOLD_KES})"

    # Linked entities JSON via concatenation (no format/printf)
    if id_col:
        linked_expr = (
            f"""'[' || '{{"txn_id":"' || cast(txn_id as varchar) || '","{id_col}":"' || """
            f"""cast({id_col} as varchar) || '"}}' || ']'"""
        )
    else:
        linked_expr = """'[' || '{"txn_id":"' || cast(txn_id as varchar) || '"}' || ']'"""

    sql = f"""
        with src as (
            select {", ".join(sel_cols)}
            from transactions
            {where_sql}
        ),
        candidates as (
            -- CTR synthetic
            select
                txn_id as id,
                'CTR'::varchar as rule_id,
                case when amount >= {CTR_THRESHOLD_KES} then 'HIGH' else 'MEDIUM' end as severity,
                ts as created_at,
                'OPEN'::varchar as status,
                null::varchar as owner,
                {linked_expr} as linked_entities,
                case when amount >= {CTR_THRESHOLD_KES}
                     then 'Transaction ≥ CTR threshold'
                     else 'Large transaction review'
                end as narrative
            from src
            where {ctr_pred}

            union all

            -- Odd hour / weekend synthetic
            select
                txn_id as id,
                'ODD_HOURS' as rule_id,
                'LOW' as severity,
                ts as created_at,
                'OPEN' as status,
                null as owner,
                {linked_expr} as linked_entities,
                'Odd hours/weekend transaction' as narrative
            from src
            where extract(hour from ts) not between 6 and 21
               or extract(isodow from ts) in (6,7)
        )
        select *
        from candidates
        order by created_at desc
        limit {limit}
    """
    return query(sql, params)
