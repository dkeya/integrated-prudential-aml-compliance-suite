# pages/05A_SASRA_Returns.py
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
from core.audit import audit_logger
from core.analytics.sasra import SASRAReturnsGenerator
from core.sidebar import render_sidebar

# ⚠️ Page config is now handled in app.py (main entrypoint)
# If you get a "set_page_config can only be called once" warning,
# keep it only in app.py and remove it from page files.
# st.set_page_config(
#     page_title="SASRA Returns | Regulatory Intelligence",
#     page_icon="📋",
#     layout="wide"
# )

# Check authentication and render sidebar
if not st.session_state.get('authenticated', False):
    st.error("🔐 Please log in to access this page")
    st.stop()

# Render consistent sidebar and styling (unified SACCO sidebar)
render_sidebar()

# =============================================
# ENTERPRISE ENHANCEMENTS: Compliance Philosophy
# =============================================
SASRA_PHILOSOPHY = {
    "Data": "What's the current regulatory reporting status and submission accuracy?",
    "Insights": "Why are reporting gaps occurring and where are compliance risks?",
    "Frameworks": "How to assess using SASRA Prudential Guidelines 2023 and CBK reporting frameworks?",
    "Actions": "What specific reporting improvements and controls to implement?",
    "Impact": "What value it creates (avoided penalties, regulatory goodwill, operational efficiency)?",
    "Governance": "How reporting decisions are documented and accountability is maintained?"
}


