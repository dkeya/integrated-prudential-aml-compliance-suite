# sacco_core/aml/submissions.py
from __future__ import annotations
from typing import Optional, Tuple, List
from datetime import datetime
from pathlib import Path
import pandas as pd

from sacco_core.db import query, execute

DATA_DIR = (Path(__file__).resolve().parents[2] / "data")
SUBMIT_DIR = DATA_DIR / "goaml_submissions"
SUBMIT_DIR.mkdir(parents=True, exist_ok=True)

# ----------------------------- helpers -----------------------------

def _exists(table: str) -> bool:
    try:
        df = query("SHOW TABLES")
        c = "name" if "name" in df.columns else df.columns[0]
        return table.lower() in df[c].str.lower().tolist()
    except Exception:
        return False

def _table_cols(table: str) -> List[str]:
    try:
        return query(f"PRAGMA table_info({table})")["name"].str.lower().tolist()
    except Exception:
        return []

# ----------------------------- schema -----------------------------

def ensure_submission_schema() -> None:
    """
    Backward-compatible schema creator (keeps your original columns).
    Does NOT alter an existing table with newer column names.
    """
    if not _exists("frc_submissions"):
        execute("""
            CREATE TABLE IF NOT EXISTS frc_submissions (
              submit_id BIGINT,
              kind VARCHAR,            -- 'STR' | 'CTR'
              key_ref VARCHAR,         -- member_id or week summary ref
              status VARCHAR,          -- 'Draft','Queued','Submitted','Acknowledged','Rejected','Error'
              file_path VARCHAR,
              created_at TIMESTAMP DEFAULT now(),
              error_message VARCHAR
            )
        """)

# Alias for older code paths
def ensure_schema() -> None:
    ensure_submission_schema()

def _next_id() -> int:
    cols = _table_cols("frc_submissions")
    if "submit_id" in cols:
        sql = "SELECT COALESCE(MAX(submit_id),0) mx FROM frc_submissions"
    elif "submission_id" in cols:
        sql = "SELECT COALESCE(MAX(submission_id),0) mx FROM frc_submissions"
    else:
        # Table missing or empty — ensure and retry
        ensure_submission_schema()
        sql = "SELECT COALESCE(MAX(submit_id),0) mx FROM frc_submissions"

    try:
        df = query(sql)
        base = int(df["mx"].iloc[0]) if not df.empty else 0
    except Exception:
        base = 0
    return base + 1

# ----------------------------- core ops (write) -----------------------------

def save_submission(kind: str,
                    key_ref: str,
                    xml_text: str,
                    status: str = "Queued",
                    error_message: Optional[str] = None) -> int:
    """
    Original API you had — preserved.
    Writes to legacy schema (submit_id, kind, key_ref, ...).
    If your DB already uses the newer names, we insert with appropriate mapping.
    """
    ensure_submission_schema()
    sid = _next_id()

    safe_ref = str(key_ref).replace("/", "_").replace("\\", "_").replace(" ", "_")
    filepath = SUBMIT_DIR / f"{sid}_{kind}_{safe_ref}.xml"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(xml_text)

    cols = _table_cols("frc_submissions")

    if "submit_id" in cols:
        # legacy schema
        execute("""INSERT INTO frc_submissions(submit_id,kind,key_ref,status,file_path,error_message)
                   VALUES (?,?,?,?,?,?)""",
                (sid, kind, key_ref, status, str(filepath.relative_to(DATA_DIR)), error_message))
    else:
        # newer schema (submission_id/sub_type/reference/updated_at)
        # We insert best-effort if columns exist; otherwise, add minimal row
        # Detect optional columns gracefully
        has_file_path = "file_path" in cols
        has_error = "error_message" in cols
        has_updated = "updated_at" in cols
        sql_cols = ["submission_id", "sub_type", "reference", "status"]
        params: List[object] = [sid, kind, key_ref, status]
        if has_file_path:
            sql_cols.append("file_path")
            params.append(str(filepath.relative_to(DATA_DIR)))
        if has_error:
            sql_cols.append("error_message")
            params.append(error_message)
        if has_updated:
            sql_cols.append("updated_at")
            params.append(pd.Timestamp.utcnow())

        placeholders = ",".join(["?"] * len(sql_cols))
        execute(f"INSERT INTO frc_submissions({', '.join(sql_cols)}) VALUES ({placeholders})", tuple(params))

    return sid

def record_submission(sub_type: str,
                      reference: str,
                      payload_xml: str,
                      status: str = "Draft",
                      notes: Optional[str] = None) -> int:
    """
    Newer wrapper used by pages. Delegates to save_submission.
    """
    return save_submission(kind=sub_type, key_ref=reference, xml_text=payload_xml,
                           status=status, error_message=notes)

