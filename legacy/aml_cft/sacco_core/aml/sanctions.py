# sacco_core/aml/sanctions.py
from __future__ import annotations
from typing import Tuple, Dict, Any, Optional, List
import pandas as pd
import numpy as np
from difflib import SequenceMatcher
from datetime import datetime

from sacco_core.db import query, execute
from sacco_core.config import get_config

# Optional audit logger (guarded import)
try:
    from sacco_core.audit import log_action
except Exception:  # pragma: no cover
    def log_action(event: str, user: str, payload: Dict[str, Any]):  # type: ignore
        pass

# ----------------------- helpers -----------------------

def _exists(table: str) -> bool:
    try:
        df = query("show tables")
        col = "name" if "name" in df.columns else df.columns[0]
        return table.lower() in df[col].str.lower().tolist()
    except Exception:
        return False

def _cols(table: str) -> List[str]:
    try:
        return query(f"PRAGMA table_info({table})")["name"].str.lower().tolist()
    except Exception:
        return []

def _norm(s: Optional[str]) -> str:
    if s is None:
        return ""
    return " ".join(str(s).strip().lower().split())

def _sim(a: str, b: str) -> float:
    return SequenceMatcher(None, _norm(a), _norm(b)).ratio()

def _next_id(table: str, col: str) -> int:
    try:
        df = query(f"SELECT COALESCE(MAX({col}), 0) + 1 AS nid FROM {table}")
        return int(df["nid"].iloc[0])
    except Exception:
        return 1

# ----------------------- core tables (idempotent) -----------------------

# register: lightweight manual IDs (no identity/constraints)
def _ensure_register():
    if not _exists("sanctions_screenings"):
        execute("""
            CREATE TABLE IF NOT EXISTS sanctions_screenings(
              screening_id BIGINT,
              entity_type VARCHAR,      -- 'member' | 'counterparty' | 'manual'
              entity_id VARCHAR,        -- member_id or free text key
              entity_name VARCHAR,
              watch_name VARCHAR,
              similarity DOUBLE,
              list VARCHAR,
              program VARCHAR,
              country VARCHAR,
              status VARCHAR,           -- 'Open' | 'Cleared' | 'Escalated'
              notes VARCHAR,
              created_at TIMESTAMP DEFAULT now()
            )
        """)

def _ensure_watchlist():
    if not _exists("sanctions_list"):
        execute("""
            CREATE TABLE IF NOT EXISTS sanctions_list(
              name VARCHAR,
              list VARCHAR,
              program VARCHAR,
              country VARCHAR,
              source VARCHAR,
              loaded_at TIMESTAMP DEFAULT now()
            )
        """)
    if not _exists("watchlist_meta"):
        execute("""
            CREATE TABLE IF NOT EXISTS watchlist_meta(
              list VARCHAR,
              program VARCHAR,
              country VARCHAR,
              source VARCHAR,
              loaded_at TIMESTAMP DEFAULT now(),
              note VARCHAR
            )
        """)

def ensure_batch_schema():
    """Batch jobs + snapshot hits (no constraints/identity)."""
    execute("""
        CREATE TABLE IF NOT EXISTS sanctions_jobs (
          job_id BIGINT,
          source VARCHAR,            -- 'members' | 'counterparties'
          threshold DOUBLE,
          status VARCHAR,            -- 'Queued' | 'Running' | 'Done' | 'Error'
          started_at TIMESTAMP,
          finished_at TIMESTAMP,
          note VARCHAR
        )
    """)
    execute("""
        CREATE TABLE IF NOT EXISTS sanctions_hits (
          hit_id BIGINT,
          job_id BIGINT,
          entity_type VARCHAR,       -- 'member' | 'counterparty'
          entity_id VARCHAR,
          entity_name VARCHAR,
          watch_name VARCHAR,
          similarity DOUBLE,
          list VARCHAR,
          program VARCHAR,
          country VARCHAR,
          ts_last TIMESTAMP,
          created_at TIMESTAMP DEFAULT now(),
          triage_status VARCHAR,     -- 'Open' | 'Cleared' | 'Escalated'
          triage_notes VARCHAR,
          case_id BIGINT
        )
    """)

