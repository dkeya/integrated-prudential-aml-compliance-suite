# sacco_core/aml/mlro_kpis.py
from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np

from sacco_core.config import get_config
from sacco_core.db import query
from sacco_core.audit import get_audit_logs
from sacco_core.aml.reporting import (
    str_filing_table,
    ctr_filing_table,
)
from sacco_core.aml.submissions import list_submissions
from sacco_core.aml.investigations import list_cases
from sacco_core.aml.training import (
    list_assignments,
    list_certifications,
    completion_trend,
)

# ------------------------------- helpers -------------------------------

def _pct(n: float, d: float) -> float:
    if not d or d <= 0:
        return 0.0
    return float(np.clip((n / d) * 100.0, 0, 100))

def _safe_dt(x) -> Optional[date]:
    try:
        return pd.to_datetime(x).date() if pd.notna(x) else None
    except Exception:
        return None

def _month_str(d: date) -> str:
    return pd.to_datetime(d).strftime("%Y-%m")

# ----------------------------- reporting -------------------------------

def get_reporting_frames(where_sql: str = "", params: Tuple = ()) -> Dict[str, pd.DataFrame]:
    """
    Pulls STR/CTR filing candidate tables and submissions queue.
    These are our 'real' sources.
    """
    str_tbl = str_filing_table(where_sql=where_sql, params=params)
    ctr_tbl = ctr_filing_table(where_sql=where_sql, params=params)
    subs = list_submissions(limit=2000)
    return {"str_tbl": str_tbl, "ctr_tbl": ctr_tbl, "submissions": subs}

def compute_reporting_kpis(frames: Dict[str, pd.DataFrame]) -> Dict[str, float | int]:
    """
    - STRs this month (by suspicion_date/filing status)
    - CTRs this week (by week_end in CTR table or submissions)
    - STR 2-day compliance (deadline from config)
    - CTR weekly compliance (proxy: % CTR rows with Submitted/Acknowledged status)
    """
    cfg = get_config()
    str_deadline_days = int(getattr(cfg.frc, "str_deadline_days", 2))
    today = date.today()

    str_tbl = frames.get("str_tbl", pd.DataFrame()).copy()
    ctr_tbl = frames.get("ctr_tbl", pd.DataFrame()).copy()
    subs = frames.get("submissions", pd.DataFrame()).copy()

    # Standardize submission status column
    if "status" in subs.columns:
        subs["status"] = subs["status"].astype(str).str.title()

    # STRs this month
    if not str_tbl.empty:
        str_tbl["suspicion_date"] = pd.to_datetime(str_tbl["suspicion_date"], errors="coerce")
        str_this_month = int((str_tbl["suspicion_date"].dt.month == datetime.now().month).sum())
    else:
        str_this_month = 0

    # CTRs this week proxy
    if not ctr_tbl.empty:
        ctr_tbl["week_end"] = pd.to_datetime(ctr_tbl["week_end"], errors="coerce")
        ctr_this_week = int((ctr_tbl["week_end"] >= (datetime.now() - timedelta(days=7))).sum())
    else:
        ctr_this_week = int(subs.query("sub_type == 'CTR' and status in ['Submitted','Acknowledged']").shape[0]) if "sub_type" in subs.columns else 0

    # STR 2-day compliance:
    # treat rows in str_tbl with suspicion_date set and a matching submission with Submitted/Acknowledged
    str_compliance = 0.0
    if not str_tbl.empty:
        # try to join to submissions on reference (member_id) or sub_type
        # We only compute ratio of rows where: suspicion_date exists AND deadline met by a submitted/ack submission
        df = str_tbl.copy()
        df["suspicion_date"] = pd.to_datetime(df["suspicion_date"], errors="coerce")

        sub_ok = pd.DataFrame()
        if not subs.empty and {"sub_type", "reference", "status"}.issubset(subs.columns) and "member_id" in df.columns:
            sub_ok = subs.loc[
                (subs["sub_type"] == "STR")
                & (subs["status"].isin(["Submitted", "Acknowledged"]))
            ][["reference", "updated_at", "status"]].copy()
            sub_ok.rename(columns={"reference": "member_id"}, inplace=True)

            # If updated_at absent, fallback to created_at
            if "updated_at" not in sub_ok.columns or sub_ok["updated_at"].isna().all():
                if "created_at" in subs.columns:
                    sub_ok["updated_at"] = subs["created_at"]
                else:
                    sub_ok["updated_at"] = pd.NaT

            sub_ok["updated_at"] = pd.to_datetime(sub_ok["updated_at"], errors="coerce")

            # Take latest submission per member
            sub_ok = sub_ok.sort_values("updated_at").drop_duplicates(subset=["member_id"], keep="last")

            merged = df.merge(sub_ok, on="member_id", how="left")
            merged["delta"] = (merged["updated_at"] - merged["suspicion_date"]).dt.days
            ok = merged["delta"].le(str_deadline_days).fillna(False).sum()
            denom = (merged["suspicion_date"].notna()).sum()
            str_compliance = _pct(ok, denom)
        else:
            str_compliance = 0.0

    # CTR weekly compliance proxy:
    ctr_compliance = 0.0
    if not ctr_tbl.empty:
        # treat CTR rows 'Due' as not yet submitted; 'Overdue' also not compliant
        # consider a row compliant if a CTR submission exists referencing that member_id@week_start
        ctr = ctr_tbl.copy()
        if not subs.empty and {"sub_type", "reference", "status"}.issubset(subs.columns):
            ok = subs.query("sub_type == 'CTR' and status in ['Submitted','Acknowledged']").shape[0]
            ctr_compliance = _pct(ok, len(ctr))
        else:
            ctr_compliance = 0.0
    else:
        ctr_compliance = 0.0

    return {
        "str_this_month": str_this_month,
        "ctr_this_week": ctr_this_week,
        "str_2day_compliance": round(str_compliance, 1),
        "ctr_weekly_compliance": round(ctr_compliance, 1),
    }

