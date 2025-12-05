# sacco_core/aml/training.py
from __future__ import annotations
from typing import Optional, Tuple, List, Dict, Any
from datetime import date, datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np

from sacco_core.db import query, execute

DATA_DIR = (Path(__file__).resolve().parents[2] / "data")
UPLOADS_DIR = DATA_DIR / "training_uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------- Schema ----------------------------

def ensure_schema() -> None:
    """
    Create minimal, constraint-free DuckDB tables for training, certs & KB.
    """
    execute("""
        CREATE TABLE IF NOT EXISTS training_courses (
          course_id BIGINT,
          title VARCHAR,
          category VARCHAR,
          provider VARCHAR,
          hours DOUBLE,
          mode VARCHAR,           -- e.g. 'eLearning','Workshop'
          active BOOLEAN,
          created_at TIMESTAMP DEFAULT now()
        )
    """)
    execute("""
        CREATE TABLE IF NOT EXISTS training_assignments (
          assignment_id BIGINT,
          member_id VARCHAR,
          course_id BIGINT,
          assigned_on DATE,
          due_on DATE,
          status VARCHAR,         -- 'Assigned','In-Progress','Completed','Expired'
          notes VARCHAR,
          attachment_path VARCHAR,
          score DOUBLE,
          completed_on DATE
        )
    """)
    execute("""
        CREATE TABLE IF NOT EXISTS training_completions (
          completion_id BIGINT,
          member_id VARCHAR,
          course_id BIGINT,
          completed_on DATE,
          score DOUBLE,
          evidence_path VARCHAR,
          recorded_at TIMESTAMP DEFAULT now()
        )
    """)
    execute("""
        CREATE TABLE IF NOT EXISTS certifications (
          cert_id BIGINT,
          member_id VARCHAR,
          cert_name VARCHAR,
          provider VARCHAR,
          issued_on DATE,
          expires_on DATE,
          status VARCHAR,         -- 'Valid','Expiring','Expired','Revoked'
          certificate_path VARCHAR,
          notes VARCHAR,
          created_at TIMESTAMP DEFAULT now()
        )
    """)
    execute("""
        CREATE TABLE IF NOT EXISTS kb_articles (
          kb_id BIGINT,
          title VARCHAR,
          body VARCHAR,
          category VARCHAR,
          url VARCHAR,
          tags VARCHAR,           -- comma separated
          created_at TIMESTAMP DEFAULT now()
        )
    """)

def _next_id(table: str, col: str) -> int:
    try:
        df = query(f"SELECT COALESCE(MAX({col}), 0) AS mx FROM {table}")
        base = int(df["mx"].iloc[0]) if not df.empty else 0
    except Exception:
        base = 0
    return base + 1

def _exists(table: str) -> bool:
    try:
        df = query("SHOW TABLES")
        c = "name" if "name" in df.columns else df.columns[0]
        return table.lower() in df[c].str.lower().tolist()
    except Exception:
        return False

def _cols(table: str) -> List[str]:
    try:
        return query(f"PRAGMA table_info({table})")["name"].str.lower().tolist()
    except Exception:
        return []

# ---------------------------- Seeding (optional, smart) ----------------------------

