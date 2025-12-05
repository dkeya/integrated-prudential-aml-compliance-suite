# pages/00_🔐_login.py
import streamlit as st
from core.session import init_session
from core.auth import AuthenticationSystem


def render_module_selector():
    st.subheader("Step 1: Select Module")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Prudential Compliance")
        st.write(
            """
            - Credit risk & PAR monitoring  
            - Liquidity & ALM  
            - Capital adequacy & employer limits  
            - SASRA prudential returns
            """
        )
        if st.button("Use Prudential Module", key="btn_prudential"):
            st.session_state.selected_module = "prudential"

    with col2:
        st.markdown("### 🛡️ AML / CFT Compliance")
        st.write(
            """
            - Transaction monitoring & alerts  
            - STR / CTR registers  
            - High-risk members & sanctions hits  
            - KYC & risk profiling
            """
        )
        if st.button("Use AML / CFT Module", key="btn_aml"):
            st.session_state.selected_module = "aml"


def render_login_form():
    module = st.session_state.get("selected_module")

    if module is None:
        st.info("Select a module above to continue to login.")
        return

    module_label = "Prudential Compliance" if module == "prudential" else "AML / CFT Compliance"

    st.markdown("---")
    st.subheader(f"Step 2: 🔐 Login – {module_label}")

    tenant_id = st.text_input("Tenant ID", value=st.session_state.get("tenant_id", ""))
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", type="primary"):
        auth = AuthenticationSystem()
        result = auth.authenticate_user(username, password, tenant_id)

        if result.success:
            st.success(result.message)

            # Redirect to module-specific dashboard
            if module == "prudential":
                st.switch_page("pages/02_📊_Prudential_Dashboard.py")
            else:
                st.switch_page("pages/03_🛡️_AML_CFT_Dashboard.py")
        else:
            st.error(result.message)


def main():
    init_session()

    st.title("🔐 SACCO Compliance Access Portal")
    st.caption("Select a module, then log in to access your dashboards.")
    st.markdown("---")

    render_module_selector()
    render_login_form()


if __name__ == "__main__":
    main()