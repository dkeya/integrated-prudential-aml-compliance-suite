# sacco_core/navigation.py
from __future__ import annotations
import streamlit as st
from dataclasses import dataclass, field
from typing import List, Optional, Dict

# ---------- Data model ----------
@dataclass
class NavItem:
    label: str
    page: Optional[str] = None          # e.g. "Risk Assessment:Customer"
    key: Optional[str] = None           # unique Streamlit key
    children: List["NavItem"] = field(default_factory=list)

# ---------- Navigation tree with subcategories (unchanged from your spec) ----------
NAV_TREE: List[NavItem] = [
    NavItem("🏠 DASHBOARD", children=[
        NavItem("Executive Overview", page="Dashboard", key="dash_exec"),
        NavItem("Compliance Metrics", page="Dashboard:Compliance", key="dash_metrics"),
        NavItem("Real-time Alerts", page="Dashboard:Alerts", key="dash_alerts"),
    ]),

    NavItem("👤 MEMBER MANAGEMENT", children=[
        NavItem("KYC", children=[
            NavItem("KYC Verification", page="KYC Management:Verification", key="mm_kyc_verify"),
            NavItem("Enhanced Due Diligence", page="KYC Management:EDD", key="mm_kyc_edd"),
            NavItem("Documents & Attestations", page="KYC Management:Docs", key="mm_kyc_docs"),
        ]),
        NavItem("Risk Profiling", children=[
            NavItem("Customer Risk Scoring", page="Risk Assessment:Customer", key="mm_risk_customer"),
            NavItem("Product Risk Scoring", page="Risk Assessment:Product", key="mm_risk_product"),
            NavItem("Geographic Risk Scoring", page="Risk Assessment:Geo", key="mm_risk_geo"),
            NavItem("Overall Risk Heatmap", page="Risk Assessment:Heatmap", key="mm_risk_heatmap"),
        ]),
        NavItem("PEP & Screening", children=[
            NavItem("PEP Screening", page="PEP Screening:PEP", key="mm_pep_main"),
            NavItem("Name Screening Engine", page="PEP Screening:Name", key="mm_name_engine"),
        ]),
    ]),

    NavItem("💳 TRANSACTION MONITORING", children=[
        NavItem("Real-time Monitoring", page="Transaction Monitoring:Realtime", key="tm_realtime"),
        NavItem("Pattern Detection", children=[
            NavItem("Structuring Staircase", page="Transaction Monitoring:Patterns.Structuring", key="tm_structuring"),
            NavItem("Rapid Movement Tracker", page="Transaction Monitoring:Patterns.Rapid", key="tm_rapid"),
            NavItem("Odd Hours / Weekend Spikes", page="Transaction Monitoring:Patterns.Odd", key="tm_odd"),
        ]),
        NavItem("Behavioral Analytics", children=[
            NavItem("High-Risk Behaviour", page="Transaction Monitoring:Behavioral.HighRisk", key="tm_behaviour"),
            NavItem("Peer Groups & Entropy", page="Transaction Monitoring:Behavioral.Peer", key="tm_peer"),
            NavItem("Risk Heatmap (Txn)", page="Transaction Monitoring:Behavioral.Heatmap", key="tm_heatmap"),
        ]),
        NavItem("Anomaly Detection (ML)", page="Anomaly Detection", key="tm_anomaly"),
        NavItem("Screening Shortcuts", children=[
            NavItem("Sanctions Screening", page="Sanctions Screening", key="tm_sanctions"),
            NavItem("PEP Monitoring", page="PEP Screening:PEP", key="tm_pep"),
        ]),
    ]),

    NavItem("📋 REGULATORY REPORTING", children=[
        NavItem("STR Management", page="STR/CTR Reporting:STR", key="rep_str"),
        NavItem("CTR Management", page="STR/CTR Reporting:CTR", key="rep_ctr"),
        NavItem("FRC Integration (goAML)", page="FRC Integration", key="rep_frc"),
        NavItem("Annual Reporting", page="FRC Integration:Annual", key="rep_annual"),
        NavItem("SAR Templates", page="STR/CTR Reporting:SAR", key="rep_sar"),
    ]),

    NavItem("🛡️ COMPLIANCE OPERATIONS", children=[
        NavItem("Sanctions Screening", page="Sanctions Screening", key="ops_sanctions"),
        NavItem("Alert Management", page="Alert Management", key="ops_alerts"),
        NavItem("Case Investigations", page="Investigations", key="ops_cases"),
    ]),

    NavItem("📚 TRAINING & AWARENESS", children=[
        NavItem("Staff Training", page="Training:Courses", key="train_courses"),
        NavItem("Compliance Certifications", page="Training:Certs", key="train_certs"),
        NavItem("Knowledge Base", page="Training:KB", key="train_kb"),
        NavItem("Trend Analysis", page="Training:Trends", key="train_trends"),
    ]),

    NavItem("🏛️ GOVERNANCE & AUDIT", children=[
        NavItem("MLRO Portal", page="MLRO Portal", key="gov_mlro"),
        NavItem("Audit Reports", children=[
            NavItem("Audit Readiness", page="Audit Reports:Readiness", key="gov_audit_ready"),
            NavItem("Immutable Audit Log", page="Audit Reports:Log", key="gov_audit_log"),
            NavItem("Board Reporting Templates", page="Audit Reports:Board", key="gov_board_packs"),
            NavItem("Documentation Center", page="Audit Reports:Docs", key="gov_docs"),
            NavItem("Gap Analysis Assistant", page="Audit Reports:Gap", key="gov_gap"),
        ]),
        NavItem("Compliance Calendar", page="Calendar", key="gov_calendar"),
    ]),
]

