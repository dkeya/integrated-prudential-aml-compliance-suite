# pages/11_📊_Audit_Reports.py
from __future__ import annotations

import os
import sys
import io

import pandas as pd
import plotly.express as px
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
from sacco_core.config import get_config
from sacco_core.aml.governance import (
    ensure_governance_schema,
    audit_readiness_snapshot,
    recent_audit,
    verify_audit_chain,
    append_audit,
    board_pack_markdown,
    add_document,
    list_documents,
    gap_analysis,
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
# 3. Governance & Audit Page – unified wrapper
# ============================================================
class GovernanceAuditPage:
    """
    AML / CFT — Governance & Audit

    - Audit readiness checklist
    - Immutable audit log (hash chain)
    - Board pack markdown generator
    - Documentation center
    - Gap analysis
    """

    def __init__(self):
        self.config_manager = ConfigManager()
        self.rbac_manager = RBACManager()
        self.audit_logger = audit_logger
        self.config = self.config_manager.load_settings()

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
            page_id="11_📊_Audit_Reports.py",
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
                    object_id="Governance_Audit",
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
                object_id="Governance_Audit",
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
                    page="Governance_Audit",
                )
            except Exception:
                pass

        return True

    # ---------------- Main render ----------------
    def run(self):
        # Shared/global filters state
        seed_shared_filters()

        st.title("📊 Governance & Audit")
        st.caption(
            "Audit Readiness • Immutable Audit Log • Board Packs • "
            "Documentation Center • Gap Analysis"
        )
        st.markdown("---")

        # Global filters (scope the readiness/board pack to a period/subset if needed)
        branch, product, d_from, d_to = filters_ui()
        where_sql, params = where_and_params(
            date_col="ts",
            date_from=d_from,
            date_to=d_to,
            branch=branch,
            product=product,
            table_hint="transactions",
        )

        ensure_governance_schema()
        cfg = get_config()  # keep existing AML config usage

        tabs = st.tabs(
            [
                "✅ Audit Readiness",
                "🔐 Immutable Audit Log",
                "📦 Board Reporting Pack",
                "📚 Documentation Center",
                "🧭 Gap Analysis",
            ]
        )

        # ----------------- Audit Readiness -----------------
        with tabs[0]:
            st.subheader("✅ Audit Readiness Checklist")
            snap = audit_readiness_snapshot(where_sql=where_sql, params=params)
            if snap.empty:
                st.info("No readiness artifacts yet.")
            else:
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Controls assessed", f"{len(snap):,}")
                with c2:
                    ok = (snap["status"] == "OK").sum()
                    st.metric("OK", f"{ok:,}")
                with c3:
                    check = (snap["status"] == "Check").sum()
                    st.metric("Check", f"{check:,}")

                st.dataframe(snap, use_container_width=True, height=360)
                st.download_button(
                    "⬇️ Export Checklist (CSV)",
                    snap.to_csv(index=False).encode("utf-8"),
                    "audit_readiness.csv",
                    use_container_width=True,
                )

        # ----------------- Immutable Audit Log -----------------
        with tabs[1]:
            st.subheader("🔐 Immutable Audit Log")
            c1, c2 = st.columns([1.5, 1])
            with c1:
                df = recent_audit(limit=800)
                if df.empty:
                    st.info(
                        "No audit records yet. "
                        "Use the form on the right to append a test event."
                    )
                else:
                    # Verify chain
                    ver = verify_audit_chain(limit=800)
                    ok_rate = float(ver["ok"].mean()) if not ver.empty else 1.0
                    st.success(f"Chain verification OK: {ok_rate:.0%}")
                    st.dataframe(df, use_container_width=True, height=360)
                    st.download_button(
                        "⬇️ Export Audit Log (CSV)",
                        df.to_csv(index=False).encode("utf-8"),
                        "immutable_audit_log.csv",
                        use_container_width=True,
                    )
            with c2:
                st.markdown("**Append Test Event**")
                actor = st.text_input(
                    "Actor",
                    value=st.session_state.get("user_role", "AML_Officer"),
                )
                action = st.text_input("Action", value="VIEW_PAGE")
                entity_type = st.text_input("Entity Type", value="page")
                entity_id = st.text_input("Entity ID", value="AuditReports")
                details = st.text_area(
                    "Details (JSON)", value='{"note":"manual test"}'
                )
                if st.button(
                    "➕ Append Event",
                    type="primary",
                    use_container_width=True,
                ):
                    try:
                        import json

                        d = json.loads(details) if details.strip() else {}
                    except Exception:
                        d = {"raw": details}
                    append_audit(actor, action, entity_type, entity_id, d)
                    st.success("Event appended.")
                    st.rerun()

        # ----------------- Board Pack -----------------
        with tabs[2]:
            st.subheader("📦 Board Reporting Pack (Markdown)")
            period_label = st.text_input(
                "Period label", value=f"{d_from} to {d_to}"
            )
            if st.button(
                "Generate Pack", type="primary", use_container_width=True
            ):
                md = board_pack_markdown(
                    period_label=period_label,
                    where_sql=where_sql,
                    params=params,
                )
                st.markdown(md)
                st.download_button(
                    "⬇️ Download Markdown",
                    md.encode("utf-8"),
                    file_name="Board_Compliance_Pack.md",
                    use_container_width=True,
                )

        # ----------------- Documentation Center -----------------
        with tabs[3]:
            st.subheader("📚 Documentation Center")
            with st.expander("➕ Add Document Link"):
                title = st.text_input("Title")
                category = st.selectbox(
                    "Category",
                    [
                        "Policies",
                        "Procedures",
                        "Training",
                        "Reports",
                        "Board Packs",
                        "Other",
                    ],
                )
                link = st.text_input("Link/URL")
                tags = st.text_input(
                    "Tags (comma separated)", value="compliance,policy"
                )
                if st.button("Add Document", use_container_width=True):
                    add_document(
                        title=title,
                        category=category,
                        link=link,
                        tags=[
                            t.strip()
                            for t in tags.split(",")
                            if t.strip()
                        ],
                    )
                    st.success("Added.")
                    st.rerun()

            cat = st.selectbox(
                "Filter by category",
                [
                    "All",
                    "Policies",
                    "Procedures",
                    "Training",
                    "Reports",
                    "Board Packs",
                    "Other",
                ],
                index=0,
            )
            docs = list_documents(None if cat == "All" else cat)
            if docs.empty:
                st.info("No documents registered yet.")
            else:
                st.dataframe(docs, use_container_width=True, height=360)
                st.download_button(
                    "⬇️ Export Docs (CSV)",
                    docs.to_csv(index=False).encode("utf-8"),
                    "governance_docs.csv",
                    use_container_width=True,
                )

        # ----------------- Gap Analysis -----------------
        with tabs[4]:
            st.subheader("🧭 Gap Analysis")
            gaps = gap_analysis(where_sql=where_sql, params=params)
            if gaps.empty:
                st.info("No gaps detected.")
            else:
                st.dataframe(gaps, use_container_width=True, height=360)
                if {"area", "status", "control"}.issubset(gaps.columns):
                    pivot = (
                        gaps.pivot_table(
                            index="area",
                            columns="status",
                            values="control",
                            aggfunc="count",
                            fill_value=0,
                        )
                        .reset_index()
                    )
                    fig = px.bar(
                        pivot,
                        x="area",
                        y=[c for c in pivot.columns if c != "area"],
                        title="Gaps by Area / Status",
                        barmode="group",
                    )
                    st.plotly_chart(fig, use_container_width=True)
                st.download_button(
                    "⬇️ Export Gaps (CSV)",
                    gaps.to_csv(index=False).encode("utf-8"),
                    "gap_analysis.csv",
                    use_container_width=True,
                )


# ============================================================
# 4. Entrypoint
# ============================================================
page = GovernanceAuditPage()
page.run()