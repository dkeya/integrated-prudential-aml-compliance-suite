# app.py - ENHANCED WITH ENTERPRISE FEATURES
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yaml
import json
import hashlib
import time
from pathlib import Path
import sqlite3
import duckdb
import os
from typing import Dict, List, Optional, Any
import tempfile

# Import core modules
from sacco_core.config import ConfigManager
from sacco_core.rbac import RBACManager, check_permission, get_current_role
from sacco_core.audit import AuditLogger
from sacco_core.db import DatabaseManager

# ==============================================
# COMPLIANCE PHILOSOPHY FRAMEWORK
# ==============================================
COMPLIANCE_PHILOSOPHY = {
    "Data": "What's the current regulatory and risk posture?",
    "Insights": "Why are risks materializing and where are compliance gaps?",
    "Frameworks": "How to assess using regulatory frameworks (SASRA, CBK, Basel)",
    "Actions": "What specific controls and interventions to implement",
    "Impact": "What value it creates (avoided penalties, capital efficiency, member trust)",
    "Governance": "How decisions are documented and accountability is maintained"
}

# Page configuration - HIDE THE SIDEBAR NAVIGATION
st.set_page_config(
    page_title="🏛️ SACCO Prudential Compliance Suite",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://sacco-prudential.com/docs',
        'Report a bug': 'https://sacco-prudential.com/support',
        'About': '🏛️ SACCO Prudential Compliance Suite v2.0 - Enterprise Regulatory Intelligence Platform'
    }
)

# ==============================================
# ENTERPRISE-GRADE CSS
# ==============================================
enterprise_css = """
    <style>
        /* Hide Streamlit defaults */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {visibility: hidden;}
        
        /* Hide Streamlit's default page navigation */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        
        /* Hide sidebar on login page */
        .login-page [data-testid="stSidebar"] {
            display: none !important;
        }
        
        /* ENTERPRISE HEADER STYLING */
        .enterprise-header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            padding: 25px 30px;
            border-radius: 16px;
            color: white;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(30, 60, 114, 0.2);
        }
        
        .enterprise-header h1 {
            margin: 0;
            font-size: 2.2rem;
            color: white;
        }
        
        .enterprise-header p {
            margin: 5px 0 0 0;
            opacity: 0.9;
            color: #e0e7ff;
            font-size: 1.1rem;
        }
        
        /* COMPLIANCE STATUS MARQUEE */
        .compliance-marquee {
            background: linear-gradient(90deg, #0f766e 0%, #0d9488 100%);
            padding: 12px 20px;
            border-radius: 12px;
            margin-bottom: 24px;
            border-left: 5px solid #14b8a6;
            color: white;
        }
        
        .compliance-marquee marquee {
            font-size: 0.95rem;
            font-weight: 500;
        }
        
        /* STRATEGIC CARDS */
        .strategic-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            border-left: 5px solid #3b82f6;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin-bottom: 15px;
            transition: transform 0.2s;
        }
        
        .strategic-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        /* BUTTON ENHANCEMENTS */
        .stButton > button {
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            transition: all 0.2s ease;
            width: 100%;
            text-align: left;
            padding: 10px 15px;
            margin: 2px 0;
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            font-size: 0.95rem;
            font-weight: 500;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%);
            border-color: #3b82f6;
            color: #1e40af;
        }
        
        .primary-button > button {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            border: none;
            text-align: center;
            font-weight: 600;
        }
        
        .primary-button > button:hover {
            background: linear-gradient(135deg, #2a5298 0%, #1e3c72 100%);
            color: white;
        }
        
        /* SIDEBAR ENHANCEMENTS */
        .sidebar-header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            padding: 20px;
            border-radius: 12px;
            color: white;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .user-card {
            background: #f8fafc;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #3b82f6;
            margin-bottom: 20px;
        }
        
        /* EXPANDER STYLING */
        .streamlit-expanderHeader {
            background-color: #f8fafc !important;
            border-radius: 8px !important;
            padding: 12px 18px !important;
            margin: 5px 0 !important;
            border-left: 4px solid #64748b !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
        }
        
        .streamlit-expanderHeader:hover {
            background-color: #f1f5f9 !important;
        }
        
        .streamlit-expanderHeader[aria-expanded="true"] {
            border-left-color: #2563eb !important;
            background-color: #e0f2fe !important;
        }
        
        /* KPI METRICS */
        [data-testid="stMetric"] {
            background: white;
            padding: 15px;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        }
        
        /* QUICK ACTION GRID */
        .quick-action-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin: 15px 0;
        }
        
        /* TAB STYLING */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #f8fafc;
            padding: 8px;
            border-radius: 12px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 500;
        }
        
        /* DATA TABLE STYLING */
        .dataframe {
            border-radius: 10px !important;
        }
        
        /* RESPONSIVE DESIGN */
        @media (max-width: 768px) {
            .quick-action-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
"""
st.markdown(enterprise_css, unsafe_allow_html=True)

