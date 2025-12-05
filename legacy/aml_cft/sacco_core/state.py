# sacco_core/state.py
from __future__ import annotations
import streamlit as st
from datetime import date, timedelta
from typing import List, Tuple, Optional
import pandas as pd

from sacco_core.db import query

# ---- helpers --------------------------------------------------------------

def _cols(table: str) -> List[str]:
    try:
        df = query(f"PRAGMA table_info({table})")
        if isinstance(df, pd.DataFrame) and "name" in df.columns:
            return df["name"].astype(str).str.lower().tolist()
    except Exception:
        pass
    return []

def _distinct_values(table: str, col: str, limit: int = 2000) -> List[str]:
    try:
        if col.lower() not in _cols(table):
            return []
        df = query(f"SELECT DISTINCT {col} AS v FROM {table} WHERE {col} IS NOT NULL LIMIT {int(limit)}")
        return sorted([str(x) for x in df["v"].dropna().tolist()])
    except Exception:
        return []

def _ts_minmax(table: str, ts_col: str) -> Tuple[Optional[date], Optional[date]]:
    try:
        if ts_col.lower() not in _cols(table):
            return None, None
        df = query(f"SELECT CAST(MIN({ts_col}) AS DATE) AS dmin, CAST(MAX({ts_col}) AS DATE) AS dmax FROM {table}")
        if df is None or df.empty:
            return None, None
        dmin = pd.to_datetime(df["dmin"].iloc[0]).date() if pd.notna(df["dmin"].iloc[0]) else None
        dmax = pd.to_datetime(df["dmax"].iloc[0]).date() if pd.notna(df["dmax"].iloc[0]) else None
        return dmin, dmax
    except Exception:
        return None, None

# ---- shared filters API ---------------------------------------------------

def seed_shared_filters():
    """
    Initialize global (session) filters used across AML pages.
    We source options from TRANSACTIONS if available; else MEMBERS.
    """
    if "filters_seeded" in st.session_state:
        return

    # Prefer transactions table to discover branches/products + date range
    source_table = "transactions" if _cols("transactions") else ("members" if _cols("members") else None)

    # Defaults
    st.session_state.setdefault("flt_branch", "All")
    st.session_state.setdefault("flt_product", "All")

    # options
    branch_opts: List[str] = ["All"]
    prod_opts: List[str] = ["All"]

    if source_table:
        if "branch" in _cols(source_table):
            branch_opts += _distinct_values(source_table, "branch")
        elif source_table != "members" and "branch" in _cols("members"):
            branch_opts += _distinct_values("members", "branch")

        if "product" in _cols(source_table):
            prod_opts += _distinct_values(source_table, "product")

    st.session_state["flt_branch_opts"] = branch_opts
    st.session_state["flt_product_opts"] = prod_opts

    # dates: 30-day window ending at max(ts) if present, else today
    dmin, dmax = (None, None)
    if source_table and ("ts" in _cols(source_table)):
        dmin, dmax = _ts_minmax(source_table, "ts")

    today = date.today()
    default_end = dmax or today
    default_start = max((default_end - timedelta(days=30)), dmin or (default_end - timedelta(days=30)))

    st.session_state.setdefault("flt_date_from", default_start)
    st.session_state.setdefault("flt_date_to", default_end)

    st.session_state["filters_seeded"] = True

def filters_ui(title: Optional[str] = None):
    """
    Render the unified filter row (branch, product, date from/to).

    Args:
        title: Optional heading to render above the filters. If omitted, nothing is shown.
    Returns:
        (branch, product, date_from, date_to)
    """
    with st.container():
        if title:
            st.subheader(title)

        c1, c2, c3, c4 = st.columns([1.2, 1.2, 1, 1])

        branch = c1.selectbox(
            "Branch",
            options=st.session_state.get("flt_branch_opts", ["All"]),
            index=(st.session_state.get("flt_branch_opts", ["All"]).index(st.session_state.get("flt_branch","All"))
                   if st.session_state.get("flt_branch","All") in st.session_state.get("flt_branch_opts", ["All"]) else 0),
            key="flt_branch"
        )
        product = c2.selectbox(
            "Product",
            options=st.session_state.get("flt_product_opts", ["All"]),
            index=(st.session_state.get("flt_product_opts", ["All"]).index(st.session_state.get("flt_product","All"))
                   if st.session_state.get("flt_product","All") in st.session_state.get("flt_product_opts", ["All"]) else 0),
            key="flt_product"
        )
        d_from = c3.date_input("From", value=st.session_state.get("flt_date_from"))
        d_to = c4.date_input("To", value=st.session_state.get("flt_date_to"))

        # Persist back
        st.session_state["flt_date_from"] = d_from
        st.session_state["flt_date_to"] = d_to

    return branch, product, d_from, d_to


def where_and_params(
    date_col: str = "ts",
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    branch: Optional[str] = None,
    product: Optional[str] = None,
    table_hint: str = "transactions",
) -> Tuple[str, Tuple]:
    cols = _cols(table_hint)
    parts: List[str] = []
    params: List = []

    # Date range (cast params to DATE so DuckDB can do date math)
    if date_from and date_col.lower() in cols:
        parts.append(f"{date_col} >= CAST(? AS DATE)")
        params.append(pd.to_datetime(date_from).strftime("%Y-%m-%d"))

    if date_to and date_col.lower() in cols:
        # exclusive upper bound: < (CAST(? AS DATE) + INTERVAL 1 DAY)
        parts.append(f"{date_col} < CAST(? AS DATE) + INTERVAL 1 DAY")
        params.append(pd.to_datetime(date_to).strftime("%Y-%m-%d"))

    # Branch
    if branch and branch != "All" and "branch" in cols:
        parts.append("branch = ?")
        params.append(branch)

    # Product
    if product and product != "All" and "product" in cols:
        parts.append("product = ?")
        params.append(product)

    return (" AND ".join(parts), tuple(params))
