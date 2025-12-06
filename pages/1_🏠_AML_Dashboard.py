# pages/1_🏠_AML_Dashboard.py
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
from sacco_core.db import query
from sacco_core.state import filters_ui, where_and_params
from sacco_core.audit import log_page_access, log_action
from sacco_core.aml.dashboard import (
    get_overview_kpis,
    inflow_outflow_trend,
    compliance_snapshot,
    realtime_alerts,
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

# Enforce that this page only makes sense in AML / CFT module
current_module = st.session_state.get("current_module", "prudential")
if current_module != "aml_cft":
    st.error("This page is available under the AML / CFT module. "
             "Please log in via AML / CFT on the main portal.")
    st.stop()

# Render unified SACCO Pro sidebar
render_sidebar()


# ============================================================
# 3. AML Dashboard Page (unified style)
# ============================================================
class AMLDashboardPage:
    """
    AML/CFT – Executive Overview dashboard, aligned with unified SACCO Pro shell.

    • Uses legacy AML analytics (sacco_core.aml.dashboard.*)
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
            page_id="1_🏠_AML_Dashboard.py",
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
                    object_id="AML_Dashboard",
                )
            except Exception:
                pass
            return False

        # Best-effort unified audit
        try:
            self.audit_logger.log_action(
                user=self.user,
                role=self.role,
                action="page_access",
                object_type="page",
                object_id="AML_Dashboard",
                extra={"module": "aml_cft", "timestamp": datetime.now().isoformat()},
            )
        except Exception:
            pass

        # Legacy audit hook (keeps old logs working)
        try:
            log_page_access(
                user=st.session_state.get("user_id", self.user),
                role=st.session_state.get("user_role", self.role),
                page="AML_Dashboard",
            )
        except Exception:
            pass

        return True

    # ---------------- Helpers ----------------
    @staticmethod
    def _options(sql: str, col: str) -> list[str]:
        """Shared options across pages (branch/product lists)."""
        try:
            return ["All"] + query(sql)[col].dropna().astype(str).tolist()
        except Exception:
            return ["All"]

    @staticmethod
    def _to_csv(df: pd.DataFrame) -> bytes:
        return df.to_csv(index=False).encode("utf-8")

    @staticmethod
    def _to_excel(df: pd.DataFrame, sheet: str = "Alerts") -> bytes:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as xw:
            df.to_excel(xw, index=False, sheet_name=sheet)
        return buf.getvalue()

    # ---------------- Main render ----------------
    def run(self):
        # Header
        st.title("AML/CFT — Executive Overview")
        st.markdown("---")

        # Shared dropdown options (branches, products)
        st.session_state["branches_options"] = self._options(
            "select distinct branch from members order by branch", "branch"
        )
        st.session_state["products_options"] = self._options(
            "select distinct product from transactions order by product", "product"
        )

        # Global filters & WHERE
        filters_ui("Global Filters")
        where_sql, params = where_and_params("ts")

        # Tabs: Executive, Compliance, Real-time Alerts
        tab_hint = st.session_state.get("nav_tab_hint")
        labels = ["Executive Overview", "Compliance Metrics", "Real-time Alerts"]
        idx = labels.index(tab_hint) if tab_hint in labels else 0
        t1, t2, t3 = st.tabs(labels)

        # -------------------------------------------------
        #  Executive Overview
        # -------------------------------------------------
        with t1:
            k = get_overview_kpis(where_sql, params)

            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.metric("Members", f"{k.members:,}")
            c2.metric("Txns (period)", f"{k.txns_period:,}")
            c3.metric("High-Risk Members", f"{k.high_risk_members:,}")
            c4.metric("PEP Records", f"{k.pep_records:,}")
            c5.metric("Sanctions Records", f"{k.sanctions_records:,}")
            c6.metric(
                "CTR ≥ KES 1.9M (cash, all time)",
                f"{k.ctr_hits_alltime:,}",
            )

            st.markdown("### 📈 Inflow / Outflow Trend")
            trend = inflow_outflow_trend(where_sql, params)
            if trend.empty:
                st.info("No transactions in the selected window.")
            else:
                st.line_chart(trend.set_index("d")[["inflow", "outflow"]])

            colx, coly = st.columns(2)
            colx.download_button(
                "⬇️ Export daily inflow/outflow (CSV)",
                data=self._to_csv(trend),
                file_name="inflow_outflow_trend.csv",
                use_container_width=True,
            )

            if coly.button("📌 Snapshot KPIs"):
                try:
                    log_action(
                        event_type="snapshot_kpis",
                        user=st.session_state.get("user_id", self.user),
                        payload={"kpis": k.__dict__},
                    )
                except Exception:
                    pass
                st.success("KPIs snapshot logged.")

        # -------------------------------------------------
        #  Compliance Metrics
        # -------------------------------------------------
        with t2:
            st.markdown("### 🎯 Compliance KPIs")
            snap = compliance_snapshot(where_sql, params)

            c1, c2, c3 = st.columns(3)
            c1.metric(
                "STR SLA (≤ 2 days)",
                snap["str_sla_status"],
                (
                    snap["str_breaches"] + " breaches"
                    if snap["str_breaches"] != "0"
                    else "—"
                ),
            )
            c2.metric(
                "CTR Weekly (cash ≥ KES 1.9M)",
                "Weeks with hits",
                snap["ctr_weeks_with_hits"],
            )
            c3.metric(
                "Record Retention (7 years)",
                snap["retention"],
                "—",
            )

            st.markdown("#### ⏱️ Deadlines in Focus")
            st.info(
                "• STR: file within 2 days of suspicion "
                "• CTR: weekly (cash ≥ KES 1.9M) "
                "• Sanctions freezing: within 24 hours"
            )

            # CTR weekly roll (preview)
            st.markdown("#### 📅 CTR Weekly Counts (preview)")
            ctr_week = query(
                """
                with w as (
                    select date_trunc('week', ts)::date week_start, count(*) c
                    from transactions
                    where channel='CASH' and amount >= 1900000
                    group by 1
                )
                select week_start, c as ctr_count
                from w
                order by week_start desc
                limit 12
                """
            )
            st.dataframe(ctr_week, use_container_width=True, height=260)

        # -------------------------------------------------
        #  Real-time Alerts
        # -------------------------------------------------
        with t3:
            st.markdown("### 🚨 Latest Alerts")
            feed = realtime_alerts(limit=100, where_sql=where_sql, params=params)

            if feed.empty:
                st.success("No alerts available for the current filters.")
            else:
                grid = feed.copy()
                # Light PII masking example
                try:
                    grid["linked_entities"] = grid["linked_entities"].str.replace(
                        r'("customer_id":"\w+")',
                        '"customer_id":"***"',
                        regex=True,
                    )
                except Exception:
                    pass

                st.dataframe(grid, use_container_width=True, height=420)

                c1, c2 = st.columns(2)
                c1.download_button(
                    "⬇️ Export Alerts (CSV)",
                    data=feed.to_csv(index=False).encode("utf-8"),
                    file_name="alerts_latest.csv",
                    use_container_width=True,
                )
                c2.download_button(
                    "⬇️ Export Alerts (XLSX)",
                    data=self._to_excel(feed),
                    file_name="alerts_latest.xlsx",
                    use_container_width=True,
                )


# ============================================================
# 4. Entrypoint
# ============================================================
if __name__ == "__main__":
    page = AMLDashboardPage()
    page.run()