# ----------------------- exact matches -----------------------

def sanctions_exact_hits(limit: int = 1000) -> pd.DataFrame:
    """
    Exact-join members.name -> sanctions_list.name (case-insensitive).
    Columns (if available): member_id, name, branch, watch_name, list, program, country
    """
    _ensure_watchlist()
    if not (_exists("members") and _exists("sanctions_list")):
        return pd.DataFrame(columns=["member_id","name","branch","watch_name","list","program","country"])

    mcols = _cols("members")
    id_col = "member_id" if "member_id" in mcols else ("id" if "id" in mcols else None)
    name_col = "name" if "name" in mcols else ("full_name" if "full_name" in mcols else None)
    branch_col = "branch" if "branch" in mcols else None
    if not id_col or not name_col:
        return pd.DataFrame(columns=["member_id","name","branch","watch_name","list","program","country"])

    sel = [f"m.{id_col} as member_id", f"m.{name_col} as name"]
    if branch_col: sel.append(f"m.{branch_col} as branch")
    sel += ["s.name as watch_name", "s.list", "s.program", "s.country"]

    sql = f"""
        SELECT {', '.join(sel)}
        FROM members m
        JOIN sanctions_list s
          ON lower(m.{name_col}) = lower(s.name)
        LIMIT {int(limit)}
    """
    return query(sql)

# ----------------------- fuzzy (name) screening -----------------------

def sanctions_fuzzy_hits(threshold: float = 0.88,
                         limit_watch: int = 5000,
                         source: str = "members") -> pd.DataFrame:
    """
    Fuzzy-match entity names against sanctions_list.
      - source='members' -> screen members table
      - source='counterparties' -> DISTINCT counterparties from transactions
    Returns: entity_id, entity_name, watch_name, list, program, country, similarity
    """
    _ensure_watchlist()
    if not _exists("sanctions_list"):
        return pd.DataFrame(columns=["entity_id","entity_name","watch_name","list","program","country","similarity"])

    # Build candidate entity set
    entities = pd.DataFrame(columns=["entity_id","entity_name"])
    if source == "members" and _exists("members"):
        mcols = _cols("members")
        id_col = "member_id" if "member_id" in mcols else ("id" if "id" in mcols else None)
        name_col = "name" if "name" in mcols else ("full_name" if "full_name" in mcols else None)
        if id_col and name_col:
            entities = query(f"SELECT {id_col} as entity_id, {name_col} as entity_name FROM members")
    elif source == "counterparties" and _exists("transactions"):
        tcols = _cols("transactions")
        if "counterparty" in tcols:
            entities = query("""
                SELECT DISTINCT counterparty as entity_name
                FROM transactions WHERE counterparty IS NOT NULL
            """)
            entities["entity_id"] = entities["entity_name"]

    if entities.empty:
        return pd.DataFrame(columns=["entity_id","entity_name","watch_name","list","program","country","similarity"])

    watch = query(f"SELECT name, list, program, country FROM sanctions_list LIMIT {int(limit_watch)}")
    if watch.empty:
        return pd.DataFrame(columns=["entity_id","entity_name","watch_name","list","program","country","similarity"])

    rows = []
    for _, e in entities.iterrows():
        ename = e.get("entity_name")
        if not isinstance(ename, str) or not ename.strip():
            continue
        best = None
        best_row = None
        for _, w in watch.iterrows():
            score = _sim(ename, w["name"])
            if score >= threshold and (best is None or score > best):
                best = score
                best_row = w
        if best is not None and best_row is not None:
            rows.append({
                "entity_id": str(e.get("entity_id", "")),
                "entity_name": ename,
                "watch_name": best_row["name"],
                "list": best_row.get("list"),
                "program": best_row.get("program"),
                "country": best_row.get("country"),
                "similarity": float(best),
            })

    out = pd.DataFrame(rows)
    return out.sort_values("similarity", ascending=False)

