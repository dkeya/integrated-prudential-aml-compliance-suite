# sacco_core/aml/reporting.py
from __future__ import annotations
from typing import Tuple, Dict, Any, Optional, List
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta

from sacco_core.db import query, execute   # ⬅ add execute
from sacco_core.config import get_config
from sacco_core.aml.transactions import (
    behavioral_stats,
    structuring_staircase,
    rapid_movement,
)

# ----------------------- helpers -----------------------

def _exists(table: str) -> bool:
    try:
        df = query("show tables")
        col = "name" if "name" in df.columns else df.columns[0]
        return table.lower() in df[col].str.lower().tolist()
    except Exception:
        return False

def _cfg():
    """Return strongly-typed Settings (Pydantic)."""
    return get_config()

def _where(where_sql: str) -> str:
    return f"WHERE {where_sql}" if where_sql.strip() else ""

def _safe_dt(x) -> Optional[date]:
    try:
        return pd.to_datetime(x).date() if pd.notna(x) else None
    except Exception:
        return None

def _next_id(table: str, col: str) -> int:
    try:
        df = query(f"SELECT COALESCE(MAX({col}), 0) AS mx FROM {table}")
        base = int(df["mx"].iloc[0]) if not df.empty else 0
    except Exception:
        base = 0
    return base + 1

# ----------------------- CTR: Single (page expects ctr_single_hits) -----------------------

def ctr_single_hits(where_sql: str = "", params: Tuple = ()) -> pd.DataFrame:
    """
    Single CASH transactions ≥ threshold (KES).
    Columns (when available): txn_id, member_id, ts, amount, channel, branch, product, hit_type
    """
    cfg = _cfg()
    ctr_kes = int(getattr(getattr(cfg, "frc", object()), "ctr_threshold_kes", 1_900_000))

    if not _exists("transactions"):
        return pd.DataFrame(columns=["txn_id","member_id","ts","amount","channel","branch","product","hit_type"])

    cols = query("PRAGMA table_info(transactions)")["name"].str.lower().tolist()
    id_col = "txn_id" if "txn_id" in cols else ("id" if "id" in cols else None)
    member_col = "member_id" if "member_id" in cols else None

    selects = []
    if id_col: selects.append(f"{id_col} as txn_id")
    if member_col: selects.append(f"{member_col} as member_id")
    for c in ["ts","amount","channel","branch","product"]:
        if c in cols: selects.append(c)

    channel_filter = "AND channel='CASH'" if "channel" in cols else ""
    sql = f"""
        SELECT {', '.join(selects)}, 'CTR_SINGLE' AS hit_type
        FROM transactions
        WHERE amount >= {ctr_kes} {channel_filter}
          {"AND (" + where_sql + ")" if where_sql.strip() else ""}
        ORDER BY ts DESC
        LIMIT 2000
    """
    return query(sql, params)

# Backwards-compat alias
def ctr_hits(where_sql: str = "", params: Tuple = ()) -> pd.DataFrame:
    return ctr_single_hits(where_sql=where_sql, params=params)

# ----------------------- CTR Weekly (page expects ctr_weekly_summary) -----------------------

def ctr_weekly_summary(where_sql: str = "", params: Tuple = ()) -> pd.DataFrame:
    """
    Weekly CTR counts & totals across all members for CASH ≥ threshold.
    Returns: iso_week, count_hits, total_amount
    """
    if not _exists("transactions"):
        return pd.DataFrame(columns=["iso_week","count_hits","total_amount"])

    cfg = _cfg()
    ctr_kes = int(getattr(getattr(cfg, "frc", object()), "ctr_threshold_kes", 1_900_000))
    cols = query("PRAGMA table_info(transactions)")["name"].str.lower().tolist()
    ch_filter = "AND channel='CASH'" if "channel" in cols else ""

    sql = f"""
    SELECT
      STRFTIME(ts, '%G-W%V') AS iso_week,
      COUNT(*) AS count_hits,
      SUM(ABS(amount)) AS total_amount
    FROM transactions
    WHERE amount >= {ctr_kes} {ch_filter}
      {"AND (" + where_sql + ")" if where_sql.strip() else ""}
    GROUP BY 1
    ORDER BY iso_week DESC
    """
    return query(sql, params)

