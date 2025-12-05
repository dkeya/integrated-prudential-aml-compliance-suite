# sacco_core/sidebar.py
import streamlit as st
from datetime import datetime
from .audit import AuditLogger
from .ui import hide_default_streamlit_elements, apply_custom_styling


def get_page_categories():
    """
    Strategic page categories aligned with the enterprise design in app.py.
    MUST stay in sync with app.py navigation.
    """
    return {
        "📊 Strategic Analytics": [
            {"name": "📊 Overview Dashboard", "module": "01_Overview.py", "icon": "📊"},
            {"name": "📈 Liquidity ALM", "module": "03_Liquidity_ALM.py", "icon": "📈"},
            {"name": "💰 Pricing Economics", "module": "04_Pricing_Economics.py", "icon": "💰"},
            {"name": "💧 Dividend Capacity", "module": "03A_Dividend_Capacity.py", "icon": "💧"},
        ],
        "🎯 Risk Intelligence": [
            {"name": "🎯 Credit Risk PAR", "module": "02_Credit_Risk_PAR.py", "icon": "🎯"},
            {"name": "📉 Vintages & Roll Rates", "module": "02A_Vintages_RollRates.py", "icon": "📉"},
            {"name": "⚖️ Concentration Risk", "module": "06_Concentration_Risk.py", "icon": "⚖️"},
            {"name": "🚨 Employer Limits & Alerts", "module": "06A_Employer_Limits_Alerts.py", "icon": "🚨"},
            {"name": "📊 Provisioning & Writeoff", "module": "09_Provisioning_Writeoff.py", "icon": "📊"},
            {"name": "🌀 ALM Stress Tests", "module": "03B_ALM_Stress_Tests.py", "icon": "🌀"},
        ],
        "⚖️ Compliance Governance": [
            {"name": "⚖️ Governance Compliance", "module": "05_Governance_Compliance.py", "icon": "⚖️"},
            {"name": "📋 SASRA Returns", "module": "05A_SASRA_Returns.py", "icon": "📋"},
            {"name": "📊 Data Quality MIS", "module": "07_Data_Quality_MIS.py", "icon": "📊"},
            {"name": "🔍 Data Quality Scans", "module": "07A_Data_Quality_Scans.py", "icon": "🔍"},
            {"name": "⚙️ Policy Engine Monitor", "module": "12_Policy_Engine_Monitor.py", "icon": "⚙️"},
        ],
        "🚀 Operations Excellence": [
            {"name": "⏱️ Operations TAT", "module": "08_Operations_TAT.py", "icon": "⏱️"},
            {"name": "📞 Collections Recovery", "module": "13_Collections_Recovery.py", "icon": "📞"},
            {"name": "📱 Collections Funnel SMS", "module": "13A_Collections_Funnel_SMS.py", "icon": "📱"},
            {"name": "🔒 Cybersecurity & BCP", "module": "10_Cybersecurity_BCP.py", "icon": "🔒"},
        ],
        "💼 Member Value": [
            {"name": "👥 Member Value", "module": "11_Member_Value.py", "icon": "👥"},
            {"name": "📈 Member Value & Churn", "module": "11A_Member_Value_Churn.py", "icon": "📈"},
            {"name": "📄 AGM Dividend Paper", "module": "14_AGM_Dividend_Paper.py", "icon": "📄"},
        ],
    }


def _ensure_sidebar_state(page_categories: dict):
    """Ensure sidebar_collapsed structure exists and matches categories."""
    if "sidebar_collapsed" not in st.session_state:
        st.session_state.sidebar_collapsed = {
            category: True for category in page_categories.keys()
        }
    else:
        # Add any new categories if they were introduced
        for category_name in page_categories.keys():
            if category_name not in st.session_state.sidebar_collapsed:
                st.session_state.sidebar_collapsed[category_name] = True


def render_sidebar():
    """
    Enterprise sidebar used on ALL pages.
    Mirrors the design and structure from app.py.
    """
    hide_default_streamlit_elements()
    apply_custom_styling()

    page_categories = get_page_categories()
    _ensure_sidebar_state(page_categories)

    # Safe session defaults
    user_name = st.session_state.get("user", "Guest User")
    user_role = st.session_state.get("role", "Guest Role")
    username = st.session_state.get("username", "guest")
    tenant = st.session_state.get("tenant", "All SACCOs")
    last_activity = st.session_state.get("last_activity", datetime.now())

    with st.sidebar:
        # Header card (same as app.py)
        st.markdown(
            f"""
            <div class="sidebar-header">
                <h3>🏛️ SACCO Pro</h3>
                <p style="font-size: 0.9rem; opacity: 0.9;">Prudential Compliance Suite</p>
                <p style="font-size: 0.8rem; margin-top: 5px;">
                    <strong>{tenant}</strong>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # User card (same as app.py)
        st.markdown(
            f"""
            <div class="user-card">
                <strong style="color: #1e3c72;">{user_name}</strong><br>
                <small style="color: #64748b;">
                    {user_role}<br>
                    {datetime.now().strftime('%H:%M')} • Active
                </small>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown("### 🧭 Strategic Navigation")

        # Dashboard home button
        if st.button(
            "🏠 Dashboard Home",
            use_container_width=True,
            key="nav_home",
            help="Return to main compliance dashboard",
        ):
            # For inner pages, jump back to root app
            try:
                st.session_state.current_page = "dashboard"
            except Exception:
                pass
            st.switch_page("app.py")

        st.markdown("---")

        # Strategic categories as expanders (same pattern as app.py)
        for category_name, pages in page_categories.items():
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

        # Quick Actions (same routes as app.py)
        st.markdown("### 🚀 Quick Actions")

        action_col1, action_col2 = st.columns(2)
        with action_col1:
            if st.button(
                "🔄 Refresh",
                use_container_width=True,
                key="sidebar_refresh",
            ):
                st.rerun()
            if st.button(
                "📊 Reports",
                use_container_width=True,
                key="sidebar_reports",
            ):
                st.switch_page("pages/05A_SASRA_Returns.py")

        with action_col2:
            if st.button(
                "🔔 Alerts",
                use_container_width=True,
                key="sidebar_alerts",
            ):
                st.switch_page("pages/06A_Employer_Limits_Alerts.py")
            if st.button(
                "📈 Analytics",
                use_container_width=True,
                key="sidebar_analytics",
            ):
                st.switch_page("pages/01_Overview.py")

        st.markdown("---")

        # System status
        st.markdown("### 🟢 System Status")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("🔵 **Live**")
        with c2:
            st.markdown("🟢 **Secure**")
        with c3:
            st.markdown("🟡 **Synced**")

        st.caption(f"Session: {username}")
        try:
            last_ts = (
                last_activity.strftime("%H:%M")
                if isinstance(last_activity, datetime)
                else str(last_activity)
            )
        except Exception:
            last_ts = "N/A"
        st.caption(f"Last activity: {last_ts}")

        # Logout button (same behaviour everywhere)
        if st.button(
            "🚪 Logout",
            use_container_width=True,
            key="logout_btn",
            type="primary",
        ):
            try:
                audit_logger = AuditLogger()
                audit_logger.log_logout(username, user_role)
            except Exception:
                pass  # Do not break logout if logging fails

            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.role = None
            st.session_state.username = None
            st.session_state.current_page = "dashboard"

            st.success("Logged out successfully")
            st.rerun()
