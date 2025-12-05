"""
Authentication system placeholder for SACCO Compliance System.

⚠️ IMPORTANT:
Replace this with your real `AuthenticationSystem` logic later.
For now, we use in-memory dummy users so you can develop and test pages.
"""

from dataclasses import dataclass
from typing import List, Optional
import streamlit as st
from .audit import log_event


@dataclass
class AuthResult:
    success: bool
    message: str = ""
    roles: Optional[List[str]] = None


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
        user_record = self._dummy_users.get(username)

        if not user_record or user_record["password"] != password:
            # Log failed attempt
            log_event(
                user=username or "UNKNOWN",
                action="login_failed",
                module="auth",
                details={"tenant_id": tenant_id},
            )
            return AuthResult(False, "Invalid username or password")

        # Successful login: set session state
        st.session_state.user = username
        st.session_state.tenant_id = tenant_id
        st.session_state.roles = user_record["roles"]
        st.session_state.is_authenticated = True

        # Log success
        log_event(
            user=username,
            action="login_success",
            module="auth",
            details={
                "tenant_id": tenant_id,
                "roles": user_record["roles"],
            },
        )

        return AuthResult(True, "Login successful", roles=user_record["roles"])
