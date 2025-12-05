"""
Security utilities and decorators.
"""

import functools
import streamlit as st

def require_auth_and_module(required_roles: list[str] | None = None):
    """
    Decorator for Streamlit pages that require authentication.
    Optionally restricts access to users with any of the required_roles.
    """
    required_roles = required_roles or []

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not st.session_state.get("is_authenticated", False):
                st.warning("Please log in to access this page.")
                st.stop()

            if required_roles:
                user_roles = st.session_state.get("roles", [])
                if not any(r in user_roles for r in required_roles):
                    st.error("You do not have permission to view this page.")
                    st.stop()

            return func(*args, **kwargs)
        return wrapper
    return decorator
