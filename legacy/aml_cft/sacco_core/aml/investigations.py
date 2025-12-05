# sacco_core/aml/investigations.py
from __future__ import annotations
from typing import Optional, Tuple, Dict, Any, List
from pathlib import Path
from datetime import date, datetime, timedelta
import pandas as pd

from sacco_core.db import query, execute
from sacco_core.config import get_config
from sacco_core.aml.sanctions import recent_screenings  # for "Create from hit"

ATTACH_DIR = (Path(__file__).resolve().parents[2] / "data" / "attachments")
ATTACH_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# Schema bootstrap (idempotent) - no unsupported constraints/identity columns
# -----------------------------------------------------------------------------
def ensure_schema() -> None:
    # Keep IDs as BIGINT (no identity), we will allocate IDs ourselves.
    execute("""
        CREATE TABLE IF NOT EXISTS cases (
          case_id BIGINT,
          created_at TIMESTAMP DEFAULT now(),
          created_by VARCHAR,
          title VARCHAR,
          status VARCHAR,                 -- Open | Under Review | Escalated | Closed
          severity VARCHAR,               -- Low | Medium | High | Critical
          category VARCHAR,               -- Sanctions | Alerts | KYC | Transaction | Other
          member_id VARCHAR,
          entity_name VARCHAR,
          branch VARCHAR,
          product VARCHAR,
          summary VARCHAR,
          due_date DATE,
          source_type VARCHAR,            -- 'sanctions' | 'alert' | 'manual'
          source_ref VARCHAR,             -- reference id from source (eg screening_id)
          signals VARCHAR
        )
    """)
    execute("""
        CREATE TABLE IF NOT EXISTS case_comments (
          comment_id BIGINT,
          case_id BIGINT,
          created_at TIMESTAMP DEFAULT now(),
          user VARCHAR,
          comment VARCHAR
        )
    """)
    execute("""
        CREATE TABLE IF NOT EXISTS case_attachments (
          attachment_id BIGINT,
          case_id BIGINT,
          uploaded_at TIMESTAMP DEFAULT now(),
          filename VARCHAR,
          path VARCHAR
        )
    """)
    execute("""
        CREATE TABLE IF NOT EXISTS case_events (
          event_id BIGINT,
          case_id BIGINT,
          created_at TIMESTAMP DEFAULT now(),
          user VARCHAR,
          event_type VARCHAR,      -- status_change | create | link | note
          details VARCHAR
        )
    """)

def _exists(table: str) -> bool:
    try:
        df = query("show tables")
        col = "name" if "name" in df.columns else df.columns[0]
        return table.lower() in df[col].str.lower().tolist()
    except Exception:
        return False

def _next_id(table: str, col: str) -> int:
    ensure_schema()
    try:
        df = query(f"SELECT COALESCE(MAX({col}), 0) + 1 AS nid FROM {table}")
        return int(df["nid"].iloc[0])
    except Exception:
        return 1

# -----------------------------------------------------------------------------
# CRUD-ish helpers
# -----------------------------------------------------------------------------
def list_cases(status: Optional[List[str]] = None,
               severity: Optional[List[str]] = None,
               date_from: Optional[date] = None,
               date_to: Optional[date] = None,
               search: Optional[str] = None) -> pd.DataFrame:
    ensure_schema()
    where: List[str] = []
    params: List[Any] = []

    if status:
        where.append("status IN ({})".format(", ".join(["?"] * len(status))))
        params.extend(status)
    if severity:
        where.append("severity IN ({})".format(", ".join(["?"] * len(severity))))
        params.extend(severity)
    if date_from:
        where.append("created_at >= ?")
        params.append(pd.to_datetime(date_from).strftime("%Y-%m-%d"))
    if date_to:
        where.append("created_at < DATE_ADD(?, INTERVAL 1 DAY)")
        params.append(pd.to_datetime(date_to).strftime("%Y-%m-%d"))
    if search:
        where.append("(lower(title) LIKE ? OR lower(summary) LIKE ? OR lower(entity_name) LIKE ?)")
        like = f"%{str(search).lower()}%"
        params += [like, like, like]

    sql = f"""
        SELECT case_id, created_at, title, status, severity, category,
               member_id, entity_name, branch, product, due_date, source_type, source_ref, signals
        FROM cases
        {"WHERE " + " AND ".join(where) if where else ""}
        ORDER BY created_at DESC
        LIMIT 5000
    """
    return query(sql, tuple(params))

