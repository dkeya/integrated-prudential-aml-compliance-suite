# sacco_core/aml/risk.py
from __future__ import annotations
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np

from sacco_core.db import query

# ---------------------------- helpers ----------------------------

def _exists(table: str) -> bool:
    try:
        df = query("SHOW TABLES")
        col = "name" if "name" in df.columns else df.columns[0]
        return table.lower() in df[col].str.lower().tolist()
    except Exception:
        return False

def _cols(table: str) -> List[str]:
    try:
        return query(f"PRAGMA table_info({table})")["name"].str.lower().tolist()
    except Exception:
        return []

def _where(where_sql: str) -> str:
    return f"WHERE {where_sql}" if where_sql and where_sql.strip() else ""

def _safe_div(a, b) -> float:
    try:
        a = float(a); b = float(b)
        return a / b if b != 0 else 0.0
    except Exception:
        return 0.0

def _z_series(s: pd.Series) -> pd.Series:
    s = s.astype(float)
    return (s - s.mean()) / (s.std(ddof=0) + 1e-9)

# ---------------------------- feature builders ----------------------------

def behavior_features(where_sql: str = "", params: Tuple = ()) -> pd.DataFrame:
    """
    Per-member features from transactions (in the filtered window).
    Returns: member_id, txn_count, inflow, outflow, avg_amt, hour_std, cash_pct, top_product
    """
    if not _exists("transactions"):
        return pd.DataFrame(columns=["member_id","txn_count","inflow","outflow","avg_amt","hour_std","cash_pct","top_product"])

    tcols = _cols("transactions")
    if not all(c in tcols for c in ["ts","amount"]):
        return pd.DataFrame(columns=["member_id","txn_count","inflow","outflow","avg_amt","hour_std","cash_pct","top_product"])
    member_col = "member_id" if "member_id" in tcols else None
    if not member_col:
        return pd.DataFrame(columns=["member_id","txn_count","inflow","outflow","avg_amt","hour_std","cash_pct","top_product"])

    # channel may be absent; compute cash_pct only if available
    channel_flag = "channel" in tcols

    # Build features + top product using windowed rank
    sql = f"""
    WITH win AS (
      SELECT
        {member_col} AS member_id,
        ts, amount,
        {"channel," if channel_flag else ""}
        {"product" if "product" in tcols else "NULL AS product"}
      FROM transactions
      {_where(where_sql)}
    ),
    agg AS (
      SELECT
        member_id,
        COUNT(*) AS txn_count,
        SUM(CASE WHEN amount>0 THEN amount ELSE 0 END) AS inflow,
        SUM(CASE WHEN amount<0 THEN -amount ELSE 0 END) AS outflow,
        AVG(ABS(amount)) AS avg_amt,
        STDDEV(EXTRACT(HOUR FROM ts)) AS hour_std,
        {("100.0 * SUM(CASE WHEN channel='CASH' THEN 1 ELSE 0 END) / COUNT(*)" if channel_flag else "CAST(NULL AS DOUBLE)")} AS cash_pct
      FROM win
      GROUP BY 1
    ),
    prod AS (
      SELECT
        member_id,
        product,
        COUNT(*) AS c,
        ROW_NUMBER() OVER (PARTITION BY member_id ORDER BY COUNT(*) DESC) AS rn
      FROM win
      WHERE product IS NOT NULL
      GROUP BY 1,2
    ),
    top_prod AS (
      SELECT member_id, product AS top_product
      FROM prod
      WHERE rn = 1
    )
    SELECT
      a.member_id, a.txn_count, a.inflow, a.outflow, a.avg_amt, a.hour_std, a.cash_pct,
      tp.top_product
    FROM agg a
    LEFT JOIN top_prod tp USING (member_id)
    ORDER BY txn_count DESC
    """
    return query(sql, params)

