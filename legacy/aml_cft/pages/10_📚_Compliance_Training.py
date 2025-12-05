# pages/10_📚_Compliance_Training.py
from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
from pathlib import Path  # 🔹 for local file checks

from sacco_core.navigation import render_sidebar
from sacco_core.state import seed_shared_filters  # reuse branch options if members has branch
from sacco_core.aml.training import (
    ensure_schema,
    seed_if_empty,
    list_courses, upsert_course,
    assign_course, list_assignments, mark_completed, expire_overdue,
    add_certification, list_certifications, cert_reminders,
    add_article, search_kb,
    completion_trend, save_upload,
)

# Page config (show sidebar on this page)
st.set_page_config(
    page_title="Training & Awareness",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Sidebar (custom only) ---
with st.sidebar:
    render_sidebar()

# Light seed
seed_shared_filters()     # reuses branch list if available
ensure_schema()
seed_if_empty()
expire_overdue()

st.markdown("## 📚 Training & Awareness")

# 🔹 Precompute a default reminder badge (non-intrusive; slider below still works)
_DEFAULT_REMINDER_DAYS = 60
try:
    _due_df = cert_reminders(int(_DEFAULT_REMINDER_DAYS))
    _badge = 0
    if not _due_df.empty and "due_status" in _due_df.columns:
        _badge = len(_due_df[_due_df["due_status"].isin(["Expiring Soon", "Expired"])])
except Exception:
    _badge = 0

tabs = st.tabs([
    "👥 Staff Training",
    f"🎓 Certifications ({_badge})",  # 🔹 tab badge
    "📖 Knowledge Base",
    "📈 Trends",
])

# ---------------------------- Staff Training ----------------------------
with tabs[0]:
    st.subheader("👥 Staff Training — Assignments & Completions")

    # Left: Catalog; Right: Assignments
    c1, c2 = st.columns([1, 2])

    with c1:
        st.markdown("### 📦 Course Catalog")
        cat = list_courses(active_only=False)
        st.dataframe(cat, use_container_width=True, height=280)

        with st.expander("➕ Add / Update Course"):
            mode = st.radio("Mode", ["Add new", "Update existing"], horizontal=True, key="course_mode_radio")
            if mode == "Add new":
                cid = None
            else:
                cid = st.selectbox(
                    "Course to update",
                    [None] + (cat["course_id"].astype(int).tolist() if not cat.empty else []),
                    key="course_to_update_select",
                )
            title = st.text_input("Title", key="course_title_input")
            category = st.text_input("Category", value="Compliance", key="course_category_input")
            provider = st.text_input("Provider", value="Internal", key="course_provider_input")
            hours = st.number_input("Hours", min_value=0.0, value=1.0, step=0.5, key="course_hours_input")
            mode_str = st.selectbox("Delivery", ["eLearning", "Workshop", "Webinar"], key="course_delivery_select")
            active = st.checkbox("Active", value=True, key="course_active_checkbox")
            if st.button("💾 Save course", use_container_width=True, key="course_save_btn"):
                new_id = upsert_course(cid, title, category, provider, hours, mode_str, active)
                st.success(f"Saved course (ID={new_id}).")
                st.rerun()

    with c2:
        st.markdown("### 🗂️ Assignments")
        filt_c1, filt_c2, filt_c3 = st.columns([1,1,1])
        status = filt_c1.selectbox("Status", ["All","Assigned","In-Progress","Completed","Expired"], key="assign_status_select")
        branch_opt = ["All"] + st.session_state.get("flt_branch_opts", [])[1:]
        branch = filt_c2.selectbox("Branch (if available)", branch_opt, key="assign_branch_select")
        q_member = filt_c3.text_input("Search member (name contains)", key="assign_search_member_input")

        df = list_assignments(status=status, branch=branch, search_member=q_member)
        st.dataframe(df, use_container_width=True, height=360)

        # 🔹 Evidence quick-view / download (optional, minimal UI)
        if not df.empty and "attachment_path" in df.columns and df["attachment_path"].notna().any():
            with st.expander("🔎 View Evidence (Assignments)"):
                avail = df[df["attachment_path"].notna()][["assignment_id", "attachment_path"]]
                sel_aid = st.selectbox(
                    "Choose assignment",
                    avail["assignment_id"].astype(int).tolist(),
                    key="assign_evidence_select"
                )
                path_str = avail[avail["assignment_id"] == sel_aid]["attachment_path"].iloc[0]
                st.caption(f"File: `{path_str}`")
                # Try to load & offer download
                try:
                    data_root = Path(__file__).resolve().parents[1] / "data"
                    fpath = (data_root / path_str).resolve()
                    if fpath.exists() and fpath.is_file():
                        with open(fpath, "rb") as fh:
                            st.download_button(
                                "⬇️ Download evidence",
                                fh.read(),
                                file_name=fpath.name,
                                key="assign_evidence_download_btn"
                            )
                        # Preview images inline
                        if fpath.suffix.lower() in [".png", ".jpg", ".jpeg"]:
                            st.image(str(fpath), use_column_width=True)
                    else:
                        st.info("File not found on disk (was it moved?).")
                except Exception:
                    st.info("Could not open file (path may be outside app).")

        # Assign a course
        with st.expander("➕ Assign Course"):
            member_id = st.text_input("Member ID", key="assign_member_id_input")
            course_id = st.selectbox(
                "Course",
                (cat["course_id"].astype(int).tolist() if not cat.empty else []),
                key="assign_course_select"
            )
            due_on = st.date_input("Due on", value=date.today() + timedelta(days=14), key="assign_due_on_date")
            notes = st.text_area("Notes", placeholder="Optional assignment note…", key="assign_notes_area")
            if st.button("📌 Assign", use_container_width=True, key="assign_course_btn"):
                if member_id.strip():
                    aid = assign_course(member_id.strip(), int(course_id), due_on, notes or None)
                    st.success(f"Assignment created (ID={aid}).")
                    st.rerun()
                else:
                    st.warning("Please enter Member ID.")

        # Mark completion
        with st.expander("✅ Mark Completed"):
            if df.empty:
                st.info("No assignments in current view.")
            else:
                open_rows = df[df["status"].isin(["Assigned","In-Progress"])]
                if open_rows.empty:
                    st.info("No open assignments to complete.")
                else:
                    sel = st.selectbox("Assignment", open_rows["assignment_id"].tolist(), key="complete_assignment_select")
                    score = st.number_input("Score", min_value=0.0, max_value=100.0, value=100.0, step=0.5, key="complete_score_input")
                    up = st.file_uploader("Upload evidence (optional)", type=["pdf","png","jpg","jpeg"], key="complete_evidence_uploader")
                    completed_on = st.date_input("Completed on", value=date.today(), key="complete_completed_on_date")
                    if st.button("✔️ Record Completion", use_container_width=True, key="complete_record_btn"):
                        path = save_upload(up) if up else None
                        mark_completed(int(sel), score=score, evidence_path=path, completed_on=completed_on)
                        st.success("Completion recorded.")
                        st.rerun()

# ---------------------------- Certifications ----------------------------
with tabs[1]:
    st.subheader("🎓 Certifications — Register & Reminders")

    c1, c2 = st.columns([2, 1])

    with c1:
        filt1, filt2, filt3 = st.columns([1,1,1])
        status = filt1.selectbox("Status", ["All","Valid","Expiring","Expired","Revoked"], key="cert_status_select")
        branch_opt = ["All"] + st.session_state.get("flt_branch_opts", [])[1:]
        branch = filt2.selectbox("Branch (if available)", branch_opt, key="cert_branch_select")
        q_member = filt3.text_input("Search member (name contains)", key="cert_search_member_input")
        certs = list_certifications(branch=branch, status=status, search_member=q_member)
        st.dataframe(certs, use_container_width=True, height=380)
        st.download_button("⬇️ Export CSV", certs.to_csv(index=False).encode("utf-8"),
                           "certifications.csv", mime="text/csv", use_container_width=True, key="cert_export_btn")

        # 🔹 Certificate quick-view / download block
        if not certs.empty and "certificate_path" in certs.columns and certs["certificate_path"].notna().any():
            with st.expander("🔎 View Certificate"):
                availc = certs[certs["certificate_path"].notna()][["cert_id", "certificate_path"]]
                sel_cid = st.selectbox(
                    "Choose certification",
                    availc["cert_id"].astype(int).tolist(),
                    key="cert_file_select"
                )
                cpath_str = availc[availc["cert_id"] == sel_cid]["certificate_path"].iloc[0]
                st.caption(f"File: `{cpath_str}`")
                try:
                    data_root = Path(__file__).resolve().parents[1] / "data"
                    fpath = (data_root / cpath_str).resolve()
                    if fpath.exists() and fpath.is_file():
                        with open(fpath, "rb") as fh:
                            st.download_button(
                                "⬇️ Download certificate",
                                fh.read(),
                                file_name=fpath.name,
                                key="cert_file_download_btn"
                            )
                        if fpath.suffix.lower() in [".png", ".jpg", ".jpeg"]:
                            st.image(str(fpath), use_column_width=True)
                    else:
                        st.info("File not found on disk (was it moved?).")
                except Exception:
                    st.info("Could not open file (path may be outside app).")

    with c2:
        st.markdown("### ⏰ Reminders")
        within = st.slider("Expiring within (days)", min_value=7, max_value=180, value=_DEFAULT_REMINDER_DAYS, step=7, key="cert_within_slider")
        due = cert_reminders(int(within))
        st.dataframe(due, use_container_width=True, height=240)

        st.markdown("### ➕ Add Certification")
        cmid = st.text_input("Member ID", key="cert_mid_input")
        cname = st.text_input("Certification Name", key="cert_name_input")
        cprov = st.text_input("Provider", value="Internal/External", key="cert_provider_input")
        issued = st.date_input("Issued on", value=date.today(), key="cert_issued_date")
        expires = st.date_input("Expires on", value=date.today() + timedelta(days=365), key="cert_expires_date")
        cfile = st.file_uploader("Upload certificate (optional)", type=["pdf","png","jpg","jpeg"], key="cert_file_uploader")
        cnotes = st.text_area("Notes", key="cert_notes_area")
        if st.button("💾 Save Certification", use_container_width=True, key="cert_save_btn"):
            if cmid.strip() and cname.strip():
                p = save_upload(cfile) if cfile else None
                cid = add_certification(cmid.strip(), cname.strip(), cprov or None, issued, expires, "Valid", p, cnotes or None)
                st.success(f"Certification saved (ID={cid}).")
                st.rerun()
            else:
                st.warning("Member ID and Certification Name are required.")

# ---------------------------- Knowledge Base ----------------------------
with tabs[2]:
    st.subheader("📖 Knowledge Base — Registry & Search")

    s1, s2, s3 = st.columns([2,1,1])
    q = s1.text_input("Search text", key="kb_search_text")
    cat = s2.text_input("Category filter (optional)", key="kb_category_filter")
    tag = s3.text_input("Tag contains (optional)", key="kb_tag_filter")
    res = search_kb(q=q or None, category=(cat or None), tag=(tag or None))
    st.dataframe(res, use_container_width=True, height=360)

    with st.expander("➕ Add Article"):
        kt = st.text_input("Title", key="kb_add_title")
        kb = st.text_area("Body (short guide / notes)", key="kb_add_body")
        kc = st.text_input("Category", value="Guides", key="kb_add_category")
        ku = st.text_input("URL (optional)", key="kb_add_url")
        ktags = st.text_input("Tags (comma-separated)", key="kb_add_tags")
        if st.button("📌 Save Article", use_container_width=True, key="kb_add_save_btn"):
            if kt.strip() and kb.strip():
                kid = add_article(kt.strip(), kb.strip(), kc or None, ku or None, ktags or None)
                st.success(f"Article saved (ID={kid}).")
                st.rerun()
            else:
                st.warning("Title and Body are required.")

# ---------------------------- Trends ----------------------------
with tabs[3]:
    st.subheader("📈 Training Completion Trends")
    by = st.radio("Group by", ["month","week","day"], horizontal=True, index=0, key="trend_groupby_radio")
    tr = completion_trend(by=by)
    if tr.empty:
        st.info("No completion data yet.")
    else:
        st.dataframe(tr, use_container_width=True, height=260)
        fig = px.line(tr, x="period", y="completions", markers=True, title=f"Completions by {by.title()}")
        st.plotly_chart(fig, use_container_width=True)
        if "avg_score" in tr.columns:
            fig2 = px.bar(tr, x="period", y="avg_score", title=f"Average Score by {by.title()}")
            st.plotly_chart(fig2, use_container_width=True)