def seed_if_empty() -> None:
    """
    Populate a small catalog, KB, and a handful of assignments from members if empty.
    Never overwrites existing data.
    """
    ensure_schema()
    try:
        n_courses = int(query("SELECT COUNT(*) c FROM training_courses")["c"].iloc[0])
    except Exception:
        n_courses = 0

    if n_courses == 0:
        rows = [
            (1, "AML Foundations", "Compliance", "Internal", 2.0, "eLearning", True),
            (2, "CTR/STR Essentials", "Regulatory", "Internal", 1.5, "eLearning", True),
            (3, "Sanctions Screening Basics", "Screening", "Internal", 1.0, "eLearning", True),
            (4, "Advanced Transaction Monitoring", "Analytics", "Internal", 2.5, "Workshop", True),
        ]
        for r in rows:
            execute("""INSERT INTO training_courses(course_id,title,category,provider,hours,mode,active)
                       VALUES (?,?,?,?,?,?,?)""", r)

    # Seed KB
    try:
        n_kb = int(query("SELECT COUNT(*) c FROM kb_articles")["c"].iloc[0])
    except Exception:
        n_kb = 0
    if n_kb == 0:
        kb = [
            (1, "How to file an STR", "Step-by-step filing guide aligned to goAML.", "Reporting", None, "STR,goAML,guide"),
            (2, "CTR thresholds & examples", "Quick reference for CTR thresholds and scenarios.", "Reporting", None, "CTR,thresholds"),
            (3, "Sanctions hit triage", "Initial triage questions for potential sanctions matches.", "Screening", None, "sanctions,triage"),
        ]
        for (kid, title, body, cat, url, tags) in kb:
            execute("""INSERT INTO kb_articles(kb_id,title,body,category,url,tags)
                       VALUES (?,?,?,?,?,?)""", (kid, title, body, cat, url, tags))

    # Seed few assignments if members exist & no assignments yet
    try:
        n_ass = int(query("SELECT COUNT(*) c FROM training_assignments")["c"].iloc[0])
    except Exception:
        n_ass = 0

    if n_ass == 0 and _exists("members") and "member_id" in _cols("members"):
        members = query("SELECT member_id FROM members LIMIT 50")
        today = date.today()
        aid = _next_id("training_assignments", "assignment_id")
        for i, r in members.iterrows():
            mid = str(r["member_id"])
            for course_id in [1, 2]:
                execute("""INSERT INTO training_assignments
                           (assignment_id, member_id, course_id, assigned_on, due_on, status, notes)
                           VALUES (?,?,?,?,?,?,?)""",
                        (aid, mid, course_id, today, today + timedelta(days=14), "Assigned", None))
                aid += 1

# ---------------------------- Courses ----------------------------

def list_courses(active_only: bool = True) -> pd.DataFrame:
    ensure_schema()
    sql = "SELECT * FROM training_courses"
    if active_only:
        sql += " WHERE COALESCE(active, TRUE)=TRUE"
    return query(sql + " ORDER BY created_at DESC")

def upsert_course(course_id: Optional[int],
                  title: str,
                  category: Optional[str],
                  provider: Optional[str],
                  hours: Optional[float],
                  mode: Optional[str],
                  active: bool = True) -> int:
    ensure_schema()
    if course_id is None:
        new_id = _next_id("training_courses", "course_id")
        execute("""INSERT INTO training_courses(course_id,title,category,provider,hours,mode,active)
                   VALUES (?,?,?,?,?,?,?)""",
                (new_id, title, category, provider, hours, mode, active))
        return new_id
    else:
        execute("""UPDATE training_courses
                   SET title=?, category=?, provider=?, hours=?, mode=?, active=?
                   WHERE course_id=?""",
                (title, category, provider, hours, mode, active, course_id))
        return int(course_id)

# ---------------------------- Assignments ----------------------------

def assign_course(member_id: str, course_id: int, due_on: Optional[date] = None, notes: Optional[str] = None) -> int:
    ensure_schema()
    aid = _next_id("training_assignments", "assignment_id")
    execute("""INSERT INTO training_assignments
               (assignment_id, member_id, course_id, assigned_on, due_on, status, notes)
               VALUES (?,?,?,?,?,?,?)""",
            (aid, member_id, course_id, date.today(), due_on or (date.today() + timedelta(days=14)), "Assigned", notes))
    return aid