def members_base() -> pd.DataFrame:
    """
    Snapshot from members (id/name/branch/country/pep_flag when present).
    """
    if not _exists("members"):
        return pd.DataFrame(columns=["member_id","name","branch","country","pep_flag"])
    mcols = _cols("members")
    id_col = "member_id" if "member_id" in mcols else ("id" if "id" in mcols else None)
    name_col = "name" if "name" in mcols else ("full_name" if "full_name" in mcols else None)
    sel = []
    if id_col: sel.append(f"{id_col} AS member_id")
    if name_col: sel.append(f"{name_col} AS name")
    if "branch" in mcols: sel.append("branch")
    if "country" in mcols: sel.append("country")
    if "pep_flag" in mcols: sel.append("pep_flag")
    if not sel:
        return pd.DataFrame(columns=["member_id","name","branch","country","pep_flag"])
    return query(f"SELECT {', '.join(sel)} FROM members")

# ---------------------------- CUSTOMER risk ----------------------------

def customer_risk_scores(where_sql: str = "", params: Tuple = ()) -> pd.DataFrame:
    """
    Weighted 0..1 score using:
      • Transaction behavior (|z| of txn_count, avg_amt, hour_std)
      • PEP flag (1/0) or cross-signal absent -> 0
      • Geography (basic heuristic if country available)
      • Product proxy risk (top_product keywords)
      • Alerts density (if alerts table exists) — preserves your original signal
    Returns: member_id, name, branch, score, band (+aux columns)
    """
    beh = behavior_features(where_sql, params)
    base = members_base()

    # If we have nothing, keep the legacy skeleton
    if beh.empty and base.empty:
        return pd.DataFrame(columns=["member_id","name","branch","score","band"])

    df = base.merge(beh, on="member_id", how="left") if not base.empty else beh.copy()

    # Ensure numeric cols
    for c in ["txn_count","avg_amt","hour_std","cash_pct"]:
        if c not in df.columns:
            df[c] = np.nan

    # Alerts density (legacy feature preserved)
    alert_counts = pd.DataFrame()
    if _exists("alerts"):
        try:
            alert_counts = query("""
                SELECT
                  CAST(json_extract(linked_entities, '$[0].member_id') AS VARCHAR) AS member_id,
                  COUNT(*) AS alert_count
                FROM alerts
                GROUP BY 1
            """)
        except Exception:
            alert_counts = pd.DataFrame()
    if not alert_counts.empty:
        df = df.merge(alert_counts, on="member_id", how="left")
    if "alert_count" not in df.columns:
        df["alert_count"] = 0

    # PEP signal
    if "pep_flag" in df.columns:
        pep = df["pep_flag"].astype(str).str.upper().isin(["1","Y","YES","TRUE","T"]).astype(int)
    else:
        pep = pd.Series(0, index=df.index)

    # Geography proxy
    def _geo_label(country: Optional[str]) -> str:
        if not isinstance(country, str) or not country.strip():
            return "Medium"
        c = country.strip().upper()
        high = {"IR","KP","SY","AF","YE","SO"}
        med = {"NG","CD","SS","ET"}
        if c in high: return "High"
        if c in med: return "Medium"
        return "Low"

    geo_score = df.get("country", pd.Series([None]*len(df))).apply(
        lambda x: {"Low":0.2,"Medium":0.6,"High":1.0}.get(_geo_label(x), 0.6)
    )

    # Product proxy
    def _prod_s(p):
        if not isinstance(p, str): return 0.5
        x = p.lower()
        if any(k in x for k in ["remit","forex","cash advance","crypto","wallet"]): return 0.9
        if any(k in x for k in ["loan","overdraft"]): return 0.6
        return 0.4
    prod_score = df.get("top_product", pd.Series([None]*len(df))).apply(_prod_s)

    # Behavior: normalized |z|
    z_txn = _z_series(df["txn_count"].fillna(0.0)).abs()
    z_amt = _z_series(df["avg_amt"].fillna(0.0)).abs()
    z_hour = _z_series(df["hour_std"].fillna(0.0)).abs()
    beh_raw = (z_txn + z_amt + z_hour) / 3.0
    beh_norm = (beh_raw - beh_raw.min()) / (beh_raw.max() - beh_raw.min() + 1e-9)

    # Alerts normalized
    ac = df["alert_count"].fillna(0.0)
    ac_norm = (ac - ac.min()) / (ac.max() - ac.min() + 1e-9)

    # Weights (compatible with your earlier approach but richer)
    score = (
        0.35 * beh_norm +     # behavior
        0.25 * pep +         # pep
        0.20 * geo_score +   # geography
        0.10 * prod_score +  # product
        0.10 * ac_norm       # alerts density (legacy signal preserved)
    )

    def _band(s):
        if s >= 0.70: return "HIGH"
        if s >= 0.40: return "MEDIUM"
        return "LOW"

    out = pd.DataFrame({
        "member_id": df["member_id"],
        "name": df.get("name"),
        "branch": df.get("branch"),
        "country": df.get("country"),
        "top_product": df.get("top_product"),
        "txn_count": df.get("txn_count"),
        "avg_amt": df.get("avg_amt"),
        "hour_std": df.get("hour_std"),
        "cash_pct": df.get("cash_pct"),
        "pep_flag": pep,
        "alert_count": df.get("alert_count"),
        "score": score.clip(0, 1),
    })
    out["band"] = out["score"].apply(_band)
    return out.sort_values(["score","txn_count"], ascending=[False, False])

