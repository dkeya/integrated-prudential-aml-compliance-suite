# pages/8_🏛️_MLRO_Portal.py
from __future__ import annotations

import os
import sys
from datetime import date, datetime

import pandas as pd
import streamlit as st

# ============================================================
# 1. Path setup – ensure legacy AML engine is importable
# ============================================================
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

AML_LEGACY_DIR = os.path.join(ROOT_DIR, "legacy", "aml_cft")
if AML_LEGACY_DIR not in sys.path:
    sys.path.append(AML_LEGACY_DIR)

# --- Legacy AML imports ---
from sacco_core.state import seed_shared_filters, filters_ui
from sacco_core.aml.investigations import (
    ensure_schema,
    list_cases,
    create_case,
    get_case,
    update_status,
    update_summary,
    add_comment,
    list_comments,
    timeline,
    save_attachment,
    list_attachments,
    create_case_from_sanction,
)
from sacco_core.aml.sanctions import recent_screenings
from sacco_core.config import get_config  # kept for future use, if needed
try:
    from sacco_core.audit import log_page_access
except Exception:
    log_page_access = None  # optional legacy audit

# --- Unified core imports ---
from core.config import ConfigManager
from core.rbac import RBACManager
from core.audit import audit_logger
from core.sidebar import render_sidebar


# ============================================================
# 2. Auth & module guards + unified sidebar
# ============================================================
if not st.session_state.get("authenticated", False):
    st.error("🔐 Please log in to access this page")
    st.stop()

current_module = st.session_state.get("current_module", "prudential")
if current_module != "aml_cft":
    st.error(
        "This page belongs to the AML / CFT module.\n\n"
        "Please log in via the AML / CFT module on the main portal."
    )
    st.stop()

# Render unified SACCO Pro sidebar
render_sidebar()


