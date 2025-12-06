# pages/2_👤_KYC_Management.py
from __future__ import annotations

import io
import os
import sys
from datetime import datetime

import pandas as pd
import streamlit as st

# ============================================================
# 1. Path setup – make sure legacy AML engine is importable
# ============================================================
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

AML_LEGACY_DIR = os.path.join(ROOT_DIR, "legacy", "aml_cft")
if AML_LEGACY_DIR not in sys.path:
    sys.path.append(AML_LEGACY_DIR)

# --- Legacy AML engine imports (re-use existing logic) ---
from sacco_core.audit import log_page_access, log_action
from sacco_core.state import filters_ui  # date filter still useful for joined Tx signals
from sacco_core.aml.kyc import (
    kyc_overview,
    kyc_completeness_table,
    edd_candidates,
    docs_register,
)

# --- Unified core imports (same pattern as Prudential pages) ---
from core.config import ConfigManager
from core.rbac import RBACManager
from core.audit import audit_logger
from core.sidebar import render_sidebar


# ============================================================
# 2. Auth guard + sidebar
# ============================================================
if not st.session_state.get("authenticated", False):
    st.error("🔐 Please log in to access this page")
    st.stop()

current_module = st.session_state.get("current_module", "prudential")
if current_module != "aml_cft":
    st.error(
        "This page is available under the AML / CFT module. "
        "Please log in via AML / CFT on the main portal."
    )
    st.stop()

# Render unified SACCO Pro sidebar
render_sidebar()


# ============================================================
# 3. KYC Management Page (unified style)
# ============================================================
class KYCManagementPage:
    """
    AML / CFT – KYC Management dashboard, aligned with unified SACCO Pro shell.

    • Uses legacy AML KYC analytics (sacco_core.aml.kyc.*)
    • Uses unified RBAC + audit from core.*
    """

    def __init__(self):
        self.config_manager = ConfigManager()
        self.rbac_manager = RBACManager()
        self.audit_logger = audit_logger
        self.config = self.config_manager.load_settings()

        # Basic context
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
            page_id="2_👤_KYC_Management.py",
            role=st.session_state.get("role"),
            config=self.config,
        )

        if not has_access:
            st.error("You do not have permission to access this page")
            # Best-effort audit
            try:
                self.audit_logger.log_action(
                    user=self.user,
                    role=self.role,
                    action="unauthorized_access_attempt",
                    object_type="page",
                    object_id="KYC_Management",
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
                object_id="KYC_Management",
                extra={"module": "aml_cft", "timestamp": datetime.now().isoformat()},
            )
        except Exception:
            pass

        # Legacy audit (keep old logs alive)
        try:
            log_page_access(
                user=st.session_state.get("user_id", self.user),
                role=st.session_state.get("user_role", self.role),
                page="KYC_Management",
            )
        except Exception:
            pass

        return True

    # ---------------- Main render ----------------
    def run(self):
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
                colf1, colf2 = st.columns([2, 1])
                with colf1:
                    min_pct = st.slider("Minimum completeness (%)", 0, 100, 0, 1)
                with colf2:
                    only_missing = st.checkbox("Show only incomplete", value=True)

                view = df.copy()
                if only_missing:
                    view = view[view["completeness_pct"] < 100]
                view = view[view["completeness_pct"] >= min_pct]

                st.dataframe(view, use_container_width=True, height=420)

                def _csv(x: pd.DataFrame) -> bytes:
                    return x.to_csv(index=False).encode("utf-8")

                st.download_button(
                    "⬇️ Export Completeness (CSV)",
                    data=_csv(view),
                    file_name="kyc_completeness.csv",
                    use_container_width=True,
                )

        # ---- Enhanced Due Diligence ----
        with t2:
            st.subheader("🔎 EDD Candidates")
            cand = edd_candidates()
            if cand.empty:
                st.success("No EDD candidates detected under current data.")
            else:
                st.dataframe(cand, use_container_width=True, height=420)
                st.download_button(
                    "⬇️ Export EDD Candidates (CSV)",
                    data=cand.to_csv(index=False).encode("utf-8"),
                    file_name="edd_candidates.csv",
                    use_container_width=True,
                )

            # Action log stub
            if st.button("📌 Log EDD review snapshot"):
                try:
                    log_action(
                        "edd_snapshot",
                        user=st.session_state.get("user_id", self.user),
                        payload={"rows": min(50, len(cand))},
                    )
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
                # Quick filters
                if "status" in docs.columns:
                    s = st.multiselect(
                        "Filter by status",
                        sorted(docs["status"].dropna().unique().tolist()),
                    )
                    if s:
                        docs = docs[docs["status"].isin(s)]

                st.dataframe(docs, use_container_width=True, height=420)

                st.download_button(
                    "⬇️ Export Docs Register (CSV)",
                    data=docs.to_csv(index=False).encode("utf-8"),
                    file_name="docs_register.csv",
                    use_container_width=True,
                )


# ============================================================
# 4. Entrypoint
# ============================================================
if __name__ == "__main__":
    page = KYCManagementPage()
    page.run()
