# pages/6_👑_PEP_Screening.py
from __future__ import annotations

import os
import sys
from datetime import datetime

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
from sacco_core.state import seed_shared_filters
from sacco_core.db import query  # used in triage query block

from sacco_core.aml.sanctions import (
    sanctions_exact_hits,
    sanctions_fuzzy_hits,
    sanctions_txn_hits,
    save_disposition,
    recent_screenings,
    refresh_watchlist_from_csv,
    ensure_batch_schema,
    enqueue_batch_job,
    run_batch_job,
    list_jobs,
    job_hits,
    triage_hit,
)

from sacco_core.audit import log_page_access, log_action

# --- Unified core imports (same shell as other pages) ---
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
# 3. AML / CFT – PEP & Screening page (unified)
# ============================================================
class PepScreeningPage:
    """
    AML / CFT – PEP & Sanctions Screening

    • Uses legacy AML sanctions engine (ad-hoc / batch / triage / watchlist).
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
            page_id="6_👑_PEP_Screening.py",
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
                    object_id="PEP_Screening",
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
                object_id="PEP_Screening",
                extra={"module": "aml_cft", "timestamp": datetime.now().isoformat()},
            )
        except Exception:
            pass

        # Legacy audit – keep previous behaviour
        try:
            log_page_access(
                user=st.session_state.get("user_id", self.user),
                role=st.session_state.get("user_role", self.role),
                page="PEP_Screening",
            )
        except Exception:
            pass

        return True

    # ---------------- Main render ----------------
    def run(self):
        # Title
        st.title("👑 PEP & Screening")

        # Shared/global filters state if needed by downstream calls
        seed_shared_filters()

        tabs = st.tabs(
            [
                "🔍 Ad-hoc Screening",
                "🧳 Batch Screening Jobs",
                "🧪 Triage (Hits → Cases)",
                "📥 Watchlist Refresh",
            ]
        )

        # ----------------------------- Ad-hoc Screening -----------------------------
        with tabs[0]:
            st.subheader("🔍 Ad-hoc Screening")

            c1, c2, c3 = st.columns([1, 1, 1])
            threshold = c1.slider(
                "Fuzzy threshold", 0.70, 0.99, 0.88, 0.01, key="adhoc_thr"
            )
            src = c2.selectbox(
                "Source", ["members", "counterparties"], key="adhoc_src"
            )
            limit_watch = int(
                c3.number_input(
                    "Watchlist rows limit",
                    value=5000,
                    min_value=100,
                    step=100,
                    key="adhoc_wl_lim",
                )
            )

            left, right = st.columns([2, 1])
            with left:
                st.markdown("### Fuzzy hits")
                fuzz = sanctions_fuzzy_hits(
                    threshold=threshold, limit_watch=limit_watch, source=src
                )
                st.dataframe(fuzz, use_container_width=True, height=320)
            with right:
                st.markdown("### Exact matches (members)")
                exact = sanctions_exact_hits(limit=1000)
                st.dataframe(exact, use_container_width=True, height=320)

            st.markdown("### Counterparty screening (from transactions)")
            cnt = sanctions_txn_hits(threshold=threshold)
            st.dataframe(cnt, use_container_width=True, height=280)

        # ----------------------------- Batch Screening Jobs -----------------------------
        with tabs[1]:
            st.subheader("🧳 Batch Screening Jobs")

            ensure_batch_schema()
            c1, c2, c3 = st.columns([1, 1, 1])
            b_src = c1.selectbox(
                "Source", ["members", "counterparties"], key="batch_src"
            )
            b_thr = c2.slider(
                "Threshold", 0.70, 0.99, 0.88, 0.01, key="batch_thr"
            )
            if c3.button("➕ Enqueue Job", use_container_width=True, key="enqueue_btn"):
                jid = enqueue_batch_job(source=b_src, threshold=float(b_thr))
                st.success(f"Job enqueued (ID={jid}).")

            st.markdown("### Jobs")
            jobs = list_jobs()
            st.dataframe(jobs, use_container_width=True, height=260)

            if not jobs.empty:
                job_ids = jobs["job_id"].tolist()
                sel = st.selectbox("Select Job", job_ids, key="job_pick")
                c_run, c_view = st.columns([1, 1])
                if c_run.button(
                    "▶ Run Job", key="run_job_btn", use_container_width=True
                ):
                    n = run_batch_job(int(sel))
                    st.success(f"Job {sel} completed. Hits: {n}")
                    st.rerun()

                hits = job_hits(int(sel))
                st.markdown("### Hits (snapshot)")
                st.dataframe(hits, use_container_width=True, height=320)
                st.download_button(
                    "⬇️ Export Hits CSV",
                    hits.to_csv(index=False).encode("utf-8"),
                    file_name=f"sanctions_hits_job_{sel}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="hits_export_btn",
                )

        # ----------------------------- Triage -----------------------------
        with tabs[2]:
            st.subheader("🧪 Hit Triage (link to Investigations)")

            c1, c2 = st.columns([1, 1])
            job_list = list_jobs()
            jopt = c1.selectbox(
                "Filter by Job (optional)",
                [None] + job_list["job_id"].tolist() if not job_list.empty else [None],
                key="tri_job",
            )
            status_filter = c2.selectbox(
                "Triage Status", ["All", "Open", "Cleared", "Escalated"], key="tri_status"
            )

            if jopt is None:
                ensure_batch_schema()
                where = []
                params = []
                if status_filter != "All":
                    where.append("triage_status = ?")
                    params.append(status_filter)
                sql = "SELECT * FROM sanctions_hits"
                if where:
                    sql += " WHERE " + " AND ".join(where)
                sql += " ORDER BY created_at DESC LIMIT 1000"
                hits = query(sql, tuple(params))
            else:
                hits = job_hits(int(jopt))
                if status_filter != "All" and "triage_status" in hits.columns:
                    hits = hits[hits["triage_status"] == status_filter]

            st.dataframe(hits, use_container_width=True, height=360)

            if not hits.empty:
                st.markdown("### Action")
                hsel = st.selectbox("Hit", hits["hit_id"].tolist(), key="tri_hit")
                act = st.selectbox("Action", ["Clear", "Escalate to Case"], key="tri_act")
                notes = st.text_input("Notes (optional)", key="tri_notes")
                if st.button("💾 Apply", use_container_width=True, key="tri_apply"):
                    if act == "Clear":
                        triage_hit(
                            int(hsel),
                            status="Cleared",
                            notes=notes or None,
                            create_case=False,
                            user=st.session_state.get("user_id", "mlro"),
                        )
                        st.success("Hit cleared.")
                    else:
                        cid = triage_hit(
                            int(hsel),
                            status="Escalated",
                            notes=notes or None,
                            create_case=True,
                            user=st.session_state.get("user_id", "mlro"),
                        )
                        if cid:
                            st.success(f"Hit escalated → Case {cid}.")
                        else:
                            st.warning("Escalation attempted, but case was not created.")
                    st.rerun()

        # ----------------------------- Watchlist Refresh -----------------------------
        with tabs[3]:
            st.subheader("📥 Watchlist Refresh & Audit")

            up = st.file_uploader(
                "Upload CSV with at least a 'name' column",
                type=["csv"],
                key="wl_file",
            )
            c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
            list_name = c1.text_input("List", value="Custom", key="wl_list")
            program = c2.text_input("Program", value="", key="wl_program")
            country = c3.text_input("Country", value="", key="wl_country")
            source = c4.text_input("Source label", value="upload", key="wl_source")
            if st.button(
                "⏫ Load / Refresh", use_container_width=True, key="wl_load_btn"
            ):
                n = refresh_watchlist_from_csv(
                    up,
                    list_name=list_name,
                    program=program,
                    country=country,
                    source=source,
                )
                if n > 0:
                    st.success(f"Loaded {n} names into sanctions_list.")
                else:
                    st.warning(
                        "No rows loaded. Ensure a 'name' column exists in the CSV."
                    )

            st.markdown("### Latest watchlist meta")
            try:
                meta = query(
                    "SELECT * FROM watchlist_meta "
                    "ORDER BY loaded_at DESC LIMIT 200"
                )  # type: ignore
            except Exception:
                meta = pd.DataFrame(
                    columns=[
                        "list",
                        "program",
                        "country",
                        "source",
                        "loaded_at",
                        "note",
                    ]
                )
            st.dataframe(meta, use_container_width=True, height=260)

        # Optional: simple action log when page fully rendered
        try:
            log_action(
                "pep_screening_view",
                user=st.session_state.get("user_id", self.user),
                payload={"module": "aml_cft"},
            )
        except Exception:
            pass


# ============================================================
# 4. Entrypoint
# ============================================================
if __name__ == "__main__":
    page = PepScreeningPage()
    page.run()
