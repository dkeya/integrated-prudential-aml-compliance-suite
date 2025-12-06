"""
Unified sidebar renderer for SACCO Pro.

- Supports two modules:
    * prudential  -> Prudential Compliance Suite
    * aml_cft     -> AML / CFT Compliance Suite
- Used by app.py and all pages via render_sidebar().
"""

from datetime import datetime
from typing import Dict, List

import streamlit as st


# -------------------------------------------------------------------
# PAGE CATEGORY DEFINITIONS
# -------------------------------------------------------------------
def get_page_categories(current_module: str = "prudential") -> Dict[str, List[dict]]:
    """
    Central definition of strategic page categories and their modules,
    depending on the active module in session_state.
    """

    if current_module == "aml_cft":
        # 🔐 AML / CFT module navigation
        return {
            "🛡️ AML Dashboard": [
                {
                    "name": "AML Overview",
                    "module": "1_🏠_AML_Dashboard.py",
                    "icon": "🛡️",
                },
            ],
            "👤 KYC & Onboarding": [
                {
                    "name": "KYC Management",
                    "module": "2_👤_KYC_Management.py",
                    "icon": "👤",
                },
            ],
            "💳 Transaction Monitoring": [
                {
                    "name": "Transaction Monitoring",
                    "module": "3_💳_Transaction_Monitoring.py",
                    "icon": "💳",
                },
                {
                    "name": "AML Alerts",
                    "module": "7_🚨_AML_Alerts.py",
                    "icon": "🚨",
                },
            ],
            "📋 STR / CTR & Reporting": [
                {
                    "name": "STR / CTR Reporting",
                    "module": "4_📋_STR_CTR_Reporting.py",
                    "icon": "📋",
                },
                {
                    "name": "FRC Integration",
                    "module": "12_🔗_FRC_Integration.py",
                    "icon": "🔗",
                },
            ],
            "🎯 AML Risk & Governance": [
                {
                    "name": "Risk Assessment",
                    "module": "5_🎯_Risk_Assessment.py",
                    "icon": "🎯",
                },
                {
                    "name": "PEP Screening",
                    "module": "6_👑_PEP_Screening.py",
                    "icon": "👑",
                },
                {
                    "name": "Sanctions Screening",
                    "module": "9_🛡️_Sanctions_Screening.py",
                    "icon": "🛡️",
                },
                {
                    "name": "MLRO Portal",
                    "module": "8_🏛️_MLRO_Portal.py",
                    "icon": "🏛️",
                },
                {
                    "name": "Compliance Training",
                    "module": "10_📚_Compliance_Training.py",
                    "icon": "📚",
                },
                {
                    "name": "Audit Reports",
                    "module": "11_📊_Audit_Reports.py",
                    "icon": "📊",
                },
                {
                    "name": "Anomaly Detection",
                    "module": "13_🤖_Anomaly_Detection.py",
                    "icon": "🤖",
                },
            ],
        }

    # 📊 Prudential module navigation (default)
    return {
        "📊 Strategic Analytics": [
            {
                "name": "Overview Dashboard",
                "module": "01_Prudential_Overview.py",
                "icon": "📊",
            },
            {
                "name": "Liquidity ALM",
                "module": "03_Liquidity_ALM.py",
                "icon": "📈",
            },
            {
                "name": "Pricing Economics",
                "module": "04_Pricing_Economics.py",
                "icon": "💰",
            },
            {
                "name": "Dividend Capacity",
                "module": "03A_Dividend_Capacity.py",
                "icon": "💧",
            },
        ],
        "🎯 Risk Intelligence": [
            {
                "name": "Credit Risk PAR",
                "module": "02_Credit_Risk_PAR.py",
                "icon": "🎯",
            },
            {
                "name": "Vintages & Roll Rates",
                "module": "02A_Vintages_RollRates.py",
                "icon": "📉",
            },
            {
                "name": "Concentration Risk",
                "module": "06_Concentration_Risk.py",
                "icon": "⚖️",
            },
            {
                "name": "Employer Limits & Alerts",
                "module": "06A_Employer_Limits_Alerts.py",
                "icon": "🚨",
            },
            {
                "name": "Provisioning & Writeoff",
                "module": "09_Provisioning_Writeoff.py",
                "icon": "📊",
            },
            {
                "name": "ALM Stress Tests",
                "module": "03B_ALM_Stress_Tests.py",
                "icon": "🌀",
            },
        ],
        "⚖️ Compliance Governance": [
            {
                "name": "Governance Compliance",
                "module": "05_Governance_Compliance.py",
                "icon": "⚖️",
            },
            {
                "name": "SASRA Returns",
                "module": "05A_SASRA_Returns.py",
                "icon": "📋",
            },
            {
                "name": "Data Quality MIS",
                "module": "07_Data_Quality_MIS.py",
                "icon": "📊",
            },
            {
                "name": "Data Quality Scans",
                "module": "07A_Data_Quality_Scans.py",
                "icon": "🔍",
            },
            {
                "name": "Policy Engine Monitor",
                "module": "12_Policy_Engine_Monitor.py",
                "icon": "⚙️",
            },
        ],
        "🚀 Operations Excellence": [
            {
                "name": "Operations TAT",
                "module": "08_Operations_TAT.py",
                "icon": "⏱️",
            },
            {
                "name": "Collections Recovery",
                "module": "13_Collections_Recovery.py",
                "icon": "📞",
            },
            {
                "name": "Collections Funnel SMS",
                "module": "13A_Collections_Funnel_SMS.py",
                "icon": "📱",
            },
            {
                "name": "Cybersecurity & BCP",
                "module": "10_Cybersecurity_BCP.py",
                "icon": "🔒",
            },
        ],
        "💼 Member Value": [
            {
                "name": "Member Value",
                "module": "11_Member_Value.py",
                "icon": "👥",
            },
            {
                "name": "Member Value & Churn",
                "module": "11A_Member_Value_Churn.py",
                "icon": "📈",
            },
            {
                "name": "AGM Dividend Paper",
                "module": "14_AGM_Dividend_Paper.py",
                "icon": "📄",
            },
        ],
    }


