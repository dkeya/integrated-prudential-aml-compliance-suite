"""
Authentication system placeholder for SACCO Compliance System.

⚠️ IMPORTANT:
Replace this with your real `AuthenticationSystem` logic later.
For now, we use in-memory dummy users so you can develop and test pages.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import logging
import streamlit as st

# We still import the shared audit logger instance
from .audit import audit_logger

logger = logging.getLogger(__name__)


@dataclass
class AuthResult:
    success: bool
    message: str = ""
    roles: Optional[List[str]] = None


def _safe_audit_log(action: str, details: Optional[Dict[str, Any]] = None, user: str = "UNKNOWN"):
    """
    Safely log auth events using whatever API audit_logger actually exposes.
    Falls back to standard logging if nothing matches.
    """
    details = details or {}

    try:
        # 1️⃣ Preferred: log_event(user=..., action=..., module=..., details=...)
        if hasattr(audit_logger, "log_event"):
            audit_logger.log_event(
                user=user,
                action=action,
                module="auth",
                details=details,
            )
            return

        # 2️⃣ Alternative name: log_security_event(event_type=..., description=..., severity=..., tenant_id=?, user_id=?)
        if hasattr(audit_logger, "log_security_event"):
            # Map our simple call into a generic security event
            audit_logger.log_security_event(
                event_type=action,
                description=f"Auth event: {action} | details={details}",
                severity="low",
                tenant_id=details.get("tenant_id", "UNKNOWN"),
                user_id=user,
            )
            return

        # 3️⃣ Generic method: log(...)
        if hasattr(audit_logger, "log"):
            audit_logger.log(
                level="INFO",
                message=f"[AUTH] {action} | user={user} | details={details}",
            )
            return

    except Exception as e:
        # If the audit logger itself misbehaves, just fall back quietly
        logger.warning(f"Auth audit logging failed: {e}")

    # Final fallback: normal Python logger
    logger.info(f"[AUTH] {action} | user={user} | details={details}")


class AuthenticationSystem:
    """
    Simplified placeholder auth system.

    Dummy users:
      - admin / admin
          roles: ADMIN, PRUDENTIAL, AML
      - prudential_officer / prud123
          roles: PRUDENTIAL
      - aml_officer / aml123
          roles: AML
    """

    def __init__(self):
        # Later, replace this with DB-backed users (SQLite/Postgres, etc.)
        self._dummy_users = {
            "admin": {
                "password": "admin",
                "roles": ["ADMIN", "PRUDENTIAL", "AML"],
            },
            "prudential_officer": {
                "password": "prud123",
                "roles": ["PRUDENTIAL"],
            },
            "aml_officer": {
                "password": "aml123",
                "roles": ["AML"],
            },
        }

    def authenticate_user(self, username: str, password: str, tenant_id: str) -> AuthResult:
        """
        Basic username/password check against in-memory dummy users.

        Also:
          - sets Streamlit session_state keys
          - logs success/failure via audit logger (safely)
        """
        user_record = self._dummy_users.get(username)

        if not user_record or user_record["password"] != password:
            # ❌ Log failed attempt (safe)
            _safe_audit_log(
                action="login_failed",
                user=username or "UNKNOWN",
                details={
                    "tenant_id": tenant_id,
                    "reason": "invalid_credentials",
                },
            )
            return AuthResult(False, "Invalid username or password")

        # ✅ Successful login: set session state
        st.session_state.user = username
        st.session_state.tenant_id = tenant_id
        st.session_state.roles = user_record["roles"]

        # Keep BOTH keys for compatibility with all pages
        st.session_state.is_authenticated = True
        st.session_state.authenticated = True

        # ✅ Log success (safe)
        _safe_audit_log(
            action="login_success",
            user=username,
            details={
                "tenant_id": tenant_id,
                "roles": user_record["roles"],
            },
        )

        return AuthResult(True, "Login successful", roles=user_record["roles"])

    def logout(self):
        """
        Optional helper to clear auth-related session state.
        """
        username = st.session_state.get("user", "UNKNOWN")
        tenant_id = st.session_state.get("tenant_id", "UNKNOWN")

        # Log logout event (safe)
        _safe_audit_log(
            action="logout",
            user=username,
            details={"tenant_id": tenant_id},
        )

        # Clear session flags
        for key in ["user", "tenant_id", "roles", "is_authenticated", "authenticated"]:
            if key in st.session_state:
                del st.session_state[key]
