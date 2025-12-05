# sacco_core/aml/alerts.py
from __future__ import annotations
from typing import Tuple, Dict, Any, Optional, List
import pandas as pd
import numpy as np
from datetime import date

from sacco_core.db import query
from sacco_core.aml.reporting import ctr_hits, ctr_weekly_aggregates
from sacco_core.aml.transactions import structuring_staircase, rapid_movement, behavioral_stats
from sacco_core.aml.sanctions import screen_members, screen_counterparties

def _tag_df(df: pd.DataFrame, kind: str) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=["alert_type","entity","member_id","ts","score","details"])
    dfx = df.copy()
    dfx["alert_type"] = kind
    return dfx

def _s(df: pd.DataFrame, col: str, default, n: Optional[int] = None) -> pd.Series:
    """
    Safe column accessor that always returns a Series of length len(df).
    If the column doesn't exist, returns a Series filled with `default`.
    """
    if df is not None and not df.empty and col in df.columns:
        return df[col]
    # fallback length
    length = (len(df) if df is not None else (n if n is not None else 0))
    return pd.Series([default] * length)

def alerts_feed(where_sql: str = "", params: Tuple = ()) -> pd.DataFrame:
    """
    Unified alert feed from rules already implemented:
      - CTR single (uses ts)
      - CTR weekly (uses week_end as ts)
      - Structuring staircase near-unit
      - Rapid movement ratio >= 0.8
      - Sanctions/PEP member hits
      - Sanctions/PEP counterparty hits
    """
    rows: List[pd.DataFrame] = []

    # CTR single
    single = ctr_hits(where_sql=where_sql, params=params)
    if single is not None and not single.empty:
        amt = _s(single, "amount", 0.0)
        mx = float(amt.abs().max()) if len(amt) else 1.0
        mx = mx if mx > 0 else 1.0
        sub = pd.DataFrame({
            "entity": _s(single, "member_id", None),
            "member_id": _s(single, "member_id", None),
            "ts": pd.to_datetime(_s(single, "ts", pd.NaT), errors="coerce"),
            "score": (amt.astype(float) / mx).fillna(0.0),
            "details": pd.Series(["Single cash >= threshold"] * len(single)),
        })
        rows.append(_tag_df(sub, "CTR_SINGLE"))

    # CTR weekly
    wk = ctr_weekly_aggregates(where_sql=where_sql, params=params)
    if wk is not None and not wk.empty:
        cash_sum = _s(wk, "cash_sum", 0.0)
        mx = float(pd.to_numeric(cash_sum, errors="coerce").max()) if len(cash_sum) else 1.0
        mx = mx if (mx and mx > 0) else 1.0
        sub = pd.DataFrame({
            "entity": _s(wk, "member_id", None),
            "member_id": _s(wk, "member_id", None),
            "ts": pd.to_datetime(_s(wk, "week_end", pd.NaT), errors="coerce"),
            "score": (pd.to_numeric(cash_sum, errors="coerce") / mx).fillna(0.0),
            "details": pd.Series(["Weekly cash >= threshold"] * len(wk)),
        })
        rows.append(_tag_df(sub, "CTR_WEEKLY"))

    # Structuring
    stairs = structuring_staircase(where_sql=where_sql, params=params)
    if stairs is not None and not stairs.empty:
        near = stairs[stairs["near_flag"] == True] if "near_flag" in stairs.columns else pd.DataFrame()
        if not near.empty:
            cash_in = _s(near, "cash_in", 0.0)
            mx = float(pd.to_numeric(cash_in, errors="coerce").max()) if len(cash_in) else 1.0
            mx = mx if (mx and mx > 0) else 1.0
            sub = pd.DataFrame({
                "entity": _s(near, "member_id", None),
                "member_id": _s(near, "member_id", None),
                "ts": pd.to_datetime(_s(near, "day", pd.NaT), errors="coerce"),
                "score": (pd.to_numeric(cash_in, errors="coerce") / mx).fillna(0.0),
                "details": pd.Series(["Structuring near-unit multiples"] * len(near)),
            })
            rows.append(_tag_df(sub, "STRUCTURING"))

    # Rapid movement
    rm = rapid_movement(where_sql=where_sql, params=params)
    if rm is not None and not rm.empty:
        ratio = pd.to_numeric(_s(rm, "ratio", 0.0), errors="coerce").fillna(0.0)
        sub = pd.DataFrame({
            "entity": _s(rm, "member_id", None),
            "member_id": _s(rm, "member_id", None),
            "ts": pd.to_datetime(_s(rm, "start_day", pd.NaT), errors="coerce"),
            "score": ratio.astype(float),
            "details": pd.Series(["Rapid inflow→outflow"] * len(rm)),
        })
        rows.append(_tag_df(sub, "RAPID_MOVE"))

    # Behavioral outliers quick tag (top 50 by txn_count)
    beh = behavioral_stats(where_sql=where_sql, params=params)
    if beh is not None and not beh.empty:
        avg_amt = pd.to_numeric(_s(beh, "avg_amt", 0.0), errors="coerce").fillna(0.0)
        z = (avg_amt - avg_amt.mean()) / (avg_amt.std(ddof=0) + 1e-9)
        sub = pd.DataFrame({
            "entity": _s(beh, "member_id", None),
            "member_id": _s(beh, "member_id", None),
            "ts": pd.Series([pd.NaT] * len(beh)),
            "score": z.abs(),
            "details": pd.Series(["Behavioral outlier (avg_amt)"] * len(beh)),
        }).nlargest(50, "score")
        rows.append(_tag_df(sub, "BEHAVIORAL"))

    # Sanctions (members)
    mem = screen_members(where_sql=where_sql, params=params)
    if mem is not None and not mem.empty:
        details_mem = (
            _s(mem, "list_type", "SANCTIONS").astype(str)
            + " | "
            + _s(mem, "method", "EXACT").astype(str)
        )
        sub = pd.DataFrame({
            "entity": _s(mem, "entity", None),
            "member_id": _s(mem, "member_id", None),
            "ts": pd.Series([pd.NaT] * len(mem)),
            "score": pd.to_numeric(_s(mem, "score", 1.0), errors="coerce").fillna(1.0),
            "details": details_mem,
        })
        rows.append(_tag_df(sub, "SCREENING_MEMBER"))

    # Sanctions (counterparties)
    cp = screen_counterparties(where_sql=where_sql, params=params)
    if cp is not None and not cp.empty:
        details_cp = (
            _s(cp, "list_type", "SANCTIONS").astype(str)
            + " | "
            + _s(cp, "method", "EXACT").astype(str)
        )
        sub = pd.DataFrame({
            "entity": _s(cp, "counterparty", None),
            "member_id": _s(cp, "member_id", None),
            "ts": pd.to_datetime(_s(cp, "last_ts", pd.NaT), errors="coerce"),
            "score": pd.to_numeric(_s(cp, "score", 1.0), errors="coerce").fillna(1.0),
            "details": details_cp,
        })
        rows.append(_tag_df(sub, "SCREENING_CP"))

    if not rows:
        return pd.DataFrame(columns=["alert_type","entity","member_id","ts","score","details"])

    feed = pd.concat(rows, ignore_index=True)
    # Clean and order
    if "ts" in feed.columns:
        feed["ts"] = pd.to_datetime(feed["ts"], errors="coerce")
    feed["score"] = pd.to_numeric(feed["score"], errors="coerce").fillna(0.0).clip(lower=0)
    feed = feed.sort_values(["ts","score"], ascending=[False, False])
    return feed.reset_index(drop=True)

def rules_summary(feed: pd.DataFrame) -> pd.DataFrame:
    if feed is None or feed.empty:
        return pd.DataFrame(columns=["alert_type","count","avg_score"])
    grp = feed.groupby("alert_type").agg(count=("alert_type","size"), avg_score=("score","mean")).reset_index()
    return grp.sort_values("count", ascending=False)
