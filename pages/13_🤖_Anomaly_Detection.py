# pages/13_🤖_Anomaly_Detection.py
from __future__ import annotations

import os
import sys
import io
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

# sklearn is optional: try to use it; fallback if unavailable
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.neighbors import LocalOutlierFactor

    _HAVE_SK = True
except Exception:
    _HAVE_SK = False

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
from sacco_core.db import query
from sacco_core.state import seed_shared_filters, filters_ui, where_and_params

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
# 2. Page config
# ============================================================
st.set_page_config(
    page_title="Anomaly Detection",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 3. Auth + module guard + unified sidebar
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

# Render unified sidebar for AML module
render_sidebar()

# ============================================================
# 4. Helper functions (unchanged core logic)
# ============================================================
def run(sql, params=None):
    return query(sql, params)


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def _safe_div(a, b):
    return float(a) / float(b) if (b not in (0, None) and float(b) != 0.0) else 0.0


def _WHERE(clause: str) -> str:
    """Turn a 'col = ? AND ...' clause into a 'WHERE ...' snippet (or empty)."""
    return f"WHERE {clause}" if clause and clause.strip() else ""


# ============================================================
# 5. Page class with RBAC + audit
# ============================================================
class AnomalyDetectionPage:
    """
    AML / CFT — Anomaly Detection
    Isolation Forest + LOF on engineered behavioral features,
    with simple |z|-based explanations.
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
            page_id="13_🤖_Anomaly_Detection.py",
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
                    object_id="Anomaly_Detection",
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
                object_id="Anomaly_Detection",
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
                    page="Anomaly_Detection",
                )
            except Exception:
                pass

        return True

    # ---------------- Main render ----------------
    def run(self):
        # ---------- Shared Filters ----------
        seed_shared_filters()
        branch, product, d_from, d_to = filters_ui()
        where_clause, params = where_and_params(
            date_col="ts",
            date_from=d_from,
            date_to=d_to,
            branch=branch,
            product=product,
            table_hint="transactions",
        )
        where_sql = _WHERE(where_clause)

        st.title("🤖 Anomaly Detection — Isolation Forest & LOF")
        st.caption(
            "Configurable ML-based detection using behavioral features; "
            "combined score with simple explanations."
        )
        st.markdown("---")

        # ---------- Feature engineering (per member in window) ----------
        st.markdown("### 🧮 Feature Engineering")
        features = run(
            f"""
            WITH win AS (
              SELECT member_id, ts, amount, channel, product, counterparty,
                     EXTRACT(HOUR FROM ts) AS hr
              FROM transactions
              {where_sql}
            ),
            agg AS (
              SELECT
                member_id,
                COUNT(*) AS txn_count,
                SUM(CASE WHEN amount>0 THEN amount ELSE 0 END) AS inflow,
                SUM(CASE WHEN amount<0 THEN -amount ELSE 0 END) AS outflow,
                AVG(ABS(amount)) AS avg_abs_amount,
                STDDEV(ABS(amount)) AS std_abs_amount,
                SUM(CASE WHEN channel='CASH' AND amount>0 THEN amount ELSE 0 END) AS cash_inflow,
                SUM(CASE WHEN hr IN (0,1,2,3,4,23) THEN 1 ELSE 0 END) AS odd_hours_txn,
                COUNT(DISTINCT counterparty) AS counterparties
              FROM win
              GROUP BY member_id
            )
            SELECT * FROM agg
            ORDER BY txn_count DESC
            """,
            params,
        )

        if features.empty:
            st.info("No transactions in the selected window; adjust filters.")
            return

        # Ratios & derived
        df = features.copy()
        df["inflow_outflow_ratio"] = df.apply(
            lambda r: _safe_div(r["outflow"], r["inflow"]), axis=1
        )
        df["pct_cash_inflow"] = df.apply(
            lambda r: _safe_div(r["cash_inflow"], r["inflow"]), axis=1
        )
        df["pct_odd_hours"] = df.apply(
            lambda r: _safe_div(r["odd_hours_txn"], r["txn_count"]), axis=1
        )

        use_cols = [
            "txn_count",
            "avg_abs_amount",
            "std_abs_amount",
            "inflow",
            "outflow",
            "inflow_outflow_ratio",
            "pct_cash_inflow",
            "pct_odd_hours",
            "counterparties",
        ]
        X = df[use_cols].fillna(0.0).values

        # ---------- Models ----------
        st.markdown("### 🧪 Models & Parameters")
        colp1, colp2, colp3 = st.columns(3)
        contamination = float(
            colp1.slider(
                "Contamination (IForest/LOF)",
                min_value=0.01,
                max_value=0.10,
                value=0.03,
                step=0.01,
            )
        )
        n_neighbors = int(
            colp2.slider(
                "LOF neighbors", min_value=10, max_value=50, value=20, step=2
            )
        )
        random_state = int(
            colp3.number_input("Random seed", value=42, step=1)
        )

        # Prepare outputs
        out = df[["member_id"]].copy()

        if _HAVE_SK:
            # Isolation Forest (higher score = more normal in sklearn; invert)
            iforest = IsolationForest(
                n_estimators=200,
                contamination=contamination,
                random_state=random_state,
            )
            iforest.fit(X)
            iso_scores = -iforest.score_samples(
                X
            )  # invert so higher = more anomalous

            # LOF (negative_outlier_factor_; invert & normalize)
            lof = LocalOutlierFactor(
                n_neighbors=n_neighbors,
                contamination=contamination,
                novelty=False,
            )
            lof.fit_predict(X)
            lof_scores_raw = -lof.negative_outlier_factor_
            lof_scores = (lof_scores_raw - np.min(lof_scores_raw)) / (
                np.ptp(lof_scores_raw) + 1e-9
            )

            # Combine scores (0..1)
            iso_norm = (iso_scores - np.min(iso_scores)) / (
                np.ptp(iso_scores) + 1e-9
            )
            combo = (iso_norm + lof_scores) / 2.0

            out["iforest_score"] = iso_norm
            out["lof_score"] = lof_scores
            out["anomaly_score"] = combo
        else:
            # Fallback: robust z magnitude on a subset of features
            z = (X - np.median(X, axis=0)) / (np.std(X, axis=0) + 1e-9)
            mag = np.sqrt((z**2).sum(axis=1))
            mag_norm = (mag - mag.min()) / (mag.ptp() + 1e-9)
            out["iforest_score"] = np.nan
            out["lof_score"] = np.nan
            out["anomaly_score"] = mag_norm
            st.warning(
                "scikit-learn not installed. Falling back to robust z-score magnitude.",
                icon="⚠️",
            )

        # Per-feature z for explanation
        for c in use_cols:
            zc = (df[c] - df[c].mean()) / (df[c].std(ddof=0) + 1e-9)
            out[f"z_{c}"] = zc

        # Simple explanation = top |z| contributors
        def explain_row(row, topk=3):
            zs = {
                c.replace("z_", ""): abs(row[c])
                for c in out.columns
                if c.startswith("z_")
            }
            top = sorted(zs.items(), key=lambda kv: kv[1], reverse=True)[:topk]
            return ", ".join(f"{k} (|z|={v:.1f})" for k, v in top)

        out["explanation"] = out.apply(lambda r: explain_row(r), axis=1)
        out = out.sort_values("anomaly_score", ascending=False)

        # Controls & Table
        topn = st.slider(
            "Top N anomalies",
            min_value=20,
            max_value=500,
            value=100,
            step=10,
        )
        st.markdown("### 🔝 Top Anomalies")
        st.dataframe(out.head(topn), use_container_width=True, height=380)

        st.download_button(
            "⬇️ Export CSV (Top Anomalies)",
            to_csv_bytes(out.head(topn)),
            file_name="anomalies_top.csv",
            use_container_width=True,
        )

        # Feature contribution overview (aggregate |z| across Top N)
        importance = pd.DataFrame(
            {
                "feature": [c for c in use_cols],
                "abs_z_sum": [
                    out.head(topn)[f"z_{c}"].abs().sum() for c in use_cols
                ],
            }
        ).sort_values("abs_z_sum", ascending=False)
        st.markdown(
            "### 🧭 Feature Contribution (aggregate |z| across Top N)"
        )
        fig_imp = px.bar(
            importance,
            x="feature",
            y="abs_z_sum",
            title="Aggregate |z|-contribution (Top N)",
        )
        st.plotly_chart(fig_imp, use_container_width=True)

        # Quick scatter: score vs avg amount (if available)
        if "avg_abs_amount" in df.columns:
            merged = out.head(topn).merge(
                df[["member_id", "txn_count", "avg_abs_amount"]],
                on="member_id",
                how="left",
            )
            fig_sc = px.scatter(
                merged,
                x="avg_abs_amount",
                y="anomaly_score",
                hover_data=["member_id", "txn_count"],
                title="Anomaly Score vs Avg Amount",
            )
            st.plotly_chart(fig_sc, use_container_width=True)

        st.markdown("---")
        st.caption(
            "Scores blend Isolation Forest & LOF on engineered behaviors; "
            "explanations list top |z|-contributors per member."
        )

        # ---- Drill-through to Transaction Monitoring ----
        if "member_id" in out.columns and not out.empty:
            sel_mid = st.selectbox(
                "Open selected member in Transaction Monitoring (Realtime)",
                out.head(topn)["member_id"].astype(str).unique(),
            )
            if st.button("🔎 Open Member in Monitoring"):
                st.session_state["nav_current"] = (
                    "Transaction Monitoring:Realtime"
                )
                st.session_state["tm_focus_member"] = str(sel_mid)
                st.switch_page("pages/3_💳_Transaction_Monitoring.py")


# ============================================================
# 6. Entrypoint
# ============================================================
page = AnomalyDetectionPage()
page.run()