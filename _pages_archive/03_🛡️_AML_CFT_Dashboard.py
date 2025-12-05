import streamlit as st
from core.session import init_session
from core.security import require_auth_and_module


@require_auth_and_module(required_roles=["AML", "ADMIN"])
def main():
    """AML / CFT Risk & Compliance Dashboard"""

    init_session()

    st.title("🛡️ AML / CFT Compliance Overview")
    st.markdown("---")

    user = st.session_state.get("user", "aml_officer")
    st.success(f"Welcome to the AML/CFT Module, {user}!")

    # --- Key metrics ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Flagged Transactions (Mtd)", "42", "+5")
    with col2:
        st.metric("High-Risk Members", "18", "+2")
    with col3:
        st.metric("Pending STRs", "3", "0")
    with col4:
        st.metric("Sanctions Hits (24h)", "1", "0")

    # --- Recent alerts ---
    st.subheader("Recent AML/CFT Alerts")
    alerts_data = [
        {"alert": "Unusual Cash Deposit Pattern", "severity": "High", "date": "2024-01-15"},
        {"alert": "High-Risk Country Exposure", "severity": "Medium", "date": "2024-01-14"},
        {"alert": "Delayed KYC Refresh", "severity": "Low", "date": "2024-01-13"},
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
        st.button("Go to Transaction Monitoring")  # to wire later
    with c2:
        st.button("View STR / CTR Register")       # to wire later
    with c3:
        st.button("Run Sanctions Screening")       # to wire later


if __name__ == "__main__":
    main()