def create_case(title: str,
                created_by: str,
                summary: str = "",
                status: str = "Open",
                severity: str = "Medium",
                category: str = "Other",
                member_id: Optional[str] = None,
                entity_name: Optional[str] = None,
                branch: Optional[str] = None,
                product: Optional[str] = None,
                due_date: Optional[date] = None,
                source_type: Optional[str] = "manual",
                source_ref: Optional[str] = None,
                signals: Optional[str] = None) -> int:
    ensure_schema()
    case_id = _next_id("cases", "case_id")
    execute("""
        INSERT INTO cases
          (case_id, created_by, title, status, severity, category, member_id, entity_name,
           branch, product, summary, due_date, source_type, source_ref, signals)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (case_id, created_by, title, status, severity, category, member_id, entity_name,
          branch, product, summary, due_date, source_type, source_ref, signals))
    add_event(case_id, created_by, "create", f"Case created: {title}")
    return case_id

def get_case(case_id: int) -> pd.DataFrame:
    ensure_schema()
    return query("SELECT * FROM cases WHERE case_id = ?", (case_id,))

def update_status(case_id: int, user: str, new_status: str) -> None:
    ensure_schema()
    execute("UPDATE cases SET status = ? WHERE case_id = ?", (new_status, case_id))
    add_event(case_id, user, "status_change", f"Status set to {new_status}")

def update_summary(case_id: int, summary: str) -> None:
    ensure_schema()
    execute("UPDATE cases SET summary = ? WHERE case_id = ?", (summary, case_id))

def add_comment(case_id: int, user: str, comment: str) -> None:
    ensure_schema()
    comment_id = _next_id("case_comments", "comment_id")
    execute("INSERT INTO case_comments (comment_id, case_id, user, comment) VALUES (?, ?, ?, ?)",
            (comment_id, case_id, user, comment))
    add_event(case_id, user, "note", "Comment added")

def list_comments(case_id: int) -> pd.DataFrame:
    ensure_schema()
    return query("""
        SELECT comment_id, created_at, user, comment
        FROM case_comments
        WHERE case_id = ?
        ORDER BY created_at DESC
    """, (case_id,))

def add_event(case_id: int, user: str, event_type: str, details: str) -> None:
    ensure_schema()
    event_id = _next_id("case_events", "event_id")
    execute("""
        INSERT INTO case_events (event_id, case_id, user, event_type, details)
        VALUES (?, ?, ?, ?, ?)
    """, (event_id, case_id, user, event_type, details))

def timeline(case_id: int) -> pd.DataFrame:
    ensure_schema()
    return query("""
        SELECT created_at, user, event_type, details
        FROM case_events
        WHERE case_id = ?
        ORDER BY created_at DESC
    """, (case_id,))

# -----------------------------------------------------------------------------
# Attachments
# -----------------------------------------------------------------------------
def save_attachment(case_id: int, filename: str, data: bytes) -> str:
    """
    Saves file to data/attachments/<case_id>_YYYYmmddHHMMSS_filename and registers it.
    Returns saved path (relative to project root data/).
    """
    ensure_schema()
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    safe_name = f"{case_id}_{ts}_{filename}".replace(" ", "_")
    path = ATTACH_DIR / safe_name
    with open(path, "wb") as f:
        f.write(data)

    rel = f"attachments/{safe_name}"  # store relative under data/
    attachment_id = _next_id("case_attachments", "attachment_id")
    execute("INSERT INTO case_attachments (attachment_id, case_id, filename, path) VALUES (?, ?, ?, ?)",
            (attachment_id, case_id, filename, rel))
    add_event(case_id, "system", "note", f"Attachment uploaded: {filename}")
    return rel

def list_attachments(case_id: int) -> pd.DataFrame:
    ensure_schema()
    return query("""
        SELECT attachment_id, uploaded_at, filename, path
        FROM case_attachments
        WHERE case_id = ?
        ORDER BY uploaded_at DESC
    """, (case_id,))

# -----------------------------------------------------------------------------
# Builders from hits (sanctions, etc.)
# -----------------------------------------------------------------------------
def create_case_from_sanction(screening_row: Dict[str, Any],
                              created_by: str = "MLRO") -> int:
    """
    Turn a sanctions_screenings row into a case.
    """
    ensure_schema()
    title = f"Sanctions match: {screening_row.get('entity_name','')}"
    summary = (
        f"Match to watchlist: {screening_row.get('watch_name','')} "
        f"(list={screening_row.get('list')}, score={screening_row.get('similarity')})"
    )
    return create_case(
        title=title,
        created_by=created_by,
        summary=summary,
        status="Open",
        severity="High",
        category="Sanctions",
        member_id=str(screening_row.get("entity_id") or ""),
        entity_name=str(screening_row.get("entity_name") or ""),
        due_date=date.today() + timedelta(days=int(get_config().frc.str_deadline_days)),
        source_type="sanctions",
        source_ref=str(screening_row.get("screening_id") or ""),
        signals="Sanctions match"
    )
