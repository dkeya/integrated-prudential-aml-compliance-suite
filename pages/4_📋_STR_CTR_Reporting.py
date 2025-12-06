# pages/4_📋_STR_CTR_Reporting.py
from __future__ import annotations

import os
import sys
from datetime import datetime

import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# 1. Path setup – make sure legacy AML engine is importable
# ============================================================
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

AML_LEGACY_DIR = os.path.join(ROOT_DIR, "legacy", "aml_cft")
if AML_LEGACY_DIR not in sys.path:
    sys.path.append(AML_LEGACY_DIR)

# --- Legacy AML engine imports ---
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
from sacco_core.audit import log_page_access, log_action

# --- Unified core imports (same as other unified pages) ---
from core.config import ConfigManager
from core.rbac import RBACManager
from core.audit import audit_logger
from core.sidebar import render_sidebar


# ============================================================
# 2. Auth guard + module guard + sidebar
# ============================================================
if not st.session_state.get("authenticated", False):
    st.error("🔐 Please log in to access this page")
    st.stop()

current_module = st.session_state.get("current_module", "prudential")
if current_module != "aml_cft":
    st.error(
        "This page is part of the AML / CFT module. "
        "Please log in via AML / CFT on the main portal."
    )
    st.stop()

# Render unified SACCO Pro sidebar
render_sidebar()


