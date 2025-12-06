# pages/01_Prudential_Overview.py

import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# OPTIONAL: ensure project root is on sys.path so `core.*` works reliably
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# Local / project imports
from core.config import ConfigManager
from core.rbac import (
    RBACManager,
    check_permission,
    get_current_role,
    get_current_username,
)
from core.audit import AuditLogger, audit_logger
from core.sidebar import render_sidebar

# ----------------------------------------------
# Page config + unified auth + unified sidebar
# ----------------------------------------------
st.set_page_config(
    page_title="Prudential Compliance Overview",
    page_icon="📊",
    layout="wide",
)

# 🔐 Require login for this page
if not st.session_state.get("authenticated", False):
    st.error("🔐 Please log in to access this page")
    st.stop()

# ✅ Draw the SACCO Pro sidebar (Strategic Navigation, Quick Actions, etc.)
render_sidebar()

# ==============================================
# COMPLIANCE PHILOSOPHY FRAMEWORK
# ==============================================
COMPLIANCE_PHILOSOPHY = {
    "Data": "What's the current regulatory and risk posture?",
    "Insights": "Why are risks materializing and where are compliance gaps?",
    "Frameworks": "How to assess using regulatory frameworks (SASRA, CBK, Basel)",
    "Actions": "What specific controls and interventions to implement",
    "Impact": "What value it creates (avoided penalties, capital efficiency, member trust)",
    "Governance": "How decisions are documented and accountability is maintained",
}