# Legacy no-arg wrapper (kept for backward compatibility)
def customer_risk_scores_legacy() -> pd.DataFrame:
    """
    Your original simpler scoring (inflow_total / txn_count / alerts / pep_flag).
    Only used if you explicitly want the legacy behavior.
    """
    mcols = _cols("members")
    if not mcols:
        return pd.DataFrame(columns=["member_id","name","branch","risk_score","risk_band"])

    id_col = "member_id" if "member_id" in mcols else ("id" if "id" in mcols else None)
    name_col = "name" if "name" in mcols else ("full_name" if "full_name" in mcols else None)
    branch_col = "branch" if "branch" in mcols else None

    base_cols = []
    if id_col: base_cols.append(id_col + " as member_id")
    if name_col: base_cols.append(name_col + " as name")
    if branch_col: base_cols.append(branch_col + " as branch")
    if "pep_flag" in mcols: base_cols.append("pep_flag")

    df = query(f"select {', '.join(base_cols)} from members") if base_cols else pd.DataFrame()
    if df is None or df.empty:
        return pd.DataFrame(columns=["member_id","name","branch","risk_score","risk_band"])

    # Txn intensity
    tcols = _cols("transactions")
    if tcols and "member_id" in tcols and "amount" in tcols:
        tx = query("""
            select member_id,
                   sum(case when amount>0 then amount else 0 end) as inflow_total,
                   count(*) as txn_count
            from transactions
            group by 1
        """)
        df = df.merge(tx, on="member_id", how="left")
    else:
        df["inflow_total"] = 0.0
        df["txn_count"] = 0

    # Alerts density
    try:
        ad = query("""
            select cast(json_extract(linked_entities, '$[0].member_id') as varchar) as member_id,
                   count(*) as alert_count
            from alerts
            group by 1
        """)
        df = df.merge(ad, on="member_id", how="left")
    except Exception:
        df["alert_count"] = 0

    # PEP flag
    if "pep_flag" in df.columns:
        df["pep_f"] = df["pep_flag"].astype(str).str.upper().isin(["1","Y","YES","TRUE"]).astype(int)
    else:
        df["pep_f"] = 0

    # Normalize
    for col in ["inflow_total","txn_count","alert_count"]:
        if col not in df.columns:
            df[col] = 0
        m = df[col].fillna(0)
        denom = (m.max() - m.min()) or 1.0
        df[col + "_n"] = (m - m.min()) / denom

    df["risk_score"] = 0.30*df["pep_f"] + 0.40*df["alert_count_n"] + 0.30*df["inflow_total_n"]
    df["risk_band"] = pd.cut(df["risk_score"], bins=[-0.01,0.4,0.7,1.0], labels=["LOW","MEDIUM","HIGH"])
    return df[["member_id","name","branch","risk_score","risk_band"]].sort_values("risk_score", ascending=False)

# ---------------------------- PRODUCT risk ----------------------------