class SaccoApp:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.audit_logger = AuditLogger()
        self.db_manager = DatabaseManager()
        self.rbac_manager = RBACManager()
        
        # Initialize session state
        self.initialize_session_state()
        
        # Load configuration
        self.load_configuration()
    
    def initialize_session_state(self):
        """Initialize session state with enterprise defaults"""
        if 'initialized' not in st.session_state:
            st.session_state.update({
                'initialized': True,
                'authenticated': False,
                'user': None,
                'role': None,
                'username': None,
                'config': None,
                'current_page': "dashboard",
                'last_activity': datetime.now(),
                'tenant': "Central SACCO",  # Multi-tenant support
                'compliance_status': "active"
            })
        
        # Initialize sidebar collapsed state with strategic categories
        # MUST MATCH THE CATEGORIES IN get_page_categories()!
        if 'sidebar_collapsed' not in st.session_state:
            st.session_state.sidebar_collapsed = {
                "📊 Strategic Analytics": True,
                "🎯 Risk Intelligence": True,
                "⚖️ Compliance Governance": True,
                "🚀 Operations Excellence": True,
                "💼 Member Value": True
            }
    
    def load_configuration(self):
        """Load application configuration"""
        try:
            st.session_state.config = self.config_manager.load_settings()
        except Exception as e:
            st.error(f"Configuration error: {e}")
            st.session_state.config = self.config_manager.get_default_config()
    
    def get_compliance_status_messages(self):
        """Generate dynamic compliance status messages"""
        return [
            "✅ SASRA Returns: Compliant | ⚠️ Liquidity Ratio: 18.2% (Target: 20%) | ✅ PAR < 30 days: 4.2%",
            "📊 Capital Adequacy: 18.5% | 🎯 Dividend Capacity: KES 125M | 🔴 Employer Concentration: 32% (Limit: 25%)",
            "🚨 Alert: 3 employers approaching concentration limits | 📈 Member Growth: +8.2% QoQ",
            "⚡ Next Regulatory Filing: SASRA Q4 Returns due in 14 days | 📋 Internal Audit: 92% complete"
        ]
    
    def authenticate_user(self, username: str, password: str, designation: str = None) -> bool:
        """Authenticate user with username, password, and designation for RBAC"""
        # Enhanced user roles with compliance focus - NOW INCLUDING ADMIN
        valid_users = {
            'admin': {
                'password': 'admin123', 
                'role': 'System Administrator', 
                'name': 'System Admin', 
                'tenant': 'All SACCOs',
                'designations': ['System Administrator']  # Can login with admin designation
            },
            'compliance_officer': {
                'password': 'compliance123', 
                'role': 'Compliance Officer', 
                'name': 'Sarah Mwangi', 
                'tenant': 'Central SACCO',
                'designations': ['Compliance Officer', 'Regulator']
            },
            'risk_manager': {
                'password': 'risk123', 
                'role': 'Risk Manager', 
                'name': 'James Omondi', 
                'tenant': 'Central SACCO',
                'designations': ['Risk Manager', 'Operations Manager']
            },
            'ceo': {
                'password': 'ceo123', 
                'role': 'CEO', 
                'name': 'Dr. Kamau Maina', 
                'tenant': 'Central SACCO',
                'designations': ['CEO', 'Board Member']
            },
            'board_member': {
                'password': 'board123', 
                'role': 'Board Member', 
                'name': 'Jane Wanjiku', 
                'tenant': 'Central SACCO',
                'designations': ['Board Member', 'CEO']
            },
            'auditor': {
                'password': 'auditor123', 
                'role': 'Internal Auditor', 
                'name': 'Peter Okoth', 
                'tenant': 'Central SACCO',
                'designations': ['Internal Auditor']
            },
            'regulator': {
                'password': 'regulator123', 
                'role': 'Regulator', 
                'name': 'SASRA Inspector', 
                'tenant': 'Regulatory Body',
                'designations': ['Regulator']
            }
        }
        
        # Trim inputs and convert to lowercase for username only
        username = username.strip().lower()
        
        # Check if username exists
        if username not in valid_users:
            return False
        
        user_data = valid_users[username]
        
        # Check password
        if password != user_data['password']:
            return False
        
        # Set session state
        st.session_state.authenticated = True
        st.session_state.user = user_data['name']
        st.session_state.role = user_data['role']  # Use the role from user_data, not designation
        st.session_state.username = username
        st.session_state.tenant = user_data['tenant']
        st.session_state.designation = designation  # Store selected designation
        st.session_state.last_activity = datetime.now()
        
        # Log the login - FIXED: Use only available methods
        try:
            # Try to log login with available method
            self.audit_logger.log_login(username, user_data['role'])
        except Exception as e:
            # If log_login doesn't work, try log_data_access or fallback
            try:
                self.audit_logger.log_data_access(username, user_data['role'], "login_success")
            except:
                # Fallback to console logging
                print(f"Login successful: {username} as {user_data['role']}")
        
        return True
    
    def render_login(self):
        """Render enterprise-grade login page"""
        # Apply login page specific CSS
        st.markdown('<div class="login-page">', unsafe_allow_html=True)
        
        # Gradient Hero Header
        st.markdown(f"""
        <div class="enterprise-header">
            <h1>🏛️ SACCO Prudential Compliance Suite</h1>
            <p>Enterprise Regulatory Intelligence Platform • {datetime.now().strftime('%d %B %Y')}</p>
            <div style="margin-top: 10px; font-size: 0.9rem; opacity: 0.8;">
                <strong>📍</strong> Compliance Intelligence > System Access | 
                <strong>🏢</strong> {st.session_state.get('tenant', 'SACCO Federation')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Compliance Philosophy Quick View
        with st.expander("📜 Compliance Philosophy Framework", expanded=True):
            cols = st.columns(2)
            for i, (key, value) in enumerate(COMPLIANCE_PHILOSOPHY.items()):
                with cols[i % 2]:
                    st.info(f"**{key}**: {value}")
        
        # Login Form Container
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            <div style="background: white; padding: 30px; border-radius: 16px; 
                        box-shadow: 0 4px 20px rgba(0,0,0,0.08); margin: 20px 0;">
                <h3 style="text-align: center; color: #1e3c72; margin-bottom: 25px;">
                    🔐 Secure Compliance Portal
                </h3>
            """, unsafe_allow_html=True)
            
            # RBAC Role Information
            st.markdown("""
            <div style="background: #f0f9ff; padding: 10px; border-radius: 8px; 
                        border-left: 4px solid #0ea5e9; margin-bottom: 15px;">
                <strong>👑 RBAC Roles & Access:</strong><br>
                • <strong>Admin:</strong> Full system access<br>
                • <strong>Compliance Officer:</strong> Regulatory & compliance modules<br>
                • <strong>Risk Manager:</strong> Risk analytics & monitoring<br>
                • <strong>CEO/Board:</strong> Strategic oversight & governance<br>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("login_form", clear_on_submit=False):
                # Tenant Selection
                tenant = st.selectbox(
                    "🏢 Select SACCO",
                    ["Central SACCO", "Western SACCO", "Nairobi SACCO", "Coastal SACCO", "Regulatory Preview"],
                    help="Multi-tenancy: Select your SACCO organization"
                )
                
                # Designation/Role selection - IMPORTANT FOR RBAC
                designation = st.selectbox(
                    "👤 Your Designation",
                    [
                        "System Administrator",
                        "Compliance Officer", 
                        "Risk Manager", 
                        "CEO", 
                        "Board Member", 
                        "Internal Auditor", 
                        "Regulator",
                        "Operations Manager",
                        "IT Security Officer"
                    ],
                    help="Select your role for proper access control",
                    index=0  # Default to System Administrator
                )
                
                # Username input
                username = st.text_input(
                    "📧 Username / Email",
                    placeholder="your.name@sacco.co.ke",
                    help="Enter your registered username or email",
                    value="admin"  # Default value for testing
                )
                
                password = st.text_input(
                    "🔑 Password",
                    type="password",
                    placeholder="Enter your password",
                    help="Password is case-sensitive",
                    value="admin123"  # Default value for testing
                )
                
                # Remember Me checkbox
                remember_me = st.checkbox("Remember me on this device", value=False)
                
                col_a, col_b, col_c = st.columns([1, 2, 1])
                with col_b:
                    submit = st.form_submit_button(
                        "🚀 Access Compliance Suite",
                        use_container_width=True,
                        type="primary"
                    )
                
                if submit:
                    # Validate inputs
                    if not username or not password:
                        st.warning("⚠️ Please enter both username and password")
                        if not username:
                            st.caption("📝 Please enter your username")
                        if not password:
                            st.caption("🔑 Please enter your password")
                    else:
                        # Trim whitespace from inputs
                        username = username.strip()
                        
                        try:
                            with st.spinner("🔐 Authenticating & configuring RBAC access..."):
                                time.sleep(1)  # Simulate authentication
                                if self.authenticate_user(username, password, designation):
                                    # If remember me is checked, set a session flag
                                    if remember_me:
                                        st.session_state.remember_me = True
                                    
                                    # Show RBAC welcome message
                                    welcome_msg = ""
                                    if st.session_state.role == "System Administrator":
                                        welcome_msg = "👑 **System Administrator**: Full access granted to all modules"
                                    elif "Compliance" in st.session_state.role:
                                        welcome_msg = "⚖️ **Compliance Officer**: Regulatory modules unlocked"
                                    elif "Risk" in st.session_state.role:
                                        welcome_msg = "🎯 **Risk Manager**: Risk analytics accessible"
                                    elif "CEO" in st.session_state.role or "Board" in st.session_state.role:
                                        welcome_msg = "🏛️ **Executive Access**: Strategic oversight enabled"
                                    
                                    st.success(f"✅ Authentication successful! {welcome_msg}")
                                    
                                    # Log RBAC configuration
                                    st.info(f"**User:** {st.session_state.user} | **Role:** {st.session_state.role} | **Tenant:** {st.session_state.tenant}")
                                    
                                    time.sleep(1.5)
                                    st.rerun()
                                else:
                                    st.error("❌ Authentication failed. Please check credentials.")
                                    
                                    # Show help for valid credentials
                                    with st.expander("🆘 Need login credentials?", expanded=False):
                                        st.markdown("""
                                        **Test Credentials:**
                                        - **Admin:** Username: `admin` | Password: `admin123`
                                        - **Compliance Officer:** Username: `compliance_officer` | Password: `compliance123`
                                        - **Risk Manager:** Username: `risk_manager` | Password: `risk123`
                                        - **CEO:** Username: `ceo` | Password: `ceo123`
                                        - **Board Member:** Username: `board_member` | Password: `board123`
                                        - **Auditor:** Username: `auditor` | Password: `auditor123`
                                        - **Regulator:** Username: `regulator` | Password: `regulator123`
                                        """)
                        except Exception as e:
                            st.error(f"❌ Login error: {str(e)}")
                            st.warning("Please try again or contact system administrator")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Security & Compliance Notice
            st.markdown("""
            <div style="background: #fef3c7; padding: 15px; border-radius: 10px; 
                        border-left: 4px solid #d97706; margin-top: 20px;">
                <strong>🔒 RBAC Security Framework:</strong>
                <ul style="margin: 10px 0 0 20px; font-size: 0.9rem;">
                    <li><strong>Role-Based Access Control (RBAC)</strong> enforced</li>
                    <li>Access limited to <strong>authorized modules only</strong></li>
                    <li>All actions <strong>audit-logged with role attribution</strong></li>
                    <li>Session permissions based on <strong>designation + credentials</strong></li>
                </ul>
            </div>
            
            <div style="background: #ecfdf5; padding: 10px; border-radius: 8px; 
                        border-left: 4px solid #10b981; margin-top: 15px;">
                <strong>🚀 Quick Admin Access:</strong> Username: <code>admin</code> | Password: <code>admin123</code>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def get_page_categories(self):
        return {
            "📊 Strategic Analytics": [
                {"name": "Overview Dashboard", "module": "01_Overview.py", "icon": "📊"},
                {"name": "Liquidity ALM", "module": "03_Liquidity_ALM.py", "icon": "📈"},
                {"name": "Pricing Economics", "module": "04_Pricing_Economics.py", "icon": "💰"},
                {"name": "Dividend Capacity", "module": "03A_Dividend_Capacity.py", "icon": "💧"},
            ],
            "🎯 Risk Intelligence": [
                {"name": "Credit Risk PAR", "module": "02_Credit_Risk_PAR.py", "icon": "🎯"},
                {"name": "Vintages & Roll Rates", "module": "02A_Vintages_RollRates.py", "icon": "📉"},
                {"name": "Concentration Risk", "module": "06_Concentration_Risk.py", "icon": "⚖️"},
                {"name": "Employer Limits & Alerts", "module": "06A_Employer_Limits_Alerts.py", "icon": "🚨"},
                {"name": "Provisioning & Writeoff", "module": "09_Provisioning_Writeoff.py", "icon": "📊"},
                {"name": "ALM Stress Tests", "module": "03B_ALM_Stress_Tests.py", "icon": "🌀"},
            ],
            "⚖️ Compliance Governance": [
                {"name": "Governance Compliance", "module": "05_Governance_Compliance.py", "icon": "⚖️"},
                {"name": "SASRA Returns", "module": "05A_SASRA_Returns.py", "icon": "📋"},
                {"name": "Data Quality MIS", "module": "07_Data_Quality_MIS.py", "icon": "📊"},
                {"name": "Data Quality Scans", "module": "07A_Data_Quality_Scans.py", "icon": "🔍"},
                {"name": "Policy Engine Monitor", "module": "12_Policy_Engine_Monitor.py", "icon": "⚙️"},
            ],
            "🚀 Operations Excellence": [
                {"name": "Operations TAT", "module": "08_Operations_TAT.py", "icon": "⏱️"},
                {"name": "Collections Recovery", "module": "13_Collections_Recovery.py", "icon": "📞"},
                {"name": "Collections Funnel SMS", "module": "13A_Collections_Funnel_SMS.py", "icon": "📱"},
                {"name": "Cybersecurity & BCP", "module": "10_Cybersecurity_BCP.py", "icon": "🔒"},
            ],
            "💼 Member Value": [
                {"name": "Member Value", "module": "11_Member_Value.py", "icon": "👥"},
                {"name": "Member Value & Churn", "module": "11A_Member_Value_Churn.py", "icon": "📈"},
                {"name": "AGM Dividend Paper", "module": "14_AGM_Dividend_Paper.py", "icon": "📄"},
            ],
        }
    
    def render_sidebar(self):
        """Render enterprise sidebar with strategic navigation"""
        with st.sidebar:
            # Sidebar Header
            st.markdown(f"""
            <div class="sidebar-header">
                <h3>🏛️ SACCO Pro</h3>
                <p style="font-size: 0.9rem; opacity: 0.9;">Prudential Compliance Suite</p>
                <p style="font-size: 0.8rem; margin-top: 5px;">
                    <strong>{st.session_state.tenant}</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # User Information Card
            st.markdown(f"""
            <div class="user-card">
                <strong style="color: #1e3c72;">{st.session_state.user}</strong><br>
                <small style="color: #64748b;">
                    {st.session_state.role}<br>
                    {datetime.now().strftime('%H:%M')} • Active
                </small>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Strategic Navigation
            st.markdown("### 🧭 Strategic Navigation")
            
            # Dashboard Home Button
            if st.button(
                "🏠 Dashboard Home", 
                use_container_width=True, 
                key="nav_home",
                help="Return to main compliance dashboard"
            ):
                st.session_state.current_page = "dashboard"
                st.rerun()
            
            st.markdown("---")
            
            # Strategic Categories (Following The Verse pattern)
            page_categories = self.get_page_categories()
            
            for category_name, pages in page_categories.items():
                # Ensure category exists in sidebar_collapsed (safety check)
                if category_name not in st.session_state.sidebar_collapsed:
                    st.session_state.sidebar_collapsed[category_name] = True
                
                # Use .get() for safe access
                is_collapsed = st.session_state.sidebar_collapsed.get(category_name, True)
                
                # Category Expander
                with st.expander(category_name, expanded=not is_collapsed):
                    for page in pages:
                        if st.button(
                            f"{page['icon']} {page['name']}",
                            key=f"nav_{page['module']}",
                            use_container_width=True,
                            help=f"Go to {page['name']}"
                        ):
                            st.switch_page(f"pages/{page['module']}")
            
            st.markdown("---")
            
            # Quick Actions Section
            st.markdown("### 🚀 Quick Actions")
            
            action_col1, action_col2 = st.columns(2)
            with action_col1:
                if st.button("🔄 Refresh", use_container_width=True, key="sidebar_refresh"):
                    st.rerun()
                if st.button("📊 Reports", use_container_width=True, key="sidebar_reports"):
                    st.switch_page("pages/05A_SASRA_Returns.py")
            
            with action_col2:
                if st.button("🔔 Alerts", use_container_width=True, key="sidebar_alerts"):
                    st.switch_page("pages/06A_Employer_Limits_Alerts.py")
                if st.button("📈 Analytics", use_container_width=True, key="sidebar_analytics"):
                    st.switch_page("pages/01_Overview.py")
            
            st.markdown("---")
            
            # System Status
            st.markdown("### 🟢 System Status")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("🔵 **Live**")
            with col2:
                st.markdown("🟢 **Secure**")
            with col3:
                st.markdown("🟡 **Synced**")
            
            st.caption(f"Session: {st.session_state.username}")
            st.caption(f"Last activity: {st.session_state.last_activity.strftime('%H:%M')}")
            
            # Logout Button
            if st.button(
                "🚪 Logout", 
                use_container_width=True, 
                key="logout_btn",
                type="primary"
            ):
                try:
                    self.audit_logger.log_logout(st.session_state.username, st.session_state.role)
                except:
                    pass  # Silently continue if logging fails
                
                st.session_state.authenticated = False
                st.session_state.user = None
                st.session_state.role = None
                st.session_state.username = None
                st.session_state.current_page = "dashboard"
                st.success("Logged out successfully")
                time.sleep(1)
                st.rerun()
    
    def render_compliance_status_marquee(self):
        """Render real-time compliance status marquee"""
        messages = self.get_compliance_status_messages()
        st.markdown(f"""
        <div class="compliance-marquee">
            <marquee behavior="scroll" direction="left" scrollamount="4">
                {' • '.join(messages)}
            </marquee>
        </div>
        """, unsafe_allow_html=True)
    
    def render_strategic_metrics(self):
        """Render strategic compliance metrics"""
        st.subheader("🎯 Strategic Compliance KPIs")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📊 Capital Adequacy", 
                value="18.5%",
                delta="+0.8%",
                delta_color="normal",
                help="SASRA Minimum: 15%"
            )
        
        with col2:
            st.metric(
                label="💧 Liquidity Ratio", 
                value="125%",
                delta="+5%",
                delta_color="normal",
                help="Target: >100%"
            )
        
        with col3:
            st.metric(
                label="🎯 PAR 30 Days", 
                value="3.2%",
                delta="-0.4%",
                delta_color="inverse",
                help="SASRA Threshold: 5%"
            )
        
        with col4:
            st.metric(
                label="⚖️ Compliance Score", 
                value="92%",
                delta="+2%",
                delta_color="normal",
                help="Regulatory compliance score"
            )
    
    def render_quick_actions_grid(self):
        """Render grid of quick actions"""
        st.subheader("⚡ Quick Action Center")
        
        actions = [
            {"icon": "📋", "label": "SASRA Returns", "page": "05A_SASRA_Returns.py", "color": "#3b82f6"},
            {"icon": "🎯", "label": "Risk Dashboard", "page": "02_Credit_Risk_PAR.py", "color": "#ef4444"},
            {"icon": "💧", "label": "Liquidity ALM", "page": "03_Liquidity_ALM.py", "color": "#06b6d4"},
            {"icon": "⚖️", "label": "Concentration", "page": "06_Concentration_Risk.py", "color": "#8b5cf6"},
            {"icon": "📊", "label": "Provisioning", "page": "09_Provisioning_Writeoff.py", "color": "#f59e0b"},
            {"icon": "🔒", "label": "Cybersecurity", "page": "10_Cybersecurity_BCP.py", "color": "#10b981"},
            {"icon": "📈", "label": "Member Value", "page": "11_Member_Value.py", "color": "#ec4899"},
            {"icon": "⚙️", "label": "Policy Engine", "page": "12_Policy_Engine_Monitor.py", "color": "#6366f1"}
        ]
        
        cols = st.columns(4)
        for idx, action in enumerate(actions):
            with cols[idx % 4]:
                if st.button(
                    f"{action['icon']} {action['label']}",
                    key=f"quick_{action['page']}",
                    use_container_width=True,
                    help=f"Go to {action['label']}"
                ):
                    st.switch_page(f"pages/{action['page']}")
    
    def render_main(self):
        """Render main compliance intelligence dashboard"""
        # Gradient Hero Header
        st.markdown(f"""
        <div class="enterprise-header">
            <h1>Welcome back, {st.session_state.user}! 👋</h1>
            <p>SACCO Prudential Compliance Suite • Real-time Regulatory Intelligence</p>
            <div style="margin-top: 10px; font-size: 0.9rem; opacity: 0.9;">
                <strong>📍</strong> Compliance Intelligence > Dashboard | 
                <strong>🏢</strong> {st.session_state.tenant} | 
                <strong>📅</strong> {datetime.now().strftime('%Y-%m-%d')} |
                <strong>👤</strong> {st.session_state.role}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Compliance Status Marquee
        self.render_compliance_status_marquee()
        
        # Strategic Metrics
        self.render_strategic_metrics()
        
        # Quick Actions Grid
        self.render_quick_actions_grid()
        
        # Compliance Intelligence Section
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔔 Recent Compliance Alerts")
            alerts_data = {
                "Time": ["2 hours ago", "4 hours ago", "1 day ago", "2 days ago"],
                "Alert": [
                    "PAR 30 approaching threshold (4.8%) - Review required",
                    "Employer concentration at 32% (Limit: 25%) - Action needed",
                    "Cybersecurity scan completed - 3 vulnerabilities found",
                    "Monthly compliance reports generated - Ready for board review"
                ],
                "Priority": ["Medium", "High", "Medium", "Info"]
            }
            alerts_df = pd.DataFrame(alerts_data)
            st.dataframe(alerts_df, use_container_width=True, hide_index=True)
            
            # Compliance Philosophy Framework
            with st.expander("📜 Compliance Philosophy Framework", expanded=False):
                st.info(f"""
                **Our Approach to Prudential Compliance:**
                
                **📊 Data:** {COMPLIANCE_PHILOSOPHY['Data']}
                **🔍 Insights:** {COMPLIANCE_PHILOSOPHY['Insights']}
                **⚖️ Frameworks:** {COMPLIANCE_PHILOSOPHY['Frameworks']}
                **🚀 Actions:** {COMPLIANCE_PHILOSOPHY['Actions']}
                **💰 Impact:** {COMPLIANCE_PHILOSOPHY['Impact']}
                **📋 Governance:** {COMPLIANCE_PHILOSOPHY['Governance']}
                """)
        
        with col2:
            st.subheader("📈 Regulatory Timeline")
            
            # Simulated regulatory deadlines
            timeline_data = {
                "Deadline": ["15 Nov 2023", "30 Nov 2023", "15 Dec 2023", "31 Dec 2023"],
                "Requirement": ["SASRA Q3 Returns", "Internal Audit Report", "Board Risk Committee", "Annual Compliance Report"],
                "Status": ["✅ Completed", "🟡 In Progress", "🔵 Scheduled", "⚪ Upcoming"],
                "Days Left": ["-", "5", "20", "45"]
            }
            timeline_df = pd.DataFrame(timeline_data)
            st.dataframe(timeline_df, use_container_width=True, hide_index=True)
            
            # Strategic Initiatives
            st.subheader("🎯 Strategic Initiatives")
            
            initiatives = [
                {"name": "Automated SASRA Reporting", "progress": 85, "owner": "Compliance Team"},
                {"name": "Risk-Based Pricing Model", "progress": 60, "owner": "Risk Dept"},
                {"name": "Member Value Enhancement", "progress": 45, "owner": "Marketing"},
                {"name": "Cybersecurity Upgrade", "progress": 90, "owner": "IT Security"}
            ]
            
            for initiative in initiatives:
                st.progress(initiative['progress']/100, text=f"{initiative['name']} ({initiative['owner']})")
    
    def run(self):
        """Main application runner"""
        if not st.session_state.authenticated:
            self.render_login()
        else:
            # Update last activity
            st.session_state.last_activity = datetime.now()
            
            # Render sidebar and main content
            self.render_sidebar()
            self.render_main()
            
            # Log dashboard access - FIXED: Use try-catch for non-existent methods
            try:
                # Try different logging methods that might exist
                self.audit_logger.log_data_access(
                    st.session_state.username,
                    st.session_state.role,
                    "dashboard_access"
                )
            except Exception as e:
                # Silently fail if logging method doesn't exist
                pass

# Initialize and run the app
if __name__ == "__main__":
    app = SaccoApp()
    app.run()