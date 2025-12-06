# pages/02_Credit_Risk_PAR.py - ENHANCED WITH ENTERPRISE FEATURES
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# ---------------------------------------------------------------------
# Ensure project root is on the path so `core.*` imports work
# ---------------------------------------------------------------------
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# LOCAL / PROJECT IMPORTS (unified core package)
from core.config import ConfigManager
from core.rbac import RBACManager
from core.audit import audit_logger
from core.sidebar import render_sidebar

# ==============================================
# CREDIT RISK PHILOSOPHY FRAMEWORK
# ==============================================
CREDIT_RISK_PHILOSOPHY = {
    "Data": "What's our current PAR profile across delinquency buckets?",
    "Insights": "Why is credit risk materializing and where are concentrations?",
    "Frameworks": "How to assess using SASRA PAR framework and Basel guidelines",
    "Actions": "What specific collections, provisioning, and risk mitigations to implement",
    "Impact": "What value it creates (reduced NPLs, optimal provisioning, capital efficiency)",
    "Governance": "How credit decisions are documented and risk accountability maintained"
}

# ✅ DO NOT set page_config here – it’s handled in app.py

# Check authentication and render sidebar
if not st.session_state.get('authenticated', False):
    st.error("🔐 Please log in to access this page")
    st.stop()

# Render consistent sidebar and styling (unified sidebar)
render_sidebar()


