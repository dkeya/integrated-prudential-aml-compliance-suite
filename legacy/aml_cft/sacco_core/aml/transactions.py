# sacco_core/aml/transactions.py
from __future__ import annotations
from typing import Tuple, Dict, Any, Optional
import pandas as pd
import numpy as np

from sacco_core.db import query
from sacco_core.config import get_config, Settings  # <-- import Settings for typing

# --- Helpers ---------------------------------------------------------------

def _exists(table: str) -> bool:
    try:
        df = query("show tables")
        col = "name" if "name" in df.columns else df.columns[0]
        return table.lower() in df[col].str.lower().tolist()
    except Exception:
        return False

def _cfg() -> Settings:
    """Return typed Settings object from config."""
    return get_config()

def _where(where_sql: str) -> str:
    return f"WHERE {where_sql}" if where_sql and where_sql.strip() else ""

# --- Realtime feed / CTR ---------------------------------------------------

def realtime_txns(limit: int = 100, where_sql: str = "", params: Tuple = ()) -> pd.DataFrame:
    """
    Recent transactions with basic context. Adapts to existing columns.
    """
    if not _exists("transactions"):
        return pd.DataFrame(columns=["txn_id","member_id","ts","amount","channel","product","branch","counterparty"])

    # probe columns
    tinfo = query("PRAGMA table_info(transactions)")
    cols = tinfo["name"].str.lower().tolist()

    id_col = "txn_id" if "txn_id" in cols else ("id" if "id" in cols else None)
    member_col = "member_id" if "member_id" in cols else None

    selects = []
    if id_col: selects.append(f"{id_col} as txn_id")
    if member_col: selects.append(f"{member_col} as member_id")
    for c in ["ts","amount","channel","product","branch","counterparty","device_id","geo"]:
        if c in cols: selects.append(c)

    if not selects:
        return pd.DataFrame(columns=["txn_id","member_id","ts","amount","channel","product","branch","counterparty"])

    sql = f"""
        SELECT {', '.join(selects)}
        FROM transactions
        {_where(where_sql)}
        ORDER BY ts DESC
        LIMIT {int(limit)}
    """
    return query(sql, params)

def ctr_hits(where_sql: str = "", params: Tuple = ()) -> pd.DataFrame:
    """
    Currency Transaction Reports: single cash txn >= configured threshold.
    """
    cfg = _cfg()
    # Use object attributes with safe fallbacks
    try:
        ctr_kes = int(getattr(cfg.frc, "ctr_threshold_kes", 1_900_000))
    except Exception:
        ctr_kes = 1_900_000

    if not _exists("transactions"):
        return pd.DataFrame(columns=["txn_id","member_id","ts","amount","channel","branch","hit_type"])

    cols = query("PRAGMA table_info(transactions)")["name"].str.lower().tolist()
    id_col = "txn_id" if "txn_id" in cols else ("id" if "id" in cols else None)
    member_col = "member_id" if "member_id" in cols else None

    selects = []
    if id_col: selects.append(f"{id_col} as txn_id")
    if member_col: selects.append(f"{member_col} as member_id")
    for c in ["ts","amount","channel","branch","product"]:
        if c in cols: selects.append(c)

    channel_filter = "AND channel='CASH'" if "channel" in cols else ""
    sql = f"""
        SELECT {', '.join(selects)}, 'CTR_SINGLE' AS hit_type
        FROM transactions
        WHERE amount >= {ctr_kes} {channel_filter}
          {"AND (" + where_sql + ")" if where_sql and where_sql.strip() else ""}
        ORDER BY ts DESC
        LIMIT 1000
    """
    return query(sql, params)

# --- Structuring staircase -------------------------------------------------