def ctr_weekly_aggregates(where_sql: str = "", params: Tuple = ()) -> pd.DataFrame:
    """
    Weekly aggregate CASH inflows per member; emits rows at/above CTR threshold.
    Columns: member_id, week_start, week_end, cash_sum, txn_count
    """
    cfg = _cfg()
    ctr_kes = int(getattr(getattr(cfg, "frc", object()), "ctr_threshold_kes", 1_900_000))

    if not _exists("transactions"):
        return pd.DataFrame(columns=["member_id","week_start","week_end","cash_sum","txn_count"])

    cols = query("PRAGMA table_info(transactions)")["name"].str.lower().tolist()
    if "member_id" not in cols or "ts" not in cols or "amount" not in cols:
        return pd.DataFrame(columns=["member_id","week_start","week_end","cash_sum","txn_count"])

    channel_filter = "AND channel='CASH'" if "channel" in cols else ""
    sql = f"""
    WITH base AS (
      SELECT
        member_id,
        CAST(date_trunc('week', ts) AS DATE) AS week_start,
        CASE WHEN amount>0 THEN amount ELSE 0 END AS cash_in
      FROM transactions
      WHERE 1=1 {channel_filter}
        {"AND (" + where_sql + ")" if where_sql.strip() else ""}
    ),
    agg AS (
      SELECT
        member_id,
        week_start,
        SUM(cash_in) AS cash_sum,
        COUNT(*) AS txn_count
      FROM base
      GROUP BY 1,2
    )
    SELECT
      member_id,
      week_start,
      week_start + INTERVAL 6 DAY AS week_end,
      cash_sum,
      txn_count
    FROM agg
    WHERE cash_sum >= {ctr_kes}
    ORDER BY week_start DESC, member_id
    """
    return query(sql, params)

# ----------------------- STR candidates -----------------------

def str_candidates(where_sql: str = "", params: Tuple = ()) -> pd.DataFrame:
    """
    Heuristic suspicious candidates using:
      - Behavioral outliers (txn_count/avg_amt/hour_std)
      - Structuring staircase near-unit patterns
      - Rapid movement ratio ≥ 0.8
    Returns: member_id, txn_count/inflow/outflow/pct_cash/pct_odd_hours/counterparties + flags, flags_total, suspicion_flags
    """
    beh = behavioral_stats(where_sql=where_sql, params=params)
    if beh.empty:
        return pd.DataFrame(columns=[
            "member_id","txn_count","inflow","outflow","pct_cash","pct_odd_hours",
            "counterparties","flag_high_cash","flag_odd_hours","flag_rapid_io","flag_many_cpty",
            "flags_total","suspicion_flags"
        ])

    for col in ["txn_count","avg_amt","hour_std","cash_pct"]:
        if col not in beh.columns:
            beh[col] = np.nan

    df = beh.copy()
    if "inflow" not in df.columns or "outflow" not in df.columns:
        df["inflow"]  = np.nan
        df["outflow"] = np.nan

    df["pct_cash"] = df["cash_pct"] / 100.0 if df["cash_pct"].max() and df["cash_pct"].max() > 1 else df["cash_pct"]
    df["pct_odd_hours"] = np.nan

    df["flag_high_cash"] = (df["pct_cash"].fillna(0) >= 0.6).astype(int)
    df["flag_odd_hours"] = 0
    df["flag_rapid_io"] = ((df["outflow"].fillna(0) >= 0.8 * df["inflow"].fillna(0)) & (df["inflow"].fillna(0) > 0)).astype(int)
    if "counterparties" not in df.columns:
        df["counterparties"] = 0
    df["flag_many_cpty"] = (df["counterparties"].fillna(0) >= 10).astype(int)

    flags_cols = ["flag_high_cash","flag_odd_hours","flag_rapid_io","flag_many_cpty"]
    df["flags_total"] = df[flags_cols].sum(axis=1)
    df["suspicion_flags"] = df[flags_cols].apply(lambda r: ",".join([c for c,v in r.items() if v==1]), axis=1)

    keep = [
        "member_id","txn_count","inflow","outflow","pct_cash","pct_odd_hours","counterparties",
        "flag_high_cash","flag_odd_hours","flag_rapid_io","flag_many_cpty","flags_total","suspicion_flags"
    ]
    for c in keep:
        if c not in df.columns:
            df[c] = pd.NA
    return df[keep].sort_values(["flags_total","txn_count"], ascending=[False, False])