# ============================================================
# 3. MLRO Portal Page – unified wrapper
# ============================================================
class MlroPortalPage:
    """
    AML / CFT — MLRO Portal (Case Investigations)

    • Uses legacy investigations engine (cases, comments, attachments, timeline).
    • Integrated into unified SACCO Pro shell (RBAC + audit + sidebar).
    """

    def __init__(self):
        self.config_manager = ConfigManager()
        self.rbac_manager = RBACManager()
        self.audit_logger = audit_logger
        self.config = self.config_manager.load_settings()

        # Try to harmonise both legacy and unified session keys
        self.user = st.session_state.get(
            "user",
            st.session_state.get("user_id", "MLRO"),
        )
        self.role = st.session_state.get(
            "role",
            st.session_state.get("user_role", "MLRO"),
        )
        self.tenant = st.session_state.get("tenant", "Central SACCO")

        if not self._check_access():
            st.stop()

        # Ensure session defaults
        st.session_state.setdefault("selected_case_id", None)

    # ---------------- RBAC + Audit ----------------
    def _check_access(self) -> bool:
        """Check RBAC access and log page access (unified + legacy)."""
        if not st.session_state.get("authenticated", False):
            st.error("Please login to access this page")
            return False

        has_access = self.rbac_manager.check_page_access(
            page_id="8_🏛️_MLRO_Portal.py",
            role=st.session_state.get("role"),
            config=self.config,
        )

        if not has_access:
            st.error("You do not have permission to access this page")

            # Unified audit – unauthorized attempt
            try:
                self.audit_logger.log_action(
                    user=self.user,
                    role=self.role,
                    action="unauthorized_access_attempt",
                    object_type="page",
                    object_id="MLRO_Portal",
                )
            except Exception:
                pass
            return False

        # Unified audit – successful access
        try:
            self.audit_logger.log_action(
                user=self.user,
                role=self.role,
                action="page_access",
                object_type="page",
                object_id="MLRO_Portal",
                extra={"module": "aml_cft", "timestamp": datetime.now().isoformat()},
            )
        except Exception:
            pass

        # Legacy audit (optional)
        if log_page_access is not None:
            try:
                log_page_access(
                    user=st.session_state.get("user_id", self.user),
                    role=st.session_state.get("user_role", self.role),
                    page="MLRO_Portal",
                )
            except Exception:
                pass

        return True

    # ---------------- Main render ----------------
    def run(self):
        # Shared filters + schema
        seed_shared_filters()
        ensure_schema()

        st.markdown("## 🏛️ MLRO Portal — Case Investigations")

        # Global context filters (for narrative / awareness)
        filters_ui("Global Context")

        tabs = st.tabs(
            [
                "📜 Case Register",
                "➕ New Case",
                "🧷 Create From Sanctions Hit",
                "🔎 Case Detail",
            ]
        )

        # -------------------- Case Register --------------------
        with tabs[0]:
            st.subheader("📜 Case Register")

            c1, c2, c3, c4, c5 = st.columns([1.1, 1.1, 1.1, 1, 1])
            status_sel = c1.multiselect(
                "Status",
                ["Open", "Under Review", "Escalated", "Closed"],
                default=["Open", "Under Review"],
            )
            severity_sel = c2.multiselect(
                "Severity", ["Low", "Medium", "High", "Critical"], default=[]
            )
            d_from = c3.date_input("From", value=None)
            d_to = c4.date_input("To", value=None)
            q = c5.text_input(
                "Search (title / entity / summary)",
                value="",
            )

            df = list_cases(
                status=status_sel or None,
                severity=severity_sel or None,
                date_from=d_from or None,
                date_to=d_to or None,
                search=q or None,
            )

            if df.empty:
                st.info("No cases found with current filters.")
            else:
                st.dataframe(df, use_container_width=True, height=420)
                # Select a case to view details
                sel = st.selectbox(
                    "Open case id", [""] + df["case_id"].astype(str).tolist()
                )
                if sel:
                    st.session_state["selected_case_id"] = int(sel)
                    st.success(f"Selected case #{sel}. Go to **Case Detail** tab.")

        # -------------------- New Case --------------------
        with tabs[1]:
            st.subheader("➕ Create New Case (Manual)")
            with st.form("new_case"):
                col1, col2, col3 = st.columns(3)
                title = col1.text_input("Title", "")
                severity = col2.selectbox(
                    "Severity", ["Low", "Medium", "High", "Critical"], index=1
                )
                category = col3.selectbox(
                    "Category",
                    ["Sanctions", "Alerts", "KYC", "Transaction", "Other"],
                    index=4,
                )

                col4, col5, col6 = st.columns(3)
                member_id = col4.text_input("Member ID (optional)")
                entity_name = col5.text_input("Entity Name (optional)")
                due = col6.date_input("Due date", value=None)

                summary = st.text_area("Summary / Narrative", height=120)
                submit = st.form_submit_button(
                    "Create case", type="primary", use_container_width=True
                )

                if submit:
                    if not title.strip():
                        st.error("Title is required.")
                    else:
                        cid = create_case(
                            title=title.strip(),
                            created_by=self.role or "MLRO",
                            summary=summary.strip(),
                            severity=severity,
                            category=category,
                            member_id=member_id.strip() or None,
                            entity_name=entity_name.strip() or None,
                            due_date=due or None,
                            status="Open",
                            source_type="manual",
                            source_ref=None,
                            signals=None,
                        )
                        st.session_state["selected_case_id"] = cid
                        st.success(f"Case #{cid} created.")
                        st.rerun()

        # -------------------- Create from Sanctions Hit --------------------
        with tabs[2]:
            st.subheader("🧷 Promote Sanctions Hit to Case")
            hits = recent_screenings(limit=300)
            if hits.empty:
                st.info(
                    "No sanctions dispositions to promote. Use the Sanctions page first."
                )
            else:
                st.caption(
                    "Tip: Filter in the Sanctions page, record disposition (Open/Escalated), "
                    "then create a case here."
                )
                st.dataframe(hits, use_container_width=True, height=360)
                idx = st.selectbox(
                    "Pick screening row index", [""] + hits.index.astype(str).tolist()
                )
                if idx:
                    row = hits.loc[int(idx)].to_dict()
                    if st.button(
                        "Create Case from Selected Hit",
                        type="primary",
                        use_container_width=True,
                    ):
                        cid = create_case_from_sanction(
                            row, created_by=self.role or "MLRO"
                        )
                        st.session_state["selected_case_id"] = cid
                        st.success(f"Case #{cid} created from sanctions hit.")
                        st.rerun()

        # -------------------- Case Detail --------------------
        with tabs[3]:
            st.subheader("🔎 Case Detail")
            cid = st.session_state.get("selected_case_id")
            if not cid:
                st.info("Select a case from the register, or create one first.")
            else:
                case = get_case(int(cid))
                if case.empty:
                    st.error("Case not found.")
                else:
                    row = case.iloc[0]
                    # Header
                    st.markdown(
                        f"### Case #{int(row['case_id'])} — {row['title']}"
                    )
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Status", str(row["status"]))
                    c2.metric("Severity", str(row["severity"]))
                    c3.metric("Category", str(row["category"]))
                    due_disp = (
                        str(row["due_date"])
                        if pd.notna(row["due_date"])
                        else "—"
                    )
                    c4.metric("Due", due_disp)

                    # Quick actions
                    st.markdown("#### ⚙️ Workflow")
                    w1, w2, w3 = st.columns([1, 1, 2])
                    status_options = ["Open", "Under Review", "Escalated", "Closed"]
                    new_status = w1.selectbox(
                        "Set status",
                        status_options,
                        index=status_options.index(str(row["status"]))
                        if str(row["status"]) in status_options
                        else 0,
                    )
                    if w2.button("Update", use_container_width=True):
                        update_status(
                            int(cid),
                            st.session_state.get("user_role", self.role or "MLRO"),
                            new_status,
                        )
                        st.success("Status updated.")
                        st.rerun()

                    # Summary editable
                    st.markdown("#### 📝 Summary")
                    new_sum = st.text_area(
                        "Summary / Narrative",
                        value=str(row.get("summary") or ""),
                        height=140,
                    )
                    if st.button("Save summary", use_container_width=True):
                        update_summary(int(cid), new_sum)
                        st.success("Summary updated.")
                        st.rerun()

                    # Comments
                    st.markdown("#### 💬 Comments")
                    with st.form("add_comment"):
                        txt = st.text_input("Add comment")
                        if st.form_submit_button("Post"):
                            if txt.strip():
                                add_comment(
                                    int(cid),
                                    st.session_state.get(
                                        "user_role", self.role or "MLRO"
                                    ),
                                    txt.strip(),
                                )
                                st.success("Comment added.")
                                st.rerun()
                    comm = list_comments(int(cid))
                    if comm.empty:
                        st.caption("No comments yet.")
                    else:
                        st.dataframe(
                            comm, use_container_width=True, height=240
                        )

                    # Attachments
                    st.markdown("#### 📎 Attachments")
                    up = st.file_uploader(
                        "Upload file (PDF, DOCX, XLSX, images…)", type=None
                    )
                    if up is not None:
                        data = up.read()
                        _rel = save_attachment(int(cid), up.name, data)
                        st.success(f"Uploaded: {up.name}")
                        st.rerun()
                    att = list_attachments(int(cid))
                    if att.empty:
                        st.caption("No attachments yet.")
                    else:
                        st.dataframe(
                            att, use_container_width=True, height=240
                        )
                        with st.expander("Paths (server-relative)"):
                            st.write(att[["filename", "path"]])

                    # Timeline
                    st.markdown("#### 🧵 Timeline")
                    tl = timeline(int(cid))
                    st.dataframe(tl, use_container_width=True, height=260)


# ============================================================
# 4. Entrypoint
# ============================================================
page = MlroPortalPage()
page.run()