def product_risk_scores(where_sql: str = "", params: Tuple = ()) -> pd.DataFrame:
    """
    Risk by product using txn behavior (amount, count, cash share, odd-hours share).
    Falls back to your original (avg_amount/txn_count) if needed.
    """
    tcols = _cols("transactions")
    if not tcols or "product" not in tcols:
        return pd.DataFrame(columns=["product","score","band","txn_count","avg_amt","cash_share","odd_share"])

    # Try richer view first
    try:
        channel_expr = "CAST(SUM(CASE WHEN channel='CASH' THEN 1 ELSE 0 END) AS DOUBLE)" if "channel" in tcols else "CAST(0 AS DOUBLE)"
        sql = f"""
          SELECT
            product,
            COUNT(*) AS txn_count,
            AVG(ABS(amount)) AS avg_amt,
            {channel_expr} / COUNT(*) AS cash_share,
            AVG(CASE WHEN (EXTRACT(HOUR FROM ts) IN (0,1,2,3,4,23)) THEN 1 ELSE 0 END) AS odd_share
          FROM transactions
          {_where(where_sql)}
          GROUP BY 1
          HAVING product IS NOT NULL
          ORDER BY txn_count DESC
        """
        df = query(sql, params)
        if df.empty:
            raise ValueError("empty")
        z_txn = _z_series(df["txn_count"].fillna(0.0)).abs()
        z_amt = _z_series(df["avg_amt"].fillna(0.0)).abs()
        cash = df["cash_share"].fillna(0.0).clip(0,1)
        odd = df["odd_share"].fillna(0.0).clip(0,1)
        raw = z_txn + z_amt + cash + odd
        score = (raw - raw.min()) / (raw.max() - raw.min() + 1e-9)
        df["score"] = score.clip(0,1)
        df["band"] = pd.cut(df["score"], bins=[-0.01,0.4,0.7,1.0], labels=["LOW","MEDIUM","HIGH"])
        return df.sort_values(["score","txn_count"], ascending=[False, False])
    except Exception:
        # Fallback (your original)
        df = query("""
            select product,
                   count(*) as txn_count,
                   avg(abs(amount)) as avg_amount
            from transactions
            group by 1
            having product is not null
        """)
        if df.empty:
            return pd.DataFrame(columns=["product","score","band","txn_count","avg_amount"])
        for col in ["txn_count","avg_amount"]:
            m = df[col].fillna(0)
            denom = (m.max() - m.min()) or 1.0
            df[col + "_n"] = (m - m.min()) / denom
        df["score"] = 0.6*df["avg_amount_n"] + 0.4*df["txn_count_n"]
        df["band"] = pd.cut(df["score"], bins=[-0.01,0.4,0.7,1.0], labels=["LOW","MEDIUM","HIGH"])
        df.rename(columns={"avg_amount":"avg_amt"}, inplace=True)
        df["cash_share"] = np.nan
        df["odd_share"] = np.nan
        return df[["product","score","band","txn_count","avg_amt","cash_share","odd_share"]].sort_values("score", ascending=False)

# ---------------------------- GEOGRAPHIC risk ----------------------------