# -------------------------------------------------------------------
# SIDEBAR STATE INITIALISATION
# -------------------------------------------------------------------
def _init_sidebar_state(current_module: str):
    """
    Ensure sidebar_collapsed dict exists in session_state so
    expanders remember their state across pages.
    """
    if "sidebar_collapsed" not in st.session_state:
        st.session_state.sidebar_collapsed = {}

    for category in get_page_categories(current_module).keys():
        if category not in st.session_state.sidebar_collapsed:
            # default collapsed = True (click to open)
            st.session_state.sidebar_collapsed[category] = True


# -------------------------------------------------------------------
# MAIN RENDER FUNCTION
# -------------------------------------------------------------------
def render_sidebar():
    """
    Enterprise sidebar with:
    - Header (tenant + module)
    - User card
    - Strategic navigation (prudential or AML) using st.switch_page
    - Quick actions
    - System status
    - Logout
    """
    current_module = st.session_state.get("current_module", "prudential")
    _init_sidebar_state(current_module)

    with st.sidebar:
        tenant = st.session_state.get("tenant", "Central SACCO")
        user = st.session_state.get("user", "Guest User")
        role = st.session_state.get("role", "Viewer")
        username = st.session_state.get("username", "guest")

        # Module-specific subtitle and home page
        if current_module == "aml_cft":
            suite_subtitle = "AML / CFT Compliance Suite"
            home_page = "pages/1_🏠_AML_Dashboard.py"
            reports_page = "pages/4_📋_STR_CTR_Reporting.py"
            alerts_page = "pages/7_🚨_AML_Alerts.py"
            analytics_page = "pages/1_🏠_AML_Dashboard.py"
        else:
            suite_subtitle = "Prudential Compliance Suite"
            home_page = "pages/01_Prudential_Overview.py"
            reports_page = "pages/05A_SASRA_Returns.py"
            alerts_page = "pages/06A_Employer_Limits_Alerts.py"
            analytics_page = "pages/01_Prudential_Overview.py"

        # Sidebar header
        st.markdown(
            f"""
            <div class="sidebar-header">
                <h3>🏛️ SACCO Pro</h3>
                <p style="font-size: 0.9rem; opacity: 0.9;">{suite_subtitle}</p>
                <p style="font-size: 0.8rem; margin-top: 5px;">
                    <strong>{tenant}</strong>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # User card
        st.markdown(
            f"""
            <div class="user-card">
                <strong style="color: #1e3c72;">{user}</strong><br>
                <small style="color: #64748b;">
                    {role}<br>
                    {datetime.now().strftime('%H:%M')} • Active
                </small>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown("### 🧭 Strategic Navigation")

        # Dashboard home (module-specific)
        if st.button(
            "🏠 Dashboard Home",
            use_container_width=True,
            key="nav_home_sidebar",
            help="Go to main dashboard for this module",
        ):
            st.switch_page(home_page)

        st.markdown("---")

        # Strategic categories and pages
        page_categories = get_page_categories(current_module)

        for category_name, pages in page_categories.items():
            # Safety: ensure in dict
            if category_name not in st.session_state.sidebar_collapsed:
                st.session_state.sidebar_collapsed[category_name] = True

            is_collapsed = st.session_state.sidebar_collapsed.get(category_name, True)

            with st.expander(category_name, expanded=not is_collapsed):
                for page in pages:
                    if st.button(
                        f"{page['icon']} {page['name']}",
                        key=f"nav_{page['module']}",
                        use_container_width=True,
                        help=f"Go to {page['name']}",
                    ):
                        st.switch_page(f"pages/{page['module']}")

        st.markdown("---")
        st.markdown("### 🚀 Quick Actions")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Refresh", use_container_width=True, key="sb_refresh"):
                st.rerun()
            if st.button("📊 Reports", use_container_width=True, key="sb_reports"):
                st.switch_page(reports_page)

        with col2:
            if st.button("🔔 Alerts", use_container_width=True, key="sb_alerts"):
                st.switch_page(alerts_page)
            if st.button("📈 Analytics", use_container_width=True, key="sb_analytics"):
                st.switch_page(analytics_page)

        st.markdown("---")
        st.markdown("### 🟢 System Status")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("🔵 **Live**")
        with c2:
            st.markdown("🟢 **Secure**")
        with c3:
            st.markdown("🟡 **Synced**")

        st.caption(f"Session: {username}")
        last_activity = st.session_state.get("last_activity")
        if last_activity is not None:
            try:
                ts = (
                    last_activity.strftime("%H:%M")
                    if hasattr(last_activity, "strftime")
                    else str(last_activity)
                )
            except Exception:
                ts = str(last_activity)
            st.caption(f"Last activity: {ts}")

        # Logout
        if st.button(
            "🚪 Logout",
            use_container_width=True,
            key="sb_logout",
        ):
            try:
                from core.audit import audit_logger

                audit_logger.log_logout(username, role)
            except Exception:
                pass

            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.role = None
            st.session_state.username = None
            st.session_state.current_page = "dashboard"
            st.success("Logged out successfully")
            st.rerun()