# ----------------------- transactions (counterparties) screening -----------

def sanctions_txn_hits(threshold: float = 0.9) -> pd.DataFrame:
    """
    Screen counterparties from recent transactions against sanctions_list using fuzzy matching.
    Emits: member_id (if present), counterparty, watch_name, similarity, list, program, country, ts_last
    """
    _ensure_watchlist()
    if not (_exists("transactions") and _exists("sanctions_list")):
        return pd.DataFrame(columns=["member_id","counterparty","watch_name","similarity","list","program","country","ts_last"])

    tcols = _cols("transactions")
    if "counterparty" not in tcols:
        return pd.DataFrame(columns=["member_id","counterparty","watch_name","similarity","list","program","country","ts_last"])

    base = query("""
        SELECT
          {mid} as member_id,
          counterparty,
          max(ts) as ts_last
        FROM transactions
        WHERE counterparty IS NOT NULL
        GROUP BY 1,2
        ORDER BY ts_last DESC
        LIMIT 10000
    """.format(mid=("member_id" if "member_id" in tcols else "NULL")))

    if base.empty:
        return pd.DataFrame(columns=["member_id","counterparty","watch_name","similarity","list","program","country","ts_last"])

    watch = query("SELECT name, list, program, country FROM sanctions_list")
    if watch.empty:
        return pd.DataFrame(columns=["member_id","counterparty","watch_name","similarity","list","program","country","ts_last"])

    rows = []
    for _, r in base.iterrows():
        cp = r["counterparty"]
        if not isinstance(cp, str) or not cp.strip():
            continue
        best = None
        best_row = None
        for _, w in watch.iterrows():
            score = _sim(cp, w["name"])
            if score >= threshold and (best is None or score > best):
                best = score
                best_row = w
        if best is not None and best_row is not None:
            rows.append({
                "member_id": r.get("member_id"),
                "counterparty": cp,
                "watch_name": best_row["name"],
                "similarity": float(best),
                "list": best_row.get("list"),
                "program": best_row.get("program"),
                "country": best_row.get("country"),
                "ts_last": r.get("ts_last"),
            })

    return pd.DataFrame(rows).sort_values(["similarity","ts_last"], ascending=[False, False])

# ----------------------- register (save disposition) -----------------------

