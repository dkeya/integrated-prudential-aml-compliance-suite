# sacco_core/aml/kyc.py
from __future__ import annotations
from typing import Dict, List
import pandas as pd

from sacco_core.db import query

# Helper: get table columns (lowercased)
def _cols(table: str) -> List[str]:
    try:
        df = query(f"PRAGMA table_info({table})")
        if isinstance(df, pd.DataFrame) and "name" in df.columns:
            return df["name"].astype(str).str.lower().tolist()
    except Exception:
        pass
    return []

def _tables_exist() -> List[str]:
    # Try information_schema first; fallback to SHOW TABLES for DuckDB
    try:
        df = query("select table_name from information_schema.tables")
        if isinstance(df, pd.DataFrame) and "table_name" in df.columns:
            return df["table_name"].astype(str).str.lower().tolist()
    except Exception:
        try:
            df = query("show tables")
            if isinstance(df, pd.DataFrame):
                col = "name" if "name" in df.columns else df.columns[0]
                return df[col].astype(str).str.lower().tolist()
        except Exception:
            pass
    return []

# --- Normalized PEP predicate (prevents mixed-type IN errors) ---
# Treat 1/true/y/yes as PEP-true
_PEP_TRUE_SET = ("'1'","'Y'","'YES'","'TRUE'","'T'")
def is_pep_expr(col: str = "pep_flag") -> str:
    # If column is numeric/bool/text, we cast to VARCHAR then compare upper()
    return f"UPPER(CAST({col} AS VARCHAR)) IN ({', '.join(_PEP_TRUE_SET)})"

def kyc_overview() -> Dict[str, int]:
    """
    Summary counters for the KYC top strip: total, missing KYC, PEP, high risk.
    Adapts to members schema.
    """
    try:
        total = int(query("select count(*) c from members")["c"].iloc[0])
    except Exception:
        total = 0

    mcols = _cols("members")
    # Choose candidate KYC fields that exist
    candidates = ["national_id","id_no","id_number","dob","date_of_birth","address","occupation","phone","email"]
    fields = [c for c in candidates if c in mcols]

    missing = 0
    if fields:
        cond = " OR ".join(f"{f} IS NULL OR CAST({f} AS VARCHAR)=''" for f in fields)
        try:
            missing = int(query(f"select count(*) c from members where {cond}")["c"].iloc[0])
        except Exception:
            missing = 0

    # PEP counting: prefer pep_flag, else join pep_list on name if available
    pep = 0
    if "pep_flag" in mcols:
        try:
            pep = int(query(f"select count(*) c from members where {is_pep_expr('pep_flag')}")["c"].iloc[0])
        except Exception:
            pep = 0
    else:
        name_col = "name" if "name" in mcols else ("full_name" if "full_name" in mcols else None)
        if name_col and "pep_list" in _tables_exist():
            try:
                pep = int(query(f"""
                    select count(*) c
                    from members m
                    join pep_list p on lower(CAST(m.{name_col} AS VARCHAR)) = lower(CAST(p.name AS VARCHAR))
                """)["c"].iloc[0])
            except Exception:
                pep = 0

    high = 0
    if "risk_band" in mcols:
        try:
            high = int(query("select count(*) c from members where upper(CAST(risk_band AS VARCHAR))='HIGH'")["c"].iloc[0])
        except Exception:
            high = 0

    return {"total": total, "missing": missing, "pep": pep, "high": high}

def kyc_completeness_table() -> pd.DataFrame:
    """
    Row-level completeness (%) built from available KYC fields.
    Returns columns: member_id, name, branch, completeness_pct, missing_fields
    """
    mcols = _cols("members")
    if not mcols:
        return pd.DataFrame(columns=["member_id","name","branch","completeness_pct","missing_fields"])

    id_col = "member_id" if "member_id" in mcols else ("id" if "id" in mcols else None)
    name_col = "name" if "name" in mcols else ("full_name" if "full_name" in mcols else None)
    branch_col = "branch" if "branch" in mcols else None

    kyc_fields = [c for c in ["national_id","id_no","id_number","dob","date_of_birth","address","occupation","phone","email"] if c in mcols]

    sel = []
    if id_col: sel.append(id_col)
    if name_col: sel.append(f"{name_col} as name")
    if branch_col: sel.append(branch_col)
    sel += kyc_fields

    if not sel:
        return pd.DataFrame(columns=["member_id","name","branch","completeness_pct","missing_fields"])

    df = query(f"select {', '.join(sel)} from members")
    if df is None or df.empty:
        return pd.DataFrame(columns=["member_id","name","branch","completeness_pct","missing_fields"])

    kcols = [c for c in kyc_fields if c in df.columns]

    def _missing(row):
        miss = [c for c in kcols if pd.isna(row.get(c)) or str(row.get(c)).strip()==""]
        return miss

    def _score(row):
        n = len(kcols)
        if n == 0: return 0.0
        filled = sum(0 if (pd.isna(row.get(c)) or str(row.get(c)).strip()=="") else 1 for c in kcols)
        return round((filled / n) * 100.0, 1)

    df["missing_fields"] = df.apply(_missing, axis=1).apply(lambda xs: ", ".join(xs) if xs else "")
    df["completeness_pct"] = df.apply(_score, axis=1)

    out = pd.DataFrame({
        "member_id": df[id_col] if id_col else pd.NA,
        "name": df["name"] if "name" in df.columns else pd.NA,
        "branch": df[branch_col] if branch_col else pd.NA,
        "completeness_pct": df["completeness_pct"],
        "missing_fields": df["missing_fields"],
    })
    return out.sort_values("completeness_pct", ascending=True, kind="mergesort")