# ---------- Page -> file routes (unchanged) ----------
ROUTES: Dict[str, str] = {
    # Dashboard
    "Dashboard": "pages/1_🏠_AML_Dashboard.py",
    "Dashboard:Compliance": "pages/1_🏠_AML_Dashboard.py",
    "Dashboard:Alerts": "pages/1_🏠_AML_Dashboard.py",

    # Member management
    "KYC Management:Verification": "pages/2_👤_KYC_Management.py",
    "KYC Management:EDD": "pages/2_👤_KYC_Management.py",
    "KYC Management:Docs": "pages/2_👤_KYC_Management.py",

    "Risk Assessment:Customer": "pages/5_🎯_Risk_Assessment.py",
    "Risk Assessment:Product": "pages/5_🎯_Risk_Assessment.py",
    "Risk Assessment:Geo": "pages/5_🎯_Risk_Assessment.py",
    "Risk Assessment:Heatmap": "pages/5_🎯_Risk_Assessment.py",

    "PEP Screening:PEP": "pages/6_👑_PEP_Screening.py",
    "PEP Screening:Name": "pages/6_👑_PEP_Screening.py",

    # Transaction monitoring
    "Transaction Monitoring:Realtime": "pages/3_💳_Transaction_Monitoring.py",
    "Transaction Monitoring:Patterns.Structuring": "pages/3_💳_Transaction_Monitoring.py",
    "Transaction Monitoring:Patterns.Rapid": "pages/3_💳_Transaction_Monitoring.py",
    "Transaction Monitoring:Patterns.Odd": "pages/3_💳_Transaction_Monitoring.py",
    "Transaction Monitoring:Behavioral.HighRisk": "pages/3_💳_Transaction_Monitoring.py",
    "Transaction Monitoring:Behavioral.Peer": "pages/3_💳_Transaction_Monitoring.py",
    "Transaction Monitoring:Behavioral.Heatmap": "pages/3_💳_Transaction_Monitoring.py",
    "Anomaly Detection": "pages/13_🤖_Anomaly_Detection.py",  # to be added

    # Reporting
    "STR/CTR Reporting:STR": "pages/4_📋_STR_CTR_Reporting.py",
    "STR/CTR Reporting:CTR": "pages/4_📋_STR_CTR_Reporting.py",
    "STR/CTR Reporting:SAR": "pages/4_📋_STR_CTR_Reporting.py",
    "FRC Integration": "pages/12_🔗_FRC_Integration.py",
    "FRC Integration:Annual": "pages/12_🔗_FRC_Integration.py",

    # Operations
    "Sanctions Screening": "pages/9_🛡️_Sanctions_Screening.py",
    "Alert Management": "pages/7_🚨_AML_Alerts.py",
    "Investigations": "pages/8_🏛️_MLRO_Portal.py",

    # Training
    "Training:Courses": "pages/10_📚_Compliance_Training.py",
    "Training:Certs": "pages/10_📚_Compliance_Training.py",
    "Training:KB": "pages/10_📚_Compliance_Training.py",
    "Training:Trends": "pages/10_📚_Compliance_Training.py",

    # Governance & audit
    "MLRO Portal": "pages/8_🏛️_MLRO_Portal.py",
    "Audit Reports:Readiness": "pages/11_📊_Audit_Reports.py",
    "Audit Reports:Log": "pages/11_📊_Audit_Reports.py",
    "Audit Reports:Board": "pages/11_📊_Audit_Reports.py",
    "Audit Reports:Docs": "pages/11_📊_Audit_Reports.py",
    "Audit Reports:Gap": "pages/11_📊_Audit_Reports.py",
    "Calendar": "pages/11_📊_Audit_Reports.py",
}

