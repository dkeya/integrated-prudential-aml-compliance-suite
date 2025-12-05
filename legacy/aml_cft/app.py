# app.py
from __future__ import annotations
import os
from pathlib import Path
from datetime import datetime
import io
import pandas as pd
import streamlit as st

from sacco_core.config import get_config
from sacco_core.navigation import render_sidebar, ROUTES  # <-- ROUTES added
from sacco_core.db import query

# --- near the top, keep collapsed so it doesn’t flash briefly ---
st.set_page_config(
    page_title="AML/CFT Compliance System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",  # collapsed by default
)

# Add this helper flag (landing page only)
SHOW_SIDEBAR = False

def _init_session():
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.user_id = os.getenv("USER", "demo_user")
        st.session_state.user_role = st.session_state.get("user_role", "AML_Officer")
        st.session_state.authenticated = True
        st.session_state.nav_current = "Dashboard"
        st.session_state.nav_tab_hint = None
_init_session()

def apply_custom_styles():
    st.markdown(
        """
        <style>
        .main-header {
            font-size: 2.2rem; margin: 0 0 .75rem 0; font-weight: 800;
            background: linear-gradient(90deg, #1f77b4, #2e8b57);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .metric-card { background:#fff; padding:1rem .9rem; border-radius:12px;
            border-left:4px solid #1f77b4; box-shadow:0 1px 3px rgba(0,0,0,.06); }
        .risk-low{border-left-color:#6bcf7f!important}
        .risk-medium{border-left-color:#ffd93d!important}
        .risk-high{border-left-color:#ff6b6b!important}
        .footer{color:#6c757d; font-size:.85rem; text-align:right; padding-top:.5rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )
apply_custom_styles()

CFG = get_config()

def tiny_health():
    try:
        m = query("select count(*) c from members")["c"].iloc[0]
        t = query("select count(*) c from transactions")["c"].iloc[0]
        return True, m, t
    except Exception:
        return False, 0, 0

ok, members_n, txns_n = tiny_health()

# --- replace your current "with st.sidebar: render_sidebar()" block with: ---
if SHOW_SIDEBAR:
    with st.sidebar:
        render_sidebar()
else:
    # Hide the sidebar region entirely on this page
    st.markdown("""
        <style>
        /* Hide the sidebar and its toggle */
        section[data-testid="stSidebar"] {display: none !important;}
        div[data-testid="stSidebarNav"] {display: none !important;}
        /* Stretch main container a bit since sidebar is gone */
        .main .block-container {padding-left: 2rem; padding-right: 2rem;}
        </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-header">SACCO Risk & Compliance OS</div>', unsafe_allow_html=True)
st.caption("World-class AML/CFT platform for SACCOs — aligned with SASRA, FRC-Kenya (goAML), POCAMLA, and FATF.")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-card">🧭 <b>Profile</b><br/>Role: {st.session_state.get("user_role","AML_Officer")}</div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card">⚙️ <b>Config</b><br/>Version: {getattr(CFG,"version","1.0")}</div>', unsafe_allow_html=True)
with c3:
    if ok:
        st.markdown(f'<div class="metric-card risk-low">🗄️ <b>Data</b><br/>{members_n:,} members • {txns_n:,} txns</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="metric-card risk-medium">🗄️ <b>Data</b><br/>Initialising…</div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-card">⏱️ <b>Today</b><br/>{datetime.now().strftime("%Y-%m-%d %H:%M")}</div>', unsafe_allow_html=True)

st.markdown("---")

# -----------------------------------------------------------------------------
# Compliance cockpit (deadlines & quick links)
# -----------------------------------------------------------------------------
st.subheader("Compliance cockpit")

col1, col2, col3 = st.columns(3)

with col1:
    st.write("**Reporting**")
    st.write("- CTR pack: weekly (≥ USD 15k cash) — build in **STR/SAR & CTR** page")
    st.write("- STR/SAR: file within **2 days** of suspicion (via goAML export)")

with col2:
    st.write("**TFS (UN & domestic)**")
    st.write("- Screen members/BOs/counterparties regularly")
    st.write("- **Freeze without delay** on a match; notify Centre within 24h")

with col3:
    st.write("**Record-keeping & Training**")
    st.write("- Retain core AML/records **≥7 years**")
    st.write("- Maintain role-based training records and Board/CEO attestations")

# ---------------- Quick Jump replaces the old 'System Notes' block ----------------
st.markdown("### 🏠 Quick Jump")
_dash_path = ROUTES.get("Dashboard")
def _go(page_key: str):
    path = ROUTES.get(page_key)
    if path:
        st.switch_page(path)
if st.button("Open Executive Dashboard", use_container_width=True, key="qt_dashboard"):
    if _dash_path:
        st.switch_page(_dash_path)

st.markdown("---")

# -----------------------------------------------------------------------------
# 📌 Quick Traceability (Guideline → Module quick-launch)
#    - Quick Launch: always visible
#    - Traceability Table: folded for detail-on-demand
# -----------------------------------------------------------------------------

st.markdown("### Traceability (Guideline → Module quick-launch)")

# ----- Quick Launch row (ALWAYS VISIBLE) -----
st.markdown("#### Quick Launch")
cta1, cta2, cta3 = st.columns(3)
with cta1:
    if st.button("🏛️ MLRO Portal", use_container_width=True, key="qt_mlro"): _go("MLRO Portal")
    if st.button("🎯 Risk Assessment", use_container_width=True, key="qt_risk"): _go("Risk Assessment:Customer")
    if st.button("👤 KYC Management", use_container_width=True, key="qt_kyc"): _go("KYC Management:Verification")
with cta2:
    if st.button("👑 PEP Screening", use_container_width=True, key="qt_pep"): _go("PEP Screening:PEP")
    if st.button("🛡️ Sanctions Screening", use_container_width=True, key="qt_sanctions"): _go("Sanctions Screening")
    if st.button("🚨 Unified Alerts", use_container_width=True, key="qt_alerts"): _go("Alert Management")
with cta3:
    if st.button("💻 Txn Monitoring", use_container_width=True, key="qt_tm"): _go("Transaction Monitoring:Realtime")
    if st.button("📋 STR / CTR Reporting", use_container_width=True, key="qt_strctr"): _go("STR/CTR Reporting:STR")
    if st.button("🔗 FRC Integration (goAML)", use_container_width=True, key="qt_frc"): _go("FRC Integration")

st.caption("👉 For the full guideline-to-module mapping, expand the panel below.")
st.divider()

# ----- Traceability Table (wrapped text + exports) — folded panel -----
with st.expander("📑 Traceability Table — detail on demand", expanded=False):
    st.markdown("#### Traceability Table")

    _trace_rows = [
        (
            "Governance & MLRO access",
            "Boards and senior management must approve and oversee the AML/CFT/CPF framework; allocate sufficient "
            "resources; and receive regular reports. A Money Laundering Reporting Officer (MLRO) must be appointed "
            "with the authority, independence, and unrestricted access to systems/records to carry out obligations. "
            "Internal controls and independent assurance (e.g., internal audit) must test effectiveness.",
            "8_🏛️_MLRO_Portal; RBAC; Audit trail",
        ),
        (
            "Risk-based approach (RBA)",
            "Institutions must identify, assess, and document money-laundering, terrorism-financing, and "
            "proliferation-financing risks across customers, products/services, delivery channels, and geographies. "
            "The Enterprise-wide Risk Assessment (EWRA) must be kept current and drive proportionate controls "
            "(e.g., stricter due diligence, heightened monitoring) with periodic review.",
            "5_🎯_Risk_Assessment; rule configs; monitoring analytics",
        ),
        (
            "CDD / EDD / PEP",
            "Customer Due Diligence (CDD): identify the customer and verify identity using reliable, independent sources; "
            "identify beneficial owners; understand purpose and intended nature of the relationship; and conduct ongoing due diligence. "
            "Enhanced Due Diligence (EDD): apply additional measures for higher-risk customers/transactions (e.g., foreign Politically "
            "Exposed Persons (PEPs), complex structures, unusual activity). EDD can include senior management approval, establishing "
            "Source of Funds (SoF) and Source of Wealth (SoW), increased monitoring, and shorter review cycles. "
            "Politically Exposed Persons (PEP): identify domestic/foreign/international PEPs and their close associates; treat foreign "
            "PEPs as high-risk by default; obtain senior approval before onboarding/continuing; and apply appropriate EDD and monitoring.",
            "2_👤_KYC_Management; 6_👑 PEP Screening; 9_🛡️ Sanctions Screening; Investigations",
        ),
        (
            "Ongoing monitoring",
            "Continuously monitor transactions and customer behaviour to ensure activity is consistent with knowledge of the customer, "
            "risk profile, and the business relationship. Refresh CDD at appropriate intervals, review triggers (material changes, alerts), "
            "and document exceptions. Conduct periodic screening against sanctions/domestic lists and act on hits.",
            "3_💻_Transaction_Monitoring; 7_🚨_AML_Alerts",
        ),
        (
            "Reporting (STR / SAR / CTR)",
            "Suspicious Transaction/Activity Reporting (STR/SAR): where reasonable grounds to suspect ML/TF/PF exist, file promptly—"
            "typically within two business days of forming suspicion. Maintain confidentiality (no tipping-off). "
            "Currency Transaction Reporting (CTR): report cash transactions at or above the regulatory threshold (per the Centre’s format), "
            "aggregating as required. Ensure robust internal escalation from front line to MLRO before external filing.",
            "4_📋_STR_CTR_Reporting; 12_🔗_FRC_Integration",
        ),
        (
            "Targeted Financial Sanctions (TFS)",
            "Screen customers, counterparties, and transactions against UN/domestic designation lists related to terrorism and proliferation. "
            "Upon a positive match, freeze funds/assets ‘without delay’ (generally within 24 hours), prevent any making available of funds or "
            "economic resources, and report to the Financial Reporting Centre (FRC) per timeline. Manage unfreezing according to competent "
            "authority guidance and keep comprehensive records of actions taken.",
            "6_👑/9_🛡️ Screening + Cases + reminders",
        ),
        (
            "Training & records (≥ 7 years)",
            "Provide role-appropriate, risk-based AML/CFT/CPF training to employees, agents, and relevant third parties with attendance tracking. "
            "Retain CDD files, transaction records, internal/external reports, screening outcomes, and case files for at least seven years "
            "and make them available to competent authorities on request.",
            "10_📚_Compliance_Training; retention config; 11_📊_Audit_Reports",
        ),
        (
            "Officer screening & independent audit",
            "Conduct pre-employment and ongoing screening of employees/agents for integrity/fitness. Ensure independent testing of the AML/CFT/CPF "
            "program (internal audit or external independent reviewer) with findings reported to senior management/board and tracked to remediation.",
            "Staff screening pipeline; immutable audit logs",
        ),
    ]

    _df_trace = pd.DataFrame(_trace_rows, columns=["Theme", "What it means (per Guideline)", "Modules / Evidence"])

    _table_css = """
    <style>
    .trace-table { width: 100%; border-collapse: collapse; table-layout: fixed; }
    .trace-table th, .trace-table td {
      border: 1px solid #e6e6e6; padding: 10px 12px; vertical-align: top;
      white-space: normal; word-break: break-word; overflow-wrap: anywhere; line-height: 1.35;
    }
    .trace-table th { background: #f7f7f9; font-weight: 700; }
    .trace-table col.col-theme   { width: 18%; }
    .trace-table col.col-meaning { width: 56%; }
    .trace-table col.col-mods    { width: 26%; }
    </style>
    """
    st.markdown(_table_css, unsafe_allow_html=True)

    _rows_html = "\n".join(
        f"<tr><td>{theme}</td><td>{meaning}</td><td>{mods}</td></tr>"
        for theme, meaning, mods in _trace_rows
    )

    _html = f"""
    <table class="trace-table">
      <colgroup>
        <col class="col-theme"/>
        <col class="col-meaning"/>
        <col class="col-mods"/>
      </colgroup>
      <thead>
        <tr>
          <th>Theme</th>
          <th>What it means (per Guideline)</th>
          <th>Modules / Evidence</th>
        </tr>
      </thead>
      <tbody>
        {_rows_html}
      </tbody>
    </table>
    """
    st.markdown(_html, unsafe_allow_html=True)

    # Export buttons
    ex1, ex2 = st.columns(2)
    with ex1:
        st.download_button(
            "⬇️ Export CSV",
            _df_trace.to_csv(index=False).encode("utf-8"),
            file_name="quick_traceability.csv",
            mime="text/csv",
            use_container_width=True,
            key="qt_exp_csv",
        )
    with ex2:
        try:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as xw:
                _df_trace.to_excel(xw, sheet_name="Traceability", index=False)
            buf.seek(0)
            st.download_button(
                "⬇️ Export XLSX",
                buf.read(),
                file_name="quick_traceability.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="qt_exp_xlsx",
            )
        except Exception:
            st.caption("Install `openpyxl` to enable XLSX export.")

st.markdown('<div class="footer">© SACCO Pro • AML/CFT Module</div>', unsafe_allow_html=True)