def edd_candidates() -> pd.DataFrame:
    """
    Returns members requiring EDD (high risk / PEP / large recent cash).
    Adapts to schema; joins transactions if available.
    """
    mcols = _cols("members")
    tcols = _cols("transactions")

    id_col = "member_id" if "member_id" in mcols else ("id" if "id" in mcols else None)
    name_col = "name" if "name" in mcols else ("full_name" if "full_name" in mcols else None)

    # Base candidate set: HIGH risk or PEP flag if available
    base_cond = []
    if "risk_band" in mcols:
        base_cond.append("upper(CAST(risk_band AS VARCHAR))='HIGH'")
    if "pep_flag" in mcols:
        base_cond.append(is_pep_expr("pep_flag"))
    base = " OR ".join(base_cond) if base_cond else "1=1"

    sel = []
    if id_col: sel.append(f"{id_col} as member_id")
    if name_col: sel.append(f"{name_col} as name")
    if "branch" in mcols: sel.append("branch")
    if "risk_band" in mcols: sel.append("risk_band")
    if "pep_flag" in mcols: sel.append("pep_flag")

    if not sel:
        sel = ["*"]

    df = query(f"select {', '.join(sel)} from members where {base}")
    if df is None or df.empty:
        df = pd.DataFrame(columns=["member_id","name","branch","risk_band","pep_flag","large_recent_cash"])

    # Large recent cash from transactions (optional)
    if tcols and ("amount" in tcols) and ("ts" in tcols):
        channel_filter = "and channel='CASH'" if "channel" in tcols else ""
        tx_join = "member_id" if ("member_id" in tcols and "member_id" in df.columns) else None
        if tx_join:
            cash = query(f"""
                with recent as (
                  select {tx_join} as member_id,
                         sum(case when amount>0 then amount else 0 end) as inflow_7d
                  from transactions
                  where ts >= (now() - interval '7 day') {channel_filter}
                  group by 1
                )
                select * from recent
            """)
            if cash is not None and not cash.empty and "member_id" in df.columns:
                df = df.merge(cash, on="member_id", how="left")
                df["large_recent_cash"] = (df["inflow_7d"].fillna(0) >= 1_000_000).astype(int)
            else:
                df["large_recent_cash"] = 0
        else:
            df["large_recent_cash"] = 0
    else:
        df["large_recent_cash"] = 0

    # Order by priority
    if "risk_band" in df.columns:
        df["risk_rank"] = df["risk_band"].astype(str).str.upper().map({"HIGH":3,"MEDIUM":2,"LOW":1}).fillna(0)
        df = df.sort_values(["risk_rank","large_recent_cash"], ascending=[False, False]).drop(columns=["risk_rank"])
    else:
        df = df.sort_values("large_recent_cash", ascending=False)

    return df

def docs_register() -> pd.DataFrame:
    """
    Simple documentation/attestation register.
    If a real documents table exists, show it; else synthesize from members.
    """
    tables = _tables_exist()
    if "documents" in tables:
        try:
            df = query("""select * from documents order by uploaded_at desc limit 500""")
            if df is not None:
                return df
        except Exception:
            pass

    # Fallback: synthesize "required docs" against members
    mcols = _cols("members")
    id_col = "member_id" if "member_id" in mcols else ("id" if "id" in mcols else None)
    name_col = "name" if "name" in mcols else ("full_name" if "full_name" in mcols else None)

    if not id_col or not name_col:
        return pd.DataFrame(columns=["member_id","name","document_type","status","uploaded_at","evidence_link"])

    dfm = query(f"select {id_col} as member_id, {name_col} as name from members")
    if dfm is None or dfm.empty:
        return pd.DataFrame(columns=["member_id","name","document_type","status","uploaded_at","evidence_link"])

    req = ["ID Copy", "Passport Photo", "Proof of Address", "KRA PIN"]
    rows = []
    for _, r in dfm.iterrows():
        for d in req:
            rows.append({
                "member_id": r["member_id"],
                "name": r["name"],
                "document_type": d,
                "status": "Pending",
                "uploaded_at": None,
                "evidence_link": None
            })
    return pd.DataFrame(rows)