def save_disposition(entity_type: str,
                     entity_id: str,
                     entity_name: str,
                     watch_name: str,
                     similarity: float,
                     list_name: Optional[str],
                     program: Optional[str],
                     country: Optional[str],
                     status: str,
                     notes: Optional[str] = None) -> None:
    """
    Persist a screening decision into sanctions_screenings.
    """
    _ensure_register()
    execute("""
        INSERT INTO sanctions_screenings
        (entity_type, entity_id, entity_name, watch_name, similarity, list, program, country, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (entity_type, entity_id, entity_name, watch_name, float(similarity),
          list_name, program, country, status, notes or None))

def recent_screenings(limit: int = 200) -> pd.DataFrame:
    _ensure_register()
    return query(f"""
        SELECT * FROM sanctions_screenings
        ORDER BY created_at DESC
        LIMIT {int(limit)}
    """)

# ----------------------- watchlist refresh -----------------------

def refresh_watchlist_from_csv(file, list_name: str = "Custom", program: str = "", country: str = "", source: str = "upload") -> int:
    """
    Load/merge a CSV (Streamlit UploadedFile or file path) into sanctions_list.
    Requires a 'name' column; optional list/program/country will be filled if provided.
    Returns number of rows inserted.
    """
    _ensure_watchlist()
    if file is None:
        return 0
    try:
        if hasattr(file, "read"):
            df = pd.read_csv(file)
        else:
            df = pd.read_csv(str(file))
    except Exception:
        return 0
    if "name" not in df.columns:
        return 0

    # Normalize minimal fields
    df = df.copy()
    if "list" not in df.columns: df["list"] = list_name
    if "program" not in df.columns: df["program"] = program
    if "country" not in df.columns: df["country"] = country
    df["source"] = source

    # Optionally clear previous entries for this (list,program,country) trio
    try:
        execute("DELETE FROM sanctions_list WHERE COALESCE(list,'')=? AND COALESCE(program,'')=? AND COALESCE(country,'')=?",
                (list_name, program, country))
    except Exception:
        pass

    # Insert rows
    n = 0
    for _, r in df.iterrows():
        execute("""
            INSERT INTO sanctions_list(name, list, program, country, source)
            VALUES (?, ?, ?, ?, ?)
        """, (str(r.get("name")), str(r.get("list")), str(r.get("program")),
              str(r.get("country")), str(r.get("source"))))
        n += 1

    # Track in meta + audit
    execute("""
        INSERT INTO watchlist_meta(list, program, country, source, note)
        VALUES (?, ?, ?, ?, ?)
    """, (list_name, program, country, source, f"Loaded {n} rows"))
    try:
        log_action("watchlist_refresh", "system", {"list": list_name, "program": program, "country": country, "rows": n})
    except Exception:
        pass
    return n

# ----------------------- batch jobs -----------------------

def enqueue_batch_job(source: str = "members", threshold: float = 0.88) -> int:
    ensure_batch_schema()
    job_id = _next_id("sanctions_jobs", "job_id")
    execute("""
        INSERT INTO sanctions_jobs(job_id, source, threshold, status, started_at)
        VALUES (?, ?, ?, 'Queued', now())
    """, (job_id, source, float(threshold)))
    try:
        log_action("sanctions_job_enqueued", "system", {"job_id": job_id, "source": source, "threshold": threshold})
    except Exception:
        pass
    return job_id

def run_batch_job(job_id: int) -> int:
    """
    Execute a queued job and populate sanctions_hits with a snapshot of matches.
    Returns number of hits inserted.
    """
    ensure_batch_schema()
    # Mark running
    execute("UPDATE sanctions_jobs SET status='Running', started_at=now() WHERE job_id=?", (job_id,))

    # Fetch job
    job = query("SELECT source, threshold FROM sanctions_jobs WHERE job_id=?", (job_id,))
    if job.empty:
        execute("UPDATE sanctions_jobs SET status='Error', note='Job not found', finished_at=now() WHERE job_id=?", (job_id,))
        return 0
    source = str(job.iloc[0]["source"])
    threshold = float(job.iloc[0]["threshold"])

    # Run fuzzy hits using existing function
    hits_df = sanctions_fuzzy_hits(threshold=threshold, source=source)
    if hits_df is None or hits_df.empty:
        execute("UPDATE sanctions_jobs SET status='Done', finished_at=now(), note='No hits' WHERE job_id=?", (job_id,))
        try:
            log_action("sanctions_job_complete", "system", {"job_id": job_id, "hits": 0})
        except Exception:
            pass
        return 0

    # Determine entity_type and ts_last if any
    entity_type = "member" if source == "members" else "counterparty"

    # Insert hits snapshot
    n = 0
    for _, r in hits_df.iterrows():
        hit_id = _next_id("sanctions_hits", "hit_id")
        execute("""
            INSERT INTO sanctions_hits(
              hit_id, job_id, entity_type, entity_id, entity_name, watch_name, similarity,
              list, program, country, ts_last, triage_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Open')
        """, (
            hit_id, job_id, entity_type,
            str(r.get("entity_id") or ""),
            str(r.get("entity_name") or ""),
            str(r.get("watch_name") or ""),
            float(r.get("similarity") or 0.0),
            str(r.get("list") or ""),
            str(r.get("program") or ""),
            str(r.get("country") or ""),
            None
        ))
        n += 1

    execute("UPDATE sanctions_jobs SET status='Done', finished_at=now(), note=? WHERE job_id=?",
            (f"{n} hits", job_id))
    try:
        log_action("sanctions_job_complete", "system", {"job_id": job_id, "hits": n})
    except Exception:
        pass
    return n

def list_jobs(limit: int = 200) -> pd.DataFrame:
    ensure_batch_schema()
    return query(f"""
        SELECT job_id, source, threshold, status, started_at, finished_at, note
        FROM sanctions_jobs
        ORDER BY COALESCE(finished_at, started_at) DESC
        LIMIT {int(limit)}
    """)

def job_hits(job_id: int) -> pd.DataFrame:
    ensure_batch_schema()
    return query("""
        SELECT hit_id, job_id, entity_type, entity_id, entity_name, watch_name, similarity,
               list, program, country, ts_last, created_at, triage_status, triage_notes, case_id
        FROM sanctions_hits
        WHERE job_id=?
        ORDER BY similarity DESC, created_at DESC
    """, (job_id,))

# ----------------------- triage workflow -----------------------

def triage_hit(hit_id: int,
               status: str,
               notes: Optional[str] = None,
               create_case: bool = False,
               user: str = "MLRO") -> Optional[int]:
    """
    Update triage status/notes on sanctions_hits.
    Optionally escalate to Case (returns case_id) and mirror disposition to sanctions_screenings.
    """
    ensure_batch_schema()
    # fetch row
    row = query("SELECT * FROM sanctions_hits WHERE hit_id=?", (hit_id,))
    if row.empty:
        return None

    # update triage on hit
    execute("UPDATE sanctions_hits SET triage_status=?, triage_notes=? WHERE hit_id=?",
            (status, notes or None, hit_id))

    # mirror into register
    _ensure_register()
    execute("""
        INSERT INTO sanctions_screenings
        (screening_id, entity_type, entity_id, entity_name, watch_name, similarity, list, program, country, status, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, now())
    """, (
        _next_id("sanctions_screenings", "screening_id"),
        str(row.iloc[0].get("entity_type") or ""),
        str(row.iloc[0].get("entity_id") or ""),
        str(row.iloc[0].get("entity_name") or ""),
        str(row.iloc[0].get("watch_name") or ""),
        float(row.iloc[0].get("similarity") or 0.0),
        str(row.iloc[0].get("list") or ""),
        str(row.iloc[0].get("program") or ""),
        str(row.iloc[0].get("country") or ""),
        status, notes or None
    ))

    case_id: Optional[int] = None
    if create_case and status.lower() == "escalated":
        try:
            # Lazy import to avoid circulars
            from sacco_core.aml.investigations import create_case
            case_id = create_case(
                title=f"Sanctions hit: {row.iloc[0].get('entity_name')}",
                created_by=user,
                summary=f"Watchlist: {row.iloc[0].get('watch_name')} (sim={row.iloc[0].get('similarity')})",
                status="Open",
                severity="High",
                category="Sanctions",
                member_id=str(row.iloc[0].get("entity_id") or ""),
                entity_name=str(row.iloc[0].get("entity_name") or ""),
                source_type="sanctions",
                source_ref=str(hit_id),
                signals="Sanctions match (batch)"
            )
            execute("UPDATE sanctions_hits SET case_id=? WHERE hit_id=?", (case_id, hit_id))
        except Exception:
            case_id = None

    try:
        log_action("sanctions_triage",
                   user,
                   {"hit_id": hit_id, "status": status, "notes": notes or "", "case_id": case_id})
    except Exception:
        pass
    return case_id

# ---------------------------------------------------------------------
# Back-compat wrappers expected by alerts.py
# ---------------------------------------------------------------------

def screen_members(where_sql: str = "", params: Tuple = (), threshold: float = 0.88,
                   limit_watch: int = 5000) -> pd.DataFrame:
    """
    Compatibility shim: return fuzzy screening hits for members.
    Ignores where_sql/params (members table often has no 'ts' column).
    """
    return sanctions_fuzzy_hits(threshold=threshold, limit_watch=limit_watch, source="members")

def screen_counterparties(where_sql: str = "", params: Tuple = (), threshold: float = 0.90) -> pd.DataFrame:
    """
    Compatibility shim: return counterparty screening hits from transactions.
    Ignores where_sql/params; filtering is handled inside sanctions_txn_hits.
    """
    return sanctions_txn_hits(threshold=threshold)
