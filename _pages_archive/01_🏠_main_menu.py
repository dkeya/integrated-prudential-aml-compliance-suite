import streamlit as st
from core.session import init_session


def main():
    init_session()

    st.title("🏠 Main Menu")

    if not st.session_state.get("is_authenticated", False):
        st.warning("Please log in first from the Login page.")
        st.stop()

    user = st.session_state.get("user", "")
    st.write(f"Welcome, **{user}**.")
    st.markdown("Select a module below or from the sidebar.")

    st.markdown("---")

    # Two big module cards
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Prudential Compliance")
        st.write(
            """
            - Credit risk & PAR monitoring  
            - Liquidity & ALM views  
            - Capital adequacy & employer limits  
            - SASRA prudential returns
            """
        )
        if st.button("Open Prudential Module"):
            st.switch_page("pages/02_📊_Prudential_Dashboard.py")

    with col2:
        st.subheader("🛡️ AML / CFT Compliance")
        st.write(
            """
            - Transaction monitoring & alerts  
            - High-risk members & sanctions hits  
            - STR / CTR workflow and registers  
            - KYC & risk profiling views
            """
        )
        if st.button("Open AML / CFT Module"):
            st.switch_page("pages/03_🛡️_AML_CFT_Dashboard.py")

    st.markdown("---")
    st.info("You can also use the left sidebar to switch between modules at any time.")


if __name__ == "__main__":
    main()