# ---------- Helpers ----------
def _activate(page_name: str):
    """Set current route and optional tab hint (anything after the colon), then switch page."""
    if not page_name:
        return
    st.session_state.nav_current = page_name
    st.session_state.nav_tab_hint = page_name.split(":", 1)[1] if ":" in page_name else None
    route = ROUTES.get(page_name)
    if route:
        st.switch_page(route)

def _btn(label: str, key: str, page: Optional[str], indent: int = 0):
    """Render a single leaf button with left indent (no nested expanders)."""
    pad = "&nbsp;" * (indent * 3)
    st.markdown(f"{pad}• **{label}**", unsafe_allow_html=True)
    if st.button("Open", key=key, use_container_width=True):
        _activate(page)

def _render_group(node: NavItem, depth: int = 0, path: str = ""):
    """
    Render a node and its descendants without nested expanders:
    - This function NEVER uses st.expander.
    - It prints group titles and renders leaves as buttons with indentation.
    """
    group_key_prefix = (path + "/" + (node.label or "")).strip("/")
    if node.children:
        # Group title (subcategory)
        indent = max(depth - 1, 0)  # inside top-level expander depth starts at 1
        pad = "&nbsp;" * (indent * 3)
        st.markdown(f"{pad}### {node.label}", unsafe_allow_html=True)
        for i, child in enumerate(node.children):
            child_path = f"{group_key_prefix}.{i}"
            if child.children:
                # Nested subgroup (still no expander)
                _render_group(child, depth + 1, child_path)
            else:
                # Leaf
                key = child.key or f"nav_{child_path}"
                _btn(child.label, key, child.page, indent=indent + 1)
    else:
        # Leaf at top-level (rare)
        key = node.key or f"nav_{group_key_prefix}"
        _btn(node.label, key, node.page, indent=max(depth - 1, 0))

# ---------- Public renderer (one expander per top-level only) ----------
def render_sidebar():
    # Hide Streamlit's default Pages navigator so only our custom menu shows
    st.markdown(
        """
        <style>
        /* Remove the auto-generated "app" pages list from the sidebar */
        div[data-testid="stSidebarNav"] { display: none !important; }
        /* Optional: tighten top padding since the nav is gone */
        section[data-testid="stSidebar"] .block-container { padding-top: 0.5rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## 🔍 AML/CFT Compliance")
    st.markdown("---")

    if "nav_current" not in st.session_state:
        st.session_state.nav_current = "Dashboard"
    if "nav_tab_hint" not in st.session_state:
        st.session_state.nav_tab_hint = None
    if "user_role" not in st.session_state:
        st.session_state.user_role = "AML_Officer"

    # Exactly one expander per top-level category; inside, we never nest expanders.
    for top in NAV_TREE:
        with st.expander(top.label, expanded=False):
            for idx, child in enumerate(top.children):
                _render_group(child, depth=1, path=f"{top.label}.{idx}")

    st.markdown("---")
    st.caption(f"User: {st.session_state.get('user_role','AML_Officer')}")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()
