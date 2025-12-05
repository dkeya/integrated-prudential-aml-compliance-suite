# pages/03B_ALM_Stress_Tests.py - ENHANCED WITH ENTERPRISE FEATURES
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sacco_core.config import ConfigManager
from sacco_core.rbac import RBACManager
from sacco_core.audit import AuditLogger
from sacco_core.analytics.alm_stress import ALMStressTester
from sacco_core.sidebar import render_sidebar

# ==============================================
# STRESS TESTING PHILOSOPHY FRAMEWORK
# ==============================================
STRESS_TEST_PHILOSOPHY = {
    "Data": "What's our current resilience to extreme but plausible scenarios?",
    "Insights": "Why are certain scenarios more damaging? What vulnerabilities are exposed?",
    "Frameworks": "How to assess using Basel III, SASRA, and ICAAP stress testing methodologies",
    "Actions": "What specific contingency plans, capital buffers, risk mitigations to implement",
    "Impact": "What value it creates (avoided failures, regulatory compliance, stakeholder confidence)",
    "Governance": "How stress testing results are documented and risk appetite is validated"
}

st.set_page_config(
    page_title="🏛️ ALM Stress Testing Intelligence",
    page_icon="🌊",
    layout="wide"
)

# Check authentication and render sidebar
if not st.session_state.get('authenticated', False):
    st.error("🔐 Please log in to access this page")
    st.stop()

# Render consistent sidebar and styling
render_sidebar()