class CreditRiskPage:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.rbac_manager = RBACManager()
        self.audit_logger = audit_logger  # use shared singleton logger
        self.config = self.config_manager.load_settings()

        if not self._check_access():
            st.stop()

    def _check_access(self):
        if not st.session_state.get('authenticated', False):
            st.error("Please login to access this page")
            return False

        has_access = self.rbac_manager.check_page_access(
            "02_Credit_Risk_PAR.py",
            st.session_state.role,
            self.config
        )

        if not has_access:
            st.error("You do not have permission to access this page")
            # Best-effort audit log (guarded)
            try:
                self.audit_logger.log_action(
                    user=st.session_state.get("user", "unknown"),
                    role=st.session_state.get("role", "unknown"),
                    action="unauthorized_access_attempt",
                    object_type="page",
                    object_id="02_Credit_Risk_PAR.py",
                )
            except Exception:
                pass
            return False

        # Log successful page access (best-effort)
        try:
            self.audit_logger.log_data_access(
                st.session_state.get("user", "unknown"),
                st.session_state.get("role", "unknown"),
                "credit_risk_intelligence_dashboard",
            )
        except Exception:
            try:
                self.audit_logger.log_action(
                    user=st.session_state.get("user", "unknown"),
                    role=st.session_state.get("role", "unknown"),
                    action="page_access",
                    object_type="dashboard",
                    object_id="02_Credit_Risk_PAR.py",
                )
            except Exception:
                pass

        return True

    def render_strategic_header(self):
        """Render enterprise-grade strategic header"""
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #b91c1c 0%, #dc2626 100%);
                    padding: 25px 30px; border-radius: 16px; color: white; margin-bottom: 20px;">
            <h1 style="margin: 0; color: white;">🎯 Credit Risk Intelligence & PAR Analysis</h1>
            <p style="margin: 5px 0 0 0; opacity: 0.9; color: #fee2e2;">
            Portfolio at Risk Monitoring • Delinquency Analytics • Risk Concentration Management
            </p>
            <div style="margin-top: 10px; font-size: 0.9rem; opacity: 0.8;">
                <strong>📍</strong> Risk Intelligence > Credit Risk Dashboard | 
                <strong>🏢</strong> {st.session_state.get('tenant', 'Central SACCO')} |
                <strong>📅</strong> {datetime.now().strftime('%d %B %Y')} |
                <strong>👤</strong> {st.session_state.get('role', 'Risk Analyst')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Risk Status Marquee
        self.render_risk_status_marquee()

    def render_risk_status_marquee(self):
        """Render real-time risk status marquee"""
        status_messages = [
            "✅ PAR 30+: 4.2% (Below 5% threshold) | ⚠️ Watch: Top employer at 28% concentration",
            "🚨 Alert: 3 accounts moved to 90+ DPD this week | 📈 Collections efficiency: 78% recovery rate",
            "💼 Portfolio: KES 245.8M total exposure | 📊 Provision coverage: 85% of NPLs",
            "⚡ Action: Review 15 accounts > 60 DPD | 🔍 Audit: Credit policy compliance 92%"
        ]

        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #b91c1c 0%, #dc2626 100%); 
                    padding: 12px 20px; border-radius: 12px; margin-bottom: 24px;
                    border-left: 5px solid #ef4444;">
            <marquee behavior="scroll" direction="left" scrollamount="4"
                     style="font-size: 0.95rem; font-weight: 500; color: white;">
                {' • '.join(status_messages)}
            </marquee>
        </div>
        """, unsafe_allow_html=True)

    def render_strategic_kpi_cards(self):
        """Render strategic credit risk KPIs"""
        st.markdown("### 🎯 Credit Risk Performance Indicators")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                label="📊 PAR 30+ Days",
                value="4.2%",
                delta="-0.5%",
                delta_color="inverse",
                help="SASRA Threshold: 5% | Target: <4%"
            )
            st.caption("Portfolio at Risk > 30 days")

        with col2:
            st.metric(
                label="⚠️ NPL Ratio",
                value="2.8%",
                delta="-0.2%",
                delta_color="inverse",
                help="Non-Performing Loans (>90 DPD)"
            )
            st.caption("Regulatory Watch: <3%")

        with col3:
            st.metric(
                label="💼 Provision Coverage",
                value="85%",
                delta="+3%",
                help="Provisions to NPLs ratio"
            )
            st.caption("Target: >80%")

        with col4:
            st.metric(
                label="📈 Collections Efficiency",
                value="78%",
                delta="+5%",
                help="Recovery rate on delinquent loans"
            )
            st.caption("Monthly recovery rate")

        with col5:
            st.metric(
                label="⚖️ Risk Concentration",
                value="28%",
                delta="+2%",
                delta_color="inverse",
                help="Top employer exposure"
            )
            st.caption("SASRA Limit: 25%")

    def generate_enhanced_par_data(self):
        """Generate enhanced sample PAR ladder data with trends"""
        dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='ME')

        data = []
        base_values = {
            'current': 200, 'dpd1_30': 12, 'dpd31_60': 6,
            'dpd61_90': 3, 'dpd91_180': 1.5, 'dpd180_plus': 0.8, 'written_off': 3.5
        }

        for i, date in enumerate(dates):
            month_factor = 1 + (i * 0.01)  # Slight growth trend
            volatility = np.random.uniform(0.95, 1.05)

            data.append({
                'month_end': date,
                'current': base_values['current'] * month_factor * volatility,
                'dpd1_30': base_values['dpd1_30'] * (0.98 + i*0.001) * volatility,
                'dpd31_60': base_values['dpd31_60'] * (1.02 - i*0.0005) * volatility,
                'dpd61_90': base_values['dpd61_90'] * (1.01 - i*0.0003) * volatility,
                'dpd91_180': base_values['dpd91_180'] * (1.00 + i*0.0002) * volatility,
                'dpd180_plus': base_values['dpd180_plus'] * (0.99 + i*0.0001) * volatility,
                'written_off': base_values['written_off'] * (1.00 - i*0.0002) * volatility
            })

        df = pd.DataFrame(data)

        # Calculate totals and percentages
        total_cols = ['current', 'dpd1_30', 'dpd31_60', 'dpd61_90', 'dpd91_180', 'dpd180_plus', 'written_off']
        df['total_portfolio'] = df[total_cols].sum(axis=1)

        for col in total_cols:
            df[f'{col}_pct'] = (df[col] / df['total_portfolio']) * 100
            df[f'{col}_trend'] = df[col].pct_change() * 100

        return df

    def render_strategic_tabs(self):
        """Render strategic analysis tabs"""
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 PAR Intelligence Dashboard",
            "🎯 Delinquency Analytics",
            "⚖️ Concentration Management",
            "🚀 Risk Mitigation Actions",
            "📈 Performance Frameworks"
        ])

        with tab1:
            self.render_par_intelligence_dashboard()

        with tab2:
            self.render_delinquency_analytics()

        with tab3:
            self.render_concentration_management()

        with tab4:
            self.render_risk_mitigation_actions()

        with tab5:
            self.render_performance_frameworks()

    def render_par_intelligence_dashboard(self):
        """Render comprehensive PAR intelligence dashboard"""
        st.subheader("📊 Portfolio at Risk Intelligence Dashboard")

        # Strategic filters
        col1, col2, col3 = st.columns(3)
        with col1:
            analysis_period = st.selectbox(
                "Analysis Period",
                ["Last 12 Months", "Year to Date", "Quarterly", "Monthly"],
                key="par_period"
            )
        with col2:
            product_filter = st.selectbox(
                "Product Filter",
                ["All Products", "Personal Loans", "Business Loans", "Asset Finance", "Emergency Loans"],
                key="par_product"
            )
        with col3:
            view_type = st.selectbox(
                "View Type",
                ["Amount (KES)", "Percentage (%)", "Trend Analysis"],
                key="par_view"
            )

        # Get enhanced data
        par_data = self.generate_enhanced_par_data()

        col1, col2 = st.columns(2)

        with col1:
            # Enhanced PAR trend chart
            st.markdown("##### 📈 PAR Ladder Trend Analysis")

            fig = go.Figure()

            # Stacked area chart for delinquency buckets
            colors = ['#10b981', '#f59e0b', '#f97316', '#dc2626', '#991b1b', '#7f1d1d']
            bucket_names = ['1-30 DPD', '31-60 DPD', '61-90 DPD', '91-180 DPD', '180+ DPD', 'Written Off']
            bucket_columns = ['dpd1_30_pct', 'dpd31_60_pct', 'dpd61_90_pct',
                              'dpd91_180_pct', 'dpd180_plus_pct', 'written_off_pct']

            for col, name, color in zip(bucket_columns, bucket_names, colors):
                fig.add_trace(go.Scatter(
                    x=par_data['month_end'],
                    y=par_data[col],
                    name=name,
                    stackgroup='one',
                    line=dict(width=0.5, color=color),
                    fillcolor=color,
                    hovertemplate=f"{name}: %{{y:.1f}}%<extra></extra>"
                ))

            # Add PAR 30+ threshold line
            par30_total = (par_data['dpd31_60_pct'] + par_data['dpd61_90_pct'] +
                           par_data['dpd91_180_pct'] + par_data['dpd180_plus_pct'])

            fig.add_trace(go.Scatter(
                x=par_data['month_end'],
                y=par30_total,
                name='PAR 30+ Total',
                mode='lines',
                line=dict(color='black', width=2, dash='dash'),
                hovertemplate='PAR 30+ Total: %{y:.1f}%<extra></extra>'
            ))

            fig.update_layout(
                title="Delinquency Bucket Trends (% of Portfolio)",
                xaxis_title="Month",
                yaxis_title="% of Portfolio",
                hovermode="x unified",
                plot_bgcolor='rgba(240, 240, 240, 0.1)',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

            # Add SASRA threshold annotation
            fig.add_hline(
                y=self.config.limits.par30_trigger_max * 100,
                line_dash="dot",
                line_color="red",
                annotation_text="SASRA Threshold (5%)",
                annotation_position="bottom right"
            )

            st.plotly_chart(fig, use_container_width=True)

            # Current portfolio distribution
            st.markdown("##### 📊 Current Portfolio Distribution")
            latest = par_data.iloc[-1]

            par_categories = ['Current (<1 DPD)', '1-30 DPD', '31-60 DPD', '61-90 DPD',
                              '91-180 DPD', '180+ DPD', 'Written Off']
            par_values = [
                latest['current_pct'],
                latest['dpd1_30_pct'],
                latest['dpd31_60_pct'],
                latest['dpd61_90_pct'],
                latest['dpd91_180_pct'],
                latest['dpd180_plus_pct'],
                latest.get('written_off_pct', 0)
            ]

            colors_pie = ['#10b981', '#f59e0b', '#f97316', '#dc2626',
                          '#991b1b', '#7f1d1d', '#475569']

            fig = px.pie(
                values=par_values,
                names=par_categories,
                title="Portfolio Quality Distribution",
                color_discrete_sequence=colors_pie,
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Risk metrics dashboard
            st.markdown("##### 📈 Risk Metrics Dashboard")

            latest = par_data.iloc[-1]
            previous = par_data.iloc[-2]

            metrics = [
                {
                    'name': 'PAR 30+',
                    'current': (latest['dpd31_60_pct'] + latest['dpd61_90_pct'] +
                                latest['dpd91_180_pct'] + latest['dpd180_plus_pct']),
                    'previous': (previous['dpd31_60_pct'] + previous['dpd61_90_pct'] +
                                 previous['dpd91_180_pct'] + previous['dpd180_plus_pct']),
                    'threshold': self.config.limits.par30_trigger_max * 100,
                    'target': 4.0
                },
                {
                    'name': 'NPL Ratio',
                    'current': latest['dpd91_180_pct'] + latest['dpd180_plus_pct'] + latest.get('written_off_pct', 0),
                    'previous': previous['dpd91_180_pct'] + previous['dpd180_plus_pct'] + previous.get('written_off_pct', 0),
                    'threshold': 3.0,
                    'target': 2.5
                },
                {
                    'name': 'Total PAR',
                    'current': 100 - latest['current_pct'],
                    'previous': 100 - previous['current_pct'],
                    'threshold': 6.0,
                    'target': 5.0
                },
                {
                    'name': 'Collection Efficiency',
                    'current': 78.0,  # Sample data
                    'previous': 73.0,
                    'threshold': 70.0,
                    'target': 80.0
                }
            ]

            for metric in metrics:
                delta = metric['current'] - metric['previous']
                threshold_status = "⚠️ Above" if metric['current'] > metric['threshold'] else "✅ Below"

                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.metric(
                        label=metric['name'],
                        value=f"{metric['current']:.1f}%",
                        delta=f"{delta:+.1f}%"
                    )
                with col_b:
                    if metric['current'] > metric['threshold']:
                        st.markdown(
                            "<div style='color: #dc2626; font-size: 0.8rem;'>🔴 "
                            f"{threshold_status}</div>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            "<div style='color: #10b981; font-size: 0.8rem;'>🟢 "
                            f"{threshold_status}</div>",
                            unsafe_allow_html=True,
                        )

            # Risk heatmap by delinquency stage
            st.markdown("##### 🔥 Delinquency Migration Heatmap")

            migration_data = pd.DataFrame({
                'From \\ To': ['Current', '1-30 DPD', '31-60 DPD', '61-90 DPD', 'Write-off'],
                'Current': [95.2, 15.3, 8.2, 5.1, 0.5],
                '1-30 DPD': [3.8, 70.5, 10.2, 5.8, 1.2],
                '31-60 DPD': [0.7, 10.5, 65.3, 15.2, 3.1],
                '61-90 DPD': [0.2, 2.8, 12.5, 60.8, 18.5],
                'Write-off': [0.1, 0.9, 3.8, 13.1, 76.7]
            }).set_index('From \\ To')

            fig = px.imshow(
                migration_data,
                text_auto='.1f',
                aspect="auto",
                color_continuous_scale='RdYlGn_r',
                title="Delinquency Migration Matrix (%)",
                labels=dict(x="To Bucket", y="From Bucket", color="Migration %")
            )
            st.plotly_chart(fig, use_container_width=True)

    def render_delinquency_analytics(self):
        """Render advanced delinquency analytics"""
        st.subheader("🎯 Advanced Delinquency Analytics")

        col1, col2 = st.columns(2)

        with col1:
            # Ageing analysis
            st.markdown("##### 📊 Loan Ageing Analysis")

            ageing_data = pd.DataFrame({
                'Days Past Due': ['0-30', '31-60', '61-90', '91-180', '180+'],
                'Amount (KES M)': [12.5, 6.8, 3.2, 1.8, 0.9],
                'No. of Accounts': [85, 42, 18, 12, 6],
                'Avg Balance (KES K)': [147, 162, 178, 150, 150],
                'Recovery Rate (%)': [78, 65, 45, 30, 15]
            })

            fig = px.bar(
                ageing_data,
                x='Days Past Due',
                y='Amount (KES M)',
                color='Recovery Rate (%)',
                title="Delinquent Amount by Age (Color = Recovery Rate)",
                color_continuous_scale='RdYlGn',
                text=ageing_data['Amount (KES M)'].apply(lambda x: f"KES {x:.1f}M")
            )
            st.plotly_chart(fig, use_container_width=True)

            # Recovery rate analysis
            st.markdown("##### 💰 Recovery Rate Analysis")

            recovery_data = pd.DataFrame({
                'Collection Action': ['SMS Reminder', 'Phone Call', 'Field Visit',
                                      'Employer Contact', 'Legal Notice'],
                'Success Rate (%)': [45, 65, 78, 85, 92],
                'Avg Days to Recover': [5, 12, 21, 35, 60],
                'Cost per Recovery (KES)': [50, 200, 1500, 2500, 10000]
            })

            fig = px.scatter(
                recovery_data,
                x='Avg Days to Recover',
                y='Success Rate (%)',
                size='Cost per Recovery (KES)',
                color='Collection Action',
                title="Collection Effectiveness Analysis",
                size_max=40,
                hover_data=['Success Rate (%)', 'Avg Days to Recover']
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Vintage analysis preview
            st.markdown("##### 📈 Vintage Performance Preview")

            vintage_data = pd.DataFrame({
                'Origination Quarter': ['Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023'],
                'Total Disbursed (KES M)': [45.2, 52.8, 48.5, 55.3],
                'Current PAR (%)': [1.2, 2.1, 3.5, 4.8],
                '90+ DPD (%)': [0.5, 0.8, 1.2, 1.8],
                'Avg Credit Score': [720, 715, 710, 705]
            })

            fig = go.Figure(data=[
                go.Bar(name='Total Disbursed', x=vintage_data['Origination Quarter'],
                       y=vintage_data['Total Disbursed (KES M)'], yaxis='y'),
                go.Scatter(name='Current PAR %', x=vintage_data['Origination Quarter'],
                           y=vintage_data['Current PAR (%)'], yaxis='y2', mode='lines+markers')
            ])

            fig.update_layout(
                title="Vintage Performance Analysis",
                yaxis=dict(title="Amount Disbursed (KES M)"),
                yaxis2=dict(title="PAR %", overlaying="y", side="right"),
                barmode='group'
            )

            st.plotly_chart(fig, use_container_width=True)

            # Early warning indicators
            st.markdown("##### 🚨 Early Warning Indicators")

            warning_data = pd.DataFrame({
                'Indicator': ['Multiple Bounced Cheques', 'Salary Delay > 30 days',
                              'Multiple Loan Applications', 'Guarantor Default',
                              'Change in Employment'],
                'Trigger Rate (%)': [85, 78, 65, 82, 72],
                'Avg Days to Default': [45, 60, 75, 30, 90],
                'Severity': ['High', 'Medium', 'Low', 'High', 'Medium']
            })

            fig = px.bar(
                warning_data,
                x='Trigger Rate (%)',
                y='Indicator',
                color='Severity',
                orientation='h',
                title="Early Warning Indicator Effectiveness",
                color_discrete_map={'High': '#dc2626', 'Medium': '#f59e0b', 'Low': '#10b981'}
            )
            st.plotly_chart(fig, use_container_width=True)

    def render_concentration_management(self):
        """Render concentration risk management"""
        st.subheader("⚖️ Concentration Risk Management")

        concentration_data = pd.DataFrame({
            'Segment': ['Government A', 'Manufacturing B', 'School C', 'Hospital D', 'Retail E', 'Others'],
            'Exposure (KES M)': [68.5, 45.2, 32.1, 28.7, 18.9, 52.4],
            'PAR30 %': [2.1, 5.8, 8.2, 3.5, 6.3, 4.1],
            'Members': [185, 120, 85, 75, 62, 723],
            'Avg Loan Size (KES K)': [370, 377, 378, 383, 305, 72],
            'Growth Rate (%)': [12.5, 8.2, 15.3, 10.8, 18.5, 5.2]
        })

        col1, col2 = st.columns(2)

        with col1:
            concentration_data['Share %'] = (
                concentration_data['Exposure (KES M)'] /
                concentration_data['Exposure (KES M)'].sum() * 100
            )

            fig = px.bar(
                concentration_data,
                x='Segment',
                y='Share %',
                color='PAR30 %',
                title="Employer Concentration & Risk Profile",
                color_continuous_scale='RdYlGn_r',
                text=concentration_data['Share %'].apply(lambda x: f"{x:.1f}%")
            )

            fig.add_hline(
                y=self.config.limits.single_employer_share_max * 100,
                line_dash="dash",
                line_color="red",
                annotation_text=f"SASRA Limit ({self.config.limits.single_employer_share_max * 100:.1f}%)",
                annotation_position="top right"
            )

            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

            max_share = concentration_data['Share %'].max()
            max_employer = concentration_data.loc[concentration_data['Share %'].idxmax(), 'Segment']

            if max_share > self.config.limits.single_employer_share_max * 100:
                st.error(f"""
                ⚠️ **Concentration Alert:** {max_employer} exposure at {max_share:.1f}% 
                exceeds SASRA limit of {self.config.limits.single_employer_share_max * 100:.1f}%
                
                **Required Actions:**
                1. Review and reduce exposure to {max_employer}
                2. Strengthen credit assessment for new loans
                3. Consider portfolio diversification strategies
                4. Report to Risk Committee within 7 days
                """)
            else:
                st.success(f"""
                ✅ **Concentration Status:** All employers within SASRA limits
                Highest exposure: {max_employer} at {max_share:.1f}%
                """)

        with col2:
            st.markdown("##### 📊 Portfolio Diversification Analysis")

            fig = px.scatter(
                concentration_data,
                x='Share %',
                y='PAR30 %',
                size='Exposure (KES M)',
                color='Growth Rate (%)',
                hover_name='Segment',
                title="Risk-Return Concentration Matrix",
                size_max=50,
                color_continuous_scale='RdYlGn'
            )

            fig.add_shape(
                type="rect",
                x0=0, x1=15,
                y0=0, y1=4,
                line=dict(color="green", width=1, dash="dot"),
                fillcolor="rgba(0, 255, 0, 0.1)"
            )
            fig.add_annotation(
                x=7.5, y=2,
                text="Optimal Zone",
                showarrow=False,
                font=dict(color="green", size=10)
            )

            fig.add_hline(
                y=self.config.limits.par30_trigger_max * 100,
                line_dash="dash",
                line_color="red"
            )

            st.plotly_chart(fig, use_container_width=True)

            st.markdown("##### 🏢 Sector Concentration Analysis")

            sector_data = pd.DataFrame({
                'Sector': ['Government', 'Manufacturing', 'Education', 'Healthcare', 'Retail', 'Services'],
                'Exposure (KES M)': [68.5, 45.2, 32.1, 28.7, 18.9, 52.4],
                'PAR %': [2.1, 5.8, 8.2, 3.5, 6.3, 4.1]
            })

            fig = px.sunburst(
                sector_data,
                path=['Sector'],
                values='Exposure (KES M)',
                color='PAR %',
                color_continuous_scale='RdYlGn_r',
                title="Sector Exposure Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)

    def render_risk_mitigation_actions(self):
        """Render risk mitigation action plans"""
        st.subheader("🚀 Risk Mitigation Action Plans")

        action_plans = [
            {
                "priority": "High",
                "risk": "Employer Concentration",
                "actions": [
                    "Implement exposure limits per employer (max 20%)",
                    "Develop portfolio diversification strategy",
                    "Review and reprice high-concentration loans",
                    "Establish employer monitoring dashboard"
                ],
                "owner": "Credit Committee",
                "deadline": "2024-02-15",
                "status": "In Progress"
            },
            {
                "priority": "High",
                "risk": "Rising PAR 30+",
                "actions": [
                    "Strengthen early collection procedures",
                    "Implement automated SMS reminders",
                    "Review credit scoring model",
                    "Train collections team on negotiation"
                ],
                "owner": "Collections Manager",
                "deadline": "2024-01-31",
                "status": "Active"
            },
            {
                "priority": "Medium",
                "risk": "Weak Recovery Rates",
                "actions": [
                    "Implement field collection strategy",
                    "Review and update recovery procedures",
                    "Train staff on legal recovery options",
                    "Establish recovery performance metrics"
                ],
                "owner": "Recovery Team",
                "deadline": "2024-03-31",
                "status": "Planned"
            },
            {
                "priority": "Low",
                "risk": "Data Quality Issues",
                "actions": [
                    "Implement data validation checks",
                    "Automate delinquency reporting",
                    "Train staff on data entry standards",
                    "Establish data quality dashboard"
                ],
                "owner": "IT Department",
                "deadline": "2024-04-30",
                "status": "Not Started"
            }
        ]

        for plan in action_plans:
            with st.expander(f"{plan['priority']} Priority: {plan['risk']} - {plan['status']}", expanded=True):
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Priority", plan['priority'])
                with col2:
                    st.metric("Owner", plan['owner'])
                with col3:
                    st.metric("Deadline", plan['deadline'])
                with col4:
                    status_color = {
                        'Completed': 'green',
                        'In Progress': 'blue',
                        'Active': 'orange',
                        'Planned': 'gray',
                        'Not Started': 'red'
                    }.get(plan['status'], 'black')
                    st.markdown(
                        f"**Status:** <span style='color:{status_color};'>{plan['status']}</span>",
                        unsafe_allow_html=True
                    )

                st.markdown("**Action Items:**")
                for action in plan['actions']:
                    st.markdown(f"• {action}")

                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"📋 View Details", key=f"details_{plan['risk']}"):
                        st.info(f"Detailed action plan loaded for {plan['risk']}")
                with col_b:
                    if st.button(f"📈 Update Progress", key=f"update_{plan['risk']}"):
                        st.success(f"Progress updated for {plan['risk']} action plan")

    def render_performance_frameworks(self):
        """Render credit risk performance frameworks"""
        st.subheader("📈 Credit Risk Performance Frameworks")

        frameworks = [
            {
                "name": "SASRA PAR Framework",
                "description": "Portfolio at Risk monitoring as per SASRA guidelines",
                "metrics": ["PAR 30+", "PAR 90+", "NPL Ratio", "Provision Coverage"],
                "status": "Fully Implemented",
                "compliance": "95%"
            },
            {
                "name": "Basel II Credit Risk",
                "description": "Standardized approach for credit risk measurement",
                "metrics": ["Risk Weighted Assets", "Capital Requirements", "PD/LGD Models"],
                "status": "Partial Implementation",
                "compliance": "65%"
            },
            {
                "name": "IFRS 9 Expected Credit Loss",
                "description": "Forward-looking credit loss provisioning",
                "metrics": ["Stage 1/2/3 ECL", "Lifetime PD", "LGD Estimates"],
                "status": "Implementation Phase",
                "compliance": "45%"
            },
            {
                "name": "Credit Scoring Model",
                "description": "Risk-based credit decision framework",
                "metrics": ["Application Score", "Behavioral Score", "Collection Score"],
                "status": "Fully Implemented",
                "compliance": "90%"
            }
        ]

        cols = st.columns(2)
        for idx, framework in enumerate(frameworks):
            with cols[idx % 2]:
                with st.container():
                    st.markdown(f"""
                    <div style="background: #f8fafc; padding: 15px; border-radius: 10px; 
                                border-left: 4px solid #dc2626; margin-bottom: 10px;">
                        <strong>{framework['name']}</strong><br>
                        <small>{framework['description']}</small><br>
                        <small><strong>Metrics:</strong> {', '.join(framework['metrics'])}</small><br>
                        <small><strong>Status:</strong> {framework['status']}</small><br>
                        <small><strong>Compliance:</strong> {framework['compliance']}</small>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("##### 📊 Framework Performance Metrics")

        performance_data = pd.DataFrame({
            'Framework': ['SASRA PAR', 'Basel II', 'IFRS 9 ECL', 'Credit Scoring'],
            'Accuracy Score': [92, 78, 65, 88],
            'Implementation %': [95, 65, 45, 90],
            'User Adoption': [90, 60, 40, 85],
            'Business Impact': [95, 75, 55, 90]
        })

        fig = px.bar(
            performance_data,
            x='Framework',
            y=['Accuracy Score', 'Implementation %', 'User Adoption', 'Business Impact'],
            title="Credit Risk Framework Performance",
            barmode='group',
            color_discrete_sequence=['#dc2626', '#f59e0b', '#3b82f6', '#10b981']
        )
        st.plotly_chart(fig, use_container_width=True)

    def render_credit_risk_philosophy(self):
        """Render credit risk philosophy framework"""
        with st.expander("📜 Credit Risk Management Philosophy", expanded=False):
            cols = st.columns(3)
            for i, (key, value) in enumerate(CREDIT_RISK_PHILOSOPHY.items()):
                with cols[i % 3]:
                    st.info(f"**{key}:**\n\n{value}")

            st.markdown("---")
            st.markdown("""
            **Strategic Credit Risk Approach:**  
            - **Proactive Monitoring:** Early identification of deteriorating accounts  
            - **Risk-Based Pricing:** Align interest rates with credit risk profiles  
            - **Portfolio Diversification:** Mitigate concentration risks  
            - **Data-Driven Decisions:** Use analytics for credit decisions  
            - **Continuous Improvement:** Regular review of credit policies  
            - **Regulatory Compliance:** Adherence to SASRA and Basel requirements
            """)

    def run(self):
        """Run the enhanced credit risk page"""
        # Strategic Header
        self.render_strategic_header()

        # Credit Risk Philosophy
        self.render_credit_risk_philosophy()

        # Strategic KPI Cards
        self.render_strategic_kpi_cards()

        st.markdown("---")

        # Strategic Analysis Tabs
        self.render_strategic_tabs()

        # Log dashboard completion using audit_logger (best-effort)
        try:
            self.audit_logger.log_action(
                user=st.session_state.get("user", "unknown"),
                role=st.session_state.get("role", "unknown"),
                action="credit_risk_dashboard_completed",
                object_type="dashboard",
                object_id="02_Credit_Risk_PAR.py"
            )
        except Exception:
            pass


if __name__ == "__main__":
    page = CreditRiskPage()
    page.run()