# core/session.py
import streamlit as st


def init_session():
    """Initialize Streamlit session state with default keys."""
    if "user" not in st.session_state:
        st.session_state.user = None

    if "tenant_id" not in st.session_state:
        st.session_state.tenant_id = None

    if "roles" not in st.session_state:
        st.session_state.roles = []

    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False

    # Which module the user wants to access: "prudential" or "aml"
    if "selected_module" not in st.session_state:
        st.session_state.selected_module = None
