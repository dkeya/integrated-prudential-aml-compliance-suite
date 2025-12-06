# pages/12_🔗_FRC_Integration.py
from __future__ import annotations

import os
import sys
import io
from datetime import date

import pandas as pd
import streamlit as st

# ============================================================
# 1. Path setup – make legacy AML engine importable
# ============================================================
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

AML_LEGACY_DIR = os.path.join(ROOT_DIR, "legacy", "aml_cft")
if AML_LEGACY_DIR not in sys.path:
    sys.path.append(AML_LEGACY_DIR)

# ---------- Legacy AML imports ----------
from sacco_core.state import seed_shared_filters, filters_ui, where_and_params
from sacco_core.config import get_config, save_aml_config
from sacco_core.aml.reporting import (
    ctr_single_hits,
    ctr_weekly_summary,
    str_candidates,
    str_filing_table,
    ctr_filing_table,
    generate_goaml_str_xml,
    generate_goaml_ctr_xml,
    ensure_submission_schema,
    record_submission,
    list_submissions,
    update_submission_status,
)

try:
    from sacco_core.audit import log_page_access
except Exception:
    log_page_access = None  # optional legacy audit

# ---------- Unified core imports ----------
from core.config import ConfigManager
from core.rbac import RBACManager
from core.audit import audit_logger
from core.sidebar import render_sidebar


# ============================================================
# 2. Auth + module guard + unified sidebar
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

# Render unified SACCO Pro sidebar for AML module
render_sidebar()


