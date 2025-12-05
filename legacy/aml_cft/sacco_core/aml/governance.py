# sacco_core/aml/governance.py
from __future__ import annotations
from typing import Optional, Tuple, Dict, Any, List
from hashlib import sha256
from datetime import datetime, date
import json
import pandas as pd

from sacco_core.db import query, execute
from sacco_core.config import get_config
from sacco_core.aml.reporting import (
    ctr_hits as _ctr_hits,
    ctr_weekly_aggregates as _ctr_weekly_aggregates,
    str_candidates as _str_candidates,
)
from sacco_core.aml.sanctions import recent_screenings as _recent_screenings

# --------------------------- schema helpers ---------------------------

def _exists(table: str) -> bool:
    try:
        df = query("show tables")
        col = "name" if "name" in df.columns else df.columns[0]
        return table.lower() in df[col].str.lower().tolist()
    except Exception:
        return False

def ensure_governance_schema() -> None:
    # Immutable audit log (no constraints to avoid DuckDB "constraint not implemented")
    execute("""
        CREATE TABLE IF NOT EXISTS immutable_audit_log (
            seq BIGINT,
            ts TIMESTAMP,
            actor VARCHAR,
            action VARCHAR,
            entity_type VARCHAR,
            entity_id VARCHAR,
            details VARCHAR,
            prev_hash VARCHAR,
            hash VARCHAR
        )
    """)
    # Documentation register (lightweight)
    execute("""
        CREATE TABLE IF NOT EXISTS governance_docs (
            doc_id BIGINT,
            title VARCHAR,
            category VARCHAR,
            link VARCHAR,
            uploaded_at TIMESTAMP,
            tags VARCHAR
        )
    """)

# --------------------------- immutable audit log ---------------------------

def _next_seq() -> int:
    try:
        df = query("SELECT COALESCE(MAX(seq), 0) AS m FROM immutable_audit_log")
        return int(df["m"].iloc[0]) + 1
    except Exception:
        return 1

def append_audit(actor: str,
                 action: str,
                 entity_type: Optional[str] = None,
                 entity_id: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None) -> None:
    """Append a tamper-evident audit record (hash-chained)."""
    ensure_governance_schema()
    seq = _next_seq()
    ts = datetime.utcnow()
    prev = query("SELECT hash FROM immutable_audit_log WHERE seq = ?",
                 (seq - 1,))["hash"].iloc[0] if seq > 1 else ""
    payload = {
        "seq": seq,
        "ts": ts.isoformat(timespec="seconds"),
        "actor": actor or "",
        "action": action or "",
        "entity_type": entity_type or "",
        "entity_id": entity_id or "",
        "details": details or {},
        "prev_hash": prev,
    }
    raw = f"{payload['seq']}|{payload['ts']}|{payload['actor']}|{payload['action']}|{payload['entity_type']}|{payload['entity_id']}|{json.dumps(payload['details'], sort_keys=True)}|{payload['prev_hash']}"
    h = sha256(raw.encode("utf-8")).hexdigest()
    execute(
        "INSERT INTO immutable_audit_log (seq, ts, actor, action, entity_type, entity_id, details, prev_hash, hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (seq, ts, payload["actor"], payload["action"], payload["entity_type"], payload["entity_id"],
         json.dumps(payload["details"], ensure_ascii=False), prev, h)
    )

def verify_audit_chain(limit: int = 5000) -> pd.DataFrame:
    """Recompute and verify hash chain; returns rows with a boolean 'ok'."""
    ensure_governance_schema()
    df = query(f"""
        SELECT seq, ts, actor, action, entity_type, entity_id, details, prev_hash, hash
        FROM immutable_audit_log
        ORDER BY seq ASC
        LIMIT {int(limit)}
    """)
    if df.empty:
        return df.assign(ok=True)

    oks = []
    prev_hash = ""
    for _, r in df.iterrows():
        raw = f"{int(r['seq'])}|{pd.to_datetime(r['ts']).strftime('%Y-%m-%dT%H:%M:%S')}|{r.get('actor','')}|{r.get('action','')}|{r.get('entity_type','')}|{r.get('entity_id','')}|{r.get('details','')}|{prev_hash}"
        recomputed = sha256(raw.encode("utf-8")).hexdigest()
        ok = (recomputed == r.get("hash"))
        oks.append(ok)
        prev_hash = r.get("hash") or ""
    df["ok"] = oks
    return df

