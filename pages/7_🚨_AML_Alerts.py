# pages/7_🚨_AML_Alerts.py
from __future__ import annotations

import os
import sys
from datetime import datetime

import pandas as pd
import streamlit as st
import plotly.express as px

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
from sacco_core.state import seed_shared_filters, filters_ui, where_and_params
from sacco_core.aml.alerts import alerts_feed, rules_summary
from sacco_core.audit import log_page_access

# --- Unified core imports (same shell as prudential) ---
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
# 3. AML / CFT – Alerts page (unified)
# ============================================================
class AmlAlertsPage:
    """
    AML / CFT – Unified Alerts Management

    • Uses legacy AML alerts engine (alerts_feed, rules_summary).
    • Integrated into unified SACCO Pro shell (RBAC + audit + sidebar).
    """

    def __init__(self):
        self.config_manager = ConfigManager()
        self.rbac_manager = RBACManager()
        self.audit_logger = audit_logger
        self.config = self.config_manager.load_settings()

        self.user = st.session_state.get("user", "demo_user")
        self.role = st.session_state.get("role", "AML_Officer")
        self.tenant = st.session_state.get("tenant", "Central SACCO")

        if not self._check_access():
            st.stop()

    # ---------------- RBAC + Audit ----------------
    def _check_access(self) -> bool:
        """Check RBAC access and log page access (unified + legacy)."""
        if not st.session_state.get("authenticated", False):
            st.error("Please login to access this page")
            return False

        has_access = self.rbac_manager.check_page_access(
            page_id="7_🚨_AML_Alerts.py",
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
                    object_id="AML_Alerts",
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
                object_id="AML_Alerts",
                extra={"module": "aml_cft", "timestamp": datetime.now().isoformat()},
            )
        except Exception:
            pass

        # Legacy audit – keep previous behaviour
        try:
            log_page_access(
                user=st.session_state.get("user_id", self.user),
                role=st.session_state.get("user_role", self.role),
                page="AML_Alerts",
            )
        except Exception:
            pass

        return True

    # ---------------- Main render ----------------
    def run(self):
        st.markdown("## 🚨 AML Alert Management")

        # Shared/global filters state
        seed_shared_filters()

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
                    chart = (
                        feed.groupby("alert_type")["score"]
                        .mean()
                        .reset_index()
                    )
                    fig = px.bar(
                        chart,
                        x="alert_type",
                        y="score",
                        title="Average Score by Alert Type",
                    )
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


# ============================================================
# 4. Entrypoint
# ============================================================
page = AmlAlertsPage()
page.run()