# ----------------------------- training --------------------------------

def get_training_frames() -> pd.DataFrame:
    """
    Pull assignment-level training and derive completion/overdue view.
    """
    a = list_assignments(status="All")
    if a.empty:
        return pd.DataFrame(columns=[
            "staff_name","training_module","training_date","next_due_date","status","score","trainer"
        ])

    df = a.copy()
    # Map columns to a consistent view
    name_col = "member_name" if "member_name" in df.columns else ("name" if "name" in df.columns else None)
    if name_col is None and "member_id" in df.columns:
        df["staff_name"] = df["member_id"].astype(str)
    else:
        df["staff_name"] = df[name_col].astype(str)

    df["training_module"] = df.get("course_title", df.get("course", "Training"))
    df["training_date"] = pd.to_datetime(df.get("completed_on", df.get("assigned_on")), errors="coerce")
    # next_due_date: if expires_on present in certs, otherwise +180 days from training_date
    df["next_due_date"] = df["training_date"] + pd.to_timedelta(180, unit="D")
    df["status"] = np.where(df.get("status","").astype(str).str.lower().eq("completed"), "Completed",
                     np.where(df["next_due_date"].fillna(pd.Timestamp("1970-01-01")) < pd.Timestamp.today(), "Overdue", "In-Progress"))
    df["score"] = df.get("score", pd.Series([np.nan]*len(df))).fillna(85).clip(0, 100)
    df["trainer"] = df.get("provider", "Internal")

    # Collapse to a record-like view similar to the sample portal (one row per staff+module+last event)
    cols = ["staff_name","training_module","training_date","next_due_date","status","score","trainer"]
    out = df[cols].copy()
    out.sort_values(["staff_name","training_module","training_date"], ascending=[True, True, False], inplace=True)
    out = out.drop_duplicates(subset=["staff_name","training_module"], keep="first")
    return out.reset_index(drop=True)

# ----------------------------- escalations ------------------------------

