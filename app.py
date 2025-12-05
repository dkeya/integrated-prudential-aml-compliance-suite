# app.py
import streamlit as st
import pandas as pd
from datetime import datetime

from core.session import init_session
from core.auth import AuthenticationSystem

# --------------------------------------------------
# Helper: clear session on logout
# --------------------------------------------------
def do_logout():
    for key in [
        "user",
        "tenant_id",
        "roles",
        "is_authenticated",
        "active_module",
        "prudential_page",
        "aml_page",
    ]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


# --------------------------------------------------
# LOGIN + MODULE SELECTION
# --------------------------------------------------
def render_login_screen():
    """Combined module selection + login form (shown when not authenticated)."""
    st.title("SACCO Compliance Portal")

    st.markdown("#### Choose a module then log in")

    # 1) Choose module first
    module_choice = st.radio(
        "Module",
        ("Prudential Compliance", "AML / CFT Compliance"),
        key="selected_module",
        horizontal=True,
    )

    # Safety guard – in rare cases Streamlit can give None on first render
    if module_choice is None:
        module_choice = st.session_state.get("selected_module", "")

    tenant_id = st.text_input(
        "Tenant ID", value=st.session_state.get("tenant_id", "")
    )
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # Make sure a module is actually selected
        if not module_choice:
            st.warning("Please select a module first.")
            return

        auth = AuthenticationSystem()
        result = auth.authenticate_user(username, password, tenant_id)

        if not result.success:
            st.error(result.message)
            return

        # Decide which module is being requested
        if "Prudential" in module_choice:
            requested_module = "PRUDENTIAL"
        else:
            requested_module = "AML"

        roles = st.session_state.get("roles") or []
        # Require matching role or ADMIN
        if requested_module not in roles and "ADMIN" not in roles:
            st.error(
                f"You are authenticated as '{username}', "
                f"but you do not have access to the {module_choice} module."
            )
            # undo auth flag
            st.session_state.is_authenticated = False
            return

        # Set active module and go to module layout
        st.session_state.active_module = requested_module
        st.success(f"Welcome {username}! Loading {module_choice} module...")
        st.rerun()