def list_assignments(status: Optional[str] = None,
                     branch: Optional[str] = None,
                     search_member: Optional[str] = None) -> pd.DataFrame:
    """
    Joins members when available to surface branch/name.
    """
    ensure_schema()
    has_members = _exists("members")
    mcols = _cols("members") if has_members else []

    sel = ["a.assignment_id","a.member_id","a.course_id","a.assigned_on","a.due_on","a.status","a.score","a.completed_on","a.notes","a.attachment_path"]
    join = ""
    where = []
    params: List[Any] = []

    if has_members and ("member_id" in mcols):
        name_col = "name" if "name" in mcols else ("full_name" if "full_name" in mcols else None)
        if name_col:
            sel.append(f"m.{name_col} AS member_name")
        if "branch" in mcols:
            sel.append("m.branch")
        join = "LEFT JOIN members m ON m.member_id=a.member_id"

        if branch and "branch" in mcols and branch != "All":
            where.append("m.branch = ?")
            params.append(branch)

        if search_member and name_col:
            where.append(f"LOWER(m.{name_col}) LIKE LOWER(?)")
            params.append(f"%{search_member}%")

    if status and status != "All":
        where.append("COALESCE(a.status,'Assigned') = ?")
        params.append(status)

    sql = f"SELECT {', '.join(sel)} FROM training_assignments a {join}"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY COALESCE(a.due_on, a.assigned_on) DESC, a.assignment_id DESC"
    return query(sql, tuple(params))

def mark_completed(assignment_id: int,
                   score: Optional[float] = None,
                   evidence_path: Optional[str] = None,
                   completed_on: Optional[date] = None) -> None:
    ensure_schema()
    # Update assignment
    execute("""UPDATE training_assignments
               SET status='Completed', score=?, completed_on=?, attachment_path=?
               WHERE assignment_id=?""",
            (score, completed_on or date.today(), evidence_path, assignment_id))
    # Mirror into completions
    df = query("SELECT member_id, course_id, completed_on, score, attachment_path FROM training_assignments WHERE assignment_id=?", (assignment_id,))
    if not df.empty:
        cid = _next_id("training_completions", "completion_id")
        r = df.iloc[0]
        execute("""INSERT INTO training_completions
                   (completion_id, member_id, course_id, completed_on, score, evidence_path)
                   VALUES (?,?,?,?,?,?)""",
                (cid, str(r.get("member_id")), int(r.get("course_id")), r.get("completed_on"), r.get("score"), r.get("attachment_path")))

def expire_overdue() -> None:
    """Set status='Expired' for overdue, non-completed assignments."""
    ensure_schema()
    execute("""
        UPDATE training_assignments
        SET status='Expired'
        WHERE COALESCE(status,'Assigned') NOT IN ('Completed')
          AND due_on IS NOT NULL AND due_on < CURRENT_DATE
    """)

# ---------------------------- Certifications ----------------------------

