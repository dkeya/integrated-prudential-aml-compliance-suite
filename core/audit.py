# core/audit.py
"""
Unified audit logger for the SACCO prudential suite.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json
import os


class AuditLogger:
    """
    Simple JSON-lines based audit logger.

    - Writes to logs/app.log by default
    - Use log_action / log_data_access / log_login / log_logout
    """

    def __init__(self, log_path: Optional[str] = None):
        project_root = Path(__file__).parent.parent
        default_dir = project_root / "logs"
        default_dir.mkdir(parents=True, exist_ok=True)

        self.log_file = Path(log_path) if log_path else (default_dir / "app.log")

    def _write(self, record: Dict[str, Any]) -> None:
        """Internal: append one record as JSON to the audit log."""
        record.setdefault("timestamp", datetime.utcnow().isoformat())
        try:
            with self.log_file.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception:
            # Don't crash the app because of audit logging
            pass

    def log_action(
        self,
        user: str,
        role: str,
        action: str,
        object_type: str,
        object_id: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._write(
            {
                "type": "action",
                "user": user,
                "role": role,
                "action": action,
                "object_type": object_type,
                "object_id": object_id,
                "details": details or {},
            }
        )

    def log_data_access(
        self,
        user: str,
        role: str,
        resource: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._write(
            {
                "type": "data_access",
                "user": user,
                "role": role,
                "resource": resource,
                "details": details or {},
            }
        )

    def log_login(self, username: str, role: str) -> None:
        self._write(
            {
                "type": "login",
                "user": username,
                "role": role,
            }
        )

    def log_logout(self, username: str, role: str) -> None:
        self._write(
            {
                "type": "logout",
                "user": username,
                "role": role,
            }
        )


# ✅ Global shared instance for the whole app
audit_logger = AuditLogger()