class OverviewPage:
    """
    Unified Prudential Overview page.

    NOTE:
    - Auth is handled via st.session_state["authenticated"].
    - RBAC & config are simplified for now; thresholds can later be wired
      to the unified config system if needed.
    """

    def __init__(self):
        # Attach unified audit logger
        self.audit_logger = audit_logger

        # Pull basic context from session
        self.user = st.session_state.get("user", "anonymous")
        self.role = st.session_state.get("role", "User")
        self.tenant = st.session_state.get("tenant", "Central SACCO")

        # PAR thresholds (defaults, but can be overridden from session)
        self.par30_trigger_max = st.session_state.get(
            "limits_par30_trigger_max", 0.05
        )  # 5%
        self.par30_warning_min = st.session_state.get(
            "limits_par30_warning_min", 0.04
        )  # 4%

        # Check access
        if not self._check_access():
            st.stop()

    # ------------------------------------------------------------------
    # ACCESS CONTROL + AUDIT
    # ------------------------------------------------------------------
    def _check_access(self) -> bool:
        """Minimal access check + audit logging for the page."""

        if not st.session_state.get("authenticated", False):
            st.error("🔐 Please log in to access this page")
            return False

        # Audit: successful page access
        try:
            self.audit_logger.log_event(
                user=self.user,
                action="page_access",
                module="01_Prudential_Overview",
                details={
                    "role": self.role,
                    "tenant": self.tenant,
                    "timestamp": datetime.now().isoformat(),
                },
            )
        except Exception:
            # We don't want the page to crash because of audit failures
            pass

        return True

    # ------------------------------------------------------------------
    # HEADER + MARQUEE
    # ------------------------------------------------------------------
    def render_strategic_header(self):
        """Render enterprise-grade strategic header."""
        st.markdown(
            f"""
        <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    padding: 25px 30px; border-radius: 16px; color: white; margin-bottom: 20px;">
            <h1 style="margin: 0; color: white;">📊 Prudential Compliance Overview</h1>
            <p style="margin: 5px 0 0 0; opacity: 0.9; color: #e0e7ff;">
            Strategic Risk Intelligence & Regulatory Performance Dashboard
            </p>
            <div style="margin-top: 10px; font-size: 0.9rem; opacity: 0.8;">
                <strong>📍</strong> Compliance Intelligence &gt; Strategic Overview | 
                <strong>🏢</strong> {self.tenant} |
                <strong>📅</strong> {datetime.now().strftime('%d %B %Y')} |
                <strong>👤</strong> {self.role}
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        self.render_compliance_marquee()

    def render_compliance_marquee(self):
        """Render real-time compliance status marquee."""
        status_messages = [
            "✅ SASRA Compliance: 92% complete | ⚠️ Risk Monitoring: 3 active alerts | 📊 Capital Adequacy: 22.1%",
            "🚨 Watch: Top employer concentration at 28% | 💧 Liquidity Buffer: 18.5% | 🎯 PAR Performance: 4.2%",
            "📈 Strategic Trend: Member growth +5% QoQ | 💼 Loan portfolio: KES 245.8M | ⚖️ Regulatory Score: 88/100",
            "🔔 Action Required: 2 pending compliance reviews | 📋 Audit Trail: 100% complete | 🛡️ Cybersecurity: Active",
        ]

        st.markdown(
            f"""
        <div style="background: linear-gradient(90deg, #0f766e 0%, #0d9488 100%); 
                    padding: 12px 20px; border-radius: 12px; margin-bottom: 24px;
                    border-left: 5px solid #14b8a6;">
            <marquee behavior="scroll" direction="left" scrollamount="4"
                     style="font-size: 0.95rem; font-weight: 500; color: white;">
                {' • '.join(status_messages)}
            </marquee>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # ------------------------------------------------------------------
    # KPI CARDS
    # ------------------------------------------------------------------
    def render_strategic_kpi_cards(self):
        """Render strategic KPI cards with compliance focus."""
        st.markdown("### 🎯 Strategic Compliance KPIs")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                label="📊 Capital Adequacy",
                value="22.1%",
                delta="+0.8%",
                delta_color="normal",
                help="SASRA Minimum: 15% | Strategic Target: 20%+",
            )
            st.caption("Core Tier 1 Capital Ratio")

        with col2:
            st.metric(
                label="🎯 PAR > 30 Days",
                value="4.2%",
                delta="-0.5%",
                delta_color="inverse",
                help="SASRA Threshold: 5% | Internal Target: <4%",
            )
            st.caption("Portfolio At Risk")

        with col3:
            st.metric(
                label="💧 Liquidity Ratio",
                value="18.5%",
                delta="+1.2%",
                help="Regulatory Minimum: 15% | Optimal: 20–25%",
            )
            st.caption("Cash to Deposits Ratio")

        with col4:
            st.metric(
                label="👥 Active Members",
                value="1,250",
                delta="+5.0%",
                help="Annual Growth Target: 8%",
            )
            st.caption("Member Retention: 94%")

        with col5:
            st.metric(
                label="⚖️ Compliance Score",
                value="88/100",
                delta="+3 points",
                help="Regulatory Compliance Index",
            )
            st.caption("Next Review: 15 Feb")

    # ------------------------------------------------------------------
    # TABS
    # ------------------------------------------------------------------
    def render_strategic_tabs(self):
        """Render strategic analysis tabs."""
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            [
                "📈 Portfolio Intelligence",
                "🎯 Risk Analytics",
                "⚖️ Compliance Monitoring",
                "🚀 Strategic Initiatives",
                "📊 Performance Frameworks",
            ]
        )

        with tab1:
            self.render_portfolio_intelligence()

        with tab2:
            self.render_risk_analytics()

        with tab3:
            self.render_compliance_monitoring()

        with tab4:
            self.render_strategic_initiatives()

        with tab5:
            self.render_performance_frameworks()

    # ------------------------------------------------------------------
    # TAB 1: PORTFOLIO INTELLIGENCE
    # ------------------------------------------------------------------
    def render_portfolio_intelligence(self):
        """Render comprehensive portfolio analysis."""
        st.subheader("📈 Portfolio Intelligence Dashboard")

        # Strategic filters (placeholders – currently not filtering mock data)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.selectbox(
                "Analysis Period",
                ["Last 12 Months", "Year to Date", "Quarterly", "Monthly"],
                key="portfolio_period",
            )
        with col2:
            st.selectbox(
                "Product Focus",
                [
                    "All Products",
                    "Personal Loans",
                    "Business Loans",
                    "Asset Finance",
                    "Emergency Loans",
                ],
                key="product_focus",
            )
        with col3:
            st.selectbox(
                "Risk Tier",
                ["All Tiers", "Low Risk", "Medium Risk", "High Risk"],
                key="risk_tier",
            )

        # Enhanced sample data (mock – replace with real warehouse later)
        dates = pd.date_range(start="2023-01-01", end="2024-01-01", freq="ME")
        portfolio_data = pd.DataFrame(
            {
                "Date": dates,
                "Total Portfolio (KES M)": np.random.normal(240, 10, len(dates)).cumsum(),
                "PAR 30+ Days (%)": np.random.uniform(3.5, 5.5, len(dates)),
                "Liquidity Ratio (%)": np.random.uniform(16, 20, len(dates)),
                "Active Members": np.random.normal(1200, 50, len(dates)).cumsum(),
                "Average Loan Size (KES K)": np.random.uniform(150, 250, len(dates)),
                "Yield (%)": np.random.uniform(12, 16, len(dates)),
            }
        )

        col1, col2 = st.columns(2)

        # ---- Left: portfolio growth + composition ----
        with col1:
            fig = px.line(
                portfolio_data,
                x="Date",
                y="Total Portfolio (KES M)",
                title="🏦 Loan Portfolio Growth Trend",
                labels={
                    "Total Portfolio (KES M)": "Portfolio Value (KES M)",
                    "Date": "",
                },
                line_shape="spline",
            )

            # Growth annotations
            for i in range(1, len(portfolio_data)):
                prev = portfolio_data.iloc[i - 1]["Total Portfolio (KES M)"]
                curr = portfolio_data.iloc[i]["Total Portfolio (KES M)"]
                growth = (curr - prev) / prev * 100

                if i % 3 == 0:
                    fig.add_annotation(
                        x=portfolio_data.iloc[i]["Date"],
                        y=curr,
                        text=f"+{growth:.1f}%",
                        showarrow=True,
                        arrowhead=1,
                        font=dict(size=10),
                    )

            fig.update_layout(
                hovermode="x unified",
                showlegend=False,
                plot_bgcolor="rgba(240, 240, 240, 0.1)",
            )
            st.plotly_chart(fig, use_container_width=True)

            # Product mix
            st.subheader("📊 Portfolio Composition")
            product_composition = pd.DataFrame(
                {
                    "Product": [
                        "Personal Loans",
                        "Business Loans",
                        "Asset Finance",
                        "Emergency",
                        "School Fees",
                    ],
                    "Exposure (KES M)": [85.2, 92.5, 45.3, 12.8, 9.9],
                    "Share (%)": [34.7, 37.6, 18.4, 5.2, 4.0],
                }
            )

            fig = px.pie(
                product_composition,
                values="Exposure (KES M)",
                names="Product",
                title="Product Mix Distribution",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3,
            )
            st.plotly_chart(fig, use_container_width=True)

        # ---- Right: risk-return + PAR trend ----
        with col2:
            st.subheader("🎯 Risk-Performance Matrix")

            product_metrics = pd.DataFrame(
                {
                    "Product": [
                        "Personal Loans",
                        "Business Loans",
                        "Asset Finance",
                        "Emergency",
                        "School Fees",
                    ],
                    "PAR (%)": [3.2, 5.8, 2.1, 8.5, 1.2],
                    "Yield (%)": [14.5, 16.2, 12.3, 18.5, 10.7],
                    "Growth (%)": [12.5, 8.2, 15.3, 25.1, 18.7],
                    "Size (KES M)": [85.2, 92.5, 45.3, 12.8, 9.9],
                }
            )

            fig = px.scatter(
                product_metrics,
                x="PAR (%)",
                y="Yield (%)",
                size="Size (KES M)",
                color="Growth (%)",
                title="Risk-Return Analysis by Product",
                hover_name="Product",
                size_max=50,
                color_continuous_scale="RdYlGn",
                labels={"PAR (%)": "Risk (PAR %)", "Yield (%)": "Return (Yield %)"},
            )

            fig.add_hline(
                y=product_metrics["Yield (%)"].mean(),
                line_dash="dash",
                line_color="gray",
            )
            fig.add_vline(
                x=product_metrics["PAR (%)"].mean(),
                line_dash="dash",
                line_color="gray",
            )

            fig.add_annotation(
                x=2,
                y=18,
                text="⭐ Stars",
                showarrow=False,
                font=dict(color="green", size=12),
            )
            fig.add_annotation(
                x=2,
                y=11,
                text="📊 Cash Cows",
                showarrow=False,
                font=dict(color="blue", size=12),
            )
            fig.add_annotation(
                x=7,
                y=18,
                text="⚠️ Question Marks",
                showarrow=False,
                font=dict(color="orange", size=12),
            )
            fig.add_annotation(
                x=7,
                y=11,
                text="🔍 Review Needed",
                showarrow=False,
                font=dict(color="red", size=12),
            )

            st.plotly_chart(fig, use_container_width=True)

            # PAR trend with thresholds
            fig = px.line(
                portfolio_data,
                x="Date",
                y="PAR 30+ Days (%)",
                title="📉 PAR 30+ Days Trend with Regulatory Thresholds",
                labels={"PAR 30+ Days (%)": "PAR %", "Date": ""},
                line_shape="spline",
            )

            fig.add_hline(
                y=self.par30_trigger_max * 100,
                line_dash="dash",
                line_color="red",
                annotation_text=f"SASRA Threshold ({self.par30_trigger_max*100:.1f}%)",
                annotation_position="bottom right",
            )
            fig.add_hline(
                y=self.par30_warning_min * 100,
                line_dash="dot",
                line_color="orange",
                annotation_text=f"Warning Level ({self.par30_warning_min*100:.1f}%)",
                annotation_position="top right",
            )

            fig.update_layout(
                hovermode="x unified",
                showlegend=False,
                plot_bgcolor="rgba(240, 240, 240, 0.1)",
            )
            st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------------------------------
    # TAB 2: RISK ANALYTICS
    # ------------------------------------------------------------------
    def render_risk_analytics(self):
        """Render comprehensive risk analytics."""
        st.subheader("🎯 Advanced Risk Analytics")

        col1, col2 = st.columns(2)

        # Left: risk heatmap + concentration
        with col1:
            st.markdown("##### 🔥 Risk Exposure Heatmap")

            risk_data = pd.DataFrame(
                {
                    "Risk Category": [
                        "Credit Risk",
                        "Liquidity Risk",
                        "Concentration Risk",
                        "Operational Risk",
                        "Market Risk",
                        "Compliance Risk",
                    ],
                    "Current Level": [4.2, 18.5, 28.0, 3.8, 2.1, 12.0],
                    "Target Level": [3.5, 20.0, 25.0, 3.0, 2.0, 5.0],
                    "Trend": [
                        "Improving",
                        "Stable",
                        "Worsening",
                        "Improving",
                        "Stable",
                        "Worsening",
                    ],
                }
            )

            fig = px.bar(
                risk_data,
                x="Risk Category",
                y="Current Level",
                color="Trend",
                title="Risk Exposure by Category",
                color_discrete_map={
                    "Improving": "#10b981",
                    "Stable": "#f59e0b",
                    "Worsening": "#ef4444",
                },
                text=risk_data["Current Level"].apply(lambda x: f"{x:.1f}%"),
            )

            for i, row in risk_data.iterrows():
                fig.add_shape(
                    type="line",
                    x0=i - 0.4,
                    x1=i + 0.4,
                    y0=row["Target Level"],
                    y1=row["Target Level"],
                    line=dict(color="red", width=2, dash="dash"),
                )

            fig.update_layout(xaxis_tickangle=-45, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("##### ⚖️ Concentration Analysis")
            employer_data = pd.DataFrame(
                {
                    "Employer": [
                        "Govt Agency A",
                        "Manufacturing B",
                        "School C",
                        "Hospital D",
                        "Others",
                    ],
                    "Exposure (%)": [28.0, 15.5, 12.3, 9.8, 34.4],
                    "PAR (%)": [3.2, 5.8, 1.5, 2.1, 4.5],
                }
            )

            fig = px.bar(
                employer_data,
                x="Employer",
                y="Exposure (%)",
                color="PAR (%)",
                title="Top Employer Exposure",
                color_continuous_scale="RdYlGn_r",
                text=employer_data["Exposure (%)"].apply(lambda x: f"{x:.1f}%"),
            )
            fig.add_hline(
                y=25,
                line_dash="dash",
                line_color="red",
                annotation_text="SASRA Limit (25%)",
            )
            st.plotly_chart(fig, use_container_width=True)

        # Right: radar + table
        with col2:
            st.markdown("##### 📊 Risk Radar Chart")

            categories = [
                "Credit Quality",
                "Liquidity",
                "Concentration",
                "Profitability",
                "Growth",
                "Compliance",
            ]

            fig = go.Figure()

            fig.add_trace(
                go.Scatterpolar(
                    r=[4.2, 18.5, 28.0, 14.5, 8.2, 12.0],
                    theta=categories,
                    fill="toself",
                    name="Current",
                    line_color="blue",
                )
            )

            fig.add_trace(
                go.Scatterpolar(
                    r=[3.5, 20.0, 25.0, 15.0, 10.0, 5.0],
                    theta=categories,
                    fill="toself",
                    name="Target",
                    line_color="red",
                )
            )

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 30]),
                ),
                showlegend=True,
                title="Risk Profile Comparison",
            )

            st.plotly_chart(fig, use_container_width=True)

            st.markdown("##### 📋 Risk Metrics Summary")

            risk_metrics = pd.DataFrame(
                {
                    "Metric": [
                        "PAR 30+ Days",
                        "PAR 90+ Days",
                        "NPL Ratio",
                        "Provision Coverage",
                        "Liquidity Ratio",
                        "Capital Adequacy",
                        "ROA",
                        "Cost to Income",
                    ],
                    "Current": [
                        "4.2%",
                        "1.8%",
                        "2.5%",
                        "85%",
                        "18.5%",
                        "22.1%",
                        "1.8%",
                        "62%",
                    ],
                    "Target": [
                        "<4.0%",
                        "<1.5%",
                        "<2.0%",
                        ">80%",
                        ">20%",
                        ">20%",
                        ">2.0%",
                        "<60%",
                    ],
                    "Status": [
                        "⚠️ Watch",
                        "✅ Good",
                        "⚠️ Watch",
                        "✅ Good",
                        "⚠️ Watch",
                        "✅ Good",
                        "⚠️ Watch",
                        "⚠️ Watch",
                    ],
                }
            )

            st.dataframe(
                risk_metrics,
                use_container_width=True,
                hide_index=True,
            )

    # ------------------------------------------------------------------
    # TAB 3: COMPLIANCE MONITORING
    # ------------------------------------------------------------------
    def render_compliance_monitoring(self):
        """Render compliance monitoring dashboard."""
        st.subheader("⚖️ Real-time Compliance Monitoring")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 📊 Compliance Scorecard")

            compliance_data = pd.DataFrame(
                {
                    "Area": [
                        "Capital Adequacy",
                        "Asset Quality",
                        "Management",
                        "Earnings",
                        "Liquidity",
                        "Sensitivity",
                        "Governance",
                    ],
                    "Score": [95, 88, 92, 85, 78, 90, 82],
                    "Status": [
                        "✅ Compliant",
                        "✅ Compliant",
                        "✅ Compliant",
                        "⚠️ Watch",
                        "⚠️ Watch",
                        "✅ Compliant",
                        "⚠️ Watch",
                    ],
                }
            )

            fig = px.bar(
                compliance_data,
                x="Area",
                y="Score",
                color="Status",
                title="CAMELS Compliance Ratings",
                color_discrete_map={
                    "✅ Compliant": "#10b981",
                    "⚠️ Watch": "#f59e0b",
                    "🔴 Non-Compliant": "#ef4444",
                },
                text=compliance_data["Score"].apply(lambda x: f"{x}%"),
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("##### 📅 Regulatory Timeline")

            deadlines = pd.DataFrame(
                {
                    "Requirement": [
                        "SASRA Q4 Returns",
                        "Annual Audit",
                        "Board Risk Report",
                        "Member AGM",
                        "CBK Reporting",
                        "Tax Compliance",
                    ],
                    "Due Date": [
                        "2024-01-31",
                        "2024-02-28",
                        "2024-03-15",
                        "2024-03-31",
                        "2024-04-30",
                        "2024-05-15",
                    ],
                    "Days Left": [15, 43, 58, 74, 104, 119],
                    "Status": [
                        "In Progress",
                        "Scheduled",
                        "Planned",
                        "Planned",
                        "Upcoming",
                        "Upcoming",
                    ],
                }
            )

            st.dataframe(deadlines, use_container_width=True, hide_index=True)

        with col2:
            st.markdown("##### 🔔 Compliance Alerts & Actions")

            alerts_data = {
                "Date": [
                    "2024-01-15 14:30",
                    "2024-01-14 09:15",
                    "2024-01-13 16:45",
                    "2024-01-12 11:20",
                    "2024-01-11 10:00",
                ],
                "Alert Type": [
                    "PAR Warning",
                    "Concentration",
                    "Liquidity",
                    "Employer Limit",
                    "Governance",
                ],
                "Severity": ["Medium", "High", "Low", "Medium", "Low"],
                "Description": [
                    "PAR30 approaching threshold at 4.2% - Review required",
                    "Top employer exposure at 28% of portfolio - Immediate action",
                    "Liquidity ratio improved to 18.5% - Monitor trend",
                    "Employer XYZ exposure exceeds 25% limit - Risk committee review",
                    "Board committee meeting overdue - Schedule immediately",
                ],
                "Owner": [
                    "Risk Manager",
                    "CEO",
                    "Treasurer",
                    "Risk Committee",
                    "Secretary",
                ],
            }

            alerts_df = pd.DataFrame(alerts_data)

            edited_df = st.data_editor(
                alerts_df,
                use_container_width=True,
                hide_index=True,
            )

            if st.button("🔄 Update Alert Status", use_container_width=True):
                # In production, you’d persist `edited_df` to the audit/compliance DB
                st.success("Alert status updated successfully!")

    # ------------------------------------------------------------------
    # TAB 4: STRATEGIC INITIATIVES
    # ------------------------------------------------------------------
    def render_strategic_initiatives(self):
        """Render strategic initiatives tracking."""
        st.subheader("🚀 Strategic Initiatives Dashboard")

        initiatives = [
            {
                "name": "Automated SASRA Reporting",
                "description": "Implement automated regulatory reporting system",
                "progress": 85,
                "owner": "Compliance Team",
                "timeline": "Q1 2024",
                "impact": "Reduced reporting time by 70%",
            },
            {
                "name": "Risk-Based Pricing Model",
                "description": "Develop AI-driven risk-based pricing framework",
                "progress": 60,
                "owner": "Risk Department",
                "timeline": "Q2 2024",
                "impact": "Improved yield by 2.5%",
            },
            {
                "name": "Member Value Enhancement",
                "description": "Launch digital member engagement platform",
                "progress": 45,
                "owner": "Marketing",
                "timeline": "Q3 2024",
                "impact": "Increased member satisfaction by 15%",
            },
            {
                "name": "Cybersecurity Upgrade",
                "description": "Implement advanced security infrastructure",
                "progress": 90,
                "owner": "IT Security",
                "timeline": "Q1 2024",
                "impact": "Reduced security incidents by 95%",
            },
        ]

        for initiative in initiatives:
            with st.expander(
                f"{initiative['name']} - {initiative['progress']}% complete",
                expanded=True,
            ):
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Progress", f"{initiative['progress']}%")

                with col2:
                    st.metric("Owner", initiative["owner"])

                with col3:
                    st.metric("Timeline", initiative["timeline"])

                with col4:
                    st.metric("Impact", initiative["impact"])

                st.progress(
                    initiative["progress"] / 100, text="Implementation Status"
                )
                st.caption(initiative["description"])

                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(
                        "📋 View Details", key=f"details_{initiative['name']}"
                    ):
                        st.info(f"Detailed plan loaded for {initiative['name']}")
                with col_b:
                    if st.button(
                        "🚀 Update Progress", key=f"update_{initiative['name']}"
                    ):
                        st.success(
                            f"Progress updated for {initiative['name']}"
                        )

    # ------------------------------------------------------------------
    # TAB 5: PERFORMANCE FRAMEWORKS
    # ------------------------------------------------------------------
    def render_performance_frameworks(self):
        """Render performance frameworks and methodologies."""
        st.subheader("📊 Performance Analysis Frameworks")

        frameworks = [
            {
                "name": "CAMELS Framework",
                "description": "Capital, Assets, Management, Earnings, Liquidity, Sensitivity",
                "application": "Regulatory compliance assessment",
                "status": "Active",
            },
            {
                "name": "BCG Matrix",
                "description": "Stars, Cash Cows, Question Marks, Dogs analysis",
                "application": "Portfolio strategy optimization",
                "status": "Active",
            },
            {
                "name": "Risk-Adjusted Return",
                "description": "Return on risk-adjusted capital (RORAC)",
                "application": "Product profitability analysis",
                "status": "Pilot",
            },
            {
                "name": "SWOT Analysis",
                "description": "Strengths, Weaknesses, Opportunities, Threats",
                "application": "Strategic planning",
                "status": "Active",
            },
            {
                "name": "PDCA Cycle",
                "description": "Plan, Do, Check, Act continuous improvement",
                "application": "Process optimization",
                "status": "Active",
            },
            {
                "name": "Balanced Scorecard",
                "description": "Financial, Customer, Internal, Learning perspectives",
                "application": "Performance measurement",
                "status": "Planned",
            },
        ]

        cols = st.columns(3)
        for idx, framework in enumerate(frameworks):
            with cols[idx % 3]:
                st.markdown(
                    f"""
                <div style="background: #f8fafc; padding: 15px; border-radius: 10px; 
                                border-left: 4px solid #3b82f6; margin-bottom: 10px;">
                    <strong>{framework['name']}</strong><br>
                    <small>{framework['description']}</small><br>
                    <small><strong>Application:</strong> {framework['application']}</small><br>
                    <small><strong>Status:</strong> {framework['status']}</small>
                </div>
                """,
                    unsafe_allow_html=True,
                )

        st.markdown("##### 📈 Framework Implementation Metrics")

        implementation_data = pd.DataFrame(
            {
                "Framework": [
                    "CAMELS",
                    "BCG Matrix",
                    "Risk-Adjusted Return",
                    "SWOT",
                    "PDCA",
                    "Balanced Scorecard",
                ],
                "Adoption Rate": [100, 85, 45, 95, 75, 20],
                "User Satisfaction": [92, 88, 75, 90, 82, 65],
                "Business Impact": [95, 85, 60, 80, 78, 40],
            }
        )

        fig = px.bar(
            implementation_data,
            x="Framework",
            y=["Adoption Rate", "User Satisfaction", "Business Impact"],
            title="Framework Implementation Performance",
            barmode="group",
        )
        st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------------------------------
    # COMPLIANCE PHILOSOPHY
    # ------------------------------------------------------------------
    def render_compliance_philosophy(self):
        """Render compliance philosophy framework."""
        with st.expander("📜 Compliance Philosophy Framework", expanded=False):
            cols = st.columns(3)
            for i, (key, value) in enumerate(COMPLIANCE_PHILOSOPHY.items()):
                with cols[i % 3]:
                    st.info(f"**{key}:**\n\n{value}")

            st.markdown("---")
            st.markdown(
                """
            **Strategic Approach:**  
            - **Proactive Compliance:** Anticipate regulatory changes  
            - **Data-Driven Decisions:** Use analytics for risk assessment  
            - **Continuous Improvement:** Regular review and enhancement  
            - **Stakeholder Transparency:** Clear reporting and communication  
            - **Regulatory Intelligence:** Stay ahead of compliance requirements
            """
            )

    # ------------------------------------------------------------------
    # ENTRY POINT
    # ------------------------------------------------------------------
    def run(self):
        """Run the enhanced overview page."""
        self.render_strategic_header()
        self.render_strategic_kpi_cards()
        self.render_compliance_philosophy()

        st.markdown("---")
        self.render_strategic_tabs()

        # Audit: dashboard completion
        try:
            self.audit_logger.log_event(
                user=self.user,
                action="strategic_overview_completed",
                module="01_Prudential_Overview",
                details={
                    "role": self.role,
                    "tenant": self.tenant,
                    "timestamp": datetime.now().isoformat(),
                },
            )
        except Exception:
            pass


# ----------------------------------------------------------------------
# Helper used by app.py
# ----------------------------------------------------------------------
def render():
    """Convenience entrypoint for the unified app."""
    page = OverviewPage()
    page.run()


# Optional: allow running standalone (for quick testing)
if __name__ == "__main__":
    page = OverviewPage()
    page.run()