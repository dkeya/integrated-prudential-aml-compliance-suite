# sacco_core/alerts/emailer.py
from __future__ import annotations
from typing import Iterable, Optional, Tuple
import smtplib
from email.message import EmailMessage
from datetime import date
import pandas as pd

from sacco_core.config import get_config
from sacco_core.aml.reporting import str_filing_table, ctr_filing_table

def _smtp() -> Tuple[Optional[str], int, Optional[str], Optional[str], Optional[str], bool]:
    cfg = get_config()
    em = getattr(cfg, "email", None)
    if not em:
        return None, 0, None, None, None, False
    return (
        getattr(em, "smtp_host", None),
        int(getattr(em, "smtp_port", 587)),
        getattr(em, "smtp_user", None),
        getattr(em, "smtp_password", None),
        getattr(em, "from_address", None),
        bool(getattr(em, "use_tls", True)),
    )

def send_email(to: Iterable[str], subject: str, body: str) -> bool:
    host, port, user, pwd, from_addr, use_tls = _smtp()
    if not host or not from_addr:
        return False
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = ", ".join(list(to))
    msg.set_content(body)

    with smtplib.SMTP(host, port, timeout=20) as server:
        if use_tls:
            server.starttls()
        if user and pwd:
            server.login(user, pwd)
        server.send_message(msg)
    return True

def format_digest(df: pd.DataFrame, header: str) -> str:
    if df is None or df.empty:
        return f"{header}\n  (none)\n"
    preview = df.head(15)
    lines = [header]
    lines.append(preview.to_csv(index=False))
    if len(df) > 15:
        lines.append(f"... and {len(df)-15} more")
    return "\n".join(lines)

def send_deadline_digest(recipients: Iterable[str],
                         where_sql: str = "",
                         params: Tuple = ()) -> bool:
    """Send a single digest email for STR/CTR deadlines (based on filters)."""
    str_tbl = str_filing_table(where_sql=where_sql, params=params)
    ctr_tbl = ctr_filing_table(where_sql=where_sql, params=params)

    body = []
    body.append(f"Compliance Deadlines Digest — {date.today().isoformat()}")
    body.append("")
    body.append(format_digest(str_tbl, "STR Filing Table"))
    body.append("")
    body.append(format_digest(ctr_tbl, "CTR Filing Table"))
    body_text = "\n".join(body)

    subject = f"[AML] Deadlines Digest — {date.today().isoformat()}"
    return send_email(recipients, subject, body_text)
