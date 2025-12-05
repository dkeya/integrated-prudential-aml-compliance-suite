# pages/1_🏠_AML_Dashboard.py
from __future__ import annotations
import io
import streamlit as st
import pandas as pd

from sacco_core.db import query
from sacco_core.state import filters_ui, where_and_params
from sacco_core.audit import log_page_access, log_action
from sacco_core.aml.dashboard import (
    get_overview_kpis,
    inflow_outflow_trend,
    compliance_snapshot,
    realtime_alerts,
)

st.set_page_config(page_title="AML Dashboard", layout="wide")
st.title("AML/CFT — Executive Overview")
st.markdown("---")

# --- Page access audit (mirrors Prudential patterns) ---
try:
    log_page_access(user=st.session_state.get("user_id","demo_user"),
                    role=st.session_state.get("user_role","AML_Officer"),
                    page="AML_Dashboard")
except Exception:
    pass

# --- Shared options across pages (branch/product lists) ---
def _options(sql: str, col: str) -> list[str]:
    try:
        return ["All"] + query(sql)[col].dropna().astype(str).tolist()
    except Exception:
        return ["All"]

st.session_state["branches_options"] = _options("select distinct branch from members order by branch", "branch")
st.session_state["products_options"] = _options("select distinct product from transactions order by product", "product")

# --- Global filters & WHERE ---
filters_ui("Global Filters")
where_sql, params = where_and_params("ts")

# --- Tabs: Executive, Compliance, Real-time Alerts ---
tab_hint = st.session_state.get("nav_tab_hint")
labels = ["Executive Overview", "Compliance Metrics", "Real-time Alerts"]
idx = labels.index(tab_hint) if tab_hint in labels else 0
t1, t2, t3 = st.tabs(labels)

# ---------------- Executive Overview ----------------
with t1:
    k = get_overview_kpis(where_sql, params)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Members", f"{k.members:,}")
    c2.metric("Txns (period)", f"{k.txns_period:,}")
    c3.metric("High-Risk Members", f"{k.high_risk_members:,}")
    c4.metric("PEP Records", f"{k.pep_records:,}")
    c5.metric("Sanctions Records", f"{k.sanctions_records:,}")
    c6.metric("CTR ≥ KES 1.9M (cash, all time)", f"{k.ctr_hits_alltime:,}")

    st.markdown("### 📈 Inflow / Outflow Trend")
    trend = inflow_outflow_trend(where_sql, params)
    if trend.empty:
        st.info("No transactions in the selected window.")
    else:
        st.line_chart(trend.set_index("d")[["inflow", "outflow"]])

    # Export
    def _to_csv(df: pd.DataFrame) -> bytes:
        return df.to_csv(index=False).encode("utf-8")

    colx, coly = st.columns(2)
    colx.download_button("⬇️ Export daily inflow/outflow (CSV)",
                         data=_to_csv(trend),
                         file_name="inflow_outflow_trend.csv",
                         use_container_width=True)
    # Audit action
    if coly.button("📌 Snapshot KPIs"):
        try:
            log_action(event_type="snapshot_kpis", user=st.session_state.get("user_id","demo_user"),
                       payload={"kpis": k.__dict__})
        except Exception:
            pass
        st.success("KPIs snapshot logged.")

# ---------------- Compliance Metrics ----------------
with t2:
    st.markdown("### 🎯 Compliance KPIs")
    snap = compliance_snapshot(where_sql, params)

    c1, c2, c3 = st.columns(3)
    c1.metric("STR SLA (≤ 2 days)", snap["str_sla_status"], snap["str_breaches"] + " breaches" if snap["str_breaches"]!="0" else "—")
    c2.metric("CTR Weekly (cash ≥ KES 1.9M)", "Weeks with hits", snap["ctr_weeks_with_hits"])
    c3.metric("Record Retention (7 years)", snap["retention"], "—")

    st.markdown("#### ⏱️ Deadlines in Focus")
    st.info("• STR: file within 2 days of suspicion • CTR: weekly (cash ≥ KES 1.9M) • Sanctions freezing: within 24 hours")

    # CTR weekly roll (preview)
    st.markdown("#### 📅 CTR Weekly Counts (preview)")
    ctr_week = query(
        """
        with w as (
            select date_trunc('week', ts)::date week_start, count(*) c
            from transactions
            where channel='CASH' and amount >= 1900000
            group by 1
        )
        select week_start, c as ctr_count from w order by week_start desc limit 12
        """
    )
    st.dataframe(ctr_week, use_container_width=True, height=260)

# ---------------- Real-time Alerts ----------------
with t3:
    st.markdown("### 🚨 Latest Alerts")
    feed = realtime_alerts(limit=100, where_sql=where_sql, params=params)
    if feed.empty:
        st.success("No alerts available for the current filters.")
    else:
        grid = feed.copy()
        # Light PII masking example
        try:
            grid["linked_entities"] = grid["linked_entities"].str.replace(r'("customer_id":"\w+")', '"customer_id":"***"', regex=True)
        except Exception:
            pass
        st.dataframe(grid, use_container_width=True, height=420)

        # Export
        def _to_excel(df: pd.DataFrame, sheet="Alerts") -> bytes:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as xw:
                df.to_excel(xw, index=False, sheet_name=sheet)
            return buf.getvalue()

        c1, c2 = st.columns(2)
        c1.download_button("⬇️ Export Alerts (CSV)", data=feed.to_csv(index=False).encode("utf-8"),
                           file_name="alerts_latest.csv", use_container_width=True)
        c2.download_button("⬇️ Export Alerts (XLSX)", data=_to_excel(feed),
                           file_name="alerts_latest.xlsx", use_container_width=True)