def update_submission_status(submission_id: int,
                             new_status: str,
                             notes: Optional[str] = None) -> None:
    """
    Works with either schema.
    - Appends notes to error_message if present; otherwise sets it.
    - Updates created_at/updated_at best-effort based on available columns.
    """
    ensure_submission_schema()
    cols = _table_cols("frc_submissions")

    # Get current notes
    if "submit_id" in cols:
        cur = query("SELECT error_message FROM frc_submissions WHERE submit_id=?", (int(submission_id),))
    else:
        cur = query("SELECT error_message FROM frc_submissions WHERE submission_id=?", (int(submission_id),))

    prev = ""
    if not cur.empty and "error_message" in cur.columns and pd.notna(cur.iloc[0]["error_message"]):
        prev = str(cur.iloc[0]["error_message"])
    merged = (prev + (" | " if prev and notes else "") + (notes or "")).strip() or None

    if "submit_id" in cols:
        execute("UPDATE frc_submissions SET status=?, error_message=? WHERE submit_id=?",
                (new_status, merged, int(submission_id)))
    else:
        if "updated_at" in cols:
            execute("UPDATE frc_submissions SET status=?, error_message=?, updated_at=now() WHERE submission_id=?",
                    (new_status, merged, int(submission_id)))
        else:
            execute("UPDATE frc_submissions SET status=?, error_message=? WHERE submission_id=?",
                    (new_status, merged, int(submission_id)))

# ----------------------------- reads (robust to either schema) -----------------------------

def list_submissions(limit: int = 500) -> pd.DataFrame:
    """
    Returns a consistent view with columns:
      submission_id, sub_type, reference, status, file_path, created_at, error_message
    Works whether the table uses old (submit_id/kind/key_ref/created_at) or new (submission_id/sub_type/reference/updated_at) names.
    """
    ensure_submission_schema()
    cols = _table_cols("frc_submissions")

    if "submit_id" in cols:
        # legacy schema
        return query(f"""
            SELECT
                submit_id       AS submission_id,
                kind            AS sub_type,
                key_ref         AS reference,
                status,
                file_path,
                created_at,
                error_message
            FROM frc_submissions
            ORDER BY submit_id DESC
            LIMIT {int(limit)}
        """)
    else:
        # newer schema (what your error message suggests)
        # Some installs may not have file_path/error_message/created_at; handle via COALESCE/NULL
        sel_file = "file_path" if "file_path" in cols else "NULL AS file_path"
        sel_err  = "error_message" if "error_message" in cols else "NULL AS error_message"
        # prefer created_at if present; else updated_at
        if "created_at" in cols and "updated_at" in cols:
            sel_created = "COALESCE(created_at, updated_at) AS created_at"
        elif "created_at" in cols:
            sel_created = "created_at"
        elif "updated_at" in cols:
            sel_created = "updated_at AS created_at"
        else:
            sel_created = "now() AS created_at"

        return query(f"""
            SELECT
                submission_id,
                sub_type,
                reference,
                status,
                {sel_file},
                {sel_created},
                {sel_err}
            FROM frc_submissions
            ORDER BY submission_id DESC
            LIMIT {int(limit)}
        """)

def list_submissions_filtered(sub_type: Optional[str] = None,
                              status: Optional[str] = None,
                              limit: int = 500) -> pd.DataFrame:
    """
    Filtered register (same consistent output columns as list_submissions).
    """
    ensure_submission_schema()
    cols = _table_cols("frc_submissions")
    where = []
    params: List[object] = []

    if "submit_id" in cols:
        # legacy schema
        if sub_type:
            where.append("kind = ?")
            params.append(sub_type)
        if status:
            where.append("status = ?")
            params.append(status)
        sql = """
            SELECT
                submit_id       AS submission_id,
                kind            AS sub_type,
                key_ref         AS reference,
                status,
                file_path,
                created_at,
                error_message
            FROM frc_submissions
        """
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY submit_id DESC LIMIT ?"
        params.append(int(limit))
        return query(sql, tuple(params))
    else:
        # newer schema
        if sub_type:
            where.append("sub_type = ?")
            params.append(sub_type)
        if status:
            where.append("status = ?")
            params.append(status)

        sel_file = "file_path" if "file_path" in cols else "NULL AS file_path"
        sel_err  = "error_message" if "error_message" in cols else "NULL AS error_message"
        if "created_at" in cols and "updated_at" in cols:
            sel_created = "COALESCE(created_at, updated_at) AS created_at"
        elif "created_at" in cols:
            sel_created = "created_at"
        elif "updated_at" in cols:
            sel_created = "updated_at AS created_at"
        else:
            sel_created = "now() AS created_at"

        sql = f"""
            SELECT
                submission_id,
                sub_type,
                reference,
                status,
                {sel_file},
                {sel_created},
                {sel_err}
            FROM frc_submissions
        """
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY submission_id DESC LIMIT ?"
        params.append(int(limit))
        return query(sql, tuple(params))
