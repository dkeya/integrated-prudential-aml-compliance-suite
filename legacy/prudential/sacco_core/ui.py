# sacco_core/ui.py
import streamlit as st


def hide_default_streamlit_elements():
    """Hide default Streamlit elements across all pages."""
    hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {visibility: hidden;}

        /* Hide Streamlit's default sidebar navigation (multi-page menu) */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }

        /* Hide the floating arrow when the sidebar is collapsed */
        [data-testid="collapsedControl"] {
            display: none !important;
        }

        /* Hide the small blue collapse button INSIDE the sidebar */
        [data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }

        /* Consistent padding */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }

        /* Collapsible sidebar styling (legacy support) */
        .sidebar-category {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 0.5rem;
            margin-bottom: 0.5rem;
            border: 1px solid #e9ecef;
        }

        /* Indented page buttons (legacy support) */
        .indented-button {
            margin-left: 1rem;
        }
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def apply_custom_styling():
    """
    Apply global styling across all pages.
    Includes:
    - Original custom styling
    - Enterprise CSS from app.py (so sidebars & metrics look identical)
    """

    # Original custom styling (kept for backwards compatibility)
    base_css = """
    <style>
        /* Custom header styling */
        .custom-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            color: white;
            margin-bottom: 2rem;
        }

        /* Button styling */
        .stButton button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }

        .stButton button:hover {
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
            color: white;
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }

        /* Category toggle buttons */
        .category-toggle {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        }

        /* Metric card styling (legacy) */
        [data-testid="metric-container"] {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 1rem;
        }

        /* Indented page buttons */
        .indented-page {
            margin-left: 1.5rem;
            background: rgba(102, 126, 234, 0.1) !important;
            border: 1px solid rgba(102, 126, 234, 0.2) !important;
        }

        .indented-page:hover {
            background: rgba(102, 126, 234, 0.2) !important;
            border: 1px solid rgba(102, 126, 234, 0.4) !important;
        }
    </style>
    """

    # Enterprise CSS copied from app.py so pages match the main dashboard
    enterprise_css = """
    <style>
        /* Hide Streamlit defaults (duplicated intentionally for robustness) */
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

        /* BUTTON ENHANCEMENTS FOR ENTERPRISE THEME */
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

        /* SIDEBAR ENHANCEMENTS (THIS IS WHAT YOU CARE ABOUT) */
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

    st.markdown(base_css, unsafe_allow_html=True)
    st.markdown(enterprise_css, unsafe_allow_html=True)
