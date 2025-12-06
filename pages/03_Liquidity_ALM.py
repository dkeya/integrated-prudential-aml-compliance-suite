# pages/03_Liquidity_ALM.py - ENHANCED WITH ENTERPRISE FEATURES

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Make sure Python can see the project root so `core.*` works
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 🔽 LOCAL / PROJECT IMPORTS (unified core modules)
from core.config import ConfigManager
from core.rbac import RBACManager
from core.audit import AuditLogger, audit_logger
from core.sidebar import render_sidebar

# ==============================================
# LIQUIDITY & ALM PHILOSOPHY FRAMEWORK
# ==============================================
LIQUIDITY_PHILOSOPHY = {
    "Data": "What's our current liquidity position and maturity mismatch exposure?",
    "Insights": "Why are liquidity gaps emerging and where are maturity mismatches?",
    "Frameworks": "How to assess using SASRA liquidity ratios and ALM gap analysis",
    "Actions": "What specific liquidity management, funding strategies to implement",
    "Impact": "What value it creates (avoided funding crises, optimal investment, regulatory compliance)",
    "Governance": "How liquidity decisions are documented and ALM strategies are monitored"
}

# ❗ Do NOT call st.set_page_config here – it is already called in app.py

# Check authentication and render sidebar
if not st.session_state.get("authenticated", False):
    st.error("🔐 Please log in to access this page")
    st.stop()

# Render unified sidebar
render_sidebar()


