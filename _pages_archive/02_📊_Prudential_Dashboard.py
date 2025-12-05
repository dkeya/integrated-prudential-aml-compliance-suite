import streamlit as st
from core.session import init_session
from core.security import require_auth_and_module


@require_auth_and_module(required_roles=["PRUDENTIAL", "ADMIN"])
def main():
    """Prudential Compliance Overview Dashboard"""

    init_session()

    st.title("📊 Prudential Compliance Overview")
    st.markdown("---")

    user = st.session_state.get("user", "prudential_officer")
    st.success(f"Welcome to the Prudential Compliance Module, {user}!")

    # --- Key metrics in columns ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Members", "100", "0")

    with col2:
        st.metric("PAR Ratio", "3.2%", "-0.1%")

    with col3:
        st.metric("Liquidity Ratio", "25.8%", "+1.2%")

    with col4:
        st.metric("Capital Adequacy", "12.3%", "+0.5%")

    # --- Recent alerts ---
    st.subheader("Recent Compliance Alerts")

    alerts_data = [
        {"alert": "Employer Limit Breach", "severity": "High", "date": "2024-01-15"},
        {"alert": "Data Quality Issue", "severity": "Medium", "date": "2024-01-14"},
        {"alert": "SASRA Returns Due", "severity": "Low", "date": "2024-01-20"},
    ]

    for alert in alerts_data:
        if alert["severity"] == "High":
            st.error(f"🚨 {alert['alert']} - {alert['date']}")
        elif alert["severity"] == "Medium":
            st.warning(f"⚠️ {alert['alert']} - {alert['date']}")
        else:
            st.info(f"ℹ️ {alert['alert']} - {alert['date']}")

    # --- Quick actions ---
    st.subheader("Quick Actions")
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("View Credit Risk Dashboard"):
            # we'll add this page later
            st.switch_page("pages/02_Credit_Risk_PAR.py")

    with c2:
        if st.button("Check Liquidity ALM"):
            # we'll add this page later
            st.switch_page("pages/03_Liquidity_ALM.py")

    with c3:
        if st.button("Generate SASRA Returns"):
        # we'll add this page later
            st.switch_page("pages/05A_SASRA_Returns.py")


if __name__ == "__main__":
    main()