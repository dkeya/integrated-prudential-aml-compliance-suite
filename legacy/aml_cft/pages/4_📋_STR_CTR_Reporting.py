# pages/4_📋_STR_CTR_Reporting.py
from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.express as px

from sacco_core.navigation import render_sidebar
from sacco_core.state import seed_shared_filters, filters_ui, where_and_params
from sacco_core.utils.export import export_buttons, df_to_csv_bytes
from sacco_core.security import guard_ui, has_perm
from sacco_core.aml.reporting import (
    ctr_single_hits,
    ctr_weekly_summary,
    str_candidates,
    filing_checklist,
    generate_goaml_str_xml,
    generate_goaml_ctr_xml,
    str_filing_table,
    ctr_filing_table,
)
from sacco_core.aml.submissions import save_submission, list_submissions
from sacco_core.alerts.emailer import send_deadline_digest
from sacco_core.config import get_config

# Page config (show sidebar on this page)
st.set_page_config(
    page_title="STR / CTR Reporting",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Sidebar (custom only) ---
with st.sidebar:
    render_sidebar()

# Shared/global filters state
seed_shared_filters()

st.markdown("## 📋 Regulatory Reporting (STR / CTR / goAML)")

branch, product, d_from, d_to = filters_ui()
where_sql, params = where_and_params(
    date_col="ts",
    date_from=d_from,
    date_to=d_to,
    branch=branch,
    product=product,
    table_hint="transactions",
)

cfg = get_config()

tabs = st.tabs([
    "🏛️ CTR (Single cash ≥ threshold)",
    "🚩 STR Candidates (Rules-based)",
    "🗓️ Deadlines & Checklist",
    "📤 Submissions Register",
])

# ----------------- CTR -----------------
with tabs[0]:
    st.subheader(f"🏛️ CTR Candidates — Cash ≥ {cfg.frc.ctr_threshold_kes:,} KES")
    ctr = ctr_single_hits(where_sql=where_sql, params=params)
    if ctr.empty:
        st.info("No CTR-eligible transactions for the selected filters.")
    else:
        export_buttons(ctr, basename="ctr_candidates", height=420)

        wk = ctr_weekly_summary(where_sql=where_sql, params=params)
        if not wk.empty:
            fig = px.bar(wk, x="iso_week", y="count_hits", title="Weekly CTR Counts")
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📄 Generate CTR XML & Queue Submission")
        if has_perm("file_ctr"):
            colx1, colx2 = st.columns([2, 1])
            with colx1:
                sel = st.selectbox(
                    "Pick a CTR row to generate XML",
                    [f"{r.member_id} | {r.ts} | {r.amount}" for r in ctr.itertuples()],
                    key="ctr_xml_select",
                )
            with colx2:
                if st.button("Generate & Queue", use_container_width=True, key="ctr_xml_btn"):
                    row = ctr.iloc[[idx for idx, s in enumerate(
                        [f"{r.member_id} | {r.ts} | {r.amount}" for r in ctr.itertuples()]
                    ) if s == sel][0]]
                    mid = str(row.get("member_id", "NA"))
                    xml = generate_goaml_ctr_xml(
                        member_id=mid,
                        week_start=pd.to_datetime(row.get("ts")).date(),
                        week_end=pd.to_datetime(row.get("ts")).date(),
                        cash_sum=float(row.get("amount", 0.0)),
                        txn_count=1,
                    )
                    sid = save_submission("CTR", key_ref=mid, xml_text=xml, status="Queued")
                    st.success(f"Queued CTR submission (ID={sid}).")
        else:
            st.info("You need `file_ctr` permission to generate/queue CTR XML (MLRO/Officer/Admin).")

# ----------------- STR -----------------
with tabs[1]:
    st.subheader("🚩 STR Candidates — rules-based signals")
    cand = str_candidates(where_sql=where_sql, params=params)
    if cand.empty:
        st.info("No STR candidates surfaced for the selected filters.")
    else:
        export_buttons(cand, basename="str_candidates", height=420)

        st.markdown("### 📄 Generate STR XML & Queue Submission")
        if has_perm("file_str"):
            c1, c2 = st.columns([2, 1])
            with c1:
                sel = st.selectbox(
                    "Pick a member_id to generate STR XML",
                    cand["member_id"].astype(str).tolist(),
                    key="str_xml_sel",
                )
            with c2:
                if st.button("Generate & Queue", use_container_width=True, key="str_xml_btn"):
                    row = cand[cand["member_id"].astype(str) == str(sel)].head(1)
                    signals = str(row.get("suspicion_flags", "Possible suspicious activity").values[0])
                    ft = str_filing_table(where_sql=where_sql, params=params)
                    ft_row = ft[ft["member_id"].astype(str) == str(sel)].head(1)
                    susp = None
                    if not ft_row.empty:
                        susp = ft_row["suspicion_date"].iloc[0]
                    xml = generate_goaml_str_xml(member_id=str(sel), suspicion_date=susp, signals=signals)
                    sid = save_submission("STR", key_ref=str(sel), xml_text=xml, status="Queued")
                    st.success(f"Queued STR submission (ID={sid}).")
        else:
            st.info("You need `file_str` permission to generate/queue STR XML (MLRO/Officer/Admin).")

# ----------------- Checklist / Deadlines -----------------
with tabs[2]:
    st.subheader("🗓️ Compliance Checklist & Deadlines")
    chk = filing_checklist()
    st.dataframe(chk, use_container_width=True, height=220)

    st.markdown("### ⛳ Filing tables")
    c1, c2 = st.columns(2)
    with c1:
        st.caption("STR Filing Table")
        sft = str_filing_table(where_sql=where_sql, params=params)
        export_buttons(sft, basename="str_filing_table", height=280)
    with c2:
        st.caption("CTR Filing Table")
        cft = ctr_filing_table(where_sql=where_sql, params=params)
        export_buttons(cft, basename="ctr_filing_table", height=280)

    st.markdown("### ✉️ Email Deadlines Digest")
    recipients = st.text_input("Recipients (comma-separated)", value="mlro@example.com", key="digest_recip")
    if st.button("Send Digest Now", key="digest_send_btn"):
        ok = send_deadline_digest([x.strip() for x in recipients.split(",") if x.strip()], where_sql, params)
        if ok:
            st.success("Digest sent.")
        else:
            st.warning("Email not sent (check Email config in `configs/aml_config.yml`).")

# ----------------- Submissions Register -----------------
with tabs[3]:
    st.subheader("📤 Submissions Register (local queue)")
    subs = list_submissions(limit=300)
    export_buttons(subs, basename="goaml_submissions", height=360)
    st.caption("Tip: if you run the optional FastAPI receiver, you can POST these XML files to your integration endpoint.")
