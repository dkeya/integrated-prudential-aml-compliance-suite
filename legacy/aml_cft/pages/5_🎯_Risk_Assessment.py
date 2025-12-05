# pages/5_🎯_Risk_Assessment.py
from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.express as px

from sacco_core.navigation import render_sidebar
from sacco_core.audit import log_page_access, log_action
from sacco_core.state import seed_shared_filters, filters_ui, where_and_params
from sacco_core.aml.risk import (
    customer_risk_scores,            # new richer scoring (accepts filters)
    customer_risk_scores_legacy,     # exact legacy scoring (fallback safety)
    product_risk_scores,
    geographic_risk_scores,
    overall_risk_heatmap,
)

st.set_page_config(page_title="Risk Assessment", page_icon="🎯", layout="wide")
with st.sidebar:
    render_sidebar()

# ---- Audit (unchanged) ----
try:
    log_page_access(
        user=st.session_state.get("user_id", "demo_user"),
        role=st.session_state.get("user_role", "AML_Officer"),
        page="Risk_Assessment",
    )
except Exception:
    pass

st.title("🎯 Risk Assessment")
st.markdown("---")

# ---- Global filters (now actually used) ----
seed_shared_filters()
branch, product, d_from, d_to = filters_ui("Global Date Filter (affects Tx-derived metrics)")
where_sql, params = where_and_params(
    date_col="ts",
    date_from=d_from,
    date_to=d_to,
    branch=branch,
    product=product,
    table_hint="transactions",
)

# Tabs (unchanged)
tab_hint = st.session_state.get("nav_tab_hint")
labels = ["Customer Risk", "Product Risk", "Geographic Risk", "Overall Heatmap"]
idx = labels.index(tab_hint) if tab_hint in labels else 0
t1, t2, t3, t4 = st.tabs(labels)

# ---------------- Customer Risk ----------------
with t1:
    st.subheader("👥 Customer Risk Scoring (0–1)")
    # Prefer richer scoring; if it fails/empty, fall back to legacy
    try:
        df = customer_risk_scores(where_sql=where_sql, params=params)
    except Exception:
        df = pd.DataFrame()
    if df is None or df.empty:
        try:
            df = customer_risk_scores_legacy()
        except Exception:
            df = pd.DataFrame()

    if df.empty:
        st.info("No member or transaction data available for scoring.")
    else:
        # Handle both naming schemes: new ('score','band') vs legacy ('risk_score','risk_band')
        score_col = "score" if "score" in df.columns else ("risk_score" if "risk_score" in df.columns else None)
        band_col = "band" if "band" in df.columns else ("risk_band" if "risk_band" in df.columns else None)
        if score_col is None:
            # Ensure page still renders even if columns differ
            score_col = next((c for c in df.columns if c.endswith("score")), None)

        c1, c2 = st.columns([3, 2])
        with c1:
            st.dataframe(df, use_container_width=True, height=420)
        with c2:
            if score_col and score_col in df.columns:
                fig = px.histogram(df, x=score_col, nbins=20, title="Distribution of Customer Risk")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.caption("Histogram skipped: score column not found.")

        st.download_button(
            "⬇️ Export Customer Risk (CSV)",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="risk_customer.csv",
            use_container_width=True,
        )

