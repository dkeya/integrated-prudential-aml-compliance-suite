# sacco_core/security.py
from __future__ import annotations
import functools
import streamlit as st
from typing import Callable, Iterable, Optional, Set

# Very light RBAC wired to st.session_state
# - st.session_state["user_id"] (str)
# - st.session_state["user_role"] (str) e.g., "AML_Officer", "Analyst", "MLRO", "Admin"

# Default role permissions (extend as needed)
ROLE_PERMS = {
    "Viewer": {
        "view_dashboard", "view_risk", "view_training", "view_reporting",
        "view_transactions", "view_ops", "view_gov"
    },
    "Analyst": {
        "view_dashboard", "view_risk", "view_training", "view_reporting",
        "view_transactions", "view_ops", "view_gov",
        "export_data"
    },
    "AML_Officer": {
        "view_dashboard", "view_risk", "view_training", "view_reporting",
        "view_transactions", "view_ops", "view_gov",
        "export_data", "file_str", "file_ctr", "change_config"
    },
    "MLRO": {
        "view_dashboard", "view_risk", "view_training", "view_reporting",
        "view_transactions", "view_ops", "view_gov",
        "export_data", "file_str", "file_ctr", "change_config", "approve_case"
    },
    "Admin": {
        "view_dashboard", "view_risk", "view_training", "view_reporting",
        "view_transactions", "view_ops", "view_gov",
        "export_data", "file_str", "file_ctr", "change_config",
        "approve_case", "manage_users"
    },
}

def current_user_id() -> str:
    return str(st.session_state.get("user_id", "demo_user"))

def current_role() -> str:
    return str(st.session_state.get("user_role", "AML_Officer"))

def has_perm(perm: str) -> bool:
    role = current_role()
    allowed: Set[str] = ROLE_PERMS.get(role, set())
    return perm in allowed

def require_perm(perm: str):
    """Decorator for button actions and API hooks."""
    def decorator(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if not has_perm(perm):
                st.warning(f"Insufficient permission: `{perm}` (role: {current_role()})")
                return None
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def guard_ui(perm: str, body: Callable[[], None], fallback_msg: Optional[str] = None):
    """Render `body()` only if perm is granted."""
    if has_perm(perm):
        body()
    else:
        st.info(fallback_msg or f"Your role (**{current_role()}**) cannot access this section.")