def add_certification(member_id: str,
                      cert_name: str,
                      provider: Optional[str],
                      issued_on: Optional[date],
                      expires_on: Optional[date],
                      status: str = "Valid",
                      certificate_path: Optional[str] = None,
                      notes: Optional[str] = None) -> int:
    ensure_schema()
    cid = _next_id("certifications", "cert_id")
    execute("""INSERT INTO certifications
               (cert_id, member_id, cert_name, provider, issued_on, expires_on, status, certificate_path, notes)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (cid, member_id, cert_name, provider, issued_on, expires_on, status, certificate_path, notes))
    return cid

def list_certifications(branch: Optional[str] = None,
                        status: Optional[str] = None,
                        search_member: Optional[str] = None) -> pd.DataFrame:
    ensure_schema()
    has_members = _exists("members")
    mcols = _cols("members") if has_members else []
    sel = ["c.cert_id","c.member_id","c.cert_name","c.provider","c.issued_on","c.expires_on","c.status","c.certificate_path","c.notes"]
    join = ""
    where = []
    params: List[Any] = []
    if has_members and "member_id" in mcols:
        name_col = "name" if "name" in mcols else ("full_name" if "full_name" in mcols else None)
        if name_col:
            sel.append(f"m.{name_col} AS member_name")
        if "branch" in mcols:
            sel.append("m.branch")
        join = "LEFT JOIN members m ON m.member_id=c.member_id"
        if branch and branch != "All" and "branch" in mcols:
            where.append("m.branch = ?")
            params.append(branch)
        if search_member and name_col:
            where.append(f"LOWER(m.{name_col}) LIKE LOWER(?)")
            params.append(f"%{search_member}%")
    if status and status != "All":
        where.append("COALESCE(c.status,'Valid') = ?")
        params.append(status)

    sql = f"SELECT {', '.join(sel)} FROM certifications c {join}"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY COALESCE(c.expires_on, c.issued_on) DESC, c.cert_id DESC"
    return query(sql, tuple(params))

def cert_reminders(within_days: int = 30) -> pd.DataFrame:
    """
    List certifications with expiry status within N days.
    Uses a computed cutoff date (today + within_days) to keep DuckDB param-safe.
    """
    ensure_schema()
    cutoff = date.today() + timedelta(days=int(within_days))

    df = query("""
        SELECT
          cert_id,
          member_id,
          cert_name,
          provider,
          expires_on,
          CASE
            WHEN expires_on IS NULL THEN NULL
            WHEN CAST(expires_on AS DATE) < CURRENT_DATE THEN 'Expired'
            WHEN CAST(expires_on AS DATE) <= ? THEN 'Expiring Soon'
            ELSE 'Valid'
          END AS due_status,
          date_diff('day', CURRENT_DATE, CAST(expires_on AS DATE)) AS days_left
        FROM certifications
        ORDER BY CAST(expires_on AS DATE) ASC
    """, (cutoff,))

    return df.sort_values(["due_status", "expires_on"], ascending=[True, True], na_position="last")

# ---------------------------- Knowledge Base ----------------------------

def add_article(title: str,
                body: str,
                category: Optional[str],
                url: Optional[str],
                tags: Optional[str]) -> int:
    ensure_schema()
    kid = _next_id("kb_articles", "kb_id")
    execute("""INSERT INTO kb_articles(kb_id,title,body,category,url,tags)
               VALUES (?,?,?,?,?,?)""", (kid, title, body, category, url, tags))
    return kid

def search_kb(q: Optional[str] = None, category: Optional[str] = None, tag: Optional[str] = None) -> pd.DataFrame:
    ensure_schema()
    where = []
    params: List[Any] = []
    if q:
        where.append("(LOWER(title) LIKE LOWER(?) OR LOWER(body) LIKE LOWER(?))")
        params += [f"%{q}%", f"%{q}%"]
    if category and category != "All":
        where.append("LOWER(category) = LOWER(?)")
        params.append(category)
    if tag and tag != "All":
        where.append("LOWER(tags) LIKE LOWER(?)")
        params.append(f"%{tag}%")

    sql = "SELECT kb_id, title, category, url, tags, created_at FROM kb_articles"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY created_at DESC"
    return query(sql, tuple(params))

# ---------------------------- Trends ----------------------------

def completion_trend(by: str = "month") -> pd.DataFrame:
    """
    Returns period, completions (#), avg_score.
    by: 'day' | 'week' | 'month'
    """
    ensure_schema()
    if by not in ("day","week","month"):
        by = "month"
    if by == "day":
        grp = "CAST(completed_on AS DATE)"
    elif by == "week":
        grp = "CAST(date_trunc('week', completed_on) AS DATE)"
    else:
        grp = "CAST(date_trunc('month', completed_on) AS DATE)"

    return query(f"""
        SELECT {grp} AS period,
               COUNT(*) AS completions,
               AVG(score) AS avg_score
        FROM training_completions
        GROUP BY 1
        ORDER BY period
    """)

# ---------------------------- Files ----------------------------

def save_upload(file) -> Optional[str]:
    """
    Save a Streamlit UploadedFile to data/training_uploads and return relative path.
    """
    if file is None:
        return None
    p = UPLOADS_DIR / f"{int(datetime.now().timestamp())}_{file.name}"
    with open(p, "wb") as f:
        f.write(file.getbuffer())
    # return relative path for storage
    rel = p.relative_to(DATA_DIR)
    return str(rel)