# ---------------- Product Risk ----------------
with t2:
    st.subheader("📦 Product Risk Scoring")
    try:
        pr = product_risk_scores(where_sql=where_sql, params=params)
    except Exception:
        pr = pd.DataFrame()

    if pr.empty:
        st.info("Product column not available in transactions.")
    else:
        c1, c2 = st.columns([3, 2])
        with c1:
            st.dataframe(pr, use_container_width=True, height=420)
        with c2:
            bar_y = "score" if "score" in pr.columns else ( "avg_amount" if "avg_amount" in pr.columns else None )
            if bar_y:
                fig = px.bar(
                    pr.sort_values(bar_y, ascending=False),
                    x="product",
                    y=bar_y,
                    title=f"Product Risk ({bar_y})"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.caption("Bar chart skipped: no suitable score column on product view.")
        st.download_button(
            "⬇️ Export Product Risk (CSV)",
            data=pr.to_csv(index=False).encode("utf-8"),
            file_name="risk_product.csv",
            use_container_width=True,
        )

# ---------------- Geographic Risk ----------------
with t3:
    st.subheader("🌍 Geographic Risk")
    try:
        gr = geographic_risk_scores(where_sql=where_sql, params=params)
    except Exception:
        gr = pd.DataFrame()

    if gr.empty:
        st.info("No geo/branch/country field available.")
    else:
        # The function can return either members/country view or txn geo fallback
        # Pick axis columns safely
        x_col = None
        if "geo" in gr.columns:
            x_col = "geo"
        elif "country" in gr.columns:
            x_col = "country"

        c1, c2 = st.columns([3, 2])
        with c1:
            st.dataframe(gr, use_container_width=True, height=420)
        with c2:
            y_col = "score" if "score" in gr.columns else None
            if x_col and y_col:
                fig = px.bar(
                    gr.sort_values(y_col, ascending=False),
                    x=x_col, y=y_col,
                    title="Geographic Risk Score"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.caption("Bar chart skipped: missing score/axis column.")
        st.download_button(
            "⬇️ Export Geographic Risk (CSV)",
            data=gr.to_csv(index=False).encode("utf-8"),
            file_name="risk_geo.csv",
            use_container_width=True,
        )

# ---------------- Overall Heatmap ----------------
with t4:
    st.subheader("🗺️ Overall Risk Heatmap (Customer × Product, txn counts or avg score)")
    try:
        hm = overall_risk_heatmap(where_sql=where_sql, params=params)
    except Exception:
        hm = pd.DataFrame()

    if hm is None or hm.empty:
        st.info("Insufficient data (need member_id and product in transactions).")
    else:
        # The new function can return:
        #   A) aggregated table: ["branch","top_product","avg_score","members"]
        #   B) legacy pivot (matrix) member×product counts
        plot_done = False

        if {"branch","top_product","avg_score"}.issubset(hm.columns):
            # Pivot to a matrix for heatmap
            mat = hm.pivot_table(index="branch", columns="top_product", values="avg_score", fill_value=0.0)
            st.dataframe(mat, use_container_width=True, height=420)
            fig = px.imshow(
                mat.values,
                aspect="auto",
                color_continuous_scale="RdBu_r",
                labels=dict(color="Avg Score"),
                title="Heatmap: Branch × Top Product (Avg Customer Score)"
            )
            fig.update_xaxes(
                title_text="Top Product",
                tickmode="array",
                tickvals=list(range(len(mat.columns))),
                ticktext=list(mat.columns),
            )
            fig.update_yaxes(
                title_text="Branch",
                tickmode="array",
                tickvals=list(range(len(mat.index))),
                ticktext=[str(x) for x in mat.index],
            )
            st.plotly_chart(fig, use_container_width=True)
            st.download_button(
                "⬇️ Export Heatmap (CSV)",
                data=mat.reset_index().to_csv(index=False).encode("utf-8"),
                file_name="risk_heatmap_avgscore.csv",
                use_container_width=True,
            )
            plot_done = True

        if not plot_done:
            # Assume it's already a pivot-like matrix (legacy)
            # If it's not a pivot, show table safely.
            if isinstance(hm.index, pd.RangeIndex) or "member_id" in hm.columns:
                # If it's a plain table, try to pivot; else display raw
                try:
                    # Attempt to find matrix shape: first column as index, rest as products
                    mat = hm.copy()
                    if "member_id" in mat.columns:
                        mat = mat.set_index("member_id")
                    st.dataframe(mat, use_container_width=True, height=420)
                    fig = px.imshow(
                        mat.values,
                        aspect="auto",
                        color_continuous_scale="RdBu_r",
                        labels=dict(color="Txn Count"),
                        title="Heatmap (top entities × products)"
                    )
                    fig.update_xaxes(
                        title_text="Product",
                        tickmode="array",
                        tickvals=list(range(len(mat.columns))),
                        ticktext=list(mat.columns),
                    )
                    fig.update_yaxes(
                        title_text="Entity",
                        tickmode="array",
                        tickvals=list(range(len(mat.index))),
                        ticktext=[str(x) for x in mat.index],
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception:
                    st.dataframe(hm, use_container_width=True, height=420)
            else:
                # Already matrix-like
                st.dataframe(hm, use_container_width=True, height=420)
                fig = px.imshow(
                    hm.values,
                    aspect="auto",
                    color_continuous_scale="RdBu_r",
                    labels=dict(color="Txn Count"),
                    title="Heatmap (top 200 customers × products)"
                )
                fig.update_xaxes(
                    title_text="Product",
                    tickmode="array",
                    tickvals=list(range(len(hm.columns))),
                    ticktext=list(hm.columns),
                )
                fig.update_yaxes(
                    title_text="Member (top)",
                    tickmode="array",
                    tickvals=list(range(len(hm.index))),
                    ticktext=[str(x) for x in hm.index],
                )
                st.plotly_chart(fig, use_container_width=True)

        # Export (raw hm table too)
        st.download_button(
            "⬇️ Export Table (CSV)",
            data=hm.reset_index().to_csv(index=False).encode("utf-8"),
            file_name="risk_heatmap_table.csv",
            use_container_width=True,
        )

# ---- Log action (unchanged) ----
if st.button("📌 Log Risk Snapshot (top stats)"):
    try:
        # keep the side-effect lightweight
        cr = customer_risk_scores(where_sql=where_sql, params=params)
        cnt = int(len(cr)) if cr is not None else 0
        log_action(
            "risk_snapshot",
            user=st.session_state.get("user_id", "demo_user"),
            payload={"customer_rows": cnt},
        )
    except Exception:
        pass
    st.success("Risk snapshot logged.")