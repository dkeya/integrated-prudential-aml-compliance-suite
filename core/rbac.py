# core/rbac.py
"""
Lightweight RBAC layer for the unified SACCO app.

This is a simplified version that:
- Reads role/username from st.session_state
- Provides basic role/permission helpers
- Gives us a single place to extend RBAC later.
"""

from typing import Optional, List
import streamlit as st


class RBACManager:
    """Minimal RBAC manager used by app.py and pages/*.py"""

    def __init__(self, config=None):
        self.config = config

    def get_user_role(self) -> Optional[str]:
        """Return current user's role from session state."""
        return st.session_state.get("role")

    def get_user_roles(self, username: str, tenant_id: Optional[str] = None) -> List[str]:
        """
        Return current user's roles.

        For now, we provide a simple default:
        - If roles already exist in session_state, return them.
        - Otherwise, assign a default role (e.g. 'admin') and store it.
        """
        existing_roles = st.session_state.get("user_roles")
        if existing_roles:
            return existing_roles

        # Simple default role until a real role map is implemented
        default_role = "admin"
        st.session_state["role"] = default_role
        st.session_state["user_roles"] = [default_role]
        return st.session_state["user_roles"]

    def get_username(self) -> Optional[str]:
        """Return current username from session state."""
        return st.session_state.get("username")

    def has_permission(self, permission: str) -> bool:
        """
        Check if current user has a given permission.

        For now we keep it simple and allow all authenticated users.
        You can later extend this to map roles -> permissions.
        """
        if not st.session_state.get("authenticated", False):
            return False
        # TODO: implement real permission mapping
        return True

    def check_page_access(self, page_id: str, role: Optional[str], config=None) -> bool:
        """
        Check if a user's role can access a given page.

        For now:
        - If not authenticated -> False
        - Otherwise -> True for all pages
        """
        if not st.session_state.get("authenticated", False):
            return False

        # Later you can use `config` to store allowed_roles per page.
        # e.g., config.pages[page_id].allowed_roles
        return True


# ----- Helper functions used in pages -----


def get_current_role() -> Optional[str]:
    """Convenience wrapper to get the current role."""
    return st.session_state.get("role")


def get_current_username() -> Optional[str]:
    """Convenience wrapper to get the current username."""
    return st.session_state.get("username")


def check_permission(permission: str) -> bool:
    """
    Functional helper to check a permission.

    Example usage in pages:
        if not check_permission("view_risk_dashboard"): ...
    """
    manager = RBACManager()
    return manager.has_permission(permission)