# ----------------------- Filing helpers / status -----------------------

def _due_in_days(tx_date: Optional[date], days: int) -> Optional[date]:
    if not tx_date:
        return None
    return tx_date + timedelta(days=days)

def str_filing_table(where_sql: str = "", params: Tuple = ()) -> pd.DataFrame:
    """
    Build a filing table for STR candidates with a deadline from config.frc.str_deadline_days.
    Uses last_activity (if available) as suspicion_date; otherwise None.
    """
    cfg = _cfg()
    deadline_days = int(getattr(getattr(cfg, "frc", object()), "str_deadline_days", 2))

    cand = str_candidates(where_sql=where_sql, params=params)
    if cand.empty:
        return pd.DataFrame(columns=["member_id","signals","score","suspicion_date","deadline","status"])

    last_tx = pd.DataFrame()
    if _exists("transactions"):
        try:
            last_tx = query(f"""
                SELECT member_id, MAX(CAST(ts AS DATE)) AS last_activity
                FROM transactions
                {_where(where_sql)}
                GROUP BY 1
            """, params)
        except Exception:
            last_tx = pd.DataFrame(columns=["member_id","last_activity"])

    cand = cand.copy()
    if not last_tx.empty:
        cand = cand.merge(last_tx, on="member_id", how="left")
    cand["suspicion_date"] = cand.get("last_activity", pd.Series([pd.NaT]*len(cand))).apply(_safe_dt)
    cand["deadline"] = cand["suspicion_date"].apply(lambda d: _due_in_days(d, deadline_days))

    today = date.today()
    def _status(deadline):
        if deadline is None:
            return "Pending"
        if deadline < today:
            return "Overdue"
        return "Due"

    cand["status"] = cand["deadline"].apply(_status)
    if "score" not in cand.columns:
        cand["score"] = cand["flags_total"].fillna(0)
    if "signals" not in cand.columns:
        cand["signals"] = cand["suspicion_flags"].fillna("")
    return cand[["member_id","signals","score","suspicion_date","deadline","status"]].sort_values(
        ["status","deadline"], ascending=[True, True]
    )

def ctr_filing_table(where_sql: str = "", params: Tuple = ()) -> pd.DataFrame:
    """
    Build CTR filing rows from weekly aggregates (deadline at week_end).
    """
    weekly = ctr_weekly_aggregates(where_sql=where_sql, params=params)
    if weekly.empty:
        return pd.DataFrame(columns=["member_id","week_start","week_end","cash_sum","txn_count","deadline","status"])

    weekly["deadline"] = weekly["week_end"]
    today = date.today()
    weekly["status"] = weekly["deadline"].apply(lambda d: "Overdue" if _safe_dt(d) and _safe_dt(d) < today else "Due")
    return weekly[["member_id","week_start","week_end","cash_sum","txn_count","deadline","status"]]

def filing_checklist() -> pd.DataFrame:
    """
    Quick compliance checklist & key deadlines from config.
    """
    cfg = _cfg()
    rows = [
        {"item":"STR Filing Deadline (days from suspicion)","value":getattr(cfg.frc, "str_deadline_days", 2)},
        {"item":"CTR Threshold (KES)","value":getattr(cfg.frc, "ctr_threshold_kes", 1_900_000)},
        {"item":"Sanctions Freezing (hours)","value":getattr(cfg.frc, "sanctions_freezing_hours", 24)},
        {"item":"Annual Compliance Report Due (MM-DD)","value":getattr(cfg.frc, "annual_report_due", "01-31")},
        {"item":"Record Retention (years)","value":getattr(cfg.frc, "record_retention_years", 7)},
    ]
    return pd.DataFrame(rows)

