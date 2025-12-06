# pages/02A_Vintages_RollRates.py - ENHANCED WITH ENTERPRISE FEATURES
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
import time  # used in advanced analysis spinner

# Make sure Python can see the project root so `core.*` works
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 🔽 LOCAL / PROJECT IMPORTS (unified core modules)
from core.config import ConfigManager
from core.rbac import RBACManager
from core.audit import AuditLogger, audit_logger
from core.sidebar import render_sidebar

# ==============================================
# VINTAGES & ROLL RATES PHILOSOPHY FRAMEWORK
# ==============================================
VINTAGES_PHILOSOPHY = {
    "Data": "How are loan cohorts performing over time across vintages?",
    "Insights": "Why are certain cohorts performing better/worse? What drives roll rates?",
    "Frameworks": "How to analyze using cohort analysis and Markov chain transition matrices",
    "Actions": "What credit policy adjustments, underwriting improvements to implement",
    "Impact": "What value it creates (improved underwriting, accurate provisioning, better pricing)",
    "Governance": "How vintage performance is tracked and underwriting decisions are refined"
}

# ⚠️ Do NOT call st.set_page_config here – app.py already does it globally

# Check authentication and render sidebar
if not st.session_state.get('authenticated', False):
    st.error("🔐 Please log in to access this page")
    st.stop()

# Render consistent sidebar and styling (unified nav)
render_sidebar()

