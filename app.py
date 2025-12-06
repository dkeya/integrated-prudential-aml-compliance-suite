# app.py – SACCO Compliance Portal front door
import streamlit as st
import sys
import os
from datetime import datetime

# Make sure root is on the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import ConfigManager
from core.rbac import RBACManager
from core.audit import audit_logger
from core.auth import AuthenticationSystem
from core.sidebar import render_sidebar

# --- Global page config ---
st.set_page_config(
    page_title="SACCO Compliance Portal",
    page_icon="🛡️",
    layout="wide",
)

# --- Init session state (base flags) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "tenant_id" not in st.session_state:
    st.session_state.tenant_id = None
if "current_module" not in st.session_state:
    st.session_state.current_module = None
if "tenant" not in st.session_state:
    st.session_state.tenant = "Central SACCO"
if "user" not in st.session_state:
    st.session_state.user = None
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None

auth_system = AuthenticationSystem()
config_mgr = ConfigManager()
rbac_mgr = RBACManager()


# --- Sidebar visibility controller -----------------------------------------
def _set_sidebar_visibility():
    """
    Hide the Streamlit sidebar completely on the login screen,
    and show it again after successful authentication.
    """
    if st.session_state.get("authenticated", False):
        # Sidebar visible for logged-in users
        st.markdown(
            """
            <style>
            [data-testid="stSidebar"] {display: block;}
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        # Sidebar completely hidden on login screen
        st.markdown(
            """
            <style>
            [data-testid="stSidebar"] {display: none;}
            </style>
            """,
            unsafe_allow_html=True,
        )


_set_sidebar_visibility()


# --- Login UI ---------------------------------------------------------------
def show_login():
    st.title("🛡️ SACCO Compliance Portal")
    st.write("### Choose a module then log in")

    col1, col2 = st.columns([2, 1])

    with col1:
        module = st.radio(
            "Module",
            ["Prudential Compliance", "AML / CFT Compliance"],
            horizontal=True,
        )

        tenant_id = st.text_input("Tenant ID")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        login_btn = st.button("Log in", type="primary")

        if login_btn:
            if not tenant_id or not username or not password:
                st.error("Please fill in Tenant ID, Username, and Password.")
                return

            # 🔐 Authenticate (adapt to your real auth backend)
            is_valid = auth_system.authenticate_user(
                username=username,
                password=password,
                tenant_id=tenant_id,
            )

            if is_valid:
                # Core auth flags
                st.session_state.authenticated = True
                st.session_state.current_user = username
                st.session_state.username = username
                st.session_state.user = username
                st.session_state.tenant_id = tenant_id
                st.session_state.tenant = tenant_id or "Central SACCO"
                st.session_state.current_module = (
                    "prudential" if module == "Prudential Compliance" else "aml_cft"
                )

                # Simple default role for now (can wire to RBAC/DB later)
                st.session_state.role = "admin"

                # Audit successful login (best effort)
                try:
                    audit_logger.log_action(
                        user=username,
                        role=st.session_state.role,
                        action="login_success",
                        object_type="portal",
                        object_id=f"{st.session_state.current_module}_portal",
                        extra={
                            "tenant_id": tenant_id,
                            "timestamp": datetime.now().isoformat(),
                        },
                    )
                except Exception:
                    pass

                st.rerun()
            else:
                # Audit failed login (best effort)
                try:
                    audit_logger.log_security_event(
                        event_type="login_failure",
                        message=f"Failed login for {username} / tenant {tenant_id}",
                        severity="medium",
                        tenant_id=tenant_id,
                        user_id=username,
                    )
                except Exception:
                    pass

                st.error("Invalid credentials. Please try again.")

    with col2:
        st.info(
            "ℹ️ Use your assigned **Tenant ID**, **Username**, and **Password**.\n\n"
            "- *Prudential Compliance* → SASRA ratios, vintages, ECL, provisioning.\n"
            "- *AML / CFT Compliance* → transaction monitoring, risk scoring, STR/CTR."
        )


# --- Main app entry ---------------------------------------------------------
if not st.session_state.authenticated:
    # Login screen ONLY, with sidebar hidden
    show_login()
    st.stop()

# If logged in, make sure sidebar is visible (CSS override on rerun)
_set_sidebar_visibility()

# Render unified sidebar and hand over to multipage nav
render_sidebar()

st.write(f"👋 Welcome **{st.session_state.current_user}**")
st.write(
    f"Tenant: `{st.session_state.tenant_id}` | "
    f"Module: `{st.session_state.current_module}` | "
    f"Role: `{st.session_state.role}`"
)

st.success("You are logged in. Use the sidebar to navigate to your module dashboards.")