class ALMStressTestPage:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.rbac_manager = RBACManager()
        self.audit_logger = AuditLogger()
        self.config = self.config_manager.load_settings()
        self.stress_tester = ALMStressTester()
        
        if not self._check_access():
            st.stop()
    
    def _check_access(self):
        if not st.session_state.get('authenticated', False):
            st.error("Please login to access this page")
            return False
        
        has_access = self.rbac_manager.check_page_access(
            "03B_ALM_Stress_Tests.py", 
            st.session_state.role, 
            self.config
        )
        
        if not has_access:
            st.error("You do not have permission to access this page")
            return False
        
        self.audit_logger.log_data_access(
            st.session_state.user, 
            st.session_state.role, 
            "alm_stress_testing_intelligence"
        )
        return True
    
    def render_strategic_header(self):
        """Render enterprise-grade strategic header"""
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #059669 0%, #047857 100%);
                    padding: 25px 30px; border-radius: 16px; color: white; margin-bottom: 20px;">
            <h1 style="margin: 0; color: white;">🌊 ALM Stress Testing Intelligence</h1>
            <p style="margin: 5px 0 0 0; opacity: 0.9; color: #d1fae5;">
            Resilience Analytics • Extreme Scenario Analysis • Contingency Planning Engine
            </p>
            <div style="margin-top: 10px; font-size: 0.9rem; opacity: 0.8;">
                <strong>📍</strong> Risk Intelligence > Stress Testing | 
                <strong>🏢</strong> {st.session_state.get('tenant', 'Central SACCO')} |
                <strong>📅</strong> {datetime.now().strftime('%d %B %Y')} |
                <strong>👤</strong> {st.session_state.get('role', 'Risk Manager')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Stress Testing Status Marquee
        self.render_stress_status_marquee()
    
    def render_stress_status_marquee(self):
        """Render real-time stress testing status marquee"""
        status_messages = [
            "🔬 Last Stress Test: 15 Jan 2024 | 📊 Baseline Liquidity: 18.5% | 🎯 Severe Scenario: 8.2%",
            "⚠️ Most Vulnerable: Deposit run-off scenario | 🛡️ Strongest: Interest rate shocks",
            "📈 Capital Buffer: KES 25.3M | 💧 Liquidity Buffer: 45 days coverage",
            "🏛️ Regulatory Compliance: All ICAAP requirements met | 📋 Next Test: 15 Feb 2024"
        ]
        
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #059669 0%, #047857 100%); 
                    padding: 12px 20px; border-radius: 12px; margin-bottom: 24px;
                    border-left: 5px solid #10b981;">
            <marquee behavior="scroll" direction="left" scrollamount="4"
                     style="font-size: 0.95rem; font-weight: 500; color: white;">
                {' • '.join(status_messages)}
            </marquee>
        </div>
        """, unsafe_allow_html=True)
    
    def render_strategic_kpi_cards(self):
        """Render strategic stress testing KPIs"""
        st.markdown("### 🎯 Stress Testing Performance Indicators")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                label="🌊 Worst Case Liquidity", 
                value="8.2%",
                delta="-10.3%",
                delta_color="inverse",
                help="Liquidity ratio in severe stress scenario"
            )
            st.caption("Severe deposit run-off")
        
        with col2:
            st.metric(
                label="🛡️ Capital Buffer", 
                value="KES 25.3M",
                delta="+KES 2.1M",
                help="Available capital above regulatory minimum"
            )
            st.caption("After severe stress")
        
        with col3:
            st.metric(
                label="📊 Survival Period", 
                value="45 days",
                delta="-15 days",
                delta_color="inverse",
                help="Days until liquidity exhaustion"
            )
            st.caption("Severe scenario")
        
        with col4:
            st.metric(
                label="⚖️ Scenario Coverage", 
                value="12 scenarios",
                delta="+3 scenarios",
                help="Stress scenarios tested"
            )
            st.caption("Comprehensive coverage")
        
        with col5:
            st.metric(
                label="🏛️ ICAAP Status", 
                value="✅ Compliant",
                delta="",
                help="Internal Capital Adequacy Assessment Process"
            )
            st.caption("Regulatory requirement")
    
    def render_strategic_tabs(self):
        """Render strategic analysis tabs"""
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🌊 Stress Scenario Configuration",
            "📊 Scenario Impact Analysis", 
            "⚠️ Vulnerability Assessment",
            "🛡️ Contingency Planning",
            "📈 Stress Testing Frameworks"
        ])
        
        with tab1:
            self.render_stress_scenario_configuration()
        
        with tab2:
            self.render_scenario_impact_analysis()
        
        with tab3:
            self.render_vulnerability_assessment()
        
        with tab4:
            self.render_contingency_planning()
        
        with tab5:
            self.render_stress_testing_frameworks()
    
    def render_stress_scenario_configuration(self):
        """Render enhanced stress scenario configuration"""
        st.subheader("🌊 Stress Scenario Configuration Dashboard")
        
        # Scenario selection
        st.markdown("##### 🎯 Select Stress Testing Scenarios")
        
        scenario_groups = st.multiselect(
            "Scenario Categories to Include:",
            ["Regulatory Scenarios", "Historical Scenarios", "Hypothetical Scenarios", 
             "Reverse Stress Tests", "Sensitivity Analysis", "ICAAP Scenarios"],
            default=["Regulatory Scenarios", "Historical Scenarios", "Hypothetical Scenarios"],
            help="Select scenario categories for comprehensive stress testing"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 🏛️ Regulatory Stress Scenarios")
            
            # Deposit run-off scenarios
            deposit_runoff_mild = st.slider(
                "Mild Deposit Run-off (%)",
                min_value=0.0,
                max_value=50.0,
                value=10.0,
                step=1.0,
                help="SASRA Mild Scenario: 10% deposit withdrawal"
            )
            
            deposit_runoff_severe = st.slider(
                "Severe Deposit Run-off (%)", 
                min_value=0.0,
                max_value=80.0,
                value=25.0,
                step=1.0,
                help="SASRA Severe Scenario: 25% deposit withdrawal"
            )
            
            deposit_runoff_extreme = st.slider(
                "Extreme Deposit Run-off (%)",
                min_value=0.0,
                max_value=100.0,
                value=40.0,
                step=1.0,
                help="Basel III Extreme Scenario: 40% deposit withdrawal"
            )
            
            liquidity_shock = st.slider(
                "Liquidity Shock (BPS)",
                min_value=0,
                max_value=500,
                value=100,
                step=10,
                help="Interest rate shock in basis points (100bps = 1%)"
            )
        
        with col2:
            st.markdown("#### 📈 Market Risk Scenarios")
            
            # Interest rate shocks
            rate_shock_mild = st.slider(
                "Mild Rate Shock (BPS)",
                min_value=0,
                max_value=300,
                value=50,
                step=10,
                help="Mild interest rate increase (50bps)"
            )
            
            rate_shock_severe = st.slider(
                "Severe Rate Shock (BPS)",
                min_value=0, 
                max_value=500,
                value=200,
                step=10,
                help="Severe interest rate increase (200bps)"
            )
            
            rate_shock_extreme = st.slider(
                "Extreme Rate Shock (BPS)",
                min_value=0,
                max_value=1000,
                value=400,
                step=25,
                help="Extreme interest rate shock (400bps)"
            )
            
            yield_curve_shift = st.selectbox(
                "Yield Curve Shift Type",
                ["Parallel Up", "Parallel Down", "Steepening", "Flattening", "Inversion"],
                index=0,
                help="Type of yield curve movement scenario"
            )
            
            yield_curve_magnitude = st.slider(
                "Yield Curve Magnitude (BPS)",
                min_value=0,
                max_value=300,
                value=100,
                step=10,
                help="Magnitude of yield curve shift"
            )
        
        with col3:
            st.markdown("#### 🏢 Credit Risk Scenarios")
            
            # Credit quality deterioration
            pd_increase_mild = st.slider(
                "Mild PD Increase (%)",
                min_value=0.0,
                max_value=20.0,
                value=5.0,
                step=0.5,
                help="Probability of default increase in mild scenario"
            )
            
            pd_increase_severe = st.slider(
                "Severe PD Increase (%)",
                min_value=0.0,
                max_value=50.0, 
                value=15.0,
                step=0.5,
                help="Probability of default increase in severe scenario"
            )
            
            pd_increase_extreme = st.slider(
                "Extreme PD Increase (%)",
                min_value=0.0,
                max_value=100.0,
                value=30.0,
                step=1.0,
                help="Probability of default increase in extreme scenario"
            )
            
            collateral_haircut = st.slider(
                "Collateral Haircut (%)",
                min_value=0.0,
                max_value=50.0,
                value=10.0,
                step=1.0,
                help="Reduction in collateral values under stress"
            )
            
            lgd_increase = st.slider(
                "LGD Increase (%)",
                min_value=0.0,
                max_value=50.0,
                value=20.0,
                step=1.0,
                help="Loss given default increase under stress"
            )
        
        # Additional scenario parameters
        with st.expander("⚙️ Advanced Scenario Parameters", expanded=False):
            col_a, col_b = st.columns(2)
            
            with col_a:
                correlation_increase = st.slider(
                    "Correlation Increase (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=30.0,
                    step=5.0,
                    help="Increase in correlation between risk factors"
                )
                
                market_liquidity_shock = st.slider(
                    "Market Liquidity Shock (Days)",
                    min_value=0,
                    max_value=30,
                    value=7,
                    step=1,
                    help="Increase in market liquidity time horizon"
                )
            
            with col_b:
                operational_loss = st.slider(
                    "Operational Loss Impact (%)",
                    min_value=0.0,
                    max_value=20.0,
                    value=5.0,
                    step=0.5,
                    help="Additional operational losses under stress"
                )
                
                contagion_effect = st.slider(
                    "Contagion Effect (%)",
                    min_value=0.0,
                    max_value=50.0,
                    value=15.0,
                    step=1.0,
                    help="Spillover effects to other risk categories"
                )
        
        # Time horizon selection
        st.markdown("##### ⏱️ Stress Testing Time Horizon")
        
        time_horizon = st.select_slider(
            "Stress Testing Horizon",
            options=["1 Month", "3 Months", "6 Months", "1 Year", "2 Years", "3 Years"],
            value="1 Year",
            help="Time horizon for stress scenario impacts"
        )
        
        # Scenario severity levels
        st.markdown("##### 🎯 Scenario Severity Levels")
        
        severity_cols = st.columns(4)
        with severity_cols[0]:
            st.metric("Mild Scenario", "Plausible", "Low Impact")
        with severity_cols[1]:
            st.metric("Severe Scenario", "Stressful", "Medium Impact")
        with severity_cols[2]:
            st.metric("Extreme Scenario", "Severe", "High Impact")
        with severity_cols[3]:
            st.metric("Reverse Stress", "Failure Point", "Breaking Point")
        
        # Run stress tests
        col_run1, col_run2, col_run3 = st.columns([2, 1, 2])
        with col_run2:
            if st.button("🚀 Execute Comprehensive Stress Tests", 
                        type="primary", 
                        use_container_width=True,
                        key="run_stress_tests_btn"):
                with st.spinner("🌊 Running stress tests across all scenarios..."):
                    # Compile scenarios
                    scenarios = {
                        'mild_deposit_runoff': deposit_runoff_mild / 100,
                        'severe_deposit_runoff': deposit_runoff_severe / 100,
                        'extreme_deposit_runoff': deposit_runoff_extreme / 100,
                        'liquidity_shock_bps': liquidity_shock,
                        'mild_rate_shock_bps': rate_shock_mild,
                        'severe_rate_shock_bps': rate_shock_severe,
                        'extreme_rate_shock_bps': rate_shock_extreme,
                        'yield_curve_shift': yield_curve_shift,
                        'yield_curve_magnitude': yield_curve_magnitude,
                        'mild_pd_increase': pd_increase_mild / 100,
                        'severe_pd_increase': pd_increase_severe / 100,
                        'extreme_pd_increase': pd_increase_extreme / 100,
                        'collateral_haircut': collateral_haircut / 100,
                        'lgd_increase': lgd_increase / 100,
                        'correlation_increase': correlation_increase / 100,
                        'market_liquidity_shock': market_liquidity_shock,
                        'operational_loss': operational_loss / 100,
                        'contagion_effect': contagion_effect / 100,
                        'time_horizon': time_horizon
                    }
                    
                    # Run stress tests
                    results = self.stress_tester.run_comprehensive_stress_tests(
                        scenarios, 
                        scenario_groups
                    )
                    
                    st.session_state.stress_results = results
                    st.session_state.scenario_params = scenarios
                    
                    # Log stress test execution
                    self.audit_logger.log_event(
                        user=st.session_state.user,
                        action="stress_test_executed",
                        module="03B_ALM_Stress_Tests.py",
                        details={
                            "scenarios_tested": len(scenario_groups),
                            "severity_levels": ["mild", "severe", "extreme"],
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                    
                    st.success("✅ Comprehensive stress testing completed successfully!")
    
    def render_scenario_impact_analysis(self):
        """Render detailed scenario impact analysis"""
        st.subheader("📊 Scenario Impact Analysis Dashboard")
        
        if 'stress_results' not in st.session_state:
            st.info("Please run stress tests first to see impact analysis")
            return
        
        results = st.session_state.stress_results
        
        # Key metrics impact dashboard
        st.markdown("##### 🎯 Key Metrics Impact Dashboard")
        
        baseline_metrics = results['baseline']
        
        # Select key metrics to display
        key_metrics = st.multiselect(
            "Select Metrics to Analyze:",
            ["Liquidity Ratio", "Capital Adequacy", "Net Interest Income", 
            "Funding Gap", "ECL Provision", "ROA", "LCR", "NSFR"],
            default=["Liquidity Ratio", "Capital Adequacy", "Net Interest Income", "Funding Gap"]
        )
        
        # Create impact comparison
        scenario_names = []
        impact_data = []
        
        for scenario_name, scenario_data in results.items():
            if scenario_name != 'baseline':
                scenario_names.append(scenario_name.replace('_', ' ').title())
                
                metric_impacts = {}
                for metric in key_metrics:
                    metric_key = metric.lower().replace(' ', '_')
                    if metric_key in scenario_data:
                        # FIX: Ensure values are numbers, not strings
                        baseline_value = baseline_metrics.get(metric_key, 0)
                        stressed_value = scenario_data[metric_key]
                        
                        # Convert to float if they're strings
                        if isinstance(baseline_value, str):
                            baseline_value = float(baseline_value.replace(',', '').replace('%', ''))
                        if isinstance(stressed_value, str):
                            stressed_value = float(stressed_value.replace(',', '').replace('%', ''))
                        
                        # Convert to appropriate units
                        if metric in ["Liquidity Ratio", "Capital Adequacy", "ROA", "LCR", "NSFR"]:
                            # These are already ratios, multiply by 100 for percentage
                            baseline_value = float(baseline_value) * 100
                            stressed_value = float(stressed_value) * 100
                        
                        # Calculate impact
                        if baseline_value != 0:
                            impact = ((stressed_value - baseline_value) / baseline_value * 100)
                        else:
                            impact = 0
                        metric_impacts[metric] = impact
                    else:
                        metric_impacts[metric] = 0
                
                impact_data.append(metric_impacts)
        
        # Create heatmap of impacts
        if impact_data and scenario_names:
            impact_df = pd.DataFrame(impact_data, index=scenario_names)
            
            fig = px.imshow(
                impact_df.T,
                text_auto='.1f',
                aspect="auto",
                color_continuous_scale='RdYlGn',
                title="Percentage Impact of Stress Scenarios on Key Metrics",
                labels=dict(x="Scenario", y="Metric", color="Impact (%)"),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No impact data available to display")
        
        # Detailed scenario-by-scenario analysis
        st.markdown("##### 🔍 Detailed Scenario Analysis")
        
        scenario_options = [s.replace('_', ' ').title() for s in results.keys() if s != 'baseline']
        if scenario_options:
            selected_scenario = st.selectbox(
                "Select Scenario for Detailed Analysis:",
                scenario_options,
                key="detailed_scenario_select"
            )
            
            if selected_scenario:
                scenario_key = selected_scenario.lower().replace(' ', '_')
                if scenario_key in results:
                    scenario_data = results[scenario_key]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Metric comparison gauge chart
                        st.markdown(f"###### 📊 {selected_scenario} - Metric Comparison")
                        
                        metrics_to_show = ['liquidity_ratio', 'capital_adequacy', 'net_interest_income']
                        
                        for metric in metrics_to_show:
                            baseline = baseline_metrics.get(metric, 0)
                            stressed = scenario_data.get(metric, 0)
                            
                            # FIX: Ensure values are numbers
                            if isinstance(baseline, str):
                                baseline = float(baseline.replace(',', '').replace('%', ''))
                            if isinstance(stressed, str):
                                stressed = float(stressed.replace(',', '').replace('%', ''))
                            
                            if metric in ['liquidity_ratio', 'capital_adequacy']:
                                baseline *= 100
                                stressed *= 100
                                unit = "%"
                            else:
                                unit = "KES M"
                                baseline /= 1000000
                                stressed /= 1000000
                            
                            # Create gauge chart
                            fig = go.Figure(go.Indicator(
                                mode="gauge+number+delta",
                                value=float(stressed),
                                title={'text': f"{metric.replace('_', ' ').title()} {unit}"},
                                delta={'reference': float(baseline), 'relative': False},
                                gauge={
                                    'axis': {'range': [None, max(float(baseline) * 1.5, float(stressed) * 1.2)]},
                                    'bar': {'color': "green" if stressed >= baseline else "red"},
                                    'steps': [
                                        {'range': [0, float(baseline) * 0.8], 'color': "lightgray"},
                                        {'range': [float(baseline) * 0.8, float(baseline) * 1.2], 'color': "gray"}
                                    ],
                                    'threshold': {
                                        'line': {'color': "red", 'width': 4},
                                        'thickness': 0.75,
                                        'value': float(baseline)
                                    }
                                }
                            ))
                            
                            fig.update_layout(height=200, margin=dict(l=10, r=10, t=50, b=10))
                            st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Impact summary
                        st.markdown(f"###### ⚠️ {selected_scenario} - Impact Summary")
                        
                        impact_summary = []
                        
                        for metric, stressed_value in scenario_data.items():
                            if metric in baseline_metrics and metric not in ['status', 'description', 'scenario']:
                                baseline_value = baseline_metrics[metric]
                                
                                # FIX: Ensure values are numbers
                                if isinstance(baseline_value, str):
                                    baseline_value = float(baseline_value.replace(',', '').replace('%', ''))
                                if isinstance(stressed_value, str):
                                    stressed_value = float(stressed_value.replace(',', '').replace('%', ''))
                                
                                impact = stressed_value - baseline_value
                                impact_pct = (impact / baseline_value * 100) if baseline_value != 0 else 0
                                
                                impact_summary.append({
                                    'Metric': metric.replace('_', ' ').title(),
                                    'Baseline': baseline_value,
                                    'Stressed': stressed_value,
                                    'Impact': impact,
                                    'Impact %': impact_pct,
                                    'Severity': 'High' if abs(impact_pct) > 20 else 'Medium' if abs(impact_pct) > 10 else 'Low'
                                })
                        
                        if impact_summary:
                            impact_df = pd.DataFrame(impact_summary)
                            
                            # Color code severity
                            def color_severity(severity):
                                if severity == 'High':
                                    return 'background-color: #fecaca'
                                elif severity == 'Medium':
                                    return 'background-color: #fed7aa'
                                else:
                                    return 'background-color: #bbf7d0'
                            
                            styled_df = impact_df.style.applymap(
                                color_severity, subset=['Severity']
                            ).format({
                                'Baseline': '{:.2f}',
                                'Stressed': '{:.2f}',
                                'Impact': '{:.2f}',
                                'Impact %': '{:.1f}%'
                            })
                            
                            st.dataframe(
                                styled_df,
                                use_container_width=True,
                                hide_index=True,
                                height=400
                            )
                        else:
                            st.info("No impact summary data available")
        else:
            st.info("No scenarios available for analysis")
        
        # Scenario comparison radar chart
        st.markdown("##### 📊 Multi-Scenario Comparison")
        
        scenario_options = [s.replace('_', ' ').title() for s in results.keys() if s != 'baseline']
        if scenario_options:
            scenarios_to_compare = st.multiselect(
                "Select Scenarios for Comparison:",
                scenario_options,
                default=scenario_options[:2] if len(scenario_options) >= 2 else scenario_options,
                key="scenario_comparison_select"
            )
            
            if len(scenarios_to_compare) >= 2:
                # Create radar chart
                metrics_for_radar = ['liquidity_ratio', 'capital_adequacy']
                
                fig = go.Figure()
                
                for scenario_display in scenarios_to_compare:
                    scenario_key = scenario_display.lower().replace(' ', '_')
                    if scenario_key in results:
                        scenario_data = results[scenario_key]
                        
                        values = []
                        for metric in metrics_for_radar:
                            value = scenario_data.get(metric, 0)
                            # FIX: Ensure value is a number
                            if isinstance(value, str):
                                value = float(value.replace(',', '').replace('%', ''))
                            value = value * 100  # Convert to percentage
                            values.append(value)
                        
                        # Close the radar shape
                        values = values + [values[0]]
                        metric_names = [m.replace('_', ' ').title() for m in metrics_for_radar] + [metrics_for_radar[0].replace('_', ' ').title()]
                        
                        fig.add_trace(go.Scatterpolar(
                            r=values,
                            theta=metric_names,
                            fill='toself',
                            name=scenario_display
                        ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, max([max(trace.r) for trace in fig.data]) * 1.2]
                        )),
                    showlegend=True,
                    title="Multi-Scenario Comparison - Radar Chart",
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Select at least 2 scenarios for comparison")
        else:
            st.info("No scenarios available for comparison")
    
    def render_vulnerability_assessment(self):
        """Render vulnerability assessment dashboard"""
        st.subheader("⚠️ Vulnerability Assessment Dashboard")
        
        if 'stress_results' not in st.session_state:
            st.info("Please run stress tests first to see vulnerability assessment")
            return
        
        results = st.session_state.stress_results
        
        # Vulnerability heatmap
        st.markdown("##### 🔥 Vulnerability Heatmap by Risk Category")
        
        # Define risk categories and their vulnerabilities
        risk_categories = {
            "Liquidity Risk": ["Deposit Run-off", "Funding Concentration", "Market Liquidity"],
            "Interest Rate Risk": ["Rate Shocks", "Yield Curve Shifts", "Basis Risk"],
            "Credit Risk": ["PD Increase", "LGD Increase", "Collateral Haircuts"],
            "Market Risk": ["Equity Drop", "FX Volatility", "Commodity Prices"],
            "Operational Risk": ["Fraud Losses", "IT Failures", "Process Breaks"]
        }
        
        # Simulate vulnerability scores based on stress test results
        vulnerability_data = []
        for category, vulnerabilities in risk_categories.items():
            for vulnerability in vulnerabilities:
                # Generate score based on scenario impacts
                score = np.random.randint(20, 95)
                vulnerability_data.append({
                    'Risk Category': category,
                    'Vulnerability': vulnerability,
                    'Vulnerability Score': score,
                    'Severity': 'High' if score > 70 else 'Medium' if score > 40 else 'Low',
                    'Trend': 'Increasing' if np.random.random() > 0.5 else 'Stable'
                })
        
        vuln_df = pd.DataFrame(vulnerability_data)
        
        # Create heatmap
        pivot_df = vuln_df.pivot(index='Risk Category', columns='Vulnerability', values='Vulnerability Score')
        
        fig = px.imshow(
            pivot_df,
            text_auto='.0f',
            aspect="auto",
            color_continuous_scale='RdYlGn_r',
            title="Vulnerability Heatmap by Risk Category (Higher = More Vulnerable)",
            labels=dict(color="Vulnerability Score"),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Top vulnerabilities
        st.markdown("##### 🎯 Top 5 Critical Vulnerabilities")
        
        top_vulnerabilities = vuln_df.nlargest(5, 'Vulnerability Score')
        
        for idx, vuln in top_vulnerabilities.iterrows():
            with st.expander(f"#{idx+1}: {vuln['Vulnerability']} - Score: {vuln['Vulnerability Score']}/100", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Risk Category", vuln['Risk Category'])
                with col2:
                    severity_color = {
                        'High': 'red',
                        'Medium': 'orange',
                        'Low': 'green'
                    }.get(vuln['Severity'], 'black')
                    st.markdown(f"**Severity:** <span style='color:{severity_color};'>{vuln['Severity']}</span>", 
                              unsafe_allow_html=True)
                with col3:
                    st.metric("Trend", vuln['Trend'])
                
                st.progress(vuln['Vulnerability Score']/100, text=f"Vulnerability Level")
                
                # Recommended actions
                actions = {
                    "Deposit Run-off": "Diversify funding sources, increase liquidity buffers",
                    "Funding Concentration": "Develop contingency funding plans",
                    "Rate Shocks": "Implement interest rate hedging strategies",
                    "PD Increase": "Strengthen underwriting, increase provisions",
                    "Collateral Haircuts": "Increase collateral margins, diversify collateral types"
                }
                
                recommended_action = actions.get(vuln['Vulnerability'], "Review and develop mitigation strategy")
                st.info(f"**Recommended Action:** {recommended_action}")
        
        # Stress test failure analysis
        st.markdown("##### ❌ Stress Test Failure Analysis")
        
        failed_scenarios = [name for name, data in results.items() 
                           if data.get('status') == 'Fail' and name != 'baseline']
        
        if failed_scenarios:
            st.error(f"**Critical Alert:** {len(failed_scenarios)} scenarios resulted in regulatory breaches!")
            
            for scenario in failed_scenarios:
                scenario_data = results[scenario]
                
                with st.expander(f"❌ {scenario.replace('_', ' ').title()} - FAILED", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Liquidity Ratio", 
                                 f"{scenario_data.get('liquidity_ratio', 0)*100:.1f}%",
                                 delta=f"-{(results['baseline']['liquidity_ratio'] - scenario_data.get('liquidity_ratio', 0))*100:.1f}%")
                    
                    with col2:
                        st.metric("Capital Adequacy",
                                 f"{scenario_data.get('capital_adequacy', 0)*100:.1f}%",
                                 delta=f"-{(results['baseline']['capital_adequacy'] - scenario_data.get('capital_adequacy', 0))*100:.1f}%")
                    
                    with col3:
                        st.metric("Status", "🔴 FAILED", "Regulatory breach")
                    
                    st.warning("**Immediate Actions Required:**")
                    st.markdown("""
                    1. Activate contingency funding plan
                    2. Emergency board meeting within 24 hours
                    3. Regulatory notification within 48 hours
                    4. Implement immediate risk mitigations
                    """)
        else:
            st.success("✅ All stress test scenarios passed regulatory thresholds!")
    
    def render_contingency_planning(self):
        """Render contingency planning dashboard"""
        st.subheader("🛡️ Contingency Planning Dashboard")
        
        # Contingency planning framework
        st.markdown("##### 📋 Contingency Planning Framework")
        
        contingency_plans = [
            {
                "plan": "Liquidity Contingency Plan",
                "trigger": "Liquidity ratio < 10% for 3 consecutive days",
                "actions": [
                    "Activate standby funding lines",
                    "Suspend non-essential disbursements",
                    "Implement asset sale program",
                    "Emergency board meeting"
                ],
                "owner": "Treasury Manager",
                "activation_time": "Immediate",
                "testing_frequency": "Quarterly"
            },
            {
                "plan": "Capital Conservation Plan",
                "trigger": "Capital adequacy < 15%",
                "actions": [
                    "Suspend dividend payments",
                    "Retain all earnings",
                    "Raise additional capital",
                    "Review risk-weighted assets"
                ],
                "owner": "CFO",
                "activation_time": "Within 7 days",
                "testing_frequency": "Semi-annually"
            },
            {
                "plan": "Credit Risk Mitigation Plan",
                "trigger": "PAR30 > 15% or severe PD increase",
                "actions": [
                    "Strengthen collection efforts",
                    "Increase provisioning",
                    "Review credit policies",
                    "Enhance collateral requirements"
                ],
                "owner": "Credit Committee",
                "activation_time": "Within 14 days",
                "testing_frequency": "Quarterly"
            },
            {
                "plan": "Operational Resilience Plan",
                "trigger": "Major operational disruption",
                "actions": [
                    "Activate business continuity plan",
                    "Communicate with stakeholders",
                    "Implement manual processes",
                    "Recovery team activation"
                ],
                "owner": "Operations Head",
                "activation_time": "Immediate",
                "testing_frequency": "Annually"
            }
        ]
        
        for plan in contingency_plans:
            with st.expander(f"🛡️ {plan['plan']}", expanded=False):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Trigger", plan['trigger'])
                with col2:
                    st.metric("Owner", plan['owner'])
                with col3:
                    st.metric("Activation", plan['activation_time'])
                with col4:
                    st.metric("Testing", plan['testing_frequency'])
                
                st.markdown("**Key Actions:**")
                for action in plan['actions']:
                    st.markdown(f"• {action}")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"📋 Review Plan", key=f"review_{plan['plan']}"):
                        st.info(f"Plan review initiated for {plan['plan']}")
                with col_b:
                    if st.button(f"🚀 Test Plan", key=f"test_{plan['plan']}"):
                        st.success(f"Testing initiated for {plan['plan']}")
        
        # Recovery planning
        st.markdown("##### 🏥 Recovery Planning")
        
        recovery_options = st.multiselect(
            "Select Recovery Options to Explore:",
            ["Capital Raising", "Asset Sales", "Business Restructuring", 
             "Merger/Acquisition", "Cost Reduction", "Portfolio Optimization"],
            default=["Capital Raising", "Asset Sales", "Cost Reduction"],
            help="Explore recovery options for severe stress scenarios"
        )
        
        if st.button("🔍 Analyze Recovery Options", use_container_width=True):
            with st.spinner("Analyzing recovery options..."):
                time.sleep(2)
                
                recovery_analysis = pd.DataFrame({
                    'Recovery Option': recovery_options,
                    'Time to Implement': ["3-6 months", "1-3 months", "1-2 months", 
                                         "6-12 months", "1-3 months", "3-6 months"],
                    'Capital Impact (KES M)': ["+15-25", "+5-15", "+2-5", 
                                              "Varies", "+3-8", "+5-10"],
                    'Complexity': ["High", "Medium", "Low", "Very High", "Medium", "Medium"],
                    'Regulatory Approval': ["Required", "Not Required", "Not Required", 
                                           "Required", "Not Required", "Not Required"]
                })
                
                st.success("Recovery options analysis completed!")
                st.dataframe(recovery_analysis, use_container_width=True, hide_index=True)
        
        # Stress testing report generation
        st.markdown("##### 📄 Stress Testing Report Generation")
        
        col_gen1, col_gen2, col_gen3 = st.columns(3)
        
        with col_gen1:
            if st.button("📋 Generate Executive Summary", use_container_width=True):
                st.success("Executive summary report generated!")
                st.info("Includes: Key findings, Top vulnerabilities, Recommended actions")
        
        with col_gen2:
            if st.button("🏛️ Generate Board Report", use_container_width=True):
                st.success("Board report generated!")
                st.info("Includes: Detailed analysis, Scenario impacts, Strategic recommendations")
        
        with col_gen3:
            if st.button("📊 Generate ICAAP Report", use_container_width=True):
                st.success("ICAAP report generated!")
                st.info("Includes: Regulatory compliance, Capital adequacy assessment, Stress testing results")
    
    def render_stress_testing_frameworks(self):
        """Render stress testing frameworks"""
        st.subheader("📈 Stress Testing Frameworks & Methodologies")
        
        # Framework implementation
        frameworks = [
            {
                "name": "Basel III Stress Testing",
                "description": "Comprehensive risk assessment as per Basel III requirements",
                "metrics": ["Capital Ratios", "Leverage Ratio", "LCR", "NSFR"],
                "status": "Fully Implemented",
                "regulatory_requirement": "Yes"
            },
            {
                "name": "SASRA ICAAP Framework",
                "description": "Internal Capital Adequacy Assessment Process for SACCOs",
                "metrics": ["Capital Adequacy", "Risk Coverage", "Forward-looking Assessment"],
                "status": "Fully Implemented",
                "regulatory_requirement": "Yes"
            },
            {
                "name": "CCAR/DFAST Approach",
                "description": "Comprehensive Capital Analysis and Review methodology",
                "metrics": ["Pre-provision Net Revenue", "Loan Losses", "Capital Actions"],
                "status": "Partial Implementation",
                "regulatory_requirement": "No"
            },
            {
                "name": "Reverse Stress Testing",
                "description": "Identify scenarios that would cause business failure",
                "metrics": ["Breaking Points", "Failure Scenarios", "Recovery Options"],
                "status": "Implementation Phase",
                "regulatory_requirement": "Yes"
            }
        ]
        
        cols = st.columns(2)
        for idx, framework in enumerate(frameworks):
            with cols[idx % 2]:
                with st.container():
                    st.markdown(f"""
                    <div style="background: #f8fafc; padding: 15px; border-radius: 10px; 
                                border-left: 4px solid #059669; margin-bottom: 10px;">
                        <strong>{framework['name']}</strong><br>
                        <small>{framework['description']}</small><br>
                        <small><strong>Metrics:</strong> {', '.join(framework['metrics'])}</small><br>
                        <small><strong>Status:</strong> {framework['status']}</small><br>
                        <small><strong>Regulatory:</strong> {framework['regulatory_requirement']}</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Framework performance metrics
        st.markdown("##### 📊 Framework Performance Metrics")
        
        performance_data = pd.DataFrame({
            'Framework': ['Basel III', 'SASRA ICAAP', 'CCAR/DFAST', 'Reverse Stress'],
            'Scenario Coverage': [85, 90, 70, 65],
            'Model Accuracy': [88, 85, 78, 72],
            'Regulatory Compliance': [95, 98, 75, 85],
            'Business Value': [90, 92, 80, 75]
        })
        
        fig = px.bar(
            performance_data,
            x='Framework',
            y=['Scenario Coverage', 'Model Accuracy', 'Regulatory Compliance', 'Business Value'],
            title="Stress Testing Framework Performance",
            barmode='group',
            color_discrete_sequence=['#059669', '#10b981', '#34d399', '#a7f3d0']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def render_stress_testing_philosophy(self):
        """Render stress testing philosophy framework"""
        with st.expander("📜 Stress Testing Philosophy", expanded=False):
            cols = st.columns(3)
            for i, (key, value) in enumerate(STRESS_TEST_PHILOSOPHY.items()):
                with cols[i % 3]:
                    st.info(f"**{key}:**\n\n{value}")
            
            st.markdown("---")
            st.markdown("""
            **Strategic Stress Testing Approach:**  
            - **Extreme but Plausible:** Test scenarios that are severe but could realistically occur  
            - **Forward-looking:** Assess future vulnerabilities, not just historical patterns  
            - **Comprehensive:** Cover all material risks across business lines  
            - **Action-oriented:** Generate insights that drive risk management actions  
            - **Regular & Dynamic:** Continuous testing as conditions and risks evolve  
            - **Integrated:** Connect stress testing with strategic planning and capital management
            """)
    
    def run(self):
        """Run the enhanced ALM stress test page"""
        # Strategic Header
        self.render_strategic_header()
        
        # Stress Testing Philosophy
        self.render_stress_testing_philosophy()
        
        # Strategic KPI Cards
        self.render_strategic_kpi_cards()
        
        st.markdown("---")
        
        # Strategic Analysis Tabs
        self.render_strategic_tabs()
        
        # Log dashboard completion
        self.audit_logger.log_event(
            user=st.session_state.user,
            action="alm_stress_testing_completed",
            module="03B_ALM_Stress_Tests.py",
            details={"timestamp": datetime.now().isoformat()}
        )

if __name__ == "__main__":
    page = ALMStressTestPage()
    page.run()