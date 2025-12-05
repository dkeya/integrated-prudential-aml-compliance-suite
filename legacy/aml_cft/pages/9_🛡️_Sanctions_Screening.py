# pages/9_🛡️_Sanctions_Screening.py
from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.express as px

from sacco_core.navigation import render_sidebar
from sacco_core.state import seed_shared_filters, filters_ui, where_and_params
from sacco_core.aml.sanctions import (
    sanctions_exact_hits,
    sanctions_fuzzy_hits,
    sanctions_txn_hits,
    save_disposition,
    recent_screenings,
)

# Page config (show sidebar on this page)
st.set_page_config(
    page_title="Sanctions Screening",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Sidebar (custom only) ---
# Render the custom navigation *inside* the sidebar container
with st.sidebar:
    render_sidebar()

# Seed shared filters (keeps date/product/branch filters consistent across pages)
seed_shared_filters()

st.markdown("## 🛡️ Sanctions Screening")

# Global filters (used for context; screening is mostly global)
branch, product, d_from, d_to = filters_ui()

tabs = st.tabs([
    "✅ Exact Name Matches",
    "🔍 Fuzzy Screening (Members)",
    "🔎 Fuzzy Screening (Counterparties)",
    "🗃️ Register (Dispositions)",
])

# ----------------- Exact matches -----------------
with tabs[0]:
    st.subheader("✅ Exact Name Matches (Members ↔ Watchlist)")
    df = sanctions_exact_hits(limit=2000)
    if df.empty:
        st.info("No exact matches detected.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Hits", f"{len(df):,}")
        with c2:
            top_list = (df["list"].value_counts().idxmax()
                        if "list" in df.columns and not df["list"].empty else "—")
            st.metric("Dominant list", str(top_list))

        st.dataframe(df, use_container_width=True, height=420)
        st.download_button(
            "⬇️ Export CSV",
            df.to_csv(index=False).encode("utf-8"),
            "sanctions_exact_hits.csv",
            mime="text/csv",
            use_container_width=True,
        )

# ----------------- Fuzzy (members) -----------------
with tabs[1]:
    st.subheader("🔍 Fuzzy Screening — Members")
    th = st.slider("Similarity threshold", 0.70, 0.99, 0.88, 0.01)
    hits = sanctions_fuzzy_hits(threshold=float(th), source="members")
    if hits.empty:
        st.info("No fuzzy hits (members) at the selected threshold.")
    else:
        st.dataframe(hits, use_container_width=True, height=420)
        st.download_button(
            "⬇️ Export CSV",
            hits.to_csv(index=False).encode("utf-8"),
            "sanctions_fuzzy_members.csv",
            mime="text/csv",
            use_container_width=True,
        )

        # Simple analyzer: similarity distribution
        if "similarity" in hits.columns:
            fig = px.histogram(hits, x="similarity", nbins=20, title="Similarity distribution (members)")
            st.plotly_chart(fig, use_container_width=True)

        # Quick disposition form
        st.markdown("### 📝 Record Disposition")
        with st.form("disp_members"):
            sel = st.selectbox("Pick a row", hits.index.astype(str).tolist())
            status = st.selectbox("Status", ["Open", "Cleared", "Escalated"])
            notes = st.text_input("Notes (optional)")
            submitted = st.form_submit_button("Save disposition")
            if submitted:
                row = hits.loc[int(sel)]
                save_disposition(
                    entity_type="member",
                    entity_id=str(row.get("entity_id", "")),
                    entity_name=str(row.get("entity_name", "")),
                    watch_name=str(row.get("watch_name", "")),
                    similarity=float(row.get("similarity", 0)),
                    list_name=row.get("list"),
                    program=row.get("program"),
                    country=row.get("country"),
                    status=status,
                    notes=notes or None
                )
                st.success("Disposition saved.")

# ----------------- Fuzzy (counterparties) -----------------
with tabs[2]:
    st.subheader("🔎 Fuzzy Screening — Counterparties (from transactions)")
    th2 = st.slider("Similarity threshold (counterparties)", 0.70, 0.99, 0.90, 0.01)
    chits = sanctions_txn_hits(threshold=float(th2))
    if chits.empty:
        st.info("No fuzzy hits (counterparties) at the selected threshold.")
    else:
        st.dataframe(chits, use_container_width=True, height=420)
        st.download_button(
            "⬇️ Export CSV",
            chits.to_csv(index=False).encode("utf-8"),
            "sanctions_fuzzy_counterparties.csv",
            mime="text/csv",
            use_container_width=True,
        )

        if "similarity" in chits.columns:
            fig = px.histogram(chits, x="similarity", nbins=20, title="Similarity distribution (counterparties)")
            st.plotly_chart(fig, use_container_width=True)

        with st.form("disp_cps"):
            sel = st.selectbox("Pick a row", chits.index.astype(str).tolist())
            status = st.selectbox("Status", ["Open", "Cleared", "Escalated"], key="cp_status")
            notes = st.text_input("Notes (optional)", key="cp_notes")
            submitted = st.form_submit_button("Save disposition", use_container_width=True)
            if submitted:
                row = chits.loc[int(sel)]
                save_disposition(
                    entity_type="counterparty",
                    entity_id=str(row.get("member_id", "")),
                    entity_name=str(row.get("counterparty", "")),
                    watch_name=str(row.get("watch_name", "")),
                    similarity=float(row.get("similarity", 0)),
                    list_name=row.get("list"),
                    program=row.get("program"),
                    country=row.get("country"),
                    status=status,
                    notes=notes or None
                )
                st.success("Disposition saved.")

# ----------------- Register -----------------
with tabs[3]:
    st.subheader("🗃️ Recent Screenings / Dispositions")
    reg = recent_screenings(limit=300)
    if reg.empty:
        st.info("No dispositions recorded yet.")
    else:
        st.dataframe(reg, use_container_width=True, height=420)
        st.download_button(
            "⬇️ Export Register CSV",
            reg.to_csv(index=False).encode("utf-8"),
            "sanctions_screenings_register.csv",
            mime="text/csv",
            use_container_width=True,
        )