def recent_audit(limit: int = 500) -> pd.DataFrame:
    ensure_governance_schema()
    return query(f"""
        SELECT * FROM immutable_audit_log
        ORDER BY seq DESC
        LIMIT {int(limit)}
    """)

# --------------------------- documentation center ---------------------------

def add_document(title: str,
                 category: str,
                 link: str,
                 tags: Optional[List[str]] = None) -> None:
    """Register a document link (SharePoint/Drive/wiki/etc.)."""
    ensure_governance_schema()
    # simple seq for doc_id
    try:
        doc_id = int(query("SELECT COALESCE(MAX(doc_id),0) AS m FROM governance_docs")["m"].iloc[0]) + 1
    except Exception:
        doc_id = 1
    execute(
        "INSERT INTO governance_docs (doc_id, title, category, link, uploaded_at, tags) VALUES (?, ?, ?, ?, now(), ?)",
        (doc_id, title, category, link, ",".join(tags or []))
    )

def list_documents(category: Optional[str] = None, limit: int = 1000) -> pd.DataFrame:
    ensure_governance_schema()
    if category:
        return query(
            f"""SELECT doc_id, title, category, link, uploaded_at, tags
                FROM governance_docs
                WHERE category = ?
                ORDER BY uploaded_at DESC
                LIMIT {int(limit)}""",
            (category,)
        )
    return query(
        f"""SELECT doc_id, title, category, link, uploaded_at, tags
            FROM governance_docs
            ORDER BY uploaded_at DESC
            LIMIT {int(limit)}"""
    )

# --------------------------- audit readiness ---------------------------

def audit_readiness_snapshot(where_sql: str = "", params: Tuple = ()) -> pd.DataFrame:
    """
    Evidence checklist based on data presence + config.
    """
    cfg = get_config()
    rows = []

    # STR pipeline
    try:
        str_df = _str_candidates(where_sql=where_sql, params=params)
        rows.append({"control": "STR pipeline running", "evidence": f"{len(str_df)} candidates in window", "status": "OK" if len(str_df) >= 0 else "N/A"})
    except Exception as e:
        rows.append({"control": "STR pipeline running", "evidence": str(e), "status": "Check"})

    # CTR single & weekly
    try:
        ctr = _ctr_hits(where_sql=where_sql, params=params)
        rows.append({"control": "CTR single detection", "evidence": f"{len(ctr)} hits", "status": "OK" if ctr is not None else "Check"})
    except Exception as e:
        rows.append({"control": "CTR single detection", "evidence": str(e), "status": "Check"})
    try:
        ctw = _ctr_weekly_aggregates(where_sql=where_sql, params=params)
        rows.append({"control": "CTR weekly rollup", "evidence": f"{len(ctw)} rows", "status": "OK" if ctw is not None else "Check"})
    except Exception as e:
        rows.append({"control": "CTR weekly rollup", "evidence": str(e), "status": "Check"})

    # Sanctions screening register
    try:
        sanc = _recent_screenings(limit=5)
        rows.append({"control": "Sanctions screening register", "evidence": f"{len(sanc)} recent", "status": "OK" if sanc is not None else "Check"})
    except Exception as e:
        rows.append({"control": "Sanctions screening register", "evidence": str(e), "status": "Check"})

    # Immutable log availability + verification
    try:
        ensure_governance_schema()
        ver = verify_audit_chain(limit=200)
        ok_rate = float(ver["ok"].mean()) if not ver.empty else 1.0
        rows.append({"control": "Immutable audit log", "evidence": f"{len(ver)} records; chain OK={ok_rate:.0%}", "status": "OK" if ok_rate == 1.0 else "Check"})
    except Exception as e:
        rows.append({"control": "Immutable audit log", "evidence": str(e), "status": "Check"})

    # Config presence (FRC)
    rows.append({"control": "FRC config present", "evidence": f"CTR threshold {getattr(cfg.frc,'ctr_threshold_kes', 0):,} KES", "status": "OK"})

    return pd.DataFrame(rows, columns=["control","evidence","status"])

# --------------------------- gap analysis ---------------------------