class LiquidityALMPage:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.rbac_manager = RBACManager()
        # You can use either the shared instance or a new one – keep pattern consistent
        self.audit_logger = audit_logger  # unified audit logger instance
        self.config = self.config_manager.load_settings()

        if not self._check_access():
            st.stop()

    def _check_access(self):
        """Check if user has access to this page"""
        if not st.session_state.get("authenticated", False):
            st.error("Please login to access this page")
            return False

        has_access = self.rbac_manager.check_page_access(
            "03_Liquidity_ALM.py",
            st.session_state.role,
            self.config,
        )

        if not has_access:
            st.error("You do not have permission to access this page")
            # Log failed access attempt, but don't break the app if logging fails
            try:
                self.audit_logger.log_action(
                    user=st.session_state.username,
                    role=st.session_state.role,
                    action="unauthorized_access_attempt",
                    object_type="page",
                    object_id="03_Liquidity_ALM.py",
                )
            except Exception:
                pass
            return False

        # Log successful page access – safe fallback
        try:
            self.audit_logger.log_data_access(
                st.session_state.user,
                st.session_state.role,
                "liquidity_alm_intelligence",
            )
        except Exception:
            try:
                self.audit_logger.log_action(
                    user=st.session_state.user,
                    role=st.session_state.role,
                    action="page_access",
                    object_type="dashboard",
                    object_id="03_Liquidity_ALM.py",
                )
            except Exception:
                pass

        return True

    def render_strategic_header(self):
        """Render enterprise-grade strategic header"""
        st.markdown(
            f"""
        <div style="background: linear-gradient(135deg, #0ea5e9 0%, #0369a1 100%);
                    padding: 25px 30px; border-radius: 16px; color: white; margin-bottom: 20px;">
            <h1 style="margin: 0; color: white;">💧 Liquidity Intelligence & ALM Analytics</h1>
            <p style="margin: 5px 0 0 0; opacity: 0.9; color: #e0f2fe;">
            Cash Flow Management • Maturity Mismatch Analysis • Funding Strategy Optimization
            </p>
            <div style="margin-top: 10px; font-size: 0.9rem; opacity: 0.8;">
                <strong>📍</strong> Treasury Management > Liquidity Dashboard | 
                <strong>🏢</strong> {st.session_state.get('tenant', 'Central SACCO')} |
                <strong>📅</strong> {datetime.now().strftime('%d %B %Y')} |
                <strong>👤</strong> {st.session_state.get('role', 'Treasury Manager')}
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Liquidity Status Marquee
        self.render_liquidity_status_marquee()

    def render_liquidity_status_marquee(self):
        """Render real-time liquidity status marquee"""
        status_messages = [
            "✅ Liquidity Ratio: 18.5% (Above 15% minimum) | 💰 Cash Buffer: KES 52.3M",
            "📈 Deposit Growth: +8.2% MoM | 📉 Loan-to-Deposit Ratio: 78.5% (Target: <80%)",
            "🔒 ALM Status: Positive cumulative gap | ⚠️ Watch: 31-90 day maturity mismatch",
            "🏦 Funding Sources: 65% member deposits, 25% institutional, 10% interbank",
        ]

        st.markdown(
            f"""
        <div style="background: linear-gradient(90deg, #0ea5e9 0%, #0369a1 100%); 
                    padding: 12px 20px; border-radius: 12px; margin-bottom: 24px;
                    border-left: 5px solid #38bdf8;">
            <marquee behavior="scroll" direction="left" scrollamount="4"
                     style="font-size: 0.95rem; font-weight: 500; color: white;">
                {' • '.join(status_messages)}
            </marquee>
        </div>
        """,
            unsafe_allow_html=True,
        )

    def render_strategic_kpi_cards(self):
        """Render strategic liquidity KPIs"""
        st.markdown("### 🎯 Liquidity Performance Indicators")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                label="💧 Liquidity Ratio",
                value="18.5%",
                delta="+1.2%",
                help="SASRA Minimum: 15% | Target: 20-25%",
            )
            st.caption("Cash/Deposits Ratio")

        with col2:
            st.metric(
                label="📊 Loan-to-Deposit",
                value="78.5%",
                delta="-2.3%",
                delta_color="inverse",
                help="Regulatory Watch: 80% | Target: <75%",
            )
            st.caption("Lending Capacity")

        with col3:
            st.metric(
                label="💰 Cash Buffer",
                value="KES 52.3M",
                delta="+KES 4.2M",
                help="Available liquid funds",
            )
            st.caption("Immediate Liquidity")

        with col4:
            st.metric(
                label="📈 Deposit Growth",
                value="+8.2%",
                delta="+1.5%",
                help="Monthly deposit growth rate",
            )
            st.caption("Funding Stability")

        with col5:
            st.metric(
                label="⚖️ ALM Gap",
                value="+KES 15.2M",
                delta="+KES 2.1M",
                help="Cumulative maturity gap",
            )
            st.caption("Positive = Asset sensitive")

    def generate_enhanced_liquidity_data(self):
        """Generate enhanced liquidity trend data"""
        dates = pd.date_range(start="2023-01-01", end="2024-01-01", freq="ME")

        # Base trends with realistic patterns
        base_cash = 45
        base_deposits = 240
        growth_trend = 1 + (np.arange(len(dates)) * 0.01)  # 1% monthly growth trend
        seasonality = np.sin(np.arange(len(dates)) * np.pi / 6) * 5  # 6-month cycle

        liquidity_data = pd.DataFrame(
            {
                "date": dates,
                "cash_equivalents": base_cash * growth_trend
                + seasonality
                + np.random.uniform(-3, 3, len(dates)),
                "short_term_investments": np.random.uniform(15, 25, len(dates))
                * growth_trend,
                "total_deposits": base_deposits * growth_trend
                + seasonality * 2
                + np.random.uniform(-5, 5, len(dates)),
                "loan_disbursements": np.random.uniform(15, 25, len(dates))
                * growth_trend,
                "member_withdrawals": np.random.uniform(8, 15, len(dates)),
                "operational_cash_flow": np.random.uniform(-2, 5, len(dates)),
            }
        )

        # Calculate derived metrics
        liquidity_data["liquidity_ratio"] = (
            liquidity_data["cash_equivalents"]
            / liquidity_data["total_deposits"]
            * 100
        )
        liquidity_data["loan_to_deposit"] = (
            liquidity_data["loan_disbursements"].cumsum()
            / liquidity_data["total_deposits"]
            * 100
        )
        liquidity_data["cash_buffer_days"] = (
            liquidity_data["cash_equivalents"]
            / liquidity_data["member_withdrawals"].rolling(30).mean()
            * 30
        )

        # Add trend indicators
        liquidity_data["liquidity_trend"] = (
            liquidity_data["liquidity_ratio"].pct_change() * 100
        )
        liquidity_data["deposit_growth"] = (
            liquidity_data["total_deposits"].pct_change() * 100
        )

        return liquidity_data

    def generate_enhanced_alm_data(self):
        """Generate enhanced ALM gap analysis data"""
        buckets = [
            "Overnight",
            "1-7 Days",
            "8-30 Days",
            "31-90 Days",
            "91-180 Days",
            "181-365 Days",
            "1-3 Years",
            "3+ Years",
        ]

        # More realistic asset-liability distribution
        gap_data = pd.DataFrame(
            {
                "Bucket": buckets,
                "Assets": [15.2, 25.8, 45.3, 60.5, 40.2, 35.8, 20.5, 10.2],
                "Liabilities": [20.5, 35.2, 55.8, 50.3, 30.5, 25.8, 15.2, 5.8],
                "Rate_Sensitive_Assets": [80, 75, 70, 65, 60, 55, 40, 20],
                "Rate_Sensitive_Liabilities": [85, 80, 75, 60, 50, 40, 30, 15],
                "Interest_Rate_Assets": [2.5, 3.0, 4.5, 5.2, 6.0, 7.5, 9.0, 10.5],
                "Interest_Rate_Liabilities": [1.5, 2.0, 3.0, 3.8, 4.5, 5.0, 6.5, 8.0],
            }
        )

        # Calculate gaps and sensitivities
        gap_data["Periodic_Gap"] = gap_data["Assets"] - gap_data["Liabilities"]
        gap_data["Cumulative_Gap"] = gap_data["Periodic_Gap"].cumsum()
        gap_data["Rate_Sensitive_Gap"] = (
            gap_data["Rate_Sensitive_Assets"] - gap_data["Rate_Sensitive_Liabilities"]
        )
        gap_data["Net_Interest_Margin_Impact"] = (
            gap_data["Rate_Sensitive_Gap"] * 0.01
        )  # 1% rate change impact

        return gap_data

    def render_strategic_tabs(self):
        """Render strategic analysis tabs"""
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            [
                "💧 Liquidity Intelligence Dashboard",
                "📊 ALM Gap & Duration Analysis",
                "💰 Funding Strategy Optimization",
                "🚀 Liquidity Risk Management",
                "📈 Treasury Performance Frameworks",
            ]
        )

        with tab1:
            self.render_liquidity_intelligence_dashboard()

        with tab2:
            self.render_alm_gap_duration_analysis()

        with tab3:
            self.render_funding_strategy_optimization()

        with tab4:
            self.render_liquidity_risk_management()

        with tab5:
            self.render_treasury_performance_frameworks()

    def render_liquidity_intelligence_dashboard(self):
        """Render comprehensive liquidity intelligence dashboard"""
        st.subheader("💧 Liquidity Intelligence Dashboard")

        # Strategic filters
        col1, col2, col3 = st.columns(3)
        with col1:
            time_period = st.selectbox(
                "Analysis Period",
                ["Last 12 Months", "Year to Date", "Quarterly", "Monthly"],
                key="liquidity_period",
            )
        with col2:
            view_type = st.selectbox(
                "View Type",
                ["Amounts (KES)", "Ratios (%)", "Trend Analysis", "Comparison"],
                key="liquidity_view",
            )
        with col3:
            scenario = st.selectbox(
                "Scenario Analysis",
                ["Current", "Stress Scenario 1", "Stress Scenario 2", "Growth Scenario"],
                key="liquidity_scenario",
            )

        # Get enhanced data
        liquidity_data = self.generate_enhanced_liquidity_data()

        col1, col2 = st.columns(2)

        with col1:
            # Enhanced liquidity ratio analysis
            st.markdown("##### 📈 Liquidity Ratio Trend Analysis")

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=liquidity_data["date"],
                    y=liquidity_data["liquidity_ratio"],
                    name="Liquidity Ratio",
                    mode="lines+markers",
                    line=dict(color="#0ea5e9", width=3),
                    fill="tozeroy",
                    fillcolor="rgba(14, 165, 233, 0.1)",
                    hovertemplate="%{y:.1f}%<extra></extra>",
                )
            )

            # Add regulatory thresholds
            fig.add_hline(
                y=self.config.limits.liquidity_ratio_min * 100,
                line_dash="dash",
                line_color="red",
                annotation_text=f"SASRA Minimum ({self.config.limits.liquidity_ratio_min * 100:.0f}%)",
                annotation_position="bottom right",
            )

            fig.add_hline(
                y=25,  # Optimal target
                line_dash="dot",
                line_color="green",
                annotation_text="Optimal Target (25%)",
                annotation_position="top right",
            )

            # Add trend line
            z = np.polyfit(
                range(len(liquidity_data)), liquidity_data["liquidity_ratio"], 1
            )
            p = np.poly1d(z)
            fig.add_trace(
                go.Scatter(
                    x=liquidity_data["date"],
                    y=p(range(len(liquidity_data))),
                    name="Trend Line",
                    line=dict(color="orange", dash="dash", width=2),
                    hovertemplate="Trend: %{y:.1f}%<extra></extra>",
                )
            )

            fig.update_layout(
                title="Liquidity Ratio Trend with Regulatory Thresholds",
                xaxis_title="Date",
                yaxis_title="Liquidity Ratio (%)",
                hovermode="x unified",
                plot_bgcolor="rgba(240, 240, 240, 0.1)",
                showlegend=True,
            )

            st.plotly_chart(fig, use_container_width=True)

            # Cash flow composition
            st.markdown("##### 💰 Cash Flow Composition")

            latest = liquidity_data.iloc[-1]
            cash_components = pd.DataFrame(
                {
                    "Component": [
                        "Cash & Equivalents",
                        "Short-term Investments",
                        "Loan Disbursements",
                        "Member Withdrawals",
                        "Operational Cash Flow",
                    ],
                    "Amount (KES M)": [
                        latest["cash_equivalents"],
                        latest["short_term_investments"],
                        latest["loan_disbursements"],
                        latest["member_withdrawals"],
                        latest["operational_cash_flow"],
                    ],
                    "Type": ["Asset", "Asset", "Outflow", "Outflow", "Net"],
                }
            )

            fig = px.bar(
                cash_components,
                x="Component",
                y="Amount (KES M)",
                color="Type",
                title="Monthly Cash Flow Components",
                color_discrete_map={
                    "Asset": "#0ea5e9",
                    "Outflow": "#ef4444",
                    "Net": "#10b981",
                },
                text=cash_components["Amount (KES M)"].apply(
                    lambda x: f"KES {x:.1f}M"
                ),
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Multi-metric dashboard
            st.markdown("##### 📊 Liquidity Metrics Dashboard")

            latest = liquidity_data.iloc[-1]
            previous = liquidity_data.iloc[-2]

            metrics = [
                {
                    "name": "Liquidity Ratio",
                    "current": latest["liquidity_ratio"],
                    "previous": previous["liquidity_ratio"],
                    "threshold": self.config.limits.liquidity_ratio_min * 100,
                    "target": 25.0,
                },
                {
                    "name": "Cash Buffer Days",
                    "current": latest.get("cash_buffer_days", 45),
                    "previous": previous.get("cash_buffer_days", 42),
                    "threshold": 30,  # Minimum days
                    "target": 60,  # Optimal days
                },
                {
                    "name": "Deposit Growth",
                    "current": latest.get("deposit_growth", 8.2),
                    "previous": previous.get("deposit_growth", 6.7),
                    "threshold": 5.0,  # Minimum growth
                    "target": 10.0,  # Target growth
                },
                {
                    "name": "Loan-to-Deposit",
                    "current": latest.get("loan_to_deposit", 78.5),
                    "previous": previous.get("loan_to_deposit", 80.8),
                    "threshold": 80.0,  # Watch level
                    "target": 75.0,  # Target
                },
            ]

            for metric in metrics:
                delta = metric["current"] - metric["previous"]
                # Default colour
                delta_color = "normal"

                if metric["name"] == "Loan-to-Deposit":
                    # For Loan-to-Deposit, *lower* is better
                    delta_color = "inverse" if delta > 0 else "normal"
                else:
                    # For other metrics, higher is generally better
                    delta_color = "normal" if delta >= 0 else "inverse"

                col_a, col_b, col_c = st.columns([3, 2, 1])
                with col_a:
                    st.metric(
                        label=metric["name"],
                        value=f"{metric['current']:.1f}{'%' if metric['name'] != 'Cash Buffer Days' else ' days'}",
                        delta=f"{delta:+.1f}",
                    )
                with col_b:
                    if metric["current"] < metric["threshold"]:
                        st.markdown(
                            "<div style='color: #dc2626; font-size: 0.8rem;'>🔴 Below Min</div>",
                            unsafe_allow_html=True,
                        )
                    elif metric["current"] > metric["target"]:
                        st.markdown(
                            "<div style='color: #10b981; font-size: 0.8rem;'>🟢 Above Target</div>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            "<div style='color: #f59e0b; font-size: 0.8rem;'>🟡 Within Range</div>",
                            unsafe_allow_html=True,
                        )
                with col_c:
                    gap_to_target = metric["current"] - metric["target"]
                    st.caption(f"{gap_to_target:+.1f} to target")

            # Liquidity heatmap by source
            st.markdown("##### 🔥 Liquidity Source Heatmap")

            source_data = pd.DataFrame(
                {
                    "Source": [
                        "Member Deposits",
                        "Institutional Funds",
                        "Interbank",
                        "Investments",
                        "Operational Cash",
                    ],
                    "Amount (KES M)": [180.5, 65.2, 28.3, 42.8, 12.5],
                    "Stability Score": [90, 75, 60, 85, 95],
                    "Cost (%)": [1.2, 2.5, 3.8, 4.2, 0.5],
                }
            )

            source_data["Share %"] = (
                source_data["Amount (KES M)"]
                / source_data["Amount (KES M)"].sum()
                * 100
            )

            fig = px.scatter(
                source_data,
                x="Cost (%)",
                y="Stability Score",
                size="Amount (KES M)",
                color="Share %",
                hover_name="Source",
                title="Liquidity Source Analysis (Size = Amount, Color = Share %)",
                size_max=50,
                color_continuous_scale="Blues",
                labels={
                    "Cost (%)": "Funding Cost",
                    "Stability Score": "Stability (0-100)",
                    "Share %": "Market Share %",
                },
            )

            # Add optimal zone
            fig.add_shape(
                type="rect",
                x0=0.5,
                x1=2.5,
                y0=80,
                y1=100,
                line=dict(color="green", width=1, dash="dot"),
                fillcolor="rgba(0, 255, 0, 0.1)",
            )
            fig.add_annotation(
                x=1.5,
                y=90,
                text="Optimal Zone",
                showarrow=False,
                font=dict(color="green", size=10),
            )

            st.plotly_chart(fig, use_container_width=True)

    def render_alm_gap_duration_analysis(self):
        """Render comprehensive ALM gap and duration analysis"""
        st.subheader("📊 ALM Gap & Duration Analysis")

        gap_data = self.generate_enhanced_alm_data()

        col1, col2 = st.columns(2)

        with col1:
            # Enhanced gap analysis
            st.markdown("##### ⚖️ Maturity Gap Analysis")

            fig = go.Figure()

            # Assets and Liabilities bars
            fig.add_trace(
                go.Bar(
                    name="Assets",
                    x=gap_data["Bucket"],
                    y=gap_data["Assets"],
                    marker_color="#0ea5e9",
                    text=gap_data["Assets"].apply(lambda x: f"KES {x:.1f}M"),
                    textposition="outside",
                )
            )

            fig.add_trace(
                go.Bar(
                    name="Liabilities",
                    x=gap_data["Bucket"],
                    y=gap_data["Liabilities"],
                    marker_color="#ef4444",
                    text=gap_data["Liabilities"].apply(lambda x: f"KES {x:.1f}M"),
                    textposition="outside",
                )
            )

            fig.update_layout(
                title="Assets vs Liabilities by Maturity Bucket",
                xaxis_title="Maturity Bucket",
                yaxis_title="Amount (KES M)",
                barmode="group",
                xaxis_tickangle=-45,
                showlegend=True,
            )

            st.plotly_chart(fig, use_container_width=True)

            # Gap analysis details
            st.markdown("##### 📈 Cumulative Gap Analysis")

            fig = go.Figure()

            fig.add_trace(
                go.Bar(
                    x=gap_data["Bucket"],
                    y=gap_data["Periodic_Gap"],
                    name="Periodic Gap",
                    marker_color=[
                        "red" if x < 0 else "green"
                        for x in gap_data["Periodic_Gap"]
                    ],
                    text=gap_data["Periodic_Gap"].apply(lambda x: f"{x:+.1f}"),
                    textposition="outside",
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=gap_data["Bucket"],
                    y=gap_data["Cumulative_Gap"],
                    name="Cumulative Gap",
                    mode="lines+markers",
                    line=dict(color="orange", width=3),
                    text=gap_data["Cumulative_Gap"].apply(
                        lambda x: f"KES {x:.1f}M"
                    ),
                    textposition="top center",
                )
            )

            fig.update_layout(
                title="Maturity Gap Analysis",
                xaxis_title="Maturity Bucket",
                yaxis_title="Gap Amount (KES M)",
                xaxis_tickangle=-45,
                showlegend=True,
            )

            # Add zero line for reference
            fig.add_hline(y=0, line_dash="dash", line_color="black")

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Interest rate sensitivity analysis
            st.markdown("##### 📊 Interest Rate Sensitivity")

            fig = go.Figure()

            fig.add_trace(
                go.Bar(
                    name="Rate Sensitive Assets",
                    x=gap_data["Bucket"],
                    y=gap_data["Rate_Sensitive_Assets"],
                    marker_color="#3b82f6",
                    text=gap_data["Rate_Sensitive_Assets"].apply(
                        lambda x: f"{x}%"
                    ),
                    textposition="inside",
                )
            )

            fig.add_trace(
                go.Bar(
                    name="Rate Sensitive Liabilities",
                    x=gap_data["Bucket"],
                    y=gap_data["Rate_Sensitive_Liabilities"],
                    marker_color="#ef4444",
                    text=gap_data["Rate_Sensitive_Liabilities"].apply(
                        lambda x: f"{x}%"
                    ),
                    textposition="inside",
                )
            )

            fig.update_layout(
                title="Interest Rate Sensitivity by Maturity",
                xaxis_title="Maturity Bucket",
                yaxis_title="Rate Sensitive (%)",
                barmode="group",
                xaxis_tickangle=-45,
                showlegend=True,
            )

            st.plotly_chart(fig, use_container_width=True)

            # Net interest margin impact
            st.markdown("##### 💰 NIM Impact Analysis")

            fig = go.Figure()

            fig.add_trace(
                go.Bar(
                    x=gap_data["Bucket"],
                    y=gap_data["Net_Interest_Margin_Impact"],
                    name="NIM Impact",
                    marker_color=[
                        "red" if x < 0 else "green"
                        for x in gap_data["Net_Interest_Margin_Impact"]
                    ],
                    text=gap_data["Net_Interest_Margin_Impact"].apply(
                        lambda x: f"{x:+.2f}%"
                    ),
                    textposition="outside",
                )
            )

            fig.update_layout(
                title="Net Interest Margin Impact per 1% Rate Change",
                xaxis_title="Maturity Bucket",
                yaxis_title="NIM Impact (%)",
                xaxis_tickangle=-45,
                showlegend=False,
            )

            # Add cumulative impact line
            cumulative_impact = gap_data["Net_Interest_Margin_Impact"].cumsum()
            fig.add_trace(
                go.Scatter(
                    x=gap_data["Bucket"],
                    y=cumulative_impact,
                    name="Cumulative Impact",
                    mode="lines+markers",
                    line=dict(color="purple", width=2, dash="dash"),
                )
            )

            st.plotly_chart(fig, use_container_width=True)

            # Duration analysis
            st.markdown("##### ⏱️ Duration Analysis")

            duration_data = pd.DataFrame(
                {
                    "Metric": [
                        "Asset Duration",
                        "Liability Duration",
                        "Duration Gap",
                        "Duration of Equity",
                        "Immunization Gap",
                    ],
                    "Value (Years)": [2.8, 1.5, 1.3, 4.2, 0.8],
                    "Target": [2.5, 1.8, 0.7, 3.5, 0.5],
                    "Status": ["Slightly High", "Low", "High", "High", "High"],
                }
            )

            fig = px.bar(
                duration_data,
                x="Metric",
                y="Value (Years)",
                color="Status",
                title="Duration Analysis Metrics",
                color_discrete_map={
                    "High": "#ef4444",
                    "Low": "#f59e0b",
                    "Slightly High": "#10b981",
                },
                text=duration_data["Value (Years)"].apply(
                    lambda x: f"{x:.1f} yrs"
                ),
            )

            # Add target lines
            for i, row in duration_data.iterrows():
                fig.add_shape(
                    type="line",
                    x0=i - 0.4,
                    x1=i + 0.4,
                    y0=row["Target"],
                    y1=row["Target"],
                    line=dict(color="red", width=2, dash="dash"),
                )

            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

    def render_funding_strategy_optimization(self):
        """Render funding strategy optimization analysis"""
        st.subheader("💰 Funding Strategy Optimization")

        # Funding strategy analysis
        strategies = [
            {
                "strategy": "Core Deposit Growth",
                "description": "Increase member deposits through value-added services",
                "current_share": "65%",
                "target_share": "70%",
                "cost": "1.2%",
                "stability": "High",
                "implementation": "6 months",
                "expected_impact": "+KES 25M deposits",
            },
            {
                "strategy": "Institutional Funding",
                "description": "Develop relationships with institutional depositors",
                "current_share": "25%",
                "target_share": "20%",
                "cost": "2.5%",
                "stability": "Medium",
                "implementation": "3 months",
                "expected_impact": "Reduce cost by 0.5%",
            },
            {
                "strategy": "Interbank Market",
                "description": "Optimize short-term interbank borrowing",
                "current_share": "10%",
                "target_share": "10%",
                "cost": "3.8%",
                "stability": "Low",
                "implementation": "1 month",
                "expected_impact": "Flexibility for liquidity spikes",
            },
            {
                "strategy": "Investment Liquidity",
                "description": "Optimize short-term investment portfolio",
                "current_share": "N/A",
                "target_share": "N/A",
                "cost": "4.2%",
                "stability": "High",
                "implementation": "2 months",
                "expected_impact": "+0.8% yield on liquidity",
            },
        ]

        for strategy in strategies:
            with st.expander(
                f"{strategy['strategy']} - Cost: {strategy['cost']}", expanded=True
            ):
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Current Share", strategy["current_share"])
                with col2:
                    st.metric("Target Share", strategy["target_share"])
                with col3:
                    st.metric("Implementation", strategy["implementation"])
                with col4:
                    stability_color = {
                        "High": "green",
                        "Medium": "orange",
                        "Low": "red",
                    }.get(strategy["stability"], "black")
                    st.markdown(
                        f"**Stability:** <span style='color:{stability_color};'>{strategy['stability']}</span>",
                        unsafe_allow_html=True,
                    )

                st.markdown(f"**Description:** {strategy['description']}")
                st.markdown(f"**Expected Impact:** {strategy['expected_impact']}")

                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(
                        f"📋 Develop Plan", key=f"plan_{strategy['strategy']}"
                    ):
                        st.info(
                            f"Strategy development started for {strategy['strategy']}"
                        )
                with col_b:
                    if st.button(
                        f"📊 Track Progress", key=f"track_{strategy['strategy']}"
                    ):
                        st.success(
                            f"Progress tracking initiated for {strategy['strategy']}"
                        )

        # Funding mix optimization
        st.markdown("##### 📈 Optimal Funding Mix Analysis")

        funding_mix = pd.DataFrame(
            {
                "Source": ["Member Deposits", "Institutional", "Interbank", "Equity"],
                "Current Mix": [65, 25, 10, 0],
                "Optimal Mix": [70, 20, 5, 5],
                "Cost": [1.2, 2.5, 3.8, 0.0],
                "Stability": [90, 75, 60, 100],
            }
        )

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                name="Current Mix",
                x=funding_mix["Source"],
                y=funding_mix["Current Mix"],
                marker_color="#0ea5e9",
                text=funding_mix["Current Mix"].apply(lambda x: f"{x}%"),
                textposition="outside",
            )
        )

        fig.add_trace(
            go.Bar(
                name="Optimal Mix",
                x=funding_mix["Source"],
                y=funding_mix["Optimal Mix"],
                marker_color="#10b981",
                text=funding_mix["Optimal Mix"].apply(lambda x: f"{x}%"),
                textposition="outside",
            )
        )

        fig.update_layout(
            title="Current vs Optimal Funding Mix",
            xaxis_title="Funding Source",
            yaxis_title="Percentage (%)",
            barmode="group",
            xaxis_tickangle=-45,
        )

        st.plotly_chart(fig, use_container_width=True)

    def render_liquidity_risk_management(self):
        """Render liquidity risk management framework"""
        st.subheader("🚀 Liquidity Risk Management Framework")

        # Risk management actions
        actions = [
            {
                "risk": "Funding Concentration",
                "actions": [
                    "Diversify funding sources beyond top 5 members",
                    "Develop institutional deposit program",
                    "Establish contingency funding lines",
                ],
                "owner": "Treasury Manager",
                "deadline": "2024-03-31",
                "priority": "High",
            },
            {
                "risk": "Maturity Mismatch",
                "actions": [
                    "Implement ALM gap limits by bucket",
                    "Develop liquidity buffer strategy",
                    "Review and adjust investment maturity profile",
                ],
                "owner": "ALM Committee",
                "deadline": "2024-02-28",
                "priority": "High",
            },
            {
                "risk": "Regulatory Compliance",
                "actions": [
                    "Daily monitoring of liquidity ratios",
                    "Monthly stress testing implementation",
                    "Quarterly ALM committee reporting",
                ],
                "owner": "Compliance Officer",
                "deadline": "Ongoing",
                "priority": "Medium",
            },
            {
                "risk": "Market Access Risk",
                "actions": [
                    "Establish relationships with multiple banks",
                    "Develop emergency funding protocol",
                    "Regular review of market conditions",
                ],
                "owner": "CFO",
                "deadline": "2024-04-30",
                "priority": "Medium",
            },
        ]

        for action in actions:
            with st.expander(
                f"{action['priority']} Priority: {action['risk']}", expanded=True
            ):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Owner", action["owner"])
                with col2:
                    st.metric("Deadline", action["deadline"])
                with col3:
                    priority_color = {
                        "High": "red",
                        "Medium": "orange",
                        "Low": "green",
                    }.get(action["priority"], "black")
                    st.markdown(
                        f"**Priority:** <span style='color:{priority_color};'>{action['priority']}</span>",
                        unsafe_allow_html=True,
                    )

                st.markdown("**Action Items:**")
                for item in action["actions"]:
                    st.markdown(f"• {item}")

                if st.button(
                    f"📋 Update Status", key=f"status_{action['risk']}"
                ):
                    st.success(f"Status updated for {action['risk']} management")

    def render_treasury_performance_frameworks(self):
        """Render treasury performance frameworks"""
        st.subheader("📈 Treasury Performance Frameworks")

        # Framework implementation
        frameworks = [
            {
                "name": "SASRA Liquidity Framework",
                "description": "Regulatory liquidity ratios and monitoring requirements",
                "metrics": ["Liquidity Ratio", "Loan-to-Deposit", "Cash Buffer"],
                "status": "Fully Implemented",
                "compliance": "98%",
            },
            {
                "name": "ALM Gap Analysis",
                "description": "Maturity mismatch analysis and interest rate risk",
                "metrics": ["Periodic Gap", "Cumulative Gap", "Duration Gap"],
                "status": "Fully Implemented",
                "compliance": "95%",
            },
            {
                "name": "Liquidity Stress Testing",
                "description": "Scenario analysis for liquidity crises",
                "metrics": ["Survival Period", "Funding Gap", "Contingency Plan"],
                "status": "Partial Implementation",
                "compliance": "70%",
            },
            {
                "name": "Funds Transfer Pricing",
                "description": "Internal pricing for liquidity and funds",
                "metrics": ["FTP Rates", "Margin Analysis", "Profit Attribution"],
                "status": "Implementation Phase",
                "compliance": "45%",
            },
        ]

        cols = st.columns(2)
        for idx, framework in enumerate(frameworks):
            with cols[idx % 2]:
                with st.container():
                    st.markdown(
                        f"""
                    <div style="background: #f8fafc; padding: 15px; border-radius: 10px; 
                                border-left: 4px solid #0ea5e9; margin-bottom: 10px;">
                        <strong>{framework['name']}</strong><br>
                        <small>{framework['description']}</small><br>
                        <small><strong>Metrics:</strong> {', '.join(framework['metrics'])}</small><br>
                        <small><strong>Status:</strong> {framework['status']}</small><br>
                        <small><strong>Compliance:</strong> {framework['compliance']}</small>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

        # Framework performance metrics
        st.markdown("##### 📊 Framework Performance Metrics")

        performance_data = pd.DataFrame(
            {
                "Framework": [
                    "SASRA Liquidity",
                    "ALM Gap",
                    "Stress Testing",
                    "FTP",
                ],
                "Accuracy Score": [95, 92, 78, 65],
                "Implementation %": [98, 95, 70, 45],
                "User Adoption": [90, 88, 65, 40],
                "Business Impact": [96, 94, 75, 55],
            }
        )

        fig = px.bar(
            performance_data,
            x="Framework",
            y=[
                "Accuracy Score",
                "Implementation %",
                "User Adoption",
                "Business Impact",
            ],
            title="Treasury Framework Performance",
            barmode="group",
            color_discrete_sequence=[
                "#0ea5e9",
                "#38bdf8",
                "#7dd3fc",
                "#bae6fd",
            ],
        )
        st.plotly_chart(fig, use_container_width=True)

    def render_liquidity_philosophy(self):
        """Render liquidity and ALM philosophy framework"""
        with st.expander("📜 Liquidity Management Philosophy", expanded=False):
            cols = st.columns(3)
            for i, (key, value) in enumerate(LIQUIDITY_PHILOSOPHY.items()):
                with cols[i % 3]:
                    st.info(f"**{key}:**\n\n{value}")

            st.markdown("---")
            st.markdown(
                """
            **Strategic Liquidity Management Approach:**  
            - **Prudent Buffer:** Maintain liquidity above regulatory minimums  
            - **Maturity Matching:** Align asset and liability maturities  
            - **Diversified Funding:** Reduce concentration in funding sources  
            - **Stress Testing:** Regular scenario analysis for liquidity crises  
            - **Cost Optimization:** Balance liquidity costs with safety needs  
            - **Regulatory Compliance:** Adherence to SASRA liquidity requirements
            """
            )

    def run(self):
        """Run the enhanced liquidity ALM page"""
        # Strategic Header
        self.render_strategic_header()

        # Liquidity Management Philosophy
        self.render_liquidity_philosophy()

        # Strategic KPI Cards
        self.render_strategic_kpi_cards()

        st.markdown("---")

        # Strategic Analysis Tabs
        self.render_strategic_tabs()

        # Log dashboard completion - using unified audit logger
        try:
            self.audit_logger.log_action(
                user=st.session_state.user,
                role=st.session_state.role,
                action="liquidity_alm_dashboard_completed",
                object_type="dashboard",
                object_id="03_Liquidity_ALM.py",
            )
        except Exception:
            # If for any reason logging fails, don't break the app
            pass


if __name__ == "__main__":
    page = LiquidityALMPage()
    page.run()