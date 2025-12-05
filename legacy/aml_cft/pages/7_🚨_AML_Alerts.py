# pages/7_🚨_AML_Alerts.py
from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.express as px

from sacco_core.navigation import render_sidebar
from sacco_core.state import seed_shared_filters, filters_ui, where_and_params
from sacco_core.aml.alerts import alerts_feed, rules_summary

# Page config (show sidebar on this page)
st.set_page_config(
    page_title="AML Alerts",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Sidebar (custom only) ---
with st.sidebar:
    render_sidebar()

# Shared/global filters state
seed_shared_filters()

st.markdown("## 🚨 AML Alert Management")

# Global filters (shared across pages)
branch, product, d_from, d_to = filters_ui()
where_sql, params = where_and_params(
    date_col="ts",
    date_from=d_from,
    date_to=d_to,
    branch=branch,
    product=product,
    table_hint="transactions",
)

# Cache alerts retrieval for perf and to avoid DataFrame truthiness across tabs
@st.cache_data(show_spinner=False)
def _get_alerts(_where_sql: str, _params: tuple) -> pd.DataFrame:
    return alerts_feed(where_sql=_where_sql, params=_params)

feed = _get_alerts(where_sql, params)

tabs = st.tabs(["📡 Feed", "📘 Rule Summary", "⬇️ Export"])

# ----------------- Feed -----------------
with tabs[0]:
    st.subheader("📡 Unified Alert Feed")
    if feed.empty:
        st.info("No alerts for the selected filters.")
    else:
        st.dataframe(feed, use_container_width=True, height=420)
        # Quick chart: average score by alert type
        if {"alert_type", "score"}.issubset(feed.columns):
            chart = feed.groupby("alert_type")["score"].mean().reset_index()
            fig = px.bar(chart, x="alert_type", y="score", title="Average Score by Alert Type")
            st.plotly_chart(fig, use_container_width=True)

# ----------------- Summary -----------------
with tabs[1]:
    st.subheader("📘 Rules Summary")
    summ = rules_summary(feed)
    if summ.empty:
        st.info("No rules to summarize.")
    else:
        st.dataframe(summ, use_container_width=True, height=320)

# ----------------- Export -----------------
with tabs[2]:
    st.subheader("⬇️ Export")
    if feed.empty:
        st.info("Nothing to export.")
    else:
        st.download_button(
            "Download feed (CSV)",
            feed.to_csv(index=False).encode("utf-8"),
            "aml_alerts_feed.csv",
            mime="text/csv",
            use_container_width=True,
        )