# ----------------------- goAML XML stubs -----------------------

def generate_goaml_str_xml(member_id: str, suspicion_date: Optional[date], signals: str) -> str:
    sd = (suspicion_date or date.today()).strftime("%Y-%m-%d")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<goAMLMessage>
  <Report>
    <ReportType>STR</ReportType>
    <SubmissionDate>{date.today().strftime("%Y-%m-%d")}</SubmissionDate>
    <ReportingPersonRole>MLRO</ReportingPersonRole>
  </Report>
  <Subjects>
    <Subject>
      <MemberID>{member_id}</MemberID>
      <SuspicionDate>{sd}</SuspicionDate>
      <Indicators>{signals}</Indicators>
    </Subject>
  </Subjects>
</goAMLMessage>
""".strip()

def generate_goaml_ctr_xml(member_id: str, week_start: date, week_end: date, cash_sum: float, txn_count: int) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<goAMLMessage>
  <Report>
    <ReportType>CTR</ReportType>
    <SubmissionDate>{date.today().strftime("%Y-%m-%d")}</SubmissionDate>
  </Report>
  <Transactions>
    <WeeklyAggregate>
      <MemberID>{member_id}</MemberID>
      <WeekStart>{pd.to_datetime(week_start).date()}</WeekStart>
      <WeekEnd>{pd.to_datetime(week_end).date()}</WeekEnd>
      <CashSum>{float(cash_sum):.2f}</CashSum>
      <TransactionCount>{int(txn_count)}</TransactionCount>
    </WeeklyAggregate>
  </Transactions>
</goAMLMessage>
""".strip()

# ----------------------- Submissions register (goAML uploads) -----------------------

def ensure_submission_schema() -> None:
    """
    Minimal, constraint-free register for submissions (STR/CTR).
    """
    execute("""
        CREATE TABLE IF NOT EXISTS frc_submissions(
          submission_id BIGINT,
          sub_type VARCHAR,       -- 'STR' | 'CTR'
          reference VARCHAR,      -- free text identifier (member_id / week label)
          payload_xml VARCHAR,    -- XML payload (stub or final)
          status VARCHAR,         -- 'Draft' | 'Submitted' | 'Acknowledged' | 'Rejected'
          notes VARCHAR,
          created_at TIMESTAMP DEFAULT now(),
          updated_at TIMESTAMP
        )
    """)

def record_submission(sub_type: str,
                      reference: str,
                      payload_xml: str,
                      status: str = "Draft",
                      notes: Optional[str] = None) -> int:
    """
    Insert a submission row and return its ID.
    """
    ensure_submission_schema()
    sid = _next_id("frc_submissions", "submission_id")
    execute("""
        INSERT INTO frc_submissions(submission_id, sub_type, reference, payload_xml, status, notes, created_at, updated_at)
        VALUES (?,?,?,?,?,?, now(), NULL)
    """, (sid, sub_type, reference, payload_xml, status, notes))
    return sid

def list_submissions(sub_type: Optional[str] = None,
                     status: Optional[str] = None,
                     limit: int = 1000) -> pd.DataFrame:
    ensure_submission_schema()
    where: List[str] = []
    params: List[Any] = []
    if sub_type:
        where.append("LOWER(sub_type) = LOWER(?)")
        params.append(sub_type)
    if status:
        where.append("LOWER(status) = LOWER(?)")
        params.append(status)
    sql = "SELECT submission_id, sub_type, reference, status, notes, created_at, updated_at FROM frc_submissions"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += f" ORDER BY created_at DESC LIMIT {int(limit)}"
    return query(sql, tuple(params))

def update_submission_status(submission_id: int,
                             new_status: str,
                             notes: Optional[str] = None) -> None:
    ensure_submission_schema()
    execute("""
        UPDATE frc_submissions
           SET status = ?, notes = COALESCE(?, notes), updated_at = now()
         WHERE submission_id = ?
    """, (new_status, notes, int(submission_id)))
