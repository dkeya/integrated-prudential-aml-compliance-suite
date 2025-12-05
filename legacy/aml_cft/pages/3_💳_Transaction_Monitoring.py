# pages/3_💳_Transaction_Monitoring.py
from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from sacco_core.navigation import render_sidebar
from sacco_core.state import seed_shared_filters, filters_ui, where_and_params
from sacco_core.aml.transactions import (
    realtime_txns,
    ctr_hits,
    structuring_staircase,
    rapid_movement,
    behavioral_stats,
)

# Page config (show sidebar on this page)
st.set_page_config(
    page_title="Transaction Monitoring",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Sidebar (custom only) ---
# IMPORTANT: render inside the sidebar container to avoid it appearing in the main area
with st.sidebar:
    render_sidebar()

# Shared/global filters state (date range, product, branch, etc.)
seed_shared_filters()

# ---------- Page Title ----------
st.markdown("## 💳 Transaction Monitoring")

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

tabs = st.tabs([
    "📡 Real-time Feed",
    "🏛️ CTR (Single Cash ≥ Threshold)",
    "🧱 Structuring Staircase",
    "⚡ Rapid Movement",
    "🧠 Behavioral Analytics",
])

# ----------------- Real-time Feed -----------------
with tabs[0]:
    st.subheader("📡 Real-time Transactions")
    feed = realtime_txns(limit=300, where_sql=where_sql, params=params)
    if feed.empty:
        st.info("No transactions found for the selected filters.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Count", f"{len(feed):,}")
        with c2:
            st.metric("Avg Amt (abs)", f"{feed['amount'].abs().mean():,.0f}" if 'amount' in feed else "—")
        with c3:
            st.metric("Max Amt", f"{feed['amount'].abs().max():,.0f}" if 'amount' in feed else "—")
        with c4:
            by_ch = (feed['channel'].value_counts().head(1).index[0]
                     if 'channel' in feed and not feed['channel'].empty else "—")
            st.metric("Top Channel", by_ch)

        st.dataframe(feed, use_container_width=True, height=420)
        st.download_button(
            "⬇️ Export CSV",
            feed.to_csv(index=False).encode("utf-8"),
            "realtime_txns.csv",
            mime="text/csv",
            use_container_width=True,
        )

# ----------------- CTR Hits -----------------
with tabs[1]:
    st.subheader("🏛️ CTR: Single Cash Transaction ≥ Threshold")
    ctr = ctr_hits(where_sql=where_sql, params=params)
    if ctr.empty:
        st.info("No CTR-eligible transactions for the selected filters.")
    else:
        st.dataframe(ctr, use_container_width=True, height=420)
        st.download_button(
            "⬇️ Export CSV",
            ctr.to_csv(index=False).encode("utf-8"),
            "ctr_hits.csv",
            mime="text/csv",
            use_container_width=True,
        )

# ----------------- Structuring Staircase -----------------
with tabs[2]:
    st.subheader("🧱 Structuring Staircase (rolling cash-in by member)")
    c1, c2, c3 = st.columns([1, 1, 1])
    window_days = c1.number_input("Window (days)", min_value=3, max_value=30, step=1, value=7)
    unit_kes = c2.number_input("Unit (KES)", min_value=10_000, max_value=5_000_000, step=10_000, value=150_000)
    near_ratio = c3.slider("Near-unit ratio", min_value=0.1, max_value=1.0, value=0.8, step=0.05)

    stairs = structuring_staircase(
        window_days=int(window_days),
        unit_kes=int(unit_kes),
        near_ratio=float(near_ratio),
        where_sql=where_sql,
        params=params,
    )
    if stairs.empty:
        st.info("No structuring staircase patterns detected for the selected filters.")
    else:
        st.dataframe(stairs, use_container_width=True, height=300)
        st.download_button(
            "⬇️ Export CSV",
            stairs.to_csv(index=False).encode("utf-8"),
            "structuring_staircase.csv",
            mime="text/csv",
            use_container_width=True,
        )

        # Visualize a selected member’s rolling cash-in vs unit
        member_list = stairs["member_id"].astype(str).unique().tolist() if "member_id" in stairs else []
        if member_list:
            sel = st.selectbox("Member", member_list)
            seg = stairs[stairs["member_id"].astype(str) == str(sel)].sort_values("day")
            if not seg.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=seg["day"], y=seg["cash_in"], mode="lines+markers", name="Rolling Cash-in"
                ))
                if "near_flag" in seg.columns:
                    near_seg = seg[seg["near_flag"] == True]
                    fig.add_trace(go.Scatter(
                        x=near_seg["day"], y=near_seg["cash_in"],
                        mode="markers", name="Near-unit", marker=dict(size=10, symbol="star")
                    ))
                fig.add_hline(y=unit_kes, line_dash="dot",
                              annotation_text="Unit", annotation_position="top left")
                fig.update_layout(
                    height=400,
                    margin=dict(l=10, r=10, t=40, b=10),
                    title=f"Structuring view — Member {sel}",
                    yaxis_title="KES (rolling cash-in)"
                )
                st.plotly_chart(fig, use_container_width=True)

# ----------------- Rapid Movement -----------------
with tabs[3]:
    st.subheader("⚡ Rapid Movement (inflow → outflow within N days)")
    days = st.slider("Window (days)", 3, 30, 5, 1)
    pct = st.slider("Outflow / Inflow ≥", 0.1, 1.0, 0.6, 0.05)
    rm = rapid_movement(days=int(days), pct_of_balance=float(pct), where_sql=where_sql, params=params)
    if rm.empty:
        st.info("No rapid movement patterns found for the selected filters.")
    else:
        st.dataframe(rm, use_container_width=True, height=400)
        st.download_button(
            "⬇️ Export CSV",
            rm.to_csv(index=False).encode("utf-8"),
            "rapid_movement.csv",
            mime="text/csv",
            use_container_width=True,
        )

# ----------------- Behavioral Analytics -----------------
with tabs[4]:
    st.subheader("🧠 Behavioral Analytics (per member)")
    beh = behavioral_stats(where_sql=where_sql, params=params)
    if beh.empty:
        st.info("No behavioral stats available.")
    else:
        st.dataframe(beh, use_container_width=True, height=350)
        st.download_button(
            "⬇️ Export CSV",
            beh.to_csv(index=False).encode("utf-8"),
            "behavioral_stats.csv",
            mime="text/csv",
            use_container_width=True,
        )

        # Simple viz: txn_count vs avg_amt (bubble ~ cash_pct if present)
        if {"txn_count", "avg_amt"}.issubset(beh.columns):
            fig = px.scatter(
                beh,
                x="txn_count",
                y="avg_amt",
                size=("cash_pct" if "cash_pct" in beh.columns else None),
                hover_data=["member_id"],
                title="Transactions vs Average Amount (bubble ~ cash %)",
            )
            st.plotly_chart(fig, use_container_width=True)