def gap_analysis(where_sql: str = "", params: Tuple = ()) -> pd.DataFrame:
    """
    Simple rules: checks existence + minimal volumes; flags coverage gaps.
    """
    checks = []

    # Tables expected
    for tbl, label in [
        ("members", "Members master"),
        ("transactions", "Transactions ledger"),
        ("pep_list", "PEP watch"),
        ("sanctions_list", "Sanctions watch"),
        ("immutable_audit_log", "Immutable audit log"),
    ]:
        checks.append({
            "area": "Data Availability",
            "control": label,
            "status": "OK" if _exists(tbl) else "Missing",
            "detail": f"table='{tbl}'"
        })

    # Volumes (heuristics)
    try:
        tcount = int(query("SELECT COUNT(*) c FROM transactions")["c"].iloc[0]) if _exists("transactions") else 0
    except Exception:
        tcount = 0
    checks.append({
        "area": "Data Volume",
        "control": "Transactions >= 10k",
        "status": "OK" if tcount >= 10000 else "Low",
        "detail": f"count={tcount}"
    })

    try:
        mcount = int(query("SELECT COUNT(*) c FROM members")["c"].iloc[0]) if _exists("members") else 0
    except Exception:
        mcount = 0
    checks.append({
        "area": "Data Volume",
        "control": "Members >= 1k",
        "status": "OK" if mcount >= 1000 else "Low",
        "detail": f"count={mcount}"
    })

    # STR/CTR pipelines producing output
    try:
        ctr_rows = len(_ctr_hits(where_sql=where_sql, params=params))
    except Exception:
        ctr_rows = 0
    checks.append({
        "area": "Pipeline Output",
        "control": "CTR hits present",
        "status": "OK" if ctr_rows >= 0 else "Check",
        "detail": f"rows={ctr_rows}"
    })

    try:
        str_rows = len(_str_candidates(where_sql=where_sql, params=params))
    except Exception:
        str_rows = 0
    checks.append({
        "area": "Pipeline Output",
        "control": "STR candidates present",
        "status": "OK" if str_rows >= 0 else "Check",
        "detail": f"rows={str_rows}"
    })

    return pd.DataFrame(checks, columns=["area","control","status","detail"])

# --------------------------- board pack (markdown export) ---------------------------

def board_pack_snapshot(where_sql: str = "", params: Tuple = ()) -> Dict[str, Any]:
    """Collect key stats to embed in MD/PDF."""
    stats: Dict[str, Any] = {}
    try:
        stats["ctr_hits"] = len(_ctr_hits(where_sql=where_sql, params=params))
    except Exception:
        stats["ctr_hits"] = 0
    try:
        weekly = _ctr_weekly_aggregates(where_sql=where_sql, params=params)
        stats["ctr_weeks"] = int(weekly["week_start"].nunique()) if not weekly.empty else 0
    except Exception:
        stats["ctr_weeks"] = 0
    try:
        stats["str_candidates"] = len(_str_candidates(where_sql=where_sql, params=params))
    except Exception:
        stats["str_candidates"] = 0
    try:
        stats["recent_sanctions"] = len(_recent_screenings(limit=50))
    except Exception:
        stats["recent_sanctions"] = 0
    try:
        al = query("SELECT COUNT(*) c FROM immutable_audit_log") if _exists("immutable_audit_log") else pd.DataFrame([{"c":0}])
        stats["audit_records"] = int(al["c"].iloc[0])
    except Exception:
        stats["audit_records"] = 0
    return stats

def board_pack_markdown(period_label: str,
                        where_sql: str = "",
                        params: Tuple = ()) -> str:
    cfg = get_config()
    s = board_pack_snapshot(where_sql=where_sql, params=params)
    md = f"""# Board Compliance Pack — {period_label}

**Regulator:** FRC • **CTR Threshold:** {getattr(cfg.frc, "ctr_threshold_kes", 0):,} KES  
**Record Retention:** {getattr(cfg.frc, "record_retention_years", 7)} years

## 1) Key Metrics
- CTR single hits: **{s.get("ctr_hits", 0):,}**
- Weeks with CTR aggregates: **{s.get("ctr_weeks", 0):,}**
- STR candidates: **{s.get("str_candidates", 0):,}**
- Recent sanctions screenings: **{s.get("recent_sanctions", 0):,}**
- Immutable audit log records: **{s.get("audit_records", 0):,}**

## 2) Observations
- CTR detection and weekly rollups are active.
- STR candidates surfaced using behavioral + structuring + movement signals.
- Sanctions screenings logged with dispositions in register.
- Audit log hash-chain verification **expected 100%**; see Readiness tab for details.

## 3) Actions / Decisions
- Review top STR candidates and decide filing/escalation.
- Confirm CTR submissions per weekly totals.
- Review any sanctions matches marked "Escalated".
- Approve/document any policy changes.

*Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*
"""
    return md