class VintagesRollRatesPage:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.rbac_manager = RBACManager()
        self.audit_logger = audit_logger  # unified audit logger instance
        self.config = self.config_manager.load_settings()

        if not self._check_access():
            st.stop()

    def _check_access(self):
        if not st.session_state.get('authenticated', False):
            st.error("Please login to access this page")
            return False

        has_access = self.rbac_manager.check_page_access(
            "02A_Vintages_RollRates.py",
            st.session_state.role,
            self.config
        )

        if not has_access:
            st.error("You do not have permission to access this page")
            # Optional: log unauthorized attempt (wrapped in try/except for safety)
            try:
                self.audit_logger.log_data_access(
                    st.session_state.user,
                    st.session_state.role,
                    "unauthorized_vintages_access"
                )
            except Exception:
                pass
            return False

        # Log successful page access
        try:
            self.audit_logger.log_data_access(
                st.session_state.user,
                st.session_state.role,
                "vintages_roll_rates_intelligence"
            )
        except Exception:
            pass

        return True

    def render_strategic_header(self):
        """Render enterprise-grade strategic header"""
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%);
                    padding: 25px 30px; border-radius: 16px; color: white; margin-bottom: 20px;">
            <h1 style="margin: 0; color: white;">📊 Vintage Intelligence & Roll Rate Analytics</h1>
            <p style="margin: 5px 0 0 0; opacity: 0.9; color: #f3e8ff;">
            Cohort Performance Analysis • Loan Migration Patterns • Underwriting Effectiveness
            </p>
            <div style="margin-top: 10px; font-size: 0.9rem; opacity: 0.8;">
                <strong>📍</strong> Risk Intelligence > Vintage Analytics | 
                <strong>🏢</strong> {st.session_state.get('tenant', 'Central SACCO')} |
                <strong>📅</strong> {datetime.now().strftime('%d %B %Y')} |
                <strong>👤</strong> {st.session_state.get('role', 'Risk Analyst')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Vintage Status Marquee
        self.render_vintage_status_marquee()

    def render_vintage_status_marquee(self):
        """Render real-time vintage status marquee"""
        status_messages = [
            "📈 Strongest Vintage: Q1 2023 (Default Rate: 1.2%) | 📉 Watch: Q4 2023 (Default: 4.8%)",
            "🔀 Roll Rate Trend: 92% of current loans remain current | ⚠️ 31-60 DPD: 25% roll to 61-90 DPD",
            "🏆 Best Performing Product: Asset Finance (Cumulative Default: 2.1%)",
            "📊 Cohort Analysis: 12 cohorts tracked | 🔍 Insight: Credit policy Q3 2023 improved performance"
        ]

        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #7c3aed 0%, #8b5cf6 100%); 
                    padding: 12px 20px; border-radius: 12px; margin-bottom: 24px;
                    border-left: 5px solid #a78bfa;">
            <marquee behavior="scroll" direction="left" scrollamount="4"
                     style="font-size: 0.95rem; font-weight: 500; color: white;">
                {' • '.join(status_messages)}
            </marquee>
        </div>
        """, unsafe_allow_html=True)

    def render_strategic_kpi_cards(self):
        """Render strategic vintage KPIs"""
        st.markdown("### 🎯 Vintage Performance Indicators")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                label="📊 Best Vintage Default",
                value="1.2%",
                delta="-0.3%",
                help="Q1 2023 cumulative default rate"
            )
            st.caption("Best performing cohort")

        with col2:
            st.metric(
                label="⚠️ Worst Vintage Default",
                value="4.8%",
                delta="+0.8%",
                delta_color="inverse",
                help="Q4 2023 cumulative default rate"
            )
            st.caption("Watch: Q4 2023")

        with col3:
            st.metric(
                label="📈 Current Stability Rate",
                value="92%",
                delta="+1.5%",
                help="% of current loans staying current"
            )
            st.caption("Roll rate T→T+1")

        with col4:
            st.metric(
                label="🔀 Migration to 90+ DPD",
                value="10%",
                delta="-2%",
                delta_color="inverse",
                help="From 61-90 DPD to 90+ DPD"
            )
            st.caption("Improving roll rate")

        with col5:
            st.metric(
                label="🏆 Vintage Count",
                value="12",
                delta="+2",
                help="Active cohorts tracked"
            )
            st.caption("Months of data")

    def generate_enhanced_vintage_data(self):
        """Generate enhanced vintage cohort data"""
        # Create cohorts from Q1 2022 to Q4 2023
        cohorts = []
        for year in [2022, 2023]:
            for quarter in [1, 2, 3, 4]:
                cohort_name = f"Q{quarter} {year}"
                cohort_date = datetime(year, quarter * 3, 1)

                # Simulate vintage performance
                base_default = 0.5 + (quarter * 0.3) + ((year - 2022) * 0.2)

                cohorts.append({
                    'cohort': cohort_name,
                    'origination_date': cohort_date,
                    'total_disbursed': np.random.uniform(40, 60),
                    'active_balance': np.random.uniform(35, 50),
                    'cumulative_default_rate': base_default + np.random.uniform(-0.2, 0.2),
                    'current_par': base_default * 0.8 + np.random.uniform(-0.1, 0.1),
                    'avg_credit_score': 700 + (quarter * 5) - ((year - 2022) * 10),
                    'avg_loan_size': 250 + (quarter * 10),
                    'product_mix_personal': np.random.uniform(40, 60),
                    'recovery_rate': 80 - (base_default * 3) + np.random.uniform(-5, 5)
                })

        return pd.DataFrame(cohorts)

    def generate_enhanced_roll_rate_matrix(self):
        """Generate enhanced roll rate transition matrix"""
        states = ['Current', '1-30 DPD', '31-60 DPD', '61-90 DPD', '90+ DPD', 'Write-off']

        # Base transition matrix with realistic probabilities
        transition_matrix = np.array([
            [0.920, 0.060, 0.012, 0.005, 0.002, 0.001],  # Current
            [0.350, 0.450, 0.120, 0.050, 0.020, 0.010],  # 1-30 DPD
            [0.150, 0.250, 0.350, 0.150, 0.070, 0.030],  # 31-60 DPD
            [0.080, 0.120, 0.200, 0.400, 0.150, 0.050],  # 61-90 DPD
            [0.020, 0.050, 0.080, 0.150, 0.650, 0.050],  # 90+ DPD
            [0.000, 0.000, 0.000, 0.000, 0.000, 1.000]   # Write-off (absorbing state)
        ])

        return states, transition_matrix

    def render_strategic_tabs(self):
        """Render strategic analysis tabs"""
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Vintage Intelligence Dashboard",
            "🎯 Cohort Performance Analytics",
            "⚖️ Roll Rate & Migration Patterns",
            "🚀 Underwriting Insights & Actions",
            "📊 Analytical Frameworks"
        ])

        with tab1:
            self.render_vintage_intelligence_dashboard()

        with tab2:
            self.render_cohort_performance_analytics()

        with tab3:
            self.render_roll_rate_migration_patterns()

        with tab4:
            self.render_underwriting_insights_actions()

        with tab5:
            self.render_analytical_frameworks()

    def render_vintage_intelligence_dashboard(self):
        """Render comprehensive vintage intelligence dashboard"""
        st.subheader("📈 Vintage Intelligence Dashboard")

        # Strategic filters
        col1, col2, col3 = st.columns(3)
        with col1:
            vintage_range = st.selectbox(
                "Vintage Range",
                ["All Vintages", "Last 12 Months", "Last 8 Quarters", "By Year"],
                key="vintage_range"
            )
        with col2:
            performance_metric = st.selectbox(
                "Performance Metric",
                ["Default Rate", "PAR", "Recovery Rate", "Active Balance", "Credit Score"],
                key="vintage_metric"
            )
        with col3:
            product_filter = st.selectbox(
                "Product Filter",
                ["All Products", "Personal Loans", "Business Loans", "Asset Finance"],
                key="vintage_product"
            )

        # Get enhanced data
        vintage_data = self.generate_enhanced_vintage_data()

        col1, col2 = st.columns(2)

        with col1:
            # Vintage performance heatmap
            st.markdown("##### 🔥 Vintage Performance Heatmap")

            # Create performance matrix
            performance_matrix = vintage_data.pivot_table(
                index=pd.DatetimeIndex(vintage_data['origination_date']).year,
                columns=pd.DatetimeIndex(vintage_data['origination_date']).quarter,
                values='cumulative_default_rate',
                aggfunc='mean'
            )

            fig = px.imshow(
                performance_matrix,
                text_auto='.1f',
                aspect="auto",
                color_continuous_scale='RdYlGn_r',
                title="Default Rate by Vintage (Year × Quarter)",
                labels=dict(x="Quarter", y="Year", color="Default Rate %")
            )
            st.plotly_chart(fig, use_container_width=True)

            # Vintage waterfall analysis
            st.markdown("##### 📊 Vintage Contribution Analysis")

            vintage_data['default_amount'] = vintage_data['total_disbursed'] * vintage_data['cumulative_default_rate'] / 100

            fig = px.bar(
                vintage_data,
                x='cohort',
                y='default_amount',
                color='cumulative_default_rate',
                title="Default Amount by Vintage Cohort",
                color_continuous_scale='RdYlGn_r',
                text=vintage_data['default_amount'].apply(lambda x: f"KES {x:.1f}M")
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Vintage performance trend
            st.markdown("##### 📈 Vintage Performance Trend")

            fig = go.Figure()

            # Add line for each vintage's performance over time
            vintage_data_sorted = vintage_data.sort_values('origination_date')

            # Simulate vintage aging curves
            for i, cohort in enumerate(vintage_data_sorted['cohort']):
                cohort_data = vintage_data_sorted.iloc[i]
                age_months = list(range(1, 13))

                # Simulate aging curve
                base_rate = cohort_data['cumulative_default_rate']
                aging_curve = [base_rate * (month / 12) * np.random.uniform(0.9, 1.1) for month in age_months]

                fig.add_trace(go.Scatter(
                    x=age_months,
                    y=aging_curve,
                    mode='lines',
                    name=cohort,
                    line=dict(width=2 if cohort == 'Q4 2023' else 1),
                    hovertemplate=f"{cohort}: %{{y:.1f}}% at month %{{x}}<extra></extra>"
                ))

            fig.update_layout(
                title="Vintage Aging Curves (Cumulative Default Rate)",
                xaxis_title="Months on Books (MOB)",
                yaxis_title="Cumulative Default Rate (%)",
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

            # Add industry benchmark line
            fig.add_hline(y=3.5, line_dash="dash", line_color="gray",
                          annotation_text="Industry Avg (3.5%)")

            st.plotly_chart(fig, use_container_width=True)

            # Vintage comparison metrics
            st.markdown("##### ⚖️ Vintage Performance Comparison")

            comparison_metrics = pd.DataFrame({
                'Metric': ['Best Vintage', 'Worst Vintage', 'Average', 'Median', 'Standard Dev'],
                'Default Rate': [
                    vintage_data['cumulative_default_rate'].min(),
                    vintage_data['cumulative_default_rate'].max(),
                    vintage_data['cumulative_default_rate'].mean(),
                    vintage_data['cumulative_default_rate'].median(),
                    vintage_data['cumulative_default_rate'].std()
                ],
                'Credit Score': [
                    vintage_data['avg_credit_score'].max(),
                    vintage_data['avg_credit_score'].min(),
                    vintage_data['avg_credit_score'].mean(),
                    vintage_data['avg_credit_score'].median(),
                    vintage_data['avg_credit_score'].std()
                ],
                'Recovery Rate': [
                    vintage_data['recovery_rate'].max(),
                    vintage_data['recovery_rate'].min(),
                    vintage_data['recovery_rate'].mean(),
                    vintage_data['recovery_rate'].median(),
                    vintage_data['recovery_rate'].std()
                ]
            })

            st.dataframe(
                comparison_metrics.style.format({
                    'Default Rate': '{:.1f}%',
                    'Credit Score': '{:.0f}',
                    'Recovery Rate': '{:.1f}%'
                }),
                use_container_width=True,
                hide_index=True
            )

    def render_cohort_performance_analytics(self):
        """Render detailed cohort performance analytics"""
        st.subheader("🎯 Cohort Performance Analytics")

        # Get enhanced data
        vintage_data = self.generate_enhanced_vintage_data()

        col1, col2 = st.columns(2)

        with col1:
            # Cohort performance drivers
            st.markdown("##### 📊 Cohort Performance Drivers")

            fig = px.scatter(
                vintage_data,
                x='avg_credit_score',
                y='cumulative_default_rate',
                size='total_disbursed',
                color='avg_loan_size',
                hover_name='cohort',
                title="Credit Score vs Default Rate by Vintage",
                size_max=50,
                color_continuous_scale='RdYlGn_r',
                labels={
                    'avg_credit_score': 'Average Credit Score',
                    'cumulative_default_rate': 'Default Rate (%)',
                    'avg_loan_size': 'Avg Loan Size (K KES)',
                    'total_disbursed': 'Total Disbursed (M KES)'
                }
            )

            # Add trend line
            z = np.polyfit(vintage_data['avg_credit_score'], vintage_data['cumulative_default_rate'], 1)
            p = np.poly1d(z)
            sorted_scores = vintage_data['avg_credit_score'].sort_values()
            fig.add_trace(go.Scatter(
                x=sorted_scores,
                y=p(sorted_scores),
                mode='lines',
                name='Trend Line',
                line=dict(color='red', dash='dash')
            ))

            st.plotly_chart(fig, use_container_width=True)

            # Product mix impact
            st.markdown("##### 🏢 Product Mix Impact Analysis")

            product_mix_data = pd.DataFrame({
                'Cohort': vintage_data['cohort'],
                'Personal Loans %': vintage_data['product_mix_personal'],
                'Business Loans %': 100 - vintage_data['product_mix_personal'],
                'Default Rate': vintage_data['cumulative_default_rate']
            })

            fig = px.scatter(
                product_mix_data,
                x='Personal Loans %',
                y='Default Rate',
                color='Business Loans %',
                size=vintage_data['total_disbursed'],
                hover_name='Cohort',
                title="Product Mix Impact on Default Rates",
                size_max=50,
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Cohort survival analysis
            st.markdown("##### 📈 Cohort Survival Analysis")

            # Generate survival curve data
            months = list(range(0, 13))
            cohorts_to_show = ['Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023']

            fig = go.Figure()

            for cohort in cohorts_to_show:
                if cohort not in vintage_data['cohort'].values:
                    continue
                cohort_idx = vintage_data[vintage_data['cohort'] == cohort].index[0]
                base_default = vintage_data.loc[cohort_idx, 'cumulative_default_rate']

                # Create survival curve (100% - cumulative default)
                survival_rate = [
                    100 - (base_default * (month / 12) * np.random.uniform(0.8, 1.2))
                    for month in months
                ]

                fig.add_trace(go.Scatter(
                    x=months,
                    y=survival_rate,
                    mode='lines+markers',
                    name=cohort,
                    line=dict(width=2),
                    hovertemplate=f"{cohort}: %{{y:.1f}}% survival at month %{{x}}<extra></extra>"
                ))

            fig.update_layout(
                title="Cohort Survival Curves (% of Loans Still Performing)",
                xaxis_title="Months on Books (MOB)",
                yaxis_title="Survival Rate (%)",
                hovermode="x unified",
                yaxis_range=[70, 101]
            )

            # Add industry benchmark
            fig.add_hline(y=94, line_dash="dash", line_color="gray",
                          annotation_text="Industry Avg Survival (94%)")

            st.plotly_chart(fig, use_container_width=True)

            # Cohort performance matrix
            st.markdown("##### 📋 Cohort Performance Matrix")

            performance_matrix = vintage_data[[
                'cohort', 'total_disbursed', 'cumulative_default_rate',
                'avg_credit_score', 'recovery_rate'
            ]].copy()
            performance_matrix['performance_score'] = (
                (100 - performance_matrix['cumulative_default_rate']) * 0.4 +
                performance_matrix['avg_credit_score'] / 10 * 0.3 +
                performance_matrix['recovery_rate'] * 0.3
            )

            performance_matrix['performance_tier'] = pd.cut(
                performance_matrix['performance_score'],
                bins=[0, 70, 85, 95, 100],
                labels=['Poor', 'Fair', 'Good', 'Excellent']
            )

            fig = px.scatter(
                performance_matrix,
                x='cumulative_default_rate',
                y='total_disbursed',
                color='performance_tier',
                size='avg_credit_score',
                hover_name='cohort',
                title="Cohort Performance Matrix",
                size_max=40,
                color_discrete_map={
                    'Excellent': '#10b981',
                    'Good': '#3b82f6',
                    'Fair': '#f59e0b',
                    'Poor': '#ef4444'
                },
                labels={
                    'cumulative_default_rate': 'Default Rate (%)',
                    'total_disbursed': 'Disbursed (M KES)',
                    'avg_credit_score': 'Credit Score',
                    'performance_tier': 'Performance Tier'
                }
            )
            st.plotly_chart(fig, use_container_width=True)

    def render_roll_rate_migration_patterns(self):
        """Render roll rate and migration pattern analysis"""
        st.subheader("⚖️ Roll Rate & Migration Patterns")

        states, transition_matrix = self.generate_enhanced_roll_rate_matrix()

        col1, col2 = st.columns(2)

        with col1:
            # Enhanced roll rate matrix
            st.markdown("##### 🔄 Roll Rate Transition Matrix")

            fig = px.imshow(
                transition_matrix,
                x=states,
                y=states,
                text_auto='.3f',
                aspect="auto",
                color_continuous_scale='Blues',
                title="Roll Rate Transition Matrix (T → T+1 Month)",
                labels=dict(x="To State", y="From State", color="Probability")
            )

            # Add annotations for key transitions
            fig.update_traces(
                texttemplate='%{z:.1%}',
                textfont=dict(size=10)
            )

            st.plotly_chart(fig, use_container_width=True)

            # Key transition metrics
            st.markdown("##### 📊 Key Transition Metrics")

            key_transitions = pd.DataFrame({
                'Transition': ['Current → Current', 'Current → 1-30 DPD',
                               '1-30 DPD → 31-60 DPD', '31-60 DPD → 61-90 DPD',
                               '61-90 DPD → 90+ DPD', '90+ DPD → Write-off'],
                'Probability': ['92.0%', '6.0%', '12.0%', '15.0%', '15.0%', '5.0%'],
                'Trend': ['↗ Improving', '↘ Stable', '↘ Worsening', '↗ Improving',
                          '↘ Stable', '↗ Improving'],
                'Impact': ['High', 'Medium', 'High', 'Medium', 'High', 'Low']
            })

            st.dataframe(key_transitions, use_container_width=True, hide_index=True)

        with col2:
            # Migration flow diagram
            st.markdown("##### 📈 Migration Flow Analysis")

            # Create sankey diagram data
            source = [0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4]
            target = [0, 1, 1, 2, 5, 2, 3, 5, 3, 4, 5, 4, 5]
            value = [920, 60, 450, 120, 30, 350, 150, 50, 400, 150, 50, 650, 50]

            fig = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=states,
                    color=["#10b981", "#f59e0b", "#f97316", "#dc2626", "#991b1b", "#475569"]
                ),
                link=dict(
                    source=source,
                    target=target,
                    value=value,
                    color=['rgba(16, 185, 129, 0.3)', 'rgba(245, 158, 11, 0.3)',
                           'rgba(249, 115, 22, 0.3)', 'rgba(220, 38, 38, 0.3)',
                           'rgba(153, 27, 27, 0.3)']
                )
            )])

            fig.update_layout(
                title="Loan State Migration Flow (Per 1000 Loans)",
                font_size=10,
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)

            # Transition stability analysis
            st.markdown("##### 🎯 Transition Stability Analysis")

            stability_data = pd.DataFrame({
                'State': states,
                'Stability Rate': [92.0, 45.0, 35.0, 40.0, 65.0, 100.0],
                'Improvement Rate': [3.5, 35.0, 15.0, 8.0, 2.0, 0.0],
                'Worsening Rate': [8.0, 20.0, 22.0, 25.0, 20.0, 0.0]
            })

            fig = go.Figure(data=[
                go.Bar(name='Stability Rate', x=stability_data['State'], y=stability_data['Stability Rate']),
                go.Bar(name='Improvement Rate', x=stability_data['State'], y=stability_data['Improvement Rate']),
                go.Bar(name='Worsening Rate', x=stability_data['State'], y=stability_data['Worsening Rate'])
            ])

            fig.update_layout(
                title="State Transition Rates Analysis",
                barmode='stack',
                xaxis_tickangle=-45
            )

            st.plotly_chart(fig, use_container_width=True)

    def render_underwriting_insights_actions(self):
        """Render underwriting insights and action plans"""
        st.subheader("🚀 Underwriting Insights & Action Plans")

        # Underwriting insights from vintage analysis
        insights = [
            {
                "insight": "Credit Score Impact",
                "finding": "Vintages with avg credit score > 715 have 40% lower default rates",
                "recommendation": "Increase minimum credit score threshold to 720",
                "expected_impact": "Reduce default rates by 1.5%",
                "priority": "High"
            },
            {
                "insight": "Product Mix Optimization",
                "finding": "Personal loan-heavy vintages underperform business loans by 2.1%",
                "recommendation": "Adjust product mix to 60% business, 40% personal",
                "expected_impact": "Improve portfolio performance by 1.2%",
                "priority": "Medium"
            },
            {
                "insight": "Seasonal Pattern",
                "finding": "Q4 vintages consistently underperform by 1.8% vs annual average",
                "recommendation": "Implement stricter underwriting in Q4 or seasonal pricing",
                "expected_impact": "Reduce Q4 defaults by 1.0%",
                "priority": "High"
            },
            {
                "insight": "Loan Size Correlation",
                "finding": "Loans > KES 300K have 30% higher recovery rates",
                "recommendation": "Review pricing for smaller loans or enhance collateral",
                "expected_impact": "Increase recovery rates by 5%",
                "priority": "Medium"
            }
        ]

        for insight in insights:
            with st.expander(f"{insight['priority']} Priority: {insight['insight']}", expanded=False):
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Finding", insight['finding'])
                with col2:
                    st.metric("Recommendation", insight['recommendation'])
                with col3:
                    st.metric("Expected Impact", insight['expected_impact'])
                with col4:
                    priority_color = {
                        'High': 'red',
                        'Medium': 'orange',
                        'Low': 'green'
                    }.get(insight['priority'], 'black')
                    st.markdown(
                        f"**Priority:** <span style='color:{priority_color};'>{insight['priority']}</span>",
                        unsafe_allow_html=True
                    )

                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"📋 Implement Action", key=f"implement_{insight['insight']}"):
                        st.success(f"Action plan initiated for {insight['insight']}")
                with col_b:
                    if st.button(f"📊 Measure Impact", key=f"measure_{insight['insight']}"):
                        st.info(f"Impact measurement started for {insight['insight']}")

        # File upload for enhanced analysis
        st.subheader("📁 Enhanced Monthly Loan States Upload")

        col1, col2 = st.columns(2)

        with col1:
            uploaded_file = st.file_uploader(
                "Upload monthly_loan_states.csv",
                type=['csv', 'xlsx'],
                help="File should contain monthly snapshots with: loan_id, month_end, state, balance, product_type"
            )

            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)

                    st.success(f"✅ Successfully loaded {len(df):,} records")

                    # Show data summary
                    st.markdown("##### 📋 Data Summary")
                    summary_data = {
                        'Metric': ['Total Records', 'Unique Loans', 'Date Range',
                                   'States Tracked', 'Avg Balance'],
                        'Value': [
                            f"{len(df):,}",
                            f"{df['loan_id'].nunique():,}",
                            f"{df['month_end'].min()} to {df['month_end'].max()}",
                            f"{df['state'].nunique()}",
                            f"KES {df['balance'].mean():,.0f}"
                        ]
                    }
                    st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)

                except Exception as e:
                    st.error(f"❌ Error loading file: {str(e)}")

        with col2:
            # Advanced analysis options
            st.markdown("##### 🔧 Advanced Analysis Options")

            analysis_type = st.selectbox(
                "Select Analysis Type",
                ["Cohort Analysis", "Transition Matrix", "Survival Analysis",
                 "Product Performance", "Seasonal Patterns"]
            )

            if st.button("🚀 Run Advanced Analysis", use_container_width=True):
                with st.spinner("Running advanced vintage analysis..."):
                    time.sleep(2)  # Simulate processing

                    # Sample analysis results
                    analysis_results = pd.DataFrame({
                        'Analysis': ['Cohort Stability', 'Transition Accuracy',
                                     'Predictive Power', 'Business Impact'],
                        'Score': [85, 78, 92, 88],
                        'Status': ['Good', 'Fair', 'Excellent', 'Good']
                    })

                    st.success("Analysis completed successfully!")
                    st.dataframe(analysis_results, use_container_width=True, hide_index=True)

    def render_analytical_frameworks(self):
        """Render analytical frameworks and methodologies"""
        st.subheader("📊 Vintage & Roll Rate Analytical Frameworks")

        # Framework implementation
        frameworks = [
            {
                "name": "Cohort Analysis Framework",
                "description": "Track loan cohorts from origination through lifetime",
                "metrics": ["Cumulative Default Rate", "Survival Rate", "Months on Books"],
                "status": "Fully Implemented",
                "usage": "95%"
            },
            {
                "name": "Markov Chain Transition",
                "description": "Model loan state transitions using Markov chains",
                "metrics": ["Transition Probabilities", "Absorption States", "Steady State"],
                "status": "Partial Implementation",
                "usage": "70%"
            },
            {
                "name": "Survival Analysis",
                "description": "Statistical analysis of time-to-event (default)",
                "metrics": ["Kaplan-Meier Curves", "Hazard Rates", "Cox Proportional"],
                "status": "Implementation Phase",
                "usage": "45%"
            },
            {
                "name": "Vintage Comparison",
                "description": "Compare cohort performance across time periods",
                "metrics": ["Benchmarking", "Trend Analysis", "Seasonal Adjustment"],
                "status": "Fully Implemented",
                "usage": "90%"
            }
        ]

        cols = st.columns(2)
        for idx, framework in enumerate(frameworks):
            with cols[idx % 2]:
                with st.container():
                    st.markdown(f"""
                    <div style="background: #f8fafc; padding: 15px; border-radius: 10px; 
                                border-left: 4px solid #8b5cf6; margin-bottom: 10px;">
                        <strong>{framework['name']}</strong><br>
                        <small>{framework['description']}</small><br>
                        <small><strong>Metrics:</strong> {', '.join(framework['metrics'])}</small><br>
                        <small><strong>Status:</strong> {framework['status']}</small><br>
                        <small><strong>Usage:</strong> {framework['usage']}</small>
                    </div>
                    """, unsafe_allow_html=True)

        # Framework adoption metrics
        st.markdown("##### 📈 Framework Adoption & Impact")

        adoption_data = pd.DataFrame({
            'Framework': ['Cohort Analysis', 'Markov Chain', 'Survival Analysis', 'Vintage Comparison'],
            'Adoption Rate': [95, 70, 45, 90],
            'User Satisfaction': [92, 75, 60, 88],
            'Business Impact': [90, 65, 50, 85],
            'ROI Estimate': ['High', 'Medium', 'Low', 'High']
        })

        fig = px.bar(
            adoption_data,
            x='Framework',
            y=['Adoption Rate', 'User Satisfaction', 'Business Impact'],
            title="Analytical Framework Performance",
            barmode='group',
            color_discrete_sequence=['#8b5cf6', '#a78bfa', '#c4b5fd']
        )
        st.plotly_chart(fig, use_container_width=True)

    def render_vintages_philosophy(self):
        """Render vintages and roll rates philosophy framework"""
        with st.expander("📜 Vintage Analytics Philosophy", expanded=False):
            cols = st.columns(3)
            for i, (key, value) in enumerate(VINTAGES_PHILOSOPHY.items()):
                with cols[i % 3]:
                    st.info(f"**{key}:**\n\n{value}")

            st.markdown("---")
            st.markdown("""
            **Strategic Vintage Analysis Approach:**  
            - **Cohort Tracking:** Monitor loan groups from origination through maturity  
            - **Predictive Insights:** Use historical patterns to forecast future performance  
            - **Underwriting Refinement:** Continuously improve credit policies based on cohort performance  
            - **Risk-Based Pricing:** Adjust pricing based on vintage performance data  
            - **Portfolio Management:** Optimize portfolio mix using vintage analytics  
            - **Regulatory Compliance:** Meet IFRS 9 and Basel requirements for expected credit losses
            """)

    def run(self):
        """Run the enhanced vintages page"""
        # Strategic Header
        self.render_strategic_header()

        # Vintage Analytics Philosophy
        self.render_vintages_philosophy()

        # Strategic KPI Cards
        self.render_strategic_kpi_cards()

        st.markdown("---")

        # Strategic Analysis Tabs
        self.render_strategic_tabs()

        # Log dashboard completion
        try:
            self.audit_logger.log_data_access(
                st.session_state.user,
                st.session_state.role,
                "vintages_analytics_completed"
            )
        except Exception:
            pass


if __name__ == "__main__":
    page = VintagesRollRatesPage()
    page.run()
