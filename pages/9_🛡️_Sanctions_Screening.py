# pages/9_🛡️_Sanctions_Screening.py
from __future__ import annotations

import os
import sys

import pandas as pd
import plotly.express as px
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
from sacco_core.state import seed_shared_filters, filters_ui, where_and_params  # noqa
from sacco_core.aml.sanctions import (
    sanctions_exact_hits,
    sanctions_fuzzy_hits,
    sanctions_txn_hits,
    save_disposition,
    recent_screenings,
)
try:
    from sacco_core.audit import log_page_access
except Exception:
    log_page_access = None  # optional

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
# 3. Sanctions Screening Page – unified wrapper
# ============================================================
class SanctionsScreeningPage:
    """
    AML / CFT — Sanctions Screening

    Uses the legacy sanctions engine, but runs inside the unified SACCO Pro shell:
    - RBAC check
    - Unified audit logger
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
        """Check RBAC access and log page access (unified + legacy)."""
        if not st.session_state.get("authenticated", False):
            st.error("Please login to access this page")
            return False

        has_access = self.rbac_manager.check_page_access(
            page_id="9_🛡️_Sanctions_Screening.py",
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
                    object_id="Sanctions_Screening",
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
                object_id="Sanctions_Screening",
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
                    page="Sanctions_Screening",
                )
            except Exception:
                pass

        return True

    # ---------------- Main render ----------------
    def run(self):
        # Keep global filters in sync with other AML pages
        seed_shared_filters()

        st.markdown("## 🛡️ Sanctions Screening")

        # Global filters (currently for context only; screening itself is mostly global)
        branch, product, d_from, d_to = filters_ui()

        tabs = st.tabs(
            [
                "✅ Exact Name Matches",
                "🔍 Fuzzy Screening (Members)",
                "🔎 Fuzzy Screening (Counterparties)",
                "🗃️ Register (Dispositions)",
            ]
        )

        # ----------------- Exact matches -----------------
        with tabs[0]:
            st.subheader("✅ Exact Name Matches (Members ↔ Watchlist)")
            df = sanctions_exact_hits(limit=2000)
            if df.empty:
                st.info("No exact matches detected.")
            else:
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Hits", f"{len(df):,}")
                with c2:
                    top_list = (
                        df["list"].value_counts().idxmax()
                        if "list" in df.columns and not df["list"].empty
                        else "—"
                    )
                    st.metric("Dominant list", str(top_list))

                st.dataframe(df, use_container_width=True, height=420)
                st.download_button(
                    "⬇️ Export CSV",
                    df.to_csv(index=False).encode("utf-8"),
                    "sanctions_exact_hits.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

        # ----------------- Fuzzy (members) -----------------
        with tabs[1]:
            st.subheader("🔍 Fuzzy Screening — Members")
            th = st.slider("Similarity threshold", 0.70, 0.99, 0.88, 0.01)
            hits = sanctions_fuzzy_hits(threshold=float(th), source="members")
            if hits.empty:
                st.info("No fuzzy hits (members) at the selected threshold.")
            else:
                st.dataframe(hits, use_container_width=True, height=420)
                st.download_button(
                    "⬇️ Export CSV",
                    hits.to_csv(index=False).encode("utf-8"),
                    "sanctions_fuzzy_members.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

                # Similarity distribution
                if "similarity" in hits.columns:
                    fig = px.histogram(
                        hits,
                        x="similarity",
                        nbins=20,
                        title="Similarity distribution (members)",
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Quick disposition form
                st.markdown("### 📝 Record Disposition")
                with st.form("disp_members"):
                    sel = st.selectbox(
                        "Pick a row", hits.index.astype(str).tolist()
                    )
                    status = st.selectbox(
                        "Status", ["Open", "Cleared", "Escalated"]
                    )
                    notes = st.text_input("Notes (optional)")
                    submitted = st.form_submit_button("Save disposition")
                    if submitted:
                        row = hits.loc[int(sel)]
                        save_disposition(
                            entity_type="member",
                            entity_id=str(row.get("entity_id", "")),
                            entity_name=str(row.get("entity_name", "")),
                            watch_name=str(row.get("watch_name", "")),
                            similarity=float(row.get("similarity", 0)),
                            list_name=row.get("list"),
                            program=row.get("program"),
                            country=row.get("country"),
                            status=status,
                            notes=notes or None,
                        )
                        st.success("Disposition saved.")

        # ----------------- Fuzzy (counterparties) -----------------
        with tabs[2]:
            st.subheader("🔎 Fuzzy Screening — Counterparties (from transactions)")
            th2 = st.slider(
                "Similarity threshold (counterparties)",
                0.70,
                0.99,
                0.90,
                0.01,
            )
            chits = sanctions_txn_hits(threshold=float(th2))
            if chits.empty:
                st.info("No fuzzy hits (counterparties) at the selected threshold.")
            else:
                st.dataframe(chits, use_container_width=True, height=420)
                st.download_button(
                    "⬇️ Export CSV",
                    chits.to_csv(index=False).encode("utf-8"),
                    "sanctions_fuzzy_counterparties.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

                if "similarity" in chits.columns:
                    fig = px.histogram(
                        chits,
                        x="similarity",
                        nbins=20,
                        title="Similarity distribution (counterparties)",
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with st.form("disp_cps"):
                    sel = st.selectbox(
                        "Pick a row", chits.index.astype(str).tolist()
                    )
                    status = st.selectbox(
                        "Status",
                        ["Open", "Cleared", "Escalated"],
                        key="cp_status",
                    )
                    notes = st.text_input(
                        "Notes (optional)", key="cp_notes"
                    )
                    submitted = st.form_submit_button(
                        "Save disposition", use_container_width=True
                    )
                    if submitted:
                        row = chits.loc[int(sel)]
                        save_disposition(
                            entity_type="counterparty",
                            entity_id=str(row.get("member_id", "")),
                            entity_name=str(row.get("counterparty", "")),
                            watch_name=str(row.get("watch_name", "")),
                            similarity=float(row.get("similarity", 0)),
                            list_name=row.get("list"),
                            program=row.get("program"),
                            country=row.get("country"),
                            status=status,
                            notes=notes or None,
                        )
                        st.success("Disposition saved.")

        # ----------------- Register -----------------
        with tabs[3]:
            st.subheader("🗃️ Recent Screenings / Dispositions")
            reg = recent_screenings(limit=300)
            if reg.empty:
                st.info("No dispositions recorded yet.")
            else:
                st.dataframe(reg, use_container_width=True, height=420)
                st.download_button(
                    "⬇️ Export Register CSV",
                    reg.to_csv(index=False).encode("utf-8"),
                    "sanctions_screenings_register.csv",
                    mime="text/csv",
                    use_container_width=True,
                )


# ============================================================
# 4. Entrypoint
# ============================================================
page = SanctionsScreeningPage()
page.run()