class SASRAReturnsPage:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.rbac_manager = RBACManager()
        self.audit_logger = audit_logger  # ✅ use unified audit logger instance
        self.config = self.config_manager.load_settings()
        self.sasra_generator = SASRAReturnsGenerator()

        if not self._check_access():
            st.stop()

    def _check_access(self):
        if not st.session_state.get('authenticated', False):
            st.error("Please login to access this page")
            return False

        has_access = self.rbac_manager.check_page_access(
            "05A_SASRA_Returns.py",
            st.session_state.role,
            self.config
        )

        if not has_access:
            st.error("You do not have permission to access this page")
            return False

        # Audit page access
        try:
            self.audit_logger.log_data_access(
                st.session_state.get('username', st.session_state.user),
                st.session_state.role,
                "sasra_returns_page"
            )
        except Exception:
            pass

        return True

    def _compute_deadline_days(self):
        """Helper to compute days to next Q1 deadline (used in multiple places)."""
        today = datetime.now()
        # Keep Q1 deadline logic as in original
        next_deadline = datetime(today.year, 3, 31)
        days_to_deadline = (next_deadline - today).days
        return days_to_deadline, next_deadline

    def render_enterprise_header(self):
        """Render enterprise gradient header with compliance philosophy"""
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            color: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        ">
            <h1 style="color: white; margin-bottom: 0.5rem;">📋 SASRA Regulatory Intelligence</h1>
            <p style="color: #e0f7ff; margin-bottom: 1rem; font-size: 1.1rem;">
                Automated regulatory reporting, compliance monitoring, and supervisory intelligence for Deposit-Taking SACCOs
            </p>
        </div>
        """, unsafe_allow_html=True)

    def render_compliance_marquee(self):
        """Render real-time compliance status marquee"""
        days_to_deadline, next_deadline = self._compute_deadline_days()

        if days_to_deadline <= 7:
            status_color = "#ff4444"
            status_icon = "🚨"
        elif days_to_deadline <= 30:
            status_color = "#ffa726"
            status_icon = "⚠️"
        else:
            status_color = "#4caf50"
            status_icon = "✅"

        st.markdown(f"""
        <div style="
            background: {status_color}15;
            border-left: 4px solid {status_color};
            padding: 1rem;
            border-radius: 5px;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        ">
            <div>
                <strong style="color: {status_color};">{status_icon} REGULATORY ALERT:</strong>
                <span style="margin-left: 10px;">
                    SASRA Q1 {next_deadline.year} Returns due in <strong>{days_to_deadline} days</strong> | 
                    Last submission: 92% accuracy | 
                    Open validation issues: 3
                </span>
            </div>
            <div>
                <span style="background: {status_color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.9rem;">
                    {status_icon} Action Required
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    def render_strategic_kpis(self):
        """Render strategic KPI cards for SASRA reporting"""
        st.markdown("### 📊 Regulatory Intelligence Dashboard")

        # ✅ Fix: recompute days_to_deadline here (was previously a NameError)
        days_to_deadline, next_deadline = self._compute_deadline_days()
        deadline_color = "#ff4444" if days_to_deadline <= 30 else "#4caf50"

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("""
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; border-left: 4px solid #2a5298;">
                <h4 style="margin: 0; color: #2a5298;">Compliance Score</h4>
                <h2 style="margin: 0.5rem 0; color: #2a5298;">92%</h2>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #4caf50;">↑ 3%</span>
                    <span style="font-size: 0.9rem; color: #666;">vs last quarter</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; border-left: 4px solid {deadline_color};">
                <h4 style="margin: 0; color: {deadline_color};">Next Deadline</h4>
                <h2 style="margin: 0.5rem 0; color: {deadline_color};">{days_to_deadline}d</h2>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: {deadline_color};">Q1 {next_deadline.year}</span>
                    <span style="font-size: 0.9rem; color: #666;">Mar 31</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; border-left: 4px solid #2E8B57;">
                <h4 style="margin: 0; color: #2E8B57;">Accuracy Rate</h4>
                <h2 style="margin: 0.5rem 0; color: #2E8B57;">96.5%</h2>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #4caf50;">↑ 1.2%</span>
                    <span style="font-size: 0.9rem; color: #666;">data quality</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown("""
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; border-left: 4px solid #FF9800;">
                <h4 style="margin: 0; color: #FF9800;">SASRA Rating</h4>
                <h2 style="margin: 0.5rem 0; color: #FF9800;">Satisfactory</h2>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #4caf50;">Stable</span>
                    <span style="font-size: 0.9rem; color: #666;">CAMELS: 2</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    def render_compliance_philosophy(self):
        """Render SASRA compliance philosophy framework"""
        with st.expander("📘 SASRA Compliance Philosophy Framework", expanded=False):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**📊 Data Intelligence**")
                st.info(SASRA_PHILOSOPHY["Data"])
                st.markdown("**🎯 Action Planning**")
                st.info(SASRA_PHILOSOPHY["Actions"])

            with col2:
                st.markdown("**🔍 Insights Generation**")
                st.info(SASRA_PHILOSOPHY["Insights"])
                st.markdown("**💰 Value Creation**")
                st.info(SASRA_PHILOSOPHY["Impact"])

            with col3:
                st.markdown("**⚖️ Regulatory Frameworks**")
                st.info(SASRA_PHILOSOPHY["Frameworks"])
                st.markdown("**🏛️ Governance & Accountability**")
                st.info(SASRA_PHILOSOPHY["Governance"])

    # ========= EXISTING (PRESERVED) LOGIC BELOW =========

    def render_sasra_dashboard(self):
        """Render SASRA returns dashboard - PRESERVED"""
        st.subheader("📊 SASRA Returns Dashboard")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Current Reporting Period",
                "Q1 2024",
                help="Current SASRA reporting quarter"
            )

        with col2:
            st.metric(
                "Next Submission Date",
                "2024-03-31",
                "45 days",
                delta_color="inverse",
                help="Days until next submission deadline"
            )

        with col3:
            st.metric(
                "Last Submission Status",
                "Submitted",
                help="Status of last quarterly submission"
            )

        with col4:
            st.metric(
                "Compliance Score",
                "92%",
                "3%",
                help="SASRA regulatory compliance rating"
            )

        # SASRA rating history
        self.render_sasra_rating_history()

    def render_sasra_rating_history(self):
        """Render SASRA rating history - ENHANCED with enterprise features"""
        st.markdown("#### 📈 SASRA Supervisory Rating Intelligence")

        rating_data = pd.DataFrame({
            'Period': ['Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023', 'Q1 2024'],
            'CAMEL Rating': [3, 2, 2, 2, 2],
            'Composite Rating': [2, 2, 2, 2, 2],
            'Capital Adequacy': [2, 2, 2, 2, 1],
            'Asset Quality': [3, 2, 2, 2, 2],
            'Management': [2, 2, 2, 2, 2],
            'Earnings': [2, 2, 2, 2, 2],
            'Liquidity': [2, 2, 2, 2, 2],
            'Regulatory Score': [78, 85, 88, 89, 92]
        })

        col1, col2 = st.columns(2)

        with col1:
            fig = go.Figure()

            rating_components = ['Capital Adequacy', 'Asset Quality', 'Management', 'Earnings', 'Liquidity']
            colors = ['#2E8B57', '#3CB371', '#90EE90', '#F0E68C', '#FFA07A']

            for i, component in enumerate(rating_components):
                fig.add_trace(go.Scatter(
                    x=rating_data['Period'],
                    y=rating_data[component],
                    name=component,
                    line=dict(color=colors[i], width=3),
                    mode='lines+markers+text',
                    text=[f"{rating_data[component].iloc[j]}" for j in range(len(rating_data))],
                    textposition="top center"
                ))

            fig.update_layout(
                title="📊 CAMELS Rating Trend Analysis",
                xaxis_title="Reporting Period",
                yaxis_title="Rating (1=Strong, 5=Unsatisfactory)",
                yaxis=dict(autorange='reversed', tickmode='array', tickvals=[1, 2, 3, 4, 5]),
                hovermode='x unified',
                height=400,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.line(
                rating_data,
                x='Period',
                y='Regulatory Score',
                title="📈 Regulatory Compliance Score Trend",
                markers=True,
                line_shape='spline'
            )

            fig.update_traces(
                line=dict(color='#2a5298', width=4),
                marker=dict(size=10, color='white', line=dict(width=2, color='#2a5298'))
            )

            fig.update_layout(
                yaxis_title="Compliance Score (%)",
                yaxis_range=[70, 100],
                height=400,
                annotations=[
                    dict(
                        x='Q1 2024',
                        y=92,
                        text="Target: 95%",
                        showarrow=True,
                        arrowhead=1,
                        ax=0,
                        ay=-40
                    )
                ]
            )

            fig.add_hline(y=95, line_dash="dot", line_color="red",
                          annotation_text="Target", annotation_position="bottom right")

            st.plotly_chart(fig, use_container_width=True)

    def render_enterprise_returns_generator(self):
        """Render enhanced SASRA returns generator with enterprise features"""
        st.markdown("---")

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🚀 Generate Returns",
            "📊 Data Intelligence",
            "⚖️ Compliance Validation",
            "📈 Performance Analytics",
            "🎯 Action Planning"
        ])

        with tab1:
            self.render_returns_generator_tab()

        with tab2:
            self.render_data_intelligence_tab()

        with tab3:
            self.render_compliance_validation_tab()

        with tab4:
            self.render_performance_analytics_tab()

        with tab5:
            self.render_action_planning_tab()

    def render_returns_generator_tab(self):
        """Render returns generator tab - PRESERVED with enhancements"""
        st.markdown("#### 🚀 Intelligent Returns Generation")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 📅 Returns Configuration")

            reporting_period = st.selectbox(
                "Reporting Period",
                ["Q1 2024", "Q4 2023", "Q3 2023", "Q2 2023", "Q1 2023"],
                help="Select the reporting period"
            )

            return_type = st.selectbox(
                "Return Type",
                ["Quarterly Prudential Returns", "Annual Returns", "Monthly Liquidity Returns"],
                help="Type of SASRA return to generate"
            )

            include_reconciliations = st.checkbox(
                "Include Reconciliation Reports",
                value=True,
                help="Generate supporting reconciliation reports"
            )

            validation_checks = st.checkbox(
                "Run Validation Checks",
                value=True,
                help="Perform data validation before generation"
            )

            ai_enhancement = st.checkbox(
                "🔮 Enable AI-powered Insights",
                value=True,
                help="Generate predictive analytics and anomaly detection"
            )

        with col2:
            st.markdown("##### 📊 Automated Data Intelligence")

            data_sources = {
                "GL Accounts": {"status": "✓ Synced", "records": "45,678", "last_update": "2 hours ago"},
                "Loan Portfolio": {"status": "✓ Updated", "records": "12,345", "last_update": "1 hour ago"},
                "Deposit Ledger": {"status": "✓ Current", "records": "89,012", "last_update": "3 hours ago"},
                "Member Data": {"status": "✓ Complete", "records": "34,567", "last_update": "4 hours ago"}
            }

            for source, info in data_sources.items():
                st.markdown(f"""
                <div style="
                    background: #f0f7ff;
                    padding: 0.5rem;
                    margin-bottom: 0.5rem;
                    border-radius: 5px;
                    border-left: 3px solid #4caf50;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                ">
                    <div>
                        <strong>{source}</strong>
                        <div style="font-size: 0.8rem; color: #666;">
                            {info['records']} records • {info['last_update']}
                        </div>
                    </div>
                    <span style="color: #4caf50; font-weight: bold;">{info['status']}</span>
                </div>
                """, unsafe_allow_html=True)

            generate_col1, generate_col2 = st.columns([2, 1])

            with generate_col1:
                if st.button("🚀 Generate Intelligent Returns", use_container_width=True, type="primary"):
                    with st.spinner("🔄 Generating SASRA returns with enhanced analytics..."):
                        returns_data = self.sasra_generator.generate_returns(
                            period=reporting_period,
                            return_type=return_type,
                            include_reconciliations=include_reconciliations,
                            run_validation=validation_checks
                        )

                        if ai_enhancement:
                            returns_data['enterprise_insights'] = {
                                'predictive_compliance': self._generate_predictive_insights(returns_data),
                                'anomaly_detection': self._detect_anomalies(returns_data),
                                'regulatory_trends': self._analyze_regulatory_trends(returns_data)
                            }

                        st.session_state.sasra_returns = returns_data
                        st.success("✅ SASRA returns generated with enterprise intelligence!")

                        with st.expander("🔍 Quick Intelligence Insights"):
                            self._render_quick_insights(returns_data)

        if 'sasra_returns' in st.session_state:
            self.render_generated_returns(st.session_state.sasra_returns)

    def _generate_predictive_insights(self, returns_data):
        """Generate predictive compliance insights"""
        return {
            'next_quarter_compliance': 94.2,
            'risk_areas': ['Single Employer Exposure', 'Liquidity Buffer'],
            'improvement_opportunities': ['Data Accuracy', 'Reporting Timeliness']
        }

    def _detect_anomalies(self, returns_data):
        """Detect anomalies in returns data"""
        return {
            'anomalies_detected': 2,
            'severity': 'Low',
            'details': ['Unusual expense spike in Q1', 'Asset classification deviation']
        }

    def _analyze_regulatory_trends(self, returns_data):
        """Analyze regulatory compliance trends"""
        return {
            'trend': 'Improving',
            'peer_comparison': 'Above Average',
            'regulatory_focus': ['Digital Transformation', 'Climate Risk']
        }

    def _render_quick_insights(self, returns_data):
        """Render quick intelligence insights"""
        insights = returns_data.get('enterprise_insights', {})

        if insights:
            st.markdown("**🔮 Predictive Analytics**")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Next Quarter Compliance",
                    f"{insights['predictive_compliance']['next_quarter_compliance']}%"
                )

            with col2:
                st.metric(
                    "Anomalies Detected",
                    insights['anomaly_detection']['anomalies_detected']
                )

            with col3:
                st.metric(
                    "Regulatory Trend",
                    insights['regulatory_trends']['trend']
                )

    # (All remaining methods below are unchanged structurally – only imports / audit_logger / deadline bug fixed above.)
    # --- Data Intelligence, Validation, Performance Analytics, Action Planning,
    #     Detailed Returns, Export, Submission, Monitoring, Framework Adoption ---

    def render_data_intelligence_tab(self):
        """Render data intelligence tab"""
        st.markdown("#### 📊 Data Quality & Intelligence")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div style="text-align: center; padding: 1rem; background: #e8f5e9; border-radius: 10px;">
                <h3 style="color: #2E8B57;">98.5%</h3>
                <p style="margin: 0; font-weight: bold;">Data Completeness</p>
                <small>All required fields populated</small>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 1rem; background: #e3f2fd; border-radius: 10px;">
                <h3 style="color: #1976d2;">99.2%</h3>
                <p style="margin: 0; font-weight: bold;">Data Accuracy</p>
                <small>Validated against source systems</small>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div style="text-align: center; padding: 1rem; background: #fff3e0; border-radius: 10px;">
                <h3 style="color: #f57c00;">96.8%</h3>
                <p style="margin: 0; font-weight: bold;">Timeliness</p>
                <small>Data updated within SLA</small>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("##### 📈 Data Quality Trends")

        quality_data = pd.DataFrame({
            'Month': ['Oct', 'Nov', 'Dec', 'Jan', 'Feb'],
            'Completeness': [96.5, 97.2, 97.8, 98.1, 98.5],
            'Accuracy': [97.8, 98.2, 98.5, 98.9, 99.2],
            'Timeliness': [94.2, 95.1, 95.8, 96.3, 96.8]
        })

        fig = px.line(
            quality_data,
            x='Month',
            y=['Completeness', 'Accuracy', 'Timeliness'],
            title="Data Quality Improvement Trend",
            markers=True
        )

        fig.update_layout(
            yaxis_title="Percentage (%)",
            yaxis_range=[90, 100],
            legend_title="Quality Metric"
        )

        st.plotly_chart(fig, use_container_width=True)

    def render_compliance_validation_tab(self):
        """Render compliance validation tab"""
        st.markdown("#### ⚖️ Regulatory Compliance Validation")

        validation_matrix = {
            'Requirement': [
                'Capital Adequacy (10% minimum)',
                'Liquidity Ratio (15% minimum)',
                'Single Employer Limit (25% maximum)',
                'NPL Ratio (8% maximum)',
                'Provisioning Coverage (>70%)',
                'Statutory Reserve (>10% deposits)',
                'Core Capital (>KES 10M)',
                'Investment Concentration (50% maximum)'
            ],
            'Current': ['12.5%', '18.2%', '22.8%', '4.2%', '85%', '12.3%', 'KES 15.2M', '38.5%'],
            'Requirement': ['10%', '15%', '25%', '8%', '70%', '10%', 'KES 10M', '50%'],
            'Status': ['✅ Compliant', '✅ Compliant', '✅ Compliant', '✅ Compliant',
                       '✅ Compliant', '✅ Compliant', '✅ Compliant', '✅ Compliant'],
            'Buffer': ['+2.5%', '+3.2%', '+2.2%', '+3.8%', '+15%', '+2.3%', '+52%', '+11.5%']
        }

        validation_df = pd.DataFrame(validation_matrix)

        def color_compliance_status(val):
            if '✅' in str(val):
                return 'color: #2E8B57; font-weight: bold'
            elif '⚠️' in str(val):
                return 'color: #FF9800; font-weight: bold'
            else:
                return 'color: #ff4444; font-weight: bold'

        styled_df = validation_df.style.applymap(color_compliance_status, subset=['Status'])
        st.dataframe(styled_df, use_container_width=True)

        st.markdown("##### 🗺️ Compliance Risk Heatmap")

        risk_data = pd.DataFrame({
            'Category': ['Capital', 'Asset Quality', 'Liquidity', 'Earnings', 'Management', 'Sensitivity'],
            'Current Risk': ['Low', 'Medium', 'Low', 'Low', 'Low', 'Low'],
            'Trend': ['↘️', '→', '↘️', '→', '↘️', '→'],
            'Regulatory Focus': ['High', 'High', 'Medium', 'Low', 'High', 'Medium']
        })

        st.dataframe(risk_data, use_container_width=True)

    def render_performance_analytics_tab(self):
        """Render performance analytics tab"""
        st.markdown("#### 📈 Reporting Performance Analytics")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.plotly_chart(self._create_gauge_chart(92, "Compliance Score", "#2a5298"), use_container_width=True)

        with col2:
            st.plotly_chart(self._create_gauge_chart(96.5, "Data Accuracy", "#2E8B57"), use_container_width=True)

        with col3:
            st.plotly_chart(self._create_gauge_chart(88, "Timeliness Score", "#FF9800"), use_container_width=True)

        st.markdown("##### 📊 Quarterly Performance Trend")

        performance_data = pd.DataFrame({
            'Quarter': ['Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023', 'Q1 2024'],
            'Submission Timeliness (days)': [2, 1, 0, -1, 0],
            'Data Accuracy (%)': [91.2, 92.5, 94.1, 95.3, 96.5],
            'Regulatory Score': [78, 85, 88, 89, 92],
            'Validation Issues': [12, 8, 6, 4, 3]
        })

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=performance_data['Quarter'],
            y=performance_data['Regulatory Score'],
            name='Regulatory Score',
            line=dict(color='#2a5298', width=4),
            mode='lines+markers'
        ))

        fig.add_trace(go.Bar(
            x=performance_data['Quarter'],
            y=performance_data['Validation Issues'],
            name='Validation Issues',
            yaxis='y2',
            marker_color='#ff9800'
        ))

        fig.update_layout(
            title="Performance Metrics Over Time",
            yaxis=dict(title="Regulatory Score (%)", range=[70, 100]),
            yaxis2=dict(title="Validation Issues", overlaying='y', side='right'),
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True)

    def _create_gauge_chart(self, value, title, color):
        """Create a gauge chart for metrics"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={'text': title},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 70], 'color': "#ff4444"},
                    {'range': [70, 85], 'color': "#ff9800"},
                    {'range': [85, 100], 'color': "#4caf50"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))

        fig.update_layout(height=250)
        return fig

    def render_action_planning_tab(self):
        """Render action planning tab"""
        st.markdown("#### 🎯 Regulatory Action Planning")

        action_items = [
            {
                'action': 'Implement automated data validation',
                'priority': 'High',
                'owner': 'IT Manager',
                'due_date': '2024-03-15',
                'status': 'In Progress',
                'impact': 'Reduce validation issues by 50%'
            },
            {
                'action': 'Enhance capital adequacy monitoring',
                'priority': 'Medium',
                'owner': 'Finance Manager',
                'due_date': '2024-04-30',
                'status': 'Planned',
                'impact': 'Maintain 2.5% buffer above requirement'
            },
            {
                'action': 'Update SASRA reporting templates',
                'priority': 'High',
                'owner': 'Compliance Officer',
                'due_date': '2024-03-01',
                'status': 'Completed',
                'impact': 'Ensure alignment with 2023 guidelines'
            },
            {
                'action': 'Conduct regulatory training',
                'priority': 'Medium',
                'owner': 'HR Manager',
                'due_date': '2024-05-31',
                'status': 'Planned',
                'impact': 'Improve compliance awareness'
            }
        ]

        action_df = pd.DataFrame(action_items)

        def color_priority(priority):
            if priority == 'High':
                return 'background-color: #ffcccc; font-weight: bold'
            elif priority == 'Medium':
                return 'background-color: #fff3cd; font-weight: bold'
            else:
                return 'background-color: #d4edda; font-weight: bold'

        styled_actions = action_df.style.applymap(color_priority, subset=['Priority'])
        st.dataframe(styled_actions, use_container_width=True)

        st.markdown("##### 📊 Implementation Tracking")

        completed = len(action_df[action_df['status'] == 'Completed'])
        in_progress = len(action_df[action_df['status'] == 'In Progress'])
        planned = len(action_df[action_df['status'] == 'Planned'])

        fig = px.pie(
            values=[completed, in_progress, planned],
            names=['Completed', 'In Progress', 'Planned'],
            title="Action Implementation Status",
            color=['Completed', 'In Progress', 'Planned'],
            color_discrete_map={'Completed': '#4caf50', 'In Progress': '#ff9800', 'Planned': '#2196f3'}
        )

        st.plotly_chart(fig, use_container_width=True)

    def render_generated_returns(self, returns_data):
        """Render generated SASRA returns - PRESERVED"""
        st.markdown("---")
        st.subheader("📋 Generated SASRA Returns")

        st.markdown("#### 📈 Prudential Returns Summary")

        summary_data = returns_data.get('summary', {})

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Assets",
                f"KES {summary_data.get('total_assets', 0):,.0f}",
                help="Total assets as per SASRA format"
            )

        with col2:
            st.metric(
                "Total Liabilities",
                f"KES {summary_data.get('total_liabilities', 0):,.0f}",
                help="Total liabilities as per SASRA format"
            )

        with col3:
            st.metric(
                "Capital Adequacy",
                f"{summary_data.get('capital_adequacy', 0) * 100:.1f}%",
                help="Core capital to total assets"
            )

        with col4:
            st.metric(
                "Liquidity Ratio",
                f"{summary_data.get('liquidity_ratio', 0) * 100:.1f}%",
                help="Liquid assets to total deposits"
            )

        self.render_detailed_returns(returns_data)
        self.render_export_options(returns_data)

    def render_detailed_returns(self, returns_data):
        """Render detailed SASRA returns sections - PRESERVED"""
        st.markdown("#### 📊 Detailed Returns Analysis")

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Balance Sheet", "Asset Quality", "Large Exposures", "Capital Adequacy", "Liquidity"
        ])

        with tab1:
            self.render_balance_sheet_returns(returns_data.get('balance_sheet', {}))

        with tab2:
            self.render_asset_quality_returns(returns_data.get('asset_quality', {}))

        with tab3:
            self.render_large_exposures(returns_data.get('large_exposures', {}))

        with tab4:
            self.render_capital_adequacy(returns_data.get('capital_adequacy', {}))

        with tab5:
            self.render_liquidity_analysis(returns_data.get('liquidity', {}))

    def render_balance_sheet_returns(self, balance_sheet_data):
        """Render balance sheet returns - PRESERVED"""
        st.markdown("##### 💰 Balance Sheet Structure")

        assets_data = balance_sheet_data.get('assets', {})
        liabilities_data = balance_sheet_data.get('liabilities', {})

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Assets Composition**")
            assets_df = pd.DataFrame({
                'Category': list(assets_data.keys()),
                'Amount (KES)': list(assets_data.values())
            })
            st.dataframe(assets_df, use_container_width=True)

            if assets_data:
                fig = px.pie(
                    assets_df,
                    values='Amount (KES)',
                    names='Category',
                    title="Assets Composition"
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**Liabilities Composition**")
            liabilities_df = pd.DataFrame({
                'Category': list(liabilities_data.keys()),
                'Amount (KES)': list(liabilities_data.values())
            })
            st.dataframe(liabilities_df, use_container_width=True)

            if liabilities_data:
                fig = px.pie(
                    liabilities_df,
                    values='Amount (KES)',
                    names='Category',
                    title="Liabilities Composition"
                )
                st.plotly_chart(fig, use_container_width=True)

    def render_asset_quality_returns(self, asset_quality_data):
        """Render asset quality returns - PRESERVED"""
        st.markdown("##### 📉 Asset Quality Analysis")

        par_data = asset_quality_data.get('par_ladder', {})

        if par_data:
            par_df = pd.DataFrame({
                'Days Past Due': list(par_data.keys()),
                'Amount (KES)': list(par_data.values()),
                'Percentage': [f"{(v / sum(par_data.values())) * 100:.1f}%" for v in par_data.values()]
            })

            st.dataframe(par_df, use_container_width=True)

            fig = px.bar(
                par_df,
                x='Days Past Due',
                y='Amount (KES)',
                title="Portfolio at Risk (PAR) Ladder",
                color='Days Past Due'
            )
            st.plotly_chart(fig, use_container_width=True)

        npl_ratio = asset_quality_data.get('npl_ratio', 0)
        provisioning_cover = asset_quality_data.get('provisioning_cover', 0)

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "NPL Ratio",
                f"{npl_ratio * 100:.2f}%",
                help="Non-performing loans to total loans"
            )

        with col2:
            st.metric(
                "Provisioning Coverage",
                f"{provisioning_cover * 100:.1f}%",
                help="Loan loss provisions to NPLs"
            )

    def render_large_exposures(self, large_exposures_data):
        """Render large exposures analysis - PRESERVED"""
        st.markdown("##### 🎯 Large Exposures & Concentration Risk")

        employer_exposures = large_exposures_data.get('employer_exposures', [])

        if employer_exposures:
            employer_df = pd.DataFrame(employer_exposures)
            st.dataframe(employer_df, use_container_width=True)

            fig = px.bar(
                employer_df.head(10),
                x='employer_name',
                y='exposure_amount',
                title="Top 10 Employer Exposures",
                labels={'exposure_amount': 'Exposure (KES)', 'employer_name': 'Employer'}
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

        concentration_ratios = large_exposures_data.get('concentration_ratios', {})

        if concentration_ratios:
            st.markdown("**Concentration Ratios**")
            for ratio_name, ratio_value in concentration_ratios.items():
                st.metric(
                    ratio_name,
                    f"{ratio_value * 100:.2f}%",
                    help=f"{ratio_name} concentration ratio"
                )

    def render_capital_adequacy(self, capital_data):
        """Render capital adequacy analysis - PRESERVED"""
        st.markdown("##### 🏛️ Capital Adequacy Analysis")

        capital_components = capital_data.get('components', {})

        if capital_components:
            capital_df = pd.DataFrame({
                'Component': list(capital_components.keys()),
                'Amount (KES)': list(capital_components.values())
            })

            st.dataframe(capital_df, use_container_width=True)

            fig = px.pie(
                capital_df,
                values='Amount (KES)',
                names='Component',
                title="Capital Structure"
            )
            st.plotly_chart(fig, use_container_width=True)

        capital_ratios = capital_data.get('ratios', {})

        col1, col2, col3 = st.columns(3)

        with col1:
            core_capital = capital_ratios.get('core_capital_ratio', 0)
            st.metric(
                "Core Capital Ratio",
                f"{core_capital * 100:.2f}%",
                delta=f"{(core_capital - 0.10) * 100:.2f}% vs min",
                help="Minimum requirement: 10%"
            )

        with col2:
            total_capital = capital_ratios.get('total_capital_ratio', 0)
            st.metric(
                "Total Capital Ratio",
                f"{total_capital * 100:.2f}%",
                help="Total capital to risk-weighted assets"
            )

        with col3:
            statutory_reserve = capital_ratios.get('statutory_reserve_ratio', 0)
            st.metric(
                "Statutory Reserve",
                f"{statutory_reserve * 100:.2f}%",
                help="Statutory reserve to total deposits"
            )

    def render_liquidity_analysis(self, liquidity_data):
        """Render liquidity analysis - PRESERVED"""
        st.markdown("##### 💧 Liquidity Analysis")

        liquidity_ratios = liquidity_data.get('ratios', {})

        col1, col2, col3 = st.columns(3)

        with col1:
            liquidity_ratio = liquidity_ratios.get('liquidity_ratio', 0)
            st.metric(
                "Liquidity Ratio",
                f"{liquidity_ratio * 100:.2f}%",
                help="Minimum requirement: 15%"
            )

        with col2:
            lcr = liquidity_ratios.get('lcr', 0)
            st.metric(
                "Liquidity Coverage Ratio",
                f"{lcr * 100:.1f}%",
                help="High-quality liquid assets to net cash outflows"
            )

        with col3:
            nsfr = liquidity_ratios.get('nsfr', 0)
            st.metric(
                "Net Stable Funding Ratio",
                f"{nsfr * 100:.1f}%",
                help="Available stable funding to required stable funding"
            )

        maturity_ladder = liquidity_data.get('maturity_ladder', {})

        if maturity_ladder:
            maturity_df = pd.DataFrame({
                'Time Bucket': list(maturity_ladder.keys()),
                'Net Gap (KES)': list(maturity_ladder.values())
            })

            fig = px.bar(
                maturity_df,
                x='Time Bucket',
                y='Net Gap (KES)',
                title="Liquidity Maturity Gap Analysis",
                color='Net Gap (KES)',
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig, use_container_width=True)

    def render_export_options(self, returns_data):
        """Render export options for SASRA returns - ENHANCED"""
        st.markdown("---")
        st.subheader("📤 Enterprise Export & Submission")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("💾 Export to Excel", use_container_width=True):
                excel_file = self.sasra_generator.export_to_excel(returns_data)
                st.success("Excel file generated successfully!")
                st.download_button(
                    label="📥 Download Excel",
                    data=excel_file,
                    file_name=f"SASRA_Returns_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.ms-excel"
                )

        with col2:
            if st.button("📄 Export to PDF", use_container_width=True):
                pdf_file = self.sasra_generator.export_to_pdf(returns_data)
                st.success("PDF report generated successfully!")
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_file,
                    file_name=f"SASRA_Returns_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )

        with col3:
            if st.button("🔍 Pre-submission Check", use_container_width=True):
                validation_results = self.sasra_generator.validate_returns(returns_data)
                self.render_validation_results(validation_results)

        with col4:
            if st.button("📤 Submit to SASRA", use_container_width=True, type="primary"):
                self._simulate_sasra_submission(returns_data)

    def _simulate_sasra_submission(self, returns_data):
        """Simulate SASRA submission process"""
        with st.spinner("🔄 Submitting to SASRA regulatory portal..."):
            import time as _time
            _time.sleep(2)

            st.success("✅ Submission successful!")

            st.markdown("""
            ### 📋 Submission Details
            
            **Transaction Reference:** SASRA-2024-Q1-0012456  
            **Submission Time:** {}  
            **Confirmation:** Received from SASRA  
            **Next Steps:** Monitor for regulatory feedback within 7 working days
            
            **Submission Package Includes:**
            1. Quarterly Prudential Returns (Q1 2024)
            2. Supporting Documentation
            3. CEO Certification
            4. Board Resolution
            """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    def render_validation_results(self, validation_results):
        """Render pre-submission validation results - ENHANCED"""
        st.markdown("#### ✅ Enterprise Validation Results")

        checks_passed = validation_results.get('checks_passed', 0)
        total_checks = validation_results.get('total_checks', 0)
        issues = validation_results.get('issues', [])
        warnings = validation_results.get('warnings', [])

        col1, col2, col3 = st.columns(3)

        with col1:
            score = (checks_passed / total_checks) * 100 if total_checks else 0
            if score >= 95:
                color = "#4caf50"
                icon = "✅"
            elif score >= 85:
                color = "#ff9800"
                icon = "⚠️"
            else:
                color = "#ff4444"
                icon = "❌"

            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: {color}15; border-radius: 10px; border: 2px solid {color};">
                <h2 style="color: {color}; margin: 0;">{icon} {score:.1f}%</h2>
                <p style="margin: 0.5rem 0 0 0; font-weight: bold;">Validation Score</p>
                <small>{checks_passed}/{total_checks} checks passed</small>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            critical_count = len([i for i in issues if 'CRITICAL' in i])
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: #fff3e0; border-radius: 10px; border: 2px solid #ff9800;">
                <h2 style="color: #ff9800; margin: 0;">{critical_count}</h2>
                <p style="margin: 0.5rem 0 0 0; font-weight: bold;">Critical Issues</p>
                <small>Require immediate attention</small>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: #f0f7ff; border-radius: 10px; border: 2px solid #2196f3;">
                <h2 style="color: #2196f3; margin: 0;">{len(warnings)}</h2>
                <p style="margin: 0.5rem 0 0 0; font-weight: bold;">Warnings</p>
                <small>Recommendations for improvement</small>
            </div>
            """, unsafe_allow_html=True)

        if issues:
            st.error("**🔴 Critical Issues Found:**")
            for issue in issues:
                st.write(f"❌ {issue}")

        if warnings:
            st.warning("**🟡 Improvement Recommendations:**")
            for warning in warnings:
                st.write(f"⚠️ {warning}")

        if not issues and not warnings:
            st.success("✅ All validation checks passed! Returns are ready for submission.")

    def render_submission_tracker(self):
        """Render SASRA submission tracker - ENHANCED"""
        st.markdown("---")
        st.subheader("📅 Enterprise Submission Intelligence")

        submission_data = pd.DataFrame({
            'Period': ['Q4 2023', 'Q3 2023', 'Q2 2023', 'Q1 2023', 'Q4 2022'],
            'Submission Date': ['2024-01-15', '2023-10-16', '2023-07-17', '2023-04-15', '2023-01-16'],
            'Status': ['✅ Submitted', '✅ Submitted', '✅ Submitted', '✅ Submitted', '✅ Submitted'],
            'SASRA Ack': ['📩 Received', '📩 Received', '📩 Received', '📩 Received', '📩 Received'],
            'Days Early/Late': [0, 0, -2, 0, 0],
            'Validation Score': ['95%', '92%', '88%', '85%', '82%'],
            'Follow-up Required': ['No', 'No', 'Yes', 'No', 'No']
        })

        st.dataframe(submission_data, use_container_width=True)

        st.markdown("##### 📊 Submission Performance Analytics")

        col1, col2, col3 = st.columns(3)

        with col1:
            on_time_rate = 100
            st.metric(
                "On-time Submission Rate",
                f"{on_time_rate}%",
                "Perfect record maintained"
            )

        with col2:
            avg_validation_score = (95 + 92 + 88 + 85 + 82) / 5
            st.metric(
                "Average Validation Score",
                f"{avg_validation_score:.1f}%",
                "↑ 2.5% from previous year"
            )

        with col3:
            sasra_feedback = "Positive"
            st.metric(
                "SASRA Feedback",
                sasra_feedback,
                "No regulatory queries"
            )

    def render_compliance_monitoring(self):
        """Render SASRA compliance monitoring - ENHANCED"""
        st.markdown("---")
        st.subheader("⚖️ Regulatory Compliance Intelligence")

        compliance_areas = pd.DataFrame({
            'Category': ['Capital', 'Asset Quality', 'Liquidity', 'Earnings', 'Management', 'Sensitivity'],
            'Current Score': [92, 88, 95, 90, 85, 87],
            'Peer Average': [85, 82, 88, 84, 80, 82],
            'Regulatory Minimum': [80, 75, 80, 75, 75, 75]
        })

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=compliance_areas['Current Score'],
            theta=compliance_areas['Category'],
            fill='toself',
            name='Current Score',
            line=dict(color='#2a5298', width=3)
        ))

        fig.add_trace(go.Scatterpolar(
            r=compliance_areas['Peer Average'],
            theta=compliance_areas['Category'],
            fill='toself',
            name='Peer Average',
            line=dict(color='#ff9800', width=2, dash='dash')
        ))

        fig.add_trace(go.Scatterpolar(
            r=compliance_areas['Regulatory Minimum'],
            theta=compliance_areas['Category'],
            fill='toself',
            name='Regulatory Minimum',
            line=dict(color='#ff4444', width=1, dash='dot')
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100])
            ),
            title="📊 Regulatory Compliance Radar Analysis",
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        compliance_table = [
            {
                'Area': 'Capital Adequacy',
                'Requirement': 'Minimum 10% core capital',
                'Current': '12.5%',
                'Status': '✅ Compliant',
                'Buffer': '+2.5%',
                'Trend': '↗️ Improving'
            },
            {
                'Area': 'Liquidity Ratio',
                'Requirement': 'Minimum 15% liquidity ratio',
                'Current': '18.2%',
                'Status': '✅ Compliant',
                'Buffer': '+3.2%',
                'Trend': '↗️ Improving'
            },
            {
                'Area': 'Single Employer Limit',
                'Requirement': 'Maximum 25% exposure',
                'Current': '22.8%',
                'Status': '✅ Compliant',
                'Buffer': '+2.2%',
                'Trend': '↘️ Decreasing'
            },
            {
                'Area': 'NPL Ratio',
                'Requirement': 'Maximum 8% NPL ratio',
                'Current': '4.2%',
                'Status': '✅ Compliant',
                'Buffer': '+3.8%',
                'Trend': '↘️ Improving'
            }
        ]

        compliance_df = pd.DataFrame(compliance_table)
        st.dataframe(compliance_df, use_container_width=True)

    def render_regulatory_framework_adoption(self):
        """Render regulatory framework adoption metrics"""
        st.markdown("---")
        st.subheader("📚 SASRA Framework Adoption Metrics")

        frameworks = {
            'SASRA Prudential Guidelines 2023': {'adoption': 95, 'implementation': 'Complete'},
            'CBK Corporate Governance': {'adoption': 88, 'implementation': 'In Progress'},
            'IFRS 9 Financial Instruments': {'adoption': 92, 'implementation': 'Complete'},
            'Basel III Standards': {'adoption': 75, 'implementation': 'Partial'},
            'Data Protection Act': {'adoption': 98, 'implementation': 'Complete'}
        }

        framework_df = pd.DataFrame([
            {'Framework': k, 'Adoption %': v['adoption'], 'Implementation': v['implementation']}
            for k, v in frameworks.items()
        ])

        fig = px.bar(
            framework_df,
            x='Framework',
            y='Adoption %',
            title="Regulatory Framework Adoption Status",
            color='Adoption %',
            color_continuous_scale='Viridis'
        )

        fig.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

        overall_adoption = framework_df['Adoption %'].mean()
        st.metric("Overall Framework Adoption", f"{overall_adoption:.1f}%", "Excellent")

    def run(self):
        """Run the enhanced SASRA returns page"""
        self.render_enterprise_header()
        self.render_compliance_marquee()
        self.render_strategic_kpis()
        self.render_compliance_philosophy()
        self.render_enterprise_returns_generator()
        self.render_submission_tracker()
        self.render_compliance_monitoring()
        self.render_regulatory_framework_adoption()


if __name__ == "__main__":
    page = SASRAReturnsPage()
    page.run()