def geographic_risk_scores(where_sql: str = "", params: Tuple = ()) -> pd.DataFrame:
    """
    Primary: members.country distribution blended with behavior aggregates.
    Fallback: transactions.geo or branch (your original approach).
    """
    # Members-based approach
    if _exists("members") and "country" in _cols("members"):
        dfm = query("SELECT country, COUNT(*) AS members FROM members GROUP BY 1")
        beh = behavior_features(where_sql, params)
        base = members_base()
        if not beh.empty and not base.empty:
            mix = beh.merge(base[["member_id","country"]], on="member_id", how="left")
            agg = mix.groupby("country", dropna=False).agg(
                txn_count=("member_id","count"),
                avg_amt=("avg_amt","mean"),
                cash_pct=("cash_pct","mean"),
            ).reset_index()
            out = dfm.merge(agg, on="country", how="left")
        else:
            out = dfm.copy()
            out["txn_count"] = np.nan
            out["avg_amt"] = np.nan
            out["cash_pct"] = np.nan

        def _geo_score(country: Optional[str]) -> float:
            if not isinstance(country, str) or not country.strip():
                return 0.6
            c = country.strip().upper()
            high = {"IR","KP","SY","AF","YE","SO"}
            med  = {"NG","CD","SS","ET"}
            if c in high: return 1.0
            if c in med:  return 0.6
            return 0.2

        out["geo_score"] = out["country"].apply(_geo_score)
        cash = (out["cash_pct"].fillna(0.0) / 100.0).clip(0,1)
        raw = out["geo_score"] + cash
        score = (raw - raw.min()) / (raw.max() - raw.min() + 1e-9)
        out["score"] = score
        out["band"] = pd.cut(out["score"], bins=[-0.01,0.4,0.7,1.0], labels=["LOW","MEDIUM","HIGH"])
        return out.sort_values(["score","members"], ascending=[False, False])

    # Fallback (your original, geo or branch from transactions)
    tcols = _cols("transactions")
    key = "geo" if "geo" in tcols else ("branch" if "branch" in tcols else None)
    if not key:
        return pd.DataFrame(columns=["geo","score","band","txn_count","total_amount"])

    df = query(f"""
        select {key} as geo,
               count(*) as txn_count,
               sum(abs(amount)) as total_amount
        from transactions
        {_where(where_sql)}
        group by 1
        having geo is not null
    """, params)
    if df.empty:
        return pd.DataFrame(columns=["geo","score","band","txn_count","total_amount"])

    for col in ["txn_count","total_amount"]:
        m = df[col].fillna(0)
        denom = (m.max() - m.min()) or 1.0
        df[col + "_n"] = (m - m.min()) / denom
    df["score"] = 0.7*df["total_amount_n"] + 0.3*df["txn_count_n"]
    df["band"] = pd.cut(df["score"], bins=[-0.01,0.4,0.7,1.0], labels=["LOW","MEDIUM","HIGH"])
    return df[["geo","score","band","txn_count","total_amount"]].sort_values("score", ascending=False)

# ---------------------------- OVERALL heatmap ----------------------------

def overall_risk_heatmap(where_sql: str = "", params: Tuple = ()) -> pd.DataFrame:
    """
    Preferred: Branch × Product with avg customer score.
    Fallback: legacy member × product pivot (counts).
    """
    cust = customer_risk_scores(where_sql, params)
    if not cust.empty and {"branch","top_product","score"}.issubset(cust.columns):
        df = cust.copy()
        df["top_product"] = df["top_product"].fillna("Unknown")
        grp = df.groupby(["branch","top_product"]).agg(
            avg_score=("score","mean"),
            members=("member_id","count")
        ).reset_index()
        return grp.sort_values(["avg_score","members"], ascending=[False, False])

    # Legacy fallback: your old pivot
    tcols = _cols("transactions")
    if not tcols or "product" not in tcols:
        return pd.DataFrame()

    key_id = "member_id" if "member_id" in tcols else None
    if not key_id:
        return pd.DataFrame()

    df = query(f"""
        select {key_id} as member_id, product, count(*) as txn_count
        from transactions
        {_where(where_sql)}
        group by 1,2
        having product is not null
    """, params)
    if df.empty:
        return pd.DataFrame()
    pivot = df.pivot_table(index="branch" if "branch" in df.columns else "member_id",
                           columns="product", values="txn_count", fill_value=0)
    return pivot.reset_index()

# ---- explicit legacy alias (if a page still expects the old shape) ----
def overall_heatmap_matrix() -> pd.DataFrame:
    """
    EXACT legacy behavior: member_id × product pivot of txn counts (head 200).
    """
    tcols = _cols("transactions")
    if not tcols or "product" not in tcols:
        return pd.DataFrame()
    key_id = "member_id" if "member_id" in tcols else None
    if not key_id:
        return pd.DataFrame()

    df = query(f"""
        select {key_id} as member_id, product, count(*) as txn_count
        from transactions
        group by 1,2
        having product is not null
    """)
    if df.empty:
        return pd.DataFrame()
    pivot = df.pivot_table(index="member_id", columns="product", values="txn_count", fill_value=0)
    return pivot.head(200)
