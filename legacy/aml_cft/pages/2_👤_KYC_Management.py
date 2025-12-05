# pages/2_👤_KYC_Management.py
from __future__ import annotations
import io
import streamlit as st
import pandas as pd

from sacco_core.audit import log_page_access, log_action
from sacco_core.navigation import render_sidebar
from sacco_core.state import filters_ui  # date filter still useful for joined Tx signals
from sacco_core.aml.kyc import kyc_overview, kyc_completeness_table, edd_candidates, docs_register

st.set_page_config(page_title="KYC Management", page_icon="👤", layout="wide")
with st.sidebar:
    render_sidebar()

# Page access audit
try:
    log_page_access(user=st.session_state.get("user_id","demo_user"),
                    role=st.session_state.get("user_role","AML_Officer"),
                    page="KYC_Management")
except Exception:
    pass

st.title("👤 KYC Management")
st.markdown("---")

# Top KPIs
ov = kyc_overview()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Members", f"{ov['total']:,}")
c2.metric("Missing KYC", f"{ov['missing']:,}")
c3.metric("PEP (flagged)", f"{ov['pep']:,}")
c4.metric("High Risk", f"{ov['high']:,}")

# Global filters (used by EDD joins if needed)
filters_ui("Global Date Filter (for joined signals)")

# Tabs
tab_hint = st.session_state.get("nav_tab_hint")
tab_labels = ["KYC Verification", "Enhanced Due Diligence", "Docs & Attestations"]
idx = tab_labels.index(tab_hint) if tab_hint in tab_labels else 0
t1, t2, t3 = st.tabs(tab_labels)

# ---- KYC Verification ----
with t1:
    st.subheader("🧾 KYC Completeness")
    df = kyc_completeness_table()
    if df.empty:
        st.info("No member records or KYC fields unavailable.")
    else:
        colf1, colf2 = st.columns([2,1])
        with colf1:
            min_pct = st.slider("Minimum completeness (%)", 0, 100, 0, 1)
        with colf2:
            only_missing = st.checkbox("Show only incomplete", value=True)
        view = df.copy()
        if only_missing:
            view = view[view["completeness_pct"] < 100]
        view = view[view["completeness_pct"] >= min_pct]
        st.dataframe(view, use_container_width=True, height=420)

        # Export
        def _csv(x): return x.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Export Completeness (CSV)", data=_csv(view),
                           file_name="kyc_completeness.csv", use_container_width=True)

# ---- Enhanced Due Diligence ----
with t2:
    st.subheader("🔎 EDD Candidates")
    cand = edd_candidates()
    if cand.empty:
        st.success("No EDD candidates detected under current data.")
    else:
        st.dataframe(cand, use_container_width=True, height=420)
        st.download_button("⬇️ Export EDD Candidates (CSV)", data=cand.to_csv(index=False).encode("utf-8"),
                           file_name="edd_candidates.csv", use_container_width=True)

    # Action log stub
    if st.button("📌 Log EDD review snapshot"):
        try:
            log_action("edd_snapshot", user=st.session_state.get("user_id","demo_user"),
                       payload={"rows": min(50, len(cand))})
        except Exception:
            pass
        st.success("EDD snapshot logged.")

# ---- Documents & Attestations ----
with t3:
    st.subheader("📂 Documents & Attestations")
    docs = docs_register()
    if docs.empty:
        st.info("No documents found.")
    else:
        st.dataframe(docs, use_container_width=True, height=420)
        # Quick filters
        if "status" in docs.columns:
            s = st.multiselect("Filter by status", sorted(docs["status"].dropna().unique().tolist()))
            if s:
                docs = docs[docs["status"].isin(s)]
        st.download_button("⬇️ Export Docs Register (CSV)", data=docs.to_csv(index=False).encode("utf-8"),
                           file_name="docs_register.csv", use_container_width=True)