# ============================================================
# 3. FRC / goAML Integration Page – unified wrapper
# ============================================================
class FRCIntegrationPage:
    """
    AML / CFT — FRC Integration (goAML)

    - FRC / goAML configuration (thresholds, deadlines, retention)
    - STR / CTR XML generation tied to current candidates
    - Submissions register with status updates
    """

    def __init__(self):
        self.config_manager = ConfigManager()
        self.rbac_manager = RBACManager()
        self.audit_logger = audit_logger
        self.core_config = self.config_manager.load_settings()

        self.user = st.session_state.get(
            "user",
            st.session_state.get("user_id", "aml_officer"),
        )
        self.role = st.session_state.get(
            "role",
            st.session_state.get("user_role", "AML_Officer"),
        )
        self.tenant = st.session_state.get("tenant", "Central SACCO")

        if not self._check_access():
            st.stop()

    # ---------------- RBAC + Audit ----------------
    def _check_access(self) -> bool:
        if not st.session_state.get("authenticated", False):
            st.error("Please login to access this page")
            return False

        has_access = self.rbac_manager.check_page_access(
            page_id="12_🔗_FRC_Integration.py",
            role=st.session_state.get("role"),
            config=self.core_config,
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
                    object_id="FRC_Integration",
                    extra={"module": "aml_cft"},
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
                object_id="FRC_Integration",
                extra={"module": "aml_cft"},
            )
        except Exception:
            pass

        # Legacy audit (optional)
        if log_page_access is not None:
            try:
                log_page_access(
                    user=st.session_state.get("user_id", self.user),
                    role=st.session_state.get("user_role", self.role),
                    page="FRC_Integration",
                )
            except Exception:
                pass

        return True

    # ---------------- Main render ----------------
    def run(self):
        # Shared/global filters state (for AML module)
        seed_shared_filters()

        st.markdown("## 🔗 FRC Integration (goAML)")
        cfg = get_config()  # AML config (frc/risk_scoring/monitoring)

        tabs = st.tabs(
            [
                "⚙️ Config (Thresholds & Deadlines)",
                "📄 STR / CTR XML",
                "🗂️ Submissions Register",
            ]
        )

        with tabs[0]:
            self._render_config_tab(cfg)

        with tabs[1]:
            self._render_xml_tab()

        with tabs[2]:
            self._render_submissions_tab()

    # ---------------- Tab 1: Config UI ----------------
    def _render_config_tab(self, cfg):
        st.subheader("⚙️ FRC / goAML Configuration")

        c1, c2 = st.columns([1, 1])

        with c1:
            st.markdown("### CTR / STR")
            ctr_threshold_kes = st.number_input(
                "CTR Threshold (KES)",
                min_value=0,
                value=int(getattr(cfg.frc, "ctr_threshold_kes", 1_900_000)),
                step=50_000,
                help="Single cash transaction threshold.",
            )
            str_deadline_days = st.number_input(
                "STR Deadline (days from suspicion date)",
                min_value=1,
                value=int(getattr(cfg.frc, "str_deadline_days", 2)),
                step=1,
            )
            ctr_reporting_day = st.selectbox(
                "CTR Reporting Day (reference)",
                [
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                    "sunday",
                ],
                index=[
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                    "sunday",
                ].index(getattr(cfg.frc, "ctr_reporting_day", "friday").lower()),
            )

        with c2:
            st.markdown("### Sanctions / Annual")
            sanctions_freezing_hours = st.number_input(
                "Sanctions Freezing (hours)",
                min_value=1,
                value=int(getattr(cfg.frc, "sanctions_freezing_hours", 24)),
                step=1,
            )
            annual_report_due = st.text_input(
                "Annual Report Due (MM-DD)",
                value=str(getattr(cfg.frc, "annual_report_due", "01-31")),
            )
            record_retention_years = st.number_input(
                "Record Retention (years)",
                min_value=1,
                value=int(getattr(cfg.frc, "record_retention_years", 7)),
                step=1,
            )

        if st.button(
            "💾 Save Configuration",
            use_container_width=True,
            key="save_cfg_btn",
        ):
            # Build a dict structure compatible with Settings → dump YAML
            new_cfg = {
                "version": getattr(cfg, "version", "1.0"),
                "frc": {
                    "str_deadline_days": int(str_deadline_days),
                    "str_threshold": int(getattr(cfg.frc, "str_threshold", 0)),
                    "ctr_threshold_kes": int(ctr_threshold_kes),
                    "ctr_reporting_day": ctr_reporting_day.lower(),
                    "sanctions_freezing_hours": int(sanctions_freezing_hours),
                    "annual_report_due": annual_report_due,
                    "record_retention_years": int(record_retention_years),
                },
                "risk_scoring": {
                    "high_risk_threshold": float(
                        getattr(cfg.risk_scoring, "high_risk_threshold", 0.7)
                    ),
                    "medium_risk_threshold": float(
                        getattr(cfg.risk_scoring, "medium_risk_threshold", 0.4)
                    ),
                    "weights": dict(
                        getattr(
                            cfg.risk_scoring,
                            "weights",
                            {
                                "transaction_behavior": 0.40,
                                "pep_status": 0.30,
                                "geography": 0.20,
                                "product": 0.10,
                            },
                        )
                    ),
                },
                "monitoring": {
                    "structuring_unit_kes": int(
                        getattr(cfg.monitoring, "structuring_unit_kes", 150000)
                    ),
                    "structuring_window_days": int(
                        getattr(cfg.monitoring, "structuring_window_days", 7)
                    ),
                    "rapid_movement_days": int(
                        getattr(cfg.monitoring, "rapid_movement_days", 5)
                    ),
                    "unusual_activity_multiplier": float(
                        getattr(
                            cfg.monitoring,
                            "unusual_activity_multiplier",
                            3.0,
                        )
                    ),
                    "odd_hours": list(
                        getattr(
                            cfg.monitoring,
                            "odd_hours",
                            [0, 1, 2, 3, 4, 23],
                        )
                    ),
                },
            }
            save_aml_config(new_cfg)
            st.success("Configuration saved. (Reloaded in memory.)")

        with st.expander("Show current configuration JSON"):
            cfg_current = get_config()
            st.json(
                {
                    "frc": {
                        "str_deadline_days": cfg_current.frc.str_deadline_days,
                        "ctr_threshold_kes": cfg_current.frc.ctr_threshold_kes,
                        "ctr_reporting_day": cfg_current.frc.ctr_reporting_day,
                        "sanctions_freezing_hours": cfg_current.frc.sanctions_freezing_hours,
                        "annual_report_due": cfg_current.frc.annual_report_due,
                        "record_retention_years": cfg_current.frc.record_retention_years,
                    }
                }
            )

    # ---------------- Tab 2: STR / CTR XML ----------------
    def _render_xml_tab(self):
        st.subheader("📄 STR / CTR XML — Generate from Current Candidates")

        # Global filters
        branch, product, d_from, d_to = filters_ui("Global Filters")
        where_sql, params = where_and_params(
            date_col="ts",
            date_from=d_from,
            date_to=d_to,
            branch=branch,
            product=product,
            table_hint="transactions",
        )

        # ---- STR ----
        st.markdown("### 🚩 STR Candidates")
        cand = str_filing_table(where_sql=where_sql, params=params)
        if cand.empty:
            st.info("No STR candidates for the selected filters.")
        else:
            st.dataframe(cand, use_container_width=True, height=300)
            sel_row = st.selectbox(
                "Select candidate (member_id)",
                cand["member_id"].astype(str).tolist(),
                key="str_pick",
            )
            if sel_row:
                row = cand[cand["member_id"].astype(str) == str(sel_row)].iloc[0]
                xml = generate_goaml_str_xml(
                    member_id=str(row.get("member_id")),
                    suspicion_date=row.get("suspicion_date"),
                    signals=str(row.get("signals") or ""),
                )
                st.download_button(
                    "⬇️ Download STR XML",
                    data=xml.encode("utf-8"),
                    file_name=f"STR_{row.get('member_id')}.xml",
                    mime="application/xml",
                    use_container_width=True,
                )
                if st.button(
                    "🗂️ Record STR Submission",
                    key="rec_str_submit",
                    use_container_width=True,
                ):
                    ensure_submission_schema()
                    record_submission(
                        sub_type="STR",
                        reference=str(row.get("member_id")),
                        payload_xml=xml,
                        status="Draft",
                        notes=f"Generated on {date.today().isoformat()}",
                    )
                    st.success("STR submission recorded in register.")

        st.markdown("---")

        # ---- CTR ----
        st.markdown("### 🏛️ CTR (Weekly Aggregates ≥ Threshold)")
        ctr = ctr_filing_table(where_sql=where_sql, params=params)
        if ctr.empty:
            st.info(
                "No CTR weekly aggregates at/above threshold for the selected filters."
            )
        else:
            st.dataframe(ctr, use_container_width=True, height=300)
            if {
                "member_id",
                "week_start",
                "week_end",
                "cash_sum",
                "txn_count",
            }.issubset(ctr.columns):
                idx = st.selectbox(
                    "Pick CTR Row",
                    list(range(len(ctr))),
                    format_func=lambda i: f"{ctr.iloc[i]['member_id']} — "
                    f"{ctr.iloc[i]['week_start']} to {ctr.iloc[i]['week_end']}",
                    key="ctr_pick",
                )
                if idx is not None:
                    r = ctr.iloc[int(idx)]
                    xml2 = generate_goaml_ctr_xml(
                        member_id=str(r["member_id"]),
                        week_start=r["week_start"],
                        week_end=r["week_end"],
                        cash_sum=float(r["cash_sum"]),
                        txn_count=int(r["txn_count"]),
                    )
                    st.download_button(
                        "⬇️ Download CTR XML",
                        data=xml2.encode("utf-8"),
                        file_name=f"CTR_{r['member_id']}_{pd.to_datetime(r['week_start']).date()}.xml",
                        mime="application/xml",
                        use_container_width=True,
                    )
                    if st.button(
                        "🗂️ Record CTR Submission",
                        key="rec_ctr_submit",
                        use_container_width=True,
                    ):
                        ensure_submission_schema()
                        record_submission(
                            sub_type="CTR",
                            reference=f"{r['member_id']}@{pd.to_datetime(r['week_start']).date()}",
                            payload_xml=xml2,
                            status="Draft",
                            notes=f"Generated on {date.today().isoformat()}",
                        )
                        st.success("CTR submission recorded in register.")

    # ---------------- Tab 3: Submissions Register ----------------
    def _render_submissions_tab(self):
        st.subheader("🗂️ Submissions Register (STR / CTR)")
        ensure_submission_schema()

        # Filters
        f1, f2 = st.columns([1, 1])
        typ = f1.selectbox(
            "Type", ["All", "STR", "CTR"], key="sub_type_filter"
        )
        stat = f2.selectbox(
            "Status",
            ["All", "Draft", "Submitted", "Acknowledged", "Rejected"],
            key="sub_status_filter",
        )

        reg = list_submissions(
            sub_type=(None if typ == "All" else typ),
            status=(None if stat == "All" else stat),
        )
        st.dataframe(reg, use_container_width=True, height=360)

        if not reg.empty:
            st.markdown("### Update Status")
            ids = reg["submission_id"].tolist()
            sel = st.selectbox("Submission", ids, key="sub_sel_update")
            new_stat = st.selectbox(
                "New status",
                ["Draft", "Submitted", "Acknowledged", "Rejected"],
                key="sub_new_status",
            )
            note = st.text_input("Notes (optional)", key="sub_note")
            if st.button(
                "💾 Update Submission",
                use_container_width=True,
                key="sub_update_btn",
            ):
                update_submission_status(int(sel), new_stat, note or None)
                st.success("Submission updated.")
                st.rerun()


# ============================================================
# 4. Entrypoint
# ============================================================
page = FRCIntegrationPage()
page.run()