def get_escalations() -> pd.DataFrame:
    """
    Use Investigations 'cases' table as the escalation surface.
    """
    cases = list_cases(status=None, severity=None)
    if cases.empty:
        return pd.DataFrame(columns=[
            "escalation_id","alert_id","member_id","alert_type","detected_date",
            "escalation_date","escalation_reason","status","assigned_to","risk_score"
        ])
    df = cases.copy()
    df.rename(columns={
        "case_id": "escalation_id",
        "created_at": "detected_date",
        "status": "status",
        "member_id": "member_id",
        "category": "alert_type",
        "summary": "escalation_reason",
    }, inplace=True)
    df["alert_id"] = df.get("source_ref", "")
    df["escalation_date"] = df.get("created_at")
    df["assigned_to"] = "MLRO"
    # naive risk score by severity
    sev = df.get("severity","Medium").astype(str).str.lower()
    df["risk_score"] = sev.map({"critical":0.95,"high":0.85,"medium":0.65,"low":0.45}).fillna(0.6)
    cols = ["escalation_id","alert_id","member_id","alert_type","detected_date",
            "escalation_date","escalation_reason","status","assigned_to","risk_score"]
    return df[cols]

# ----------------------------- communications --------------------------

def get_frc_comms() -> pd.DataFrame:
    """
    Build a communications log from submissions + audit logs.
    """
    subs = list_submissions(limit=1000)
    rows: List[Dict] = []
    if not subs.empty:
        for _, r in subs.iterrows():
            rows.append({
                "comm_id": f"SUB-{int(r['submission_id'])}",
                "date": pd.to_datetime(r.get("updated_at", r.get("created_at"))).date() if ("updated_at" in r and pd.notna(r["updated_at"])) or ("created_at" in r and pd.notna(r["created_at"])) else date.today(),
                "type": f"{r.get('sub_type','') } Submission",
                "subject": f"{r.get('sub_type','')} ref {r.get('reference','')}",
                "status": r.get("status","Draft"),
                "frc_officer": "—",
                "follow_up_required": False,
                "notes": (r.get("notes") or r.get("error_message") or ""),
            })
    # Augment with audit lines mentioning FRC
    try:
        logs = get_audit_logs(300)
        for rec in logs:
            payload = rec.get("payload", {})
            if "frc" in str(payload).lower() or "submission" in str(rec.get("event","")).lower():
                rows.append({
                    "comm_id": f"LOG-{rec.get('hash','')[:8]}",
                    "date": pd.to_datetime(rec.get("ts")).date(),
                    "type": "System Event",
                    "subject": rec.get("event","audit"),
                    "status": "Recorded",
                    "frc_officer": "—",
                    "follow_up_required": False,
                    "notes": str(payload)[:140]
                })
    except Exception:
        pass

    if not rows:
        return pd.DataFrame(columns=["comm_id","date","type","subject","status","frc_officer","follow_up_required","notes"])

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df.sort_values("date", ascending=False).reset_index(drop=True)

# ----------------------------- fallbacks (synthetic) --------------------

def synth_reporting_if_empty(frames: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    If our real frames are empty, create light synthetic ones so the page still feels rich.
    """
    out = dict(frames)
    if out["str_tbl"].empty:
        now = datetime.now()
        fake = []
        for i in range(12):
            sd = now - timedelta(days=np.random.randint(1, 90))
            fake.append({
                "member_id": f"M{10000+i}",
                "signals": "Behavioral outlier",
                "score": np.random.randint(1,4),
                "suspicion_date": sd.date(),
                "deadline": sd.date() + timedelta(days=2),
                "status": np.random.choice(["Due","Overdue","Pending"]),
            })
        out["str_tbl"] = pd.DataFrame(fake)
    if out["ctr_tbl"].empty:
        now = datetime.now()
        fake = []
        for i in range(24):
            ws = (now - timedelta(days=np.random.randint(1, 35))).date()
            fake.append({
                "member_id": f"M{10000+i}",
                "week_start": ws,
                "week_end": ws + timedelta(days=6),
                "cash_sum": np.random.randint(1_900_000, 10_000_000),
                "txn_count": np.random.randint(5, 40),
                "deadline": ws + timedelta(days=6),
                "status": np.random.choice(["Due","Overdue"]),
            })
        out["ctr_tbl"] = pd.DataFrame(fake)
    return out