# --------------------------------------------------
# PRUDENTIAL MODULE – SIDEBAR + CONTENT
# --------------------------------------------------
def render_prudential_sidebar() -> str:
    """Sidebar navigation for the Prudential module (styled like the sample)."""
    side = st.sidebar

    # Default page
    if "prudential_page" not in st.session_state:
        st.session_state.prudential_page = "Overview"

    # Small helper so all nav buttons set the same state
    def nav_button(label: str, page_name: str, key: str):
        if side.button(label, key=key, use_container_width=True):
            st.session_state.prudential_page = page_name

    # Header card (SACCO Pro / suite / all SACCOs)
    with side.container():
        side.markdown(
            """
            <div style="
                padding: 0.8rem 0.9rem;
                border-radius: 0.8rem;
                background: linear-gradient(135deg, #1f4b99, #2156c5);
                color: white;
                font-size: 0.95rem;
            ">
                <div style="font-weight: 600; font-size: 1.0rem;">🏦 SACCO Pro</div>
                <div style="font-size: 0.85rem; opacity: 0.9;">
                    Prudential Compliance Suite
                </div>
                <div style="margin-top: 0.4rem; font-size: 0.8rem; opacity: 0.9;">
                    All SACCOs
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # User card
    side.markdown("")
    side.markdown(
        f"""
        **System Admin**  
        <span style="font-size: 0.8rem; opacity: 0.8;">
        {st.session_state.get('user', 'admin')} • Active
        </span>
        """,
        unsafe_allow_html=True,
    )

    side.markdown("---")
    side.markdown("#### Strategic Navigation")

    # Navigation sections – similar feel to screenshot
    with side.expander("📊 Dashboard Home", expanded=True):
        nav_button("Overview", "Overview", "prud_nav_overview")

    with side.expander("📈 Strategic Analytics"):
        nav_button("Strategic KPIs", "Strategic KPIs", "prud_nav_kpis")
        nav_button("Dividend Capacity", "Dividend Capacity", "prud_nav_dividends")

    with side.expander("⚠️ Risk Intelligence"):
        nav_button("Credit Risk (PAR)", "Credit Risk (PAR)", "prud_nav_par")
        nav_button("Concentration Risk", "Concentration Risk", "prud_nav_concentration")

    with side.expander("🏛️ Compliance Governance"):
        nav_button("Compliance Scorecard", "Compliance Scorecard", "prud_nav_scorecard")
        nav_button("Regulatory Timeline", "Regulatory Timeline", "prud_nav_timeline")

    with side.expander("⚙️ Operations Excellence"):
        nav_button("Provisioning & ECL", "Provisioning & ECL", "prud_nav_ecl")
        nav_button("Cybersecurity", "Cybersecurity", "prud_nav_cyber")

    with side.expander("👥 Member Value"):
        nav_button("Member Value", "Member Value", "prud_nav_member_value")
        nav_button("Policy Engine", "Policy Engine", "prud_nav_policy_engine")

    side.markdown("---")
    side.markdown("#### Quick Actions")

    qc1, qc2 = side.columns(2)
    with qc1:
        side.button("🔄 Refresh", key="prud_quick_refresh")
    with qc2:
        side.button("🚨 Alerts", key="prud_quick_alerts")

    qc3, qc4 = side.columns(2)
    with qc3:
        side.button("📑 Reports", key="prud_quick_reports")
    with qc4:
        side.button("📊 Analytics", key="prud_quick_analytics")

    side.markdown("---")
    side.caption(f"User: {st.session_state.get('user', '')}")
    if side.button("Logout", key="prud_logout_btn"):
        do_logout()

    return st.session_state.prudential_page


def render_prudential_content(page: str):
    """Render main area based on selected prudential page."""
    user = st.session_state.get("user", "System Admin")

    if page == "Overview":
        # Top welcome banner
        st.markdown(
            f"""
            <div style="
                padding: 1.5rem 1.8rem;
                border-radius: 1rem;
                background: linear-gradient(135deg, #1f4b99, #2156c5);
                color: white;
                margin-bottom: 1rem;
            ">
                <div style="font-size: 1.2rem; font-weight: 600;">
                    Welcome back, {user}! 👋
                </div>
                <div style="font-size: 0.9rem; opacity: 0.9; margin-top: 0.3rem;">
                    SACCO Prudential Compliance Suite • Real-time Regulatory Intelligence
                </div>
                <div style="font-size: 0.8rem; opacity: 0.85; margin-top: 0.4rem;">
                    Compliance Intelligence ▸ Dashboard ▸ All SACCOs ▸ {datetime.today().date()}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Green status ribbon (SASRA, Liquidity, PAR, etc.)
        st.markdown(
            """
            <div style="
                padding: 0.55rem 0.9rem;
                border-radius: 999px;
                background-color: #0f9960;
                color: white;
                font-size: 0.78rem;
                display: flex;
                gap: 0.7rem;
                flex-wrap: wrap;
                margin-bottom: 1.2rem;
            ">
                ✅ SASRA Returns: Compliant |
                💧 Liquidity Ratio: 128% [Target: 20%] |
                📉 PAR &lt; 30 days: 4.2% |
                🏦 Capital Adequacy: 18.5% |
                💸 Dividend Capacity: KES 125M |
                🧑‍💼 Employer Concentration: 32% [Limit: 25%]
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Strategic KPIs
        st.subheader("🎯 Strategic Compliance KPIs")
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("Capital Adequacy", "18.5%", "+0.8%")
        with k2:
            st.metric("Liquidity Ratio", "125%", "+5%")
        with k3:
            st.metric("PAR 30 Days", "3.2%", "-0.4%")
        with k4:
            st.metric("Compliance Score", "92%", "+2%")

        st.markdown("")

        # Quick Action Center (inside main area)
        st.subheader("⚡ Quick Action Center")
        qa1, qa2, qa3, qa4 = st.columns(4)
        with qa1:
            st.button("📑 SASRA Returns", use_container_width=True)
        with qa2:
            st.button("📉 Risk Dashboard", use_container_width=True)
        with qa3:
            st.button("💧 Liquidity ALM", use_container_width=True)
        with qa4:
            st.button("📊 Concentration", use_container_width=True)

        qa5, qa6, qa7, qa8 = st.columns(4)
        with qa5:
            st.button("🧮 Provisioning", use_container_width=True)
        with qa6:
            st.button("🛡️ Cybersecurity", use_container_width=True)
        with qa7:
            st.button("👥 Member Value", use_container_width=True)
        with qa8:
            st.button("⚙️ Policy Engine", use_container_width=True)

        st.markdown("")

        # Layout with Recent Alerts + Regulatory Timeline
        left_col, right_col = st.columns((1.1, 1))

        with left_col:
            st.subheader("🔔 Recent Compliance Alerts")
            alerts_df = pd.DataFrame(
                [
                    {
                        "Time": "2 hours ago",
                        "Alert": "PAR 30 approaching threshold (4.8%) – Review required",
                        "Priority": "Medium",
                    },
                    {
                        "Time": "4 hours ago",
                        "Alert": "Employer concentration at 32% (Limit: 25%) – Action needed",
                        "Priority": "High",
                    },
                    {
                        "Time": "1 day ago",
                        "Alert": "Cybersecurity scan completed – 3 vulnerabilities found",
                        "Priority": "High",
                    },
                    {
                        "Time": "2 days ago",
                        "Alert": "Monthly compliance reports generated – Ready for board review",
                        "Priority": "Info",
                    },
                ]
            )
            st.dataframe(alerts_df, use_container_width=True, hide_index=True)

        with right_col:
            st.subheader("📆 Regulatory Timeline")
            timeline_df = pd.DataFrame(
                [
                    {
                        "Deadline": "15 Nov 2025",
                        "Requirement": "SASRA Q3 Returns",
                        "Status": "Completed",
                        "Days Left": "-",
                    },
                    {
                        "Deadline": "30 Nov 2025",
                        "Requirement": "Internal Audit Report",
                        "Status": "In Progress",
                        "Days Left": 5,
                    },
                    {
                        "Deadline": "15 Dec 2025",
                        "Requirement": "Board Risk Committee",
                        "Status": "Scheduled",
                        "Days Left": 20,
                    },
                    {
                        "Deadline": "31 Dec 2025",
                        "Requirement": "Annual Compliance Report",
                        "Status": "Upcoming",
                        "Days Left": 45,
                    },
                ]
            )
            st.dataframe(timeline_df, use_container_width=True, hide_index=True)

        st.markdown("")
        st.subheader("📌 Strategic Initiatives")

        initiatives = {
            "Automated SASRA Reporting (Compliance Team)": 0.85,
            "Risk-Based Pricing Model (Risk Dept)": 0.65,
            "Member Value Enhancement (Marketing)": 0.55,
            "Cybersecurity Upgrade (IT Security)": 0.40,
        }

        for name, progress in initiatives.items():
            st.markdown(f"**{name}**")
            st.progress(progress)

    elif page in [
        "Strategic KPIs",
        "Dividend Capacity",
        "Credit Risk (PAR)",
        "Concentration Risk",
        "Compliance Scorecard",
        "Regulatory Timeline",
        "Provisioning & ECL",
        "Cybersecurity",
        "Member Value",
        "Policy Engine",
    ]:
        # Simple placeholders for now – we can wire real dashboards later
        st.title(f"📊 {page}")
        st.info(
            "This is a placeholder for the detailed prudential view: "
            f"**{page}**. We can plug in the specific dashboards, "
            "tables, and charts here from your older pages."
        )

    else:
        st.write("Unknown Prudential page.")


# --------------------------------------------------
# AML / CFT MODULE – SIDEBAR + CONTENT
# --------------------------------------------------
def render_aml_sidebar() -> str:
    """Sidebar navigation for the AML/CFT module (button-based expanders)."""
    side = st.sidebar
    side.title("🛡️ AML/CFT Compliance")

    if "aml_page" not in st.session_state:
        st.session_state.aml_page = "Overview"

    def nav_button(label: str, page_name: str, key: str):
        if side.button(label, key=key, use_container_width=True):
            st.session_state.aml_page = page_name

    with side.expander("📊 Dashboard", expanded=True):
        nav_button("Overview", "Overview", "aml_nav_overview")

    with side.expander("👥 Member Management"):
        nav_button("KYC Management", "KYC Management", "aml_nav_kyc")

    with side.expander("💳 Transaction Monitoring"):
        nav_button("Alerts & Cases", "Alerts & Cases", "aml_nav_alerts")

    with side.expander("📜 Regulatory Reporting"):
        nav_button("STR / CTR Reporting", "STR / CTR Reporting", "aml_nav_str")

    with side.expander("⚙️ Compliance Operations"):
        nav_button(
            "Sanctions & PEP Screening",
            "Sanctions & PEP Screening",
            "aml_nav_sanctions",
        )

    with side.expander("🎓 Training & Awareness"):
        nav_button("Training Records", "Training Records", "aml_nav_training")

    with side.expander("🧭 Governance & Audit"):
        nav_button("Audit Trail", "Audit Trail", "aml_nav_audit")

    side.markdown("---")
    side.caption(f"User: {st.session_state.get('user', '')}")
    if side.button("Logout", key="aml_logout_btn"):
        do_logout()

    return st.session_state.aml_page


def render_aml_content(page: str):
    """Render main area based on selected AML page."""
    if page == "Overview":
        st.title("🛡️ AML / CFT Overview")
        st.success(
            f"Welcome to the AML/CFT Compliance Module, "
            f"{st.session_state.get('user', '')}."
        )
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Members", "1,200")
        with col2:
            st.metric("Missing KYC", "0")
        with col3:
            st.metric("PEP (flagged)", "53")
        with col4:
            st.metric("High Risk", "98")

    elif page == "KYC Management":
        st.title("👤 KYC Management")
        st.subheader("KYC Completeness")
        st.write("Placeholder for completeness table, filters, and CSV export.")

    elif page == "Alerts & Cases":
        st.title("🚨 Transaction Monitoring – Alerts & Cases")
        st.write("Placeholder for alerts dashboard, filters, and case details.")

    elif page == "STR / CTR Reporting":
        st.title("📜 STR / CTR Reporting")
        st.write("Placeholder for reports, queues, and submission status.")

    elif page == "Sanctions & PEP Screening":
        st.title("🧾 Sanctions & PEP Screening")
        st.write("Placeholder for sanctions hits, reviews, and outcomes.")

    elif page == "Training Records":
        st.title("🎓 Training & Awareness")
        st.write("Placeholder for training records, attendance, and schedules.")

    elif page == "Audit Trail":
        st.title("🧭 Governance & Audit – Audit Trail")
        st.write("Placeholder for full AML audit logs and actions.")

    else:
        st.write("Unknown AML page.")


# --------------------------------------------------
# MAIN ENTRY
# --------------------------------------------------
def main():
    st.set_page_config(
        page_title="SACCO Compliance System",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session()

    if not st.session_state.get("is_authenticated", False):
        # Show combined module selection + login screen
        render_login_screen()
        return

    # Authenticated & module selected
    active_module = st.session_state.get("active_module")

    if active_module == "PRUDENTIAL":
        page = render_prudential_sidebar()
        render_prudential_content(page)

    elif active_module == "AML":
        page = render_aml_sidebar()
        render_aml_content(page)

    else:
        st.error("No active module selected. Please log out and log in again.")
        if st.button("Logout and reset"):
            do_logout()


if __name__ == "__main__":
    main()