def structuring_staircase(window_days: int = 7,
                          unit_kes: int = 150_000,
                          near_ratio: float = 0.8,
                          where_sql: str = "",
                          params: Tuple = ()) -> pd.DataFrame:
    """
    Detect staircase deposits: rolling sum of cash credits per member within window,
    many near-unit multiples that sit just under CTR threshold (patterning).
    Emits member_id, day, cash_in, unit_multiple, near_flag.
    """
    if not _exists("transactions"):
        return pd.DataFrame(columns=["member_id","day","cash_in","unit_multiple","near_flag"])

    # Try to pull defaults from config when caller uses the function defaults
    try:
        cfg = _cfg()
        if window_days == 7:
            window_days = int(getattr(cfg.monitoring, "structuring_window_days", window_days))
        if unit_kes == 150_000:
            unit_kes = int(getattr(cfg.monitoring, "structuring_unit_kes", unit_kes))
    except Exception:
        pass

    cols = query("PRAGMA table_info(transactions)")["name"].str.lower().tolist()
    member_col = "member_id" if "member_id" in cols else None
    if not member_col or "amount" not in cols or "ts" not in cols:
        return pd.DataFrame(columns=["member_id","day","cash_in","unit_multiple","near_flag"])

    channel_filter = "AND channel='CASH'" if "channel" in cols else ""
    sql = f"""
    WITH base AS (
      SELECT
        {member_col} AS member_id,
        CAST(ts AS DATE) AS day,
        CASE WHEN amount > 0 THEN amount ELSE 0 END AS cash_in
      FROM transactions
      WHERE 1=1 {channel_filter}
        {"AND (" + where_sql + ")" if where_sql and where_sql.strip() else ""}
    ),
    daily AS (
      SELECT member_id, day, SUM(cash_in) AS cash_in
      FROM base
      GROUP BY 1,2
    ),
    windowed AS (
      SELECT
        member_id,
        day,
        SUM(cash_in) OVER (PARTITION BY member_id ORDER BY day
                           ROWS BETWEEN {window_days-1} PRECEDING AND CURRENT ROW) AS win_cash_in
      FROM daily
    )
    SELECT
      member_id,
      day,
      win_cash_in AS cash_in,
      win_cash_in / {float(unit_kes)} AS unit_multiple,
      CASE
        WHEN win_cash_in >= {int(unit_kes*near_ratio)}
         AND MOD(CAST(win_cash_in AS BIGINT), {int(unit_kes)}) BETWEEN 0 AND {int(unit_kes*0.1)}
        THEN TRUE ELSE FALSE
      END AS near_flag
    FROM windowed
    WHERE win_cash_in > 0
    ORDER BY day DESC, member_id
    """
    return query(sql, params)

# --- Rapid movement --------------------------------------------------------

def rapid_movement(days: int = 5, pct_of_balance: float = 0.6,
                   where_sql: str = "", params: Tuple = ()) -> pd.DataFrame:
    """
    Inflow -> outflow within N days that is >= pct_of_balance (approximate).
    If balances table exists use it; else approximate with rolling net position.
    """
    if not _exists("transactions"):
        return pd.DataFrame(columns=["member_id","start_day","inflow","outflow","ratio"])

    # Sync defaults with config if caller didn't override
    try:
        cfg = _cfg()
        if days == 5:
            days = int(getattr(cfg.monitoring, "rapid_movement_days", days))
    except Exception:
        pass

    cols = query("PRAGMA table_info(transactions)")["name"].str.lower().tolist()
    member_col = "member_id" if "member_id" in cols else None
    if not member_col or "amount" not in cols or "ts" not in cols:
        return pd.DataFrame(columns=["member_id","start_day","inflow","outflow","ratio"])

    sql = f"""
    WITH base AS (
      SELECT {member_col} AS member_id, CAST(ts AS DATE) AS day, amount
      FROM transactions
      WHERE 1=1 {"AND (" + where_sql + ")" if where_sql and where_sql.strip() else ""}
    ),
    inflow AS (
      SELECT member_id, day, SUM(CASE WHEN amount>0 THEN amount ELSE 0 END) AS inflow
      FROM base GROUP BY 1,2
    ),
    outflow AS (
      SELECT member_id, day, SUM(CASE WHEN amount<0 THEN -amount ELSE 0 END) AS outflow
      FROM base GROUP BY 1,2
    ),
    joined AS (
      SELECT COALESCE(i.member_id,o.member_id) AS member_id,
             COALESCE(i.day,o.day) AS day,
             COALESCE(i.inflow,0) AS inflow,
             COALESCE(o.outflow,0) AS outflow
      FROM inflow i FULL OUTER JOIN outflow o
        ON i.member_id=o.member_id AND i.day=o.day
    ),
    windowed AS (
      SELECT
        member_id,
        day AS start_day,
        SUM(inflow) OVER (PARTITION BY member_id ORDER BY day
                          ROWS BETWEEN CURRENT ROW AND {days-1} FOLLOWING) AS inflow_n,
        SUM(outflow) OVER (PARTITION BY member_id ORDER BY day
                           ROWS BETWEEN CURRENT ROW AND {days-1} FOLLOWING) AS outflow_n
      FROM joined
    )
    SELECT member_id, start_day, inflow_n AS inflow, outflow_n AS outflow,
           CASE WHEN inflow_n>0 THEN outflow_n / inflow_n ELSE 0 END AS ratio
    FROM windowed
    WHERE inflow_n>0 AND outflow_n>0 AND outflow_n/inflow_n >= {float(pct_of_balance)}
    ORDER BY start_day DESC, member_id
    """
    return query(sql, params)

# --- Behavioral stats ------------------------------------------------------

def behavioral_stats(where_sql: str = "", params: Tuple = ()) -> pd.DataFrame:
    """
    Per-member behavior: freq, avg amount, hour-of-day spread, channel mix.
    """
    if not _exists("transactions"):
        return pd.DataFrame(columns=["member_id","txn_count","avg_amt","hour_std","cash_pct"])

    cols = query("PRAGMA table_info(transactions)")["name"].str.lower().tolist()
    member_col = "member_id" if "member_id" in cols else None
    if not member_col or "amount" not in cols or "ts" not in cols:
        return pd.DataFrame(columns=["member_id","txn_count","avg_amt","hour_std","cash_pct"])

    channel_expr = "100.0 * SUM(CASE WHEN channel='CASH' THEN 1 ELSE 0 END) / COUNT(*)" if "channel" in cols else "NULL"
    sql = f"""
    SELECT
      {member_col} AS member_id,
      COUNT(*) AS txn_count,
      AVG(ABS(amount)) AS avg_amt,
      STDDEV(EXTRACT(HOUR FROM ts)) AS hour_std,
      {channel_expr} AS cash_pct
    FROM transactions
    {_where(where_sql)}
    GROUP BY 1
    ORDER BY txn_count DESC
    """
    return query(sql, params)

# --- Anomaly detection (IF + LOF with graceful fallback) -------------------

def anomaly_scores(top_n: int = 100,
                   where_sql: str = "",
                   params: Tuple = ()) -> pd.DataFrame:
    """
    Isolation Forest + LOF on engineered features. If scikit-learn is missing,
    fall back to robust z-scores. Returns: member_id, score, method, explain JSON.
    """
    feats = behavioral_stats(where_sql, params)
    if feats.empty:
        return pd.DataFrame(columns=["member_id","score","method","explain"])

    Xcols = ["txn_count","avg_amt","hour_std"]
    X = feats[Xcols].fillna(0.0).astype(float).values

    rows = []
    try:
        from sklearn.ensemble import IsolationForest
        from sklearn.neighbors import LocalOutlierFactor

        # Isolation Forest
        iso = IsolationForest(n_estimators=200, contamination=0.02, random_state=42)
        iso.fit(X)
        iso_score = (-iso.decision_function(X))
        z = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-6)

        for i, mid in enumerate(feats["member_id"]):
            rows.append({
                "member_id": mid,
                "score": float(iso_score[i]),
                "method": "IF",
                "explain": {
                    "z_txn_count": float(z[i,0]),
                    "z_avg_amt": float(z[i,1]),
                    "z_hour_std": float(z[i,2]),
                }
            })

        # LOF
        lof = LocalOutlierFactor(n_neighbors=20, contamination=0.02)
        lof.fit_predict(X)
        lof_scores = -lof.negative_outlier_factor_

        for i, mid in enumerate(feats["member_id"]):
            rows.append({
                "member_id": mid,
                "score": float(lof_scores[i]),
                "method": "LOF",
                "explain": {
                    "neighbors": 20,
                    "txn_count": float(feats.iloc[i]["txn_count"]),
                    "avg_amt": float(feats.iloc[i]["avg_amt"]),
                    "hour_std": float(feats.iloc[i]["hour_std"]),
                }
            })

    except Exception:
        # Fallback: robust z-score
        z = (X - np.median(X, axis=0)) / (np.std(X, axis=0) + 1e-6)
        mag = np.sqrt((z**2).sum(axis=1))
        for i, mid in enumerate(feats["member_id"]):
            rows.append({
                "member_id": mid,
                "score": float(mag[i]),
                "method": "ROBUST_Z",
                "explain": {
                    "z_txn_count": float(z[i,0]),
                    "z_avg_amt": float(z[i,1]),
                    "z_hour_std": float(z[i,2]),
                }
            })

    out = pd.DataFrame(rows)
    out = out.sort_values("score", ascending=False).groupby("member_id", as_index=False).first()
    return out.sort_values("score", ascending=False).head(top_n)