# ============================================================
# 3. STR / CTR Reporting Page (unified style)
# ============================================================
class StrCtrReportingPage:
    """
    AML / CFT – STR / CTR Reporting & goAML integration, aligned with unified SACCO Pro shell.

    • Uses legacy AML reporting engine (sacco_core.aml.reporting.*)
    • Uses unified RBAC + audit from core.*
    """

    def __init__(self):
        self.config_manager = ConfigManager()
        self.rbac_manager = RBACManager()
        self.audit_logger = audit_logger
        self.config = self.config_manager.load_settings()

        # Context
        self.user = st.session_state.get("user", "demo_user")
        self.role = st.session_state.get("role", "AML_Officer")
        self.tenant = st.session_state.get("tenant", "Central SACCO")

        if not self._check_access():
            st.stop()

    # ---------------- RBAC + Audit ----------------
    def _check_access(self) -> bool:
        """Check RBAC access and log page access."""
        if not st.session_state.get("authenticated", False):
            st.error("Please login to access this page")
            return False

        has_access = self.rbac_manager.check_page_access(
            page_id="4_📋_STR_CTR_Reporting.py",
            role=st.session_state.get("role"),
            config=self.config,
        )

        if not has_access:
            st.error("You do not have permission to access this page")
            # Best-effort unified audit
            try:
                self.audit_logger.log_action(
                    user=self.user,
                    role=self.role,
                    action="unauthorized_access_attempt",
                    object_type="page",
                    object_id="STR_CTR_Reporting",
                )
            except Exception:
                pass
            return False

        # Unified audit
        try:
            self.audit_logger.log_action(
                user=self.user,
                role=self.role,
                action="page_access",
                object_type="page",
                object_id="STR_CTR_Reporting",
                extra={"module": "aml_cft", "timestamp": datetime.now().isoformat()},
            )
        except Exception:
            pass

        # Legacy audit (keep old logging intact)
        try:
            log_page_access(
                user=st.session_state.get("user_id", self.user),
                role=st.session_state.get("user_role", self.role),
                page="STR_CTR_Reporting",
            )
        except Exception:
            pass

        return True

    # ---------------- Main render ----------------
    def run(self):
        st.markdown("## 📋 Regulatory Reporting (STR / CTR / goAML)")

        # Shared/global filters state
        seed_shared_filters()

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

        tabs = st.tabs(
            [
                "🏛️ CTR (Single cash ≥ threshold)",
                "🚩 STR Candidates (Rules-based)",
                "🗓️ Deadlines & Checklist",
                "📤 Submissions Register",
            ]
        )

        # ----------------- CTR -----------------
        with tabs[0]:
            st.subheader(
                f"🏛️ CTR Candidates — Cash ≥ {cfg.frc.ctr_threshold_kes:,} KES"
            )
            ctr = ctr_single_hits(where_sql=where_sql, params=params)
            if ctr.empty:
                st.info("No CTR-eligible transactions for the selected filters.")
            else:
                export_buttons(ctr, basename="ctr_candidates", height=420)

                wk = ctr_weekly_summary(where_sql=where_sql, params=params)
                if not wk.empty:
                    fig = px.bar(
                        wk, x="iso_week", y="count_hits", title="Weekly CTR Counts"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                st.markdown("### 📄 Generate CTR XML & Queue Submission")
                if has_perm("file_ctr"):
                    colx1, colx2 = st.columns([2, 1])
                    labels = [
                        f"{r.member_id} | {r.ts} | {r.amount}"
                        for r in ctr.itertuples()
                    ]
                    with colx1:
                        sel = st.selectbox(
                            "Pick a CTR row to generate XML",
                            labels,
                            key="ctr_xml_select",
                        )
                    with colx2:
                        if st.button(
                            "Generate & Queue",
                            use_container_width=True,
                            key="ctr_xml_btn",
                        ):
                            # Find selected row index
                            idx = labels.index(sel)
                            row = ctr.iloc[idx]
                            mid = str(row.get("member_id", "NA"))
                            ts = pd.to_datetime(row.get("ts")).date()
                            xml = generate_goaml_ctr_xml(
                                member_id=mid,
                                week_start=ts,
                                week_end=ts,
                                cash_sum=float(row.get("amount", 0.0)),
                                txn_count=1,
                            )
                            sid = save_submission(
                                "CTR", key_ref=mid, xml_text=xml, status="Queued"
                            )
                            st.success(f"Queued CTR submission (ID={sid}).")
                else:
                    st.info(
                        "You need `file_ctr` permission to generate/queue CTR XML (MLRO/Officer/Admin)."
                    )

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
                    member_ids = cand["member_id"].astype(str).tolist()
                    with c1:
                        sel = st.selectbox(
                            "Pick a member_id to generate STR XML",
                            member_ids,
                            key="str_xml_sel",
                        )
                    with c2:
                        if st.button(
                            "Generate & Queue",
                            use_container_width=True,
                            key="str_xml_btn",
                        ):
                            row = cand[cand["member_id"].astype(str) == str(sel)].head(
                                1
                            )
                            signals = str(
                                row.get(
                                    "suspicion_flags",
                                    "Possible suspicious activity",
                                ).values[0]
                            )
                            ft = str_filing_table(
                                where_sql=where_sql, params=params
                            )
                            ft_row = ft[
                                ft["member_id"].astype(str) == str(sel)
                            ].head(1)
                            susp = None
                            if not ft_row.empty:
                                susp = ft_row["suspicion_date"].iloc[0]
                            xml = generate_goaml_str_xml(
                                member_id=str(sel),
                                suspicion_date=susp,
                                signals=signals,
                            )
                            sid = save_submission(
                                "STR", key_ref=str(sel), xml_text=xml, status="Queued"
                            )
                            st.success(f"Queued STR submission (ID={sid}).")
                            try:
                                log_action(
                                    event_type="file_str",
                                    user=st.session_state.get(
                                        "user_id", self.user
                                    ),
                                    payload={"member_id": str(sel)},
                                )
                            except Exception:
                                pass
                else:
                    st.info(
                        "You need `file_str` permission to generate/queue STR XML (MLRO/Officer/Admin)."
                    )

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
            recipients = st.text_input(
                "Recipients (comma-separated)",
                value="mlro@example.com",
                key="digest_recip",
            )
            if st.button("Send Digest Now", key="digest_send_btn"):
                try:
                    ok = send_deadline_digest(
                        [x.strip() for x in recipients.split(",") if x.strip()],
                        where_sql,
                        params,
                    )
                except Exception:
                    ok = False
                if ok:
                    st.success("Digest sent.")
                else:
                    st.warning(
                        "Email not sent (check Email config in `configs/aml_config.yml`)."
                    )

        # ----------------- Submissions Register -----------------
        with tabs[3]:
            st.subheader("📤 Submissions Register (local queue)")
            subs = list_submissions(limit=300)
            export_buttons(subs, basename="goaml_submissions", height=360)
            st.caption(
                "Tip: if you run the optional FastAPI receiver, you can POST these XML "
                "files to your integration endpoint."
            )


# ============================================================
# 4. Entrypoint
# ============================================================
if __name__ == "__main__":
    page = StrCtrReportingPage()
    page.run()
