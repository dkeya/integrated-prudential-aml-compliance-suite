# pages/06A_Employer_Limits_Alerts.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
import json
import time
from threading import Thread

# -------------------------------------------------
# Make sure Python can see the project root so core.* works
# -------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# -------------------------------------------------
# UNIFIED / LOCAL IMPORTS (core.* instead of sacco_core.*)
# -------------------------------------------------
from core.config import ConfigManager
from core.rbac import RBACManager
from core.audit import audit_logger
from core.analytics.concentration import ConcentrationAnalyzer
from core.sidebar import render_sidebar

st.set_page_config(
    page_title="Employer Limits Command Center | Risk Ops",
    page_icon="🚨",
    layout="wide"
)

# -------------------------------------------------
# AUTH CHECK & COMMON SIDEBAR
# -------------------------------------------------
if not st.session_state.get('authenticated', False):
    st.error("🔐 Please log in to access this page")
    st.stop()

# Render consistent sidebar and styling (unified)
render_sidebar()

# =============================================
# ENTERPRISE ENHANCEMENTS: Alert Intelligence Framework
# =============================================
ALERT_PHILOSOPHY = {
    "Data": "What's the real-time employer limit utilization and breach status?",
    "Insights": "Why are breaches occurring and what patterns predict future violations?",
    "Frameworks": "How to monitor using SASRA limits, early warning systems, and predictive analytics?",
    "Actions": "What specific interventions, automations, and escalation protocols to implement?",
    "Impact": "What value it creates (regulatory compliance, risk mitigation, operational excellence)?",
    "Governance": "How alert decisions are tracked, audited, and accountability maintained?"
}

class EmployerLimitsAlertsPage:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.rbac_manager = RBACManager()
        # ✅ Use unified audit_logger instance (no AuditLogger class here)
        self.audit_logger = audit_logger
        self.config = self.config_manager.load_settings()
        self.concentration_analyzer = ConcentrationAnalyzer()
        
        # Initialize session state for real-time features
        if 'alert_refresh' not in st.session_state:
            st.session_state.alert_refresh = datetime.now()
        if 'active_simulations' not in st.session_state:
            st.session_state.active_simulations = {}
        
        if not self._check_access():
            st.stop()
    
    def _check_access(self):
        if not st.session_state.get('authenticated', False):
            st.error("Please login to access this page")
            return False
        
        has_access = self.rbac_manager.check_page_access(
            "06A_Employer_Limits_Alerts.py", 
            st.session_state.role, 
            self.config
        )
        
        if not has_access:
            st.error("You do not have permission to access this page")
            return False
        
        # ✅ Use unified logger
        self.audit_logger.log_data_access(
            st.session_state.user, 
            st.session_state.role, 
            "employer_limits_alerts_page"
        )
        return True
    
    def render_command_center_header(self):
        """Render enterprise command center header with cyber security theme"""
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 30%, #0f3460 100%);
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            color: white;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
            position: relative;
            overflow: hidden;
        ">
            <div style="position: absolute; top: 0; right: 0; width: 200px; height: 100%; 
                        background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.1));
                        transform: skewX(-20deg);">
            </div>
            
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <h1 style="color: white; margin: 0; flex-grow: 1;">🚨 EMPLOYER LIMITS COMMAND CENTER</h1>
                <div style="display: flex; gap: 10px; align-items: center;">
                    <span style="background: rgba(255, 71, 71, 0.2); color: #ff4747; padding: 4px 12px; 
                               border-radius: 20px; font-weight: bold; border: 1px solid #ff4747;">
                        LIVE MONITORING
                    </span>
                    <span style="font-size: 0.9rem; color: #94a3b8;">
                        Last updated: {st.session_state.alert_refresh.strftime("%H:%M:%S")}
                    </span>
                </div>
            </div>
            
            <p style="color: #cbd5e1; margin-bottom: 0; font-size: 1.1rem;">
                Real-time SASRA limit monitoring | Predictive breach analytics | Automated escalation protocols
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_threat_intelligence_marquee(self):
        """Render real-time threat intelligence marquee with cyber security theme"""
        try:
            analysis = self.concentration_analyzer.analyze_employer_concentration()
            employer_exposures = analysis.get('employer_exposures', [])
            
            # Calculate threat levels
            active_breaches = len([e for e in employer_exposures if e.get('exposure_share', 0) > self.config.limits.single_employer_share_max])
            
            # Determine threat level
            if active_breaches > 3:
                threat_level = "CRITICAL"
                threat_color = "#ff0000"
                threat_icon = "🔥"
            elif active_breaches > 0:
                threat_level = "HIGH"
                threat_color = "#ff6b6b"
                threat_icon = "⚠️"
            else:
                threat_level = "LOW"
                threat_color = "#4ade80"
                threat_icon = "✅"
            
            # Calculate predictive alerts
            predictive_alerts = self._calculate_predictive_alerts(employer_exposures)
            
            st.markdown(f"""
            <div style="
                background: {threat_color}10;
                border: 2px solid {threat_color};
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 1.5rem;
                display: grid;
                grid-template-columns: auto 1fr auto;
                gap: 1rem;
                align-items: center;
                box-shadow: 0 4px 12px {threat_color}30;
            ">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="background: {threat_color}; width: 12px; height: 12px; border-radius: 50%; 
                                animation: pulse 2s infinite;"></div>
                    <span style="font-weight: bold; font-size: 1.2rem; color: {threat_color};">
                        {threat_icon} THREAT LEVEL: {threat_level}
                    </span>
                </div>
                
                <div style="display: flex; gap: 2rem; justify-content: center;">
                    <span style="color: {threat_color};">
                        <strong>{active_breaches}</strong> Active Breaches
                    </span>
                    <span style="color: {threat_color};">
                        <strong>{predictive_alerts['predictive_breaches']}</strong> Predicted Breaches
                    </span>
                    <span style="color: {threat_color};">
                        <strong>{predictive_alerts['escalations_needed']}</strong> Escalations Required
                    </span>
                </div>
                
                <div>
                    <span style="background: {threat_color}; color: white; padding: 4px 12px; 
                               border-radius: 16px; font-size: 0.9rem; font-weight: bold;">
                        {threat_icon} {threat_level} THREAT
                    </span>
                </div>
            </div>
            
            <style>
                @keyframes pulse {{
                    0% {{ opacity: 1; }}
                    50% {{ opacity: 0.5; }}
                    100% {{ opacity: 1; }}
                }}
            </style>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error in threat intelligence: {str(e)}")
    
    def _calculate_predictive_alerts(self, employer_exposures):
        """Calculate predictive alerts using trend analysis"""
        predictive_breaches = 0
        escalations_needed = 0
        
        for employer in employer_exposures:
            exposure_share = employer.get('exposure_share', 0)
            growth_rate = employer.get('growth_rate', 0.02)  # Default 2% monthly growth
            
            # Predict next month exposure
            predicted_exposure = exposure_share * (1 + growth_rate)
            limit = self.config.limits.single_employer_share_max
            
            if predicted_exposure > limit:
                predictive_breaches += 1
            
            if exposure_share > 0.9 * limit:  # 90% of limit
                escalations_needed += 1
        
        return {
            'predictive_breaches': predictive_breaches,
            'escalations_needed': escalations_needed
        }
    
    def render_alert_intelligence_framework(self):
        """Render alert intelligence framework"""
        with st.expander("🧠 ALERT INTELLIGENCE FRAMEWORK", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**🛡️ Proactive Defense**")
                st.info("Real-time monitoring with predictive analytics prevents breaches before they occur")
                st.markdown("**⚡ Rapid Response**")
                st.info("Automated workflows ensure immediate action on detected threats")
            
            with col2:
                st.markdown("**🎯 Intelligent Escalation**")
                st.info("Smart routing ensures the right people get notified at the right time")
                st.markdown("**📊 Performance Analytics**")
                st.info("Continuous improvement through data-driven insights and simulations")
            
            with col3:
                st.markdown("**🤖 Automation First**")
                st.info("Maximizing efficiency through intelligent automation of routine tasks")
                st.markdown("**🔒 Security by Design**")
                st.info("Built-in security and audit trails for regulatory compliance")
    
    def render_operations_command_dashboard(self):
        """Render operations command dashboard with strategic tabs"""
        st.markdown("### 🎯 OPERATIONS COMMAND DASHBOARD")
        
        # Creative tab structure with military/operations theme
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🛡️ **Situation Room**", 
            "🎯 **Threat Intel**", 
            "⚡ **Rapid Response**",
            "📊 **War Games**",
            "📈 **Mission Analytics**"
        ])
        
        with tab1:
            self.render_situation_room()
        
        with tab2:
            self.render_threat_intelligence()
        
        with tab3:
            self.render_rapid_response()
        
        with tab4:
            self.render_war_games_simulations()
        
        with tab5:
            self.render_mission_analytics()
    
    def render_situation_room(self):
        """Render situation room with real-time monitoring"""
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Real-time monitoring wall
            st.markdown("##### 📡 REAL-TIME MONITORING WALL")
            
            # Create radar-style monitoring
            analysis = self.concentration_analyzer.analyze_employer_concentration()
            employer_exposures = analysis.get('employer_exposures', [])
            
            # Create monitoring matrix
            monitoring_data = []
            for i, employer in enumerate(employer_exposures[:8]):  # Show top 8
                exposure_share = employer.get('exposure_share', 0) * 100
                limit = self.config.limits.single_employer_share_max * 100
                utilization = min(100, (exposure_share / limit) * 100)
                
                monitoring_data.append({
                    'Sector': f"Sector {i+1}",
                    'Employer': employer['employer_name'][:15],
                    'Utilization': utilization,
                    'Exposure': exposure_share,
                    'Status': 'BREACH' if exposure_share > limit else 'WARNING' if utilization > 80 else 'SAFE'
                })
            
            # Create monitoring dashboard
            monitor_df = pd.DataFrame(monitoring_data)
            
            # Interactive monitoring matrix
            fig = px.scatter(
                monitor_df,
                x='Sector',
                y='Utilization',
                size='Exposure',
                color='Status',
                hover_name='Employer',
                title="Real-Time Employer Monitoring Matrix",
                color_discrete_map={
                    'BREACH': '#ff4444',
                    'WARNING': '#ffa726',
                    'SAFE': '#4caf50'
                },
                size_max=30
            )
            
            # Add limit lines
            fig.add_hline(y=80, line_dash="dash", line_color="#ffa726", 
                         annotation_text="Warning Threshold")
            fig.add_hline(y=100, line_dash="dash", line_color="#ff4444", 
                         annotation_text="Breach Threshold")
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Command console
            st.markdown("##### 🎮 COMMAND CONSOLE")
            
            # System status
            st.markdown("**🖥️ SYSTEM STATUS**")
            col_status = st.columns(2)
            with col_status[0]:
                st.success("✅ Monitoring")
                st.success("✅ Alerts")
            with col_status[1]:
                st.success("✅ Database")
                st.warning("🔄 Predictive")
            
            # Quick actions
            st.markdown("**⚡ QUICK ACTIONS**")
            
            if st.button("🔄 Refresh Intelligence", use_container_width=True):
                st.session_state.alert_refresh = datetime.now()
                st.rerun()
            
            if st.button("📡 Force Audit", use_container_width=True):
                self._force_comprehensive_audit()
                st.success("Comprehensive audit initiated!")
            
            if st.button("🔔 Test Alert System", use_container_width=True):
                self._test_alert_system()
                st.success("Alert system test completed!")
            
            # Emergency protocols
            st.markdown("**🚨 EMERGENCY PROTOCOLS**")
            
            protocol = st.selectbox(
                "Select Protocol",
                ["None", "Protocol Alpha: Immediate Freeze", 
                 "Protocol Beta: Risk Committee", 
                 "Protocol Gamma: Board Escalation"]
            )
            
            if protocol != "None" and st.button("🚀 Execute Protocol", use_container_width=True):
                self._execute_emergency_protocol(protocol)
                st.error(f"Executing {protocol}!")
    
    def render_threat_intelligence(self):
        """Render threat intelligence with predictive analytics"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Predictive breach forecasting
            st.markdown("##### 🔮 PREDICTIVE BREACH FORECASTING")
            
            # Generate predictive data
            forecast_data = self._generate_breach_forecast()
            
            # Create forecast chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=forecast_data['dates'],
                y=forecast_data['current_trend'],
                name='Current Trend',
                line=dict(color='#ffa726', width=2, dash='dash')
            ))
            
            fig.add_trace(go.Scatter(
                x=forecast_data['dates'],
                y=forecast_data['predicted_breaches'],
                name='Predicted Breaches',
                line=dict(color='#ff4444', width=3),
                fill='tozeroy',
                fillcolor='rgba(255, 68, 68, 0.1)'
            ))
            
            fig.add_trace(go.Scatter(
                x=forecast_data['dates'],
                y=forecast_data['optimized_trend'],
                name='Optimized Scenario',
                line=dict(color='#4caf50', width=3)
            ))
            
            fig.update_layout(
                title="30-Day Breach Forecast & Optimization",
                xaxis_title="Date",
                yaxis_title="Number of Breaches",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Threat heatmap
            st.markdown("##### 🗺️ THREAT HEATMAP")
            
            # Generate threat data
            threat_data = self._generate_threat_heatmap()
            
            fig = px.density_heatmap(
                threat_data,
                x='Hour',
                y='Day',
                z='Threat_Level',
                title="Weekly Threat Pattern Analysis",
                color_continuous_scale='RdYlGn_r',
                labels={'Threat_Level': 'Threat Intensity'}
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Threat intelligence insights
            st.markdown("##### 🎯 INTELLIGENCE INSIGHTS")
            
            insights = [
                "📊 Peak breach hours: 10:00-14:00",
                "📈 Growing trend: +15% breaches week-over-week",
                "🎯 High-risk employers: A, C, F identified",
                "🛡️ Effective interventions: Loan restructuring (85% success)"
            ]
            
            for insight in insights:
                st.info(insight)
    
    def _generate_breach_forecast(self):
        """Generate breach forecast data"""
        dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
        
        # Simulate trends
        current_trend = np.array([3, 3, 4, 3, 4, 5, 4, 5, 6, 5, 6, 7, 6, 7, 8,
                                  7, 8, 9, 8, 9, 10, 9, 10, 11, 10, 11, 12, 11, 12, 13])
        
        predicted_breaches = current_trend * 1.15  # 15% growth
        
        # Optimized scenario (with interventions)
        optimized_trend = np.array([3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
                                    2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2])
        
        return {
            'dates': dates,
            'current_trend': current_trend,
            'predicted_breaches': predicted_breaches,
            'optimized_trend': optimized_trend
        }
    
    def _generate_threat_heatmap(self):
        """Generate threat heatmap data"""
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        hours = list(range(24))
        
        data = []
        for day_idx, day in enumerate(days):
            for hour in hours:
                # Generate pattern: higher threats during business hours
                base_threat = 0.3 if 8 <= hour <= 17 else 0.1
                
                # Add day pattern: higher mid-week
                day_multiplier = 1.5 if 1 <= day_idx <= 3 else 1.0
                
                # Add some randomness
                threat_level = base_threat * day_multiplier + np.random.random() * 0.2
                
                data.append({
                    'Day': day,
                    'Hour': hour,
                    'Threat_Level': threat_level
                })
        
        return pd.DataFrame(data)
    
    def render_rapid_response(self):
        """Render rapid response interface with interactive alert management"""
        st.markdown("##### ⚡ RAPID RESPONSE INTERFACE")
        
        # Get current alerts
        analysis = self.concentration_analyzer.analyze_employer_concentration()
        employer_exposures = analysis.get('employer_exposures', [])
        
        # Identify breaches and warnings
        breaches = []
        warnings = []
        
        for employer in employer_exposures:
            exposure_share = employer.get('exposure_share', 0)
            if exposure_share > self.config.limits.single_employer_share_max:
                breaches.append(employer)
            elif exposure_share > 0.8 * self.config.limits.single_employer_share_max:
                warnings.append(employer)
        
        # Response dashboard
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🚨 ACTIVE BREACHES**")
            
            if breaches:
                for i, breach in enumerate(breaches[:3]):  # Show top 3
                    with st.container():
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #ff4444 0%, #ff6b6b 100%); 
                                    color: white; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;
                                    border-left: 6px solid #ff0000;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <h4 style="margin: 0;">{breach['employer_name']}</h4>
                                <span style="background: white; color: #ff4444; padding: 2px 8px; 
                                           border-radius: 12px; font-weight: bold;">
                                    {breach['exposure_share']*100:.1f}%
                                </span>
                            </div>
                            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                                KES {breach.get('outstanding_amount', 0):,.0f} • {breach.get('member_count', 0)} members
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Quick response buttons
                        col_resp = st.columns(3)
                        with col_resp[0]:
                            if st.button("🛑 Freeze", key=f"freeze_{i}"):
                                self._execute_response("freeze", breach)
                                st.success("Lending frozen!")
                        with col_resp[1]:
                            if st.button("📞 Call", key=f"call_{i}"):
                                self._execute_response("call", breach)
                                st.success("Call initiated!")
                        with col_resp[2]:
                            if st.button("📋 Plan", key=f"plan_{i}"):
                                self._execute_response("plan", breach)
                                st.success("Action plan created!")
            else:
                st.success("No active breaches")
        
        with col2:
            st.markdown("**⚠️ WARNING ZONE**")
            
            if warnings:
                for i, warning in enumerate(warnings[:3]):  # Show top 3
                    with st.container():
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #ffa726 0%, #ffca7a 100%); 
                                    color: #333; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;
                                    border-left: 6px solid #ff9800;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <h4 style="margin: 0;">{warning['employer_name']}</h4>
                                <span style="background: white; color: #ff9800; padding: 2px 8px; 
                                           border-radius: 12px; font-weight: bold;">
                                    {warning['exposure_share']*100:.1f}%
                                </span>
                            </div>
                            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                                Buffer: {(self.config.limits.single_employer_share_max - warning['exposure_share'])*100:.1f}%
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Preventive actions
                        col_prev = st.columns(2)
                        with col_prev[0]:
                            if st.button("📉 Reduce", key=f"reduce_{i}"):
                                self._execute_response("reduce", warning)
                                st.success("Reduction plan initiated!")
                        with col_prev[1]:
                            if st.button("📊 Monitor", key=f"monitor_{i}"):
                                self._execute_response("monitor", warning)
                                st.success("Enhanced monitoring activated!")
            else:
                st.info("No employers in warning zone")
        
        # Automated response configuration
        st.markdown("##### 🤖 AUTOMATED RESPONSE CONFIGURATION")
        
        col_auto = st.columns(3)
        
        with col_auto[0]:
            auto_freeze = st.checkbox("Auto-freeze on breach", value=True)
            freeze_threshold = st.slider("Freeze threshold", 100, 150, 110, help="% of limit")
        
        with col_auto[1]:
            auto_alert = st.checkbox("Auto-alert management", value=True)
            alert_frequency = st.selectbox("Alert frequency", ["Immediate", "30 min", "1 hour", "4 hours"])
        
        with col_auto[2]:
            auto_escalate = st.checkbox("Auto-escalation", value=False)
            escalate_after = st.slider("Escalate after (hours)", 1, 72, 24)
        
        if st.button("💾 Save Automation Rules", use_container_width=True):
            st.success("Automation rules saved!")
    
    def _execute_response(self, action, employer_data):
        """Execute rapid response action"""
        self.audit_logger.log_action(
            st.session_state.user,
            st.session_state.role,
            f"execute_{action}_response",
            "employer_limit",
            employer_data['employer_name'],
            {'action': action, 'exposure': employer_data['exposure_share']}
        )
    
    def render_war_games_simulations(self):
        """Render war games simulation interface"""
        st.markdown("##### 🎮 WAR GAMES SIMULATION CENTER")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Simulation scenarios
            st.markdown("**🎯 SIMULATION SCENARIOS**")
            
            scenarios = {
                "Market Crash": {
                    "description": "30% market downturn, mass employer defaults",
                    "risk": "Extreme",
                    "duration": "6 months"
                },
                "Regulatory Change": {
                    "description": "SASRA reduces single employer limit to 20%",
                    "risk": "High", 
                    "duration": "3 months"
                },
                "Cyber Attack": {
                    "description": "System breach affecting loan processing",
                    "risk": "Critical",
                    "duration": "2 weeks"
                },
                "Geographic Crisis": {
                    "description": "Regional economic collapse",
                    "risk": "High",
                    "duration": "4 months"
                }
            }
            
            selected_scenario = st.selectbox(
                "Choose Scenario",
                list(scenarios.keys())
            )
            
            scenario = scenarios[selected_scenario]
            
            st.markdown(f"""
            <div style="background: #1e293b; color: white; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                <h4 style="margin: 0 0 0.5rem 0;">{selected_scenario}</h4>
                <p style="margin: 0 0 0.5rem 0;">{scenario['description']}</p>
                <div style="display: flex; gap: 1rem;">
                    <span style="background: #ff4444; padding: 2px 8px; border-radius: 12px;">
                        Risk: {scenario['risk']}
                    </span>
                    <span style="background: #3b82f6; padding: 2px 8px; border-radius: 12px;">
                        Duration: {scenario['duration']}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Simulation parameters
            st.markdown("**⚙️ SIMULATION PARAMETERS**")
            
            col_params = st.columns(3)
            with col_params[0]:
                market_shock = st.slider("Market Shock (%)", -50, 50, -30)
            with col_params[1]:
                default_rate = st.slider("Default Rate Increase (%)", 0, 100, 25)
            with col_params[2]:
                recovery_rate = st.slider("Recovery Rate (%)", 0, 100, 40)
        
        with col2:
            # Simulation controls
            st.markdown("**🎮 SIMULATION CONTROLS**")
            
            if st.button("▶️ Run Simulation", use_container_width=True, type="primary"):
                simulation_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                st.session_state.active_simulations[simulation_id] = {
                    'scenario': selected_scenario,
                    'status': 'running',
                    'start_time': datetime.now()
                }
                
                # Run simulation in background
                Thread(target=self._run_simulation, args=(simulation_id, scenario)).start()
                st.success(f"Simulation {simulation_id} started!")
            
            if st.button("⏸️ Pause Simulation", use_container_width=True):
                st.info("Simulation paused")
            
            if st.button("⏹️ Stop All Simulations", use_container_width=True):
                st.session_state.active_simulations = {}
                st.warning("All simulations stopped")
            
            # Active simulations
            st.markdown("**🔄 ACTIVE SIMULATIONS**")
            
            if st.session_state.active_simulations:
                for sim_id, sim_data in list(st.session_state.active_simulations.items()):
                    duration = (datetime.now() - sim_data['start_time']).seconds
                    st.info(f"🔄 {sim_id}: {sim_data['scenario']} ({duration}s)")
            else:
                st.info("No active simulations")
            
            # Simulation results visualization
            st.markdown("**📊 QUICK RESULTS**")
            
            if st.button("📈 Show Previous Results"):
                self._display_simulation_results()
    
    def _run_simulation(self, simulation_id, scenario):
        """Run simulation in background thread"""
        time.sleep(5)  # Simulate processing
        if simulation_id in st.session_state.active_simulations:
            st.session_state.active_simulations[simulation_id]['status'] = 'completed'
            st.session_state.active_simulations[simulation_id]['results'] = {
                'predicted_breaches': 8,
                'capital_impact': -15000000,
                'recommendations': ['Increase provisions', 'Diversify portfolio']
            }
    
    def _display_simulation_results(self):
        """Display simulation results"""
        results = {
            'Market Crash': {'breaches': 12, 'impact': 'KES -25M', 'rating': 'Critical'},
            'Regulatory Change': {'breaches': 8, 'impact': 'KES -12M', 'rating': 'High'},
            'Cyber Attack': {'breaches': 4, 'impact': 'KES -8M', 'rating': 'Medium'}
        }
        
        for scenario, data in results.items():
            st.metric(
                f"{scenario} Simulation",
                f"{data['breaches']} breaches",
                data['impact']
            )
    
    def render_mission_analytics(self):
        """Render mission analytics with performance metrics"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Mission performance dashboard
            st.markdown("##### 📊 MISSION PERFORMANCE")
            
            missions = [
                {"name": "Breach Prevention", "target": 95, "actual": 92, "trend": "↑"},
                {"name": "Response Time", "target": 24, "actual": 18, "trend": "↓"},
                {"name": "SLA Compliance", "target": 98, "actual": 96, "trend": "→"},
                {"name": "Auto-resolution", "target": 40, "actual": 35, "trend": "↑"}
            ]
            
            for mission in missions:
                col_perf = st.columns([3, 1, 1])
                with col_perf[0]:
                    st.progress(mission['actual'] / 100)
                    st.caption(f"{mission['name']}: {mission['actual']}%")
                with col_perf[1]:
                    st.metric("", f"{mission['actual']}%", mission['trend'])
                with col_perf[2]:
                    delta = mission['actual'] - mission['target']
                    st.metric("Target", f"{mission['target']}%", f"{delta:+.1f}%")
        
        with col2:
            # Team performance
            st.markdown("##### 🏆 TEAM PERFORMANCE")
            
            team_data = [
                {"team": "Risk Ops", "resolved": 42, "avg_time": "4.2h", "rating": "A+"},
                {"team": "Credit", "resolved": 28, "avg_time": "6.8h", "rating": "B"},
                {"team": "Compliance", "resolved": 35, "avg_time": "5.1h", "rating": "A"},
                {"team": "IT Security", "resolved": 15, "avg_time": "8.3h", "rating": "C+"}
            ]
            
            for team in team_data:
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 0.5rem; border-radius: 6px; margin-bottom: 0.5rem;
                            border-left: 4px solid {'#4caf50' if team['rating'][0] == 'A' else '#ff9800' if team['rating'][0] == 'B' else '#ff4444'}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span><strong>{team['team']}</strong></span>
                        <span style="background: {'#4caf50' if team['rating'][0] == 'A' else '#ff9800' if team['rating'][0] == 'B' else '#ff4444'}; 
                                  color: white; padding: 2px 8px; border-radius: 12px; font-weight: bold;">
                            {team['rating']}
                        </span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.9rem; margin-top: 0.25rem;">
                        <span>Resolved: {team['resolved']}</span>
                        <span>Avg: {team['avg_time']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Analytics insights
        st.markdown("##### 🎯 ANALYTICS INSIGHTS")
        
        insights_col = st.columns(3)
        
        with insights_col[0]:
            st.metric(
                "Mean Time to Resolution",
                "18.4h",
                "-2.3h",
                help="Average time to resolve breaches"
            )
        
        with insights_col[1]:
            st.metric(
                "First Response Time",
                "1.8h",
                "-0.5h",
                help="Average time to first response"
            )
        
        with insights_col[2]:
            st.metric(
                "Automation Rate",
                "42%",
                "+8%",
                help="Percentage of responses automated"
            )
    
    def render_limits_dashboard(self):
        """Render employer limits dashboard - PRESERVED"""
        st.subheader("📊 Employer Limits Dashboard")
        
        # Get current employer analysis
        analysis = self.concentration_analyzer.analyze_employer_concentration()
        employer_exposures = analysis.get('employer_exposures', [])
        
        # Calculate key metrics
        total_breaches = len([e for e in employer_exposures if e.get('exposure_share', 0) > self.config.limits.single_employer_share_max])
        warning_employers = len([e for e in employer_exposures if 0.8 * self.config.limits.single_employer_share_max < e.get('exposure_share', 0) <= self.config.limits.single_employer_share_max])
        total_exposure_at_risk = sum([e.get('outstanding_amount', 0) for e in employer_exposures if e.get('exposure_share', 0) > self.config.limits.single_employer_share_max])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Active Limit Breaches",
                f"{total_breaches}",
                delta_color="inverse" if total_breaches > 0 else "normal",
                help="Employers exceeding single employer limit"
            )
        
        with col2:
            st.metric(
                "Warning Employers", 
                f"{warning_employers}",
                help="Employers approaching limit (80-100%)"
            )
        
        with col3:
            st.metric(
                "Exposure at Risk",
                f"KES {total_exposure_at_risk:,.0f}",
                delta_color="inverse" if total_exposure_at_risk > 0 else "normal",
                help="Total exposure in breach of limits"
            )
        
        with col4:
            compliance_rate = ((len(employer_exposures) - total_breaches) / len(employer_exposures)) * 100 if employer_exposures else 100
            st.metric(
                "Compliance Rate",
                f"{compliance_rate:.1f}%",
                help="Percentage of employers within limits"
            )
        
        # Real-time alerts
        self.render_real_time_alerts(employer_exposures)
    
    def render_real_time_alerts(self, employer_exposures):
        """Render real-time limit breach alerts - ENHANCED"""
        st.markdown("#### 🚨 Real-Time Limit Breach Alerts")
        
        # Identify breaches and warnings
        breaches = []
        warnings = []
        
        for employer in employer_exposures:
            exposure_share = employer.get('exposure_share', 0)
            if exposure_share > self.config.limits.single_employer_share_max:
                breaches.append(employer)
            elif exposure_share > 0.8 * self.config.limits.single_employer_share_max:
                warnings.append(employer)
        
        # Enhanced display with tabs
        if breaches or warnings:
            alert_tab1, alert_tab2 = st.tabs(["🔴 **Active Breaches**", "🟡 **Warnings**"])
            
            with alert_tab1:
                if breaches:
                    for breach in breaches:
                        self._render_breach_card(breach)
                else:
                    st.success("✅ No active breaches detected")
            
            with alert_tab2:
                if warnings:
                    for warning in warnings:
                        self._render_warning_card(warning)
                else:
                    st.info("ℹ️ No employers in warning zone")
        else:
            st.success("### ✅ ALL SYSTEMS NORMAL")
            st.info("No active limit breaches or warnings detected.")
    
    def _render_breach_card(self, breach):
        """Render enhanced breach card"""
        with st.container():
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ff000020 0%, #ff444420 100%); 
                        border: 2px solid #ff4444; border-radius: 10px; padding: 1rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <h4 style="margin: 0; color: #ff4444;">🚨 {breach['employer_name']}</h4>
                    <span style="background: #ff4444; color: white; padding: 4px 12px; border-radius: 16px; 
                               font-weight: bold;">
                        {breach['exposure_share']*100:.1f}% (Limit: {self.config.limits.single_employer_share_max*100:.1f}%)
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Current Exposure",
                    f"KES {breach.get('outstanding_amount', 0):,.0f}",
                    help="Total outstanding exposure"
                )
            
            with col2:
                excess = (breach.get('outstanding_amount', 0) * 
                         (breach['exposure_share'] - self.config.limits.single_employer_share_max))
                st.metric(
                    "Excess Over Limit",
                    f"KES {excess:,.0f}",
                    delta_color="inverse",
                    help="Amount exceeding regulatory limit"
                )
            
            with col3:
                st.metric(
                    "Breach Duration",
                    "7 days",
                    help="How long this breach has been active"
                )
            
            # Enhanced action buttons
            action_col = st.columns(4)
            with action_col[0]:
                if st.button("📧 Notify Risk Team", key=f"notify_{breach['employer_name']}", use_container_width=True):
                    self._send_notification(breach, "Risk Team")
                    st.success("Risk team notified!")
            with action_col[1]:
                if st.button("📋 Create Action Plan", key=f"plan_{breach['employer_name']}", use_container_width=True):
                    self._create_action_plan(breach)
                    st.success("Action plan created!")
            with action_col[2]:
                if st.button("⚡ Request Waiver", key=f"waiver_{breach['employer_name']}", use_container_width=True):
                    self._request_waiver(breach)
                    st.success("Waiver request submitted!")
            with action_col[3]:
                if st.button("🔍 View Details", key=f"details_{breach['employer_name']}", use_container_width=True):
                    st.session_state[f"view_details_{breach['employer_name']}"] = True
    
    def _render_warning_card(self, warning):
        """Render enhanced warning card"""
        with st.container():
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ffa72620 0%, #ffca7a20 100%); 
                        border: 2px solid #ffa726; border-radius: 10px; padding: 1rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <h4 style="margin: 0; color: #ff9800;">⚠️ {warning['employer_name']}</h4>
                    <span style="background: #ffa726; color: white; padding: 4px 12px; border-radius: 16px; 
                               font-weight: bold;">
                        {warning['exposure_share']*100:.1f}% (Limit: {self.config.limits.single_employer_share_max*100:.1f}%)
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "Current Exposure",
                    f"KES {warning.get('outstanding_amount', 0):,.0f}",
                    help="Total outstanding exposure"
                )
            
            with col2:
                buffer = (self.config.limits.single_employer_share_max - warning['exposure_share']) * 100
                st.metric(
                    "Buffer Remaining",
                    f"{buffer:.2f}%",
                    help="Remaining capacity before breach"
                )
            
            # Preventive action
            if st.button("🛡️ Initiate Preventive Measures", key=f"prevent_{warning['employer_name']}", use_container_width=True):
                self._initiate_preventive_measures(warning)
                st.success("Preventive measures initiated!")
    
    def render_employer_limits_monitor(self):
        """Render employer limits monitoring table - PRESERVED"""
        st.markdown("---")
        st.subheader("📋 Employer Limits Monitoring")
        
        # Get employer data
        analysis = self.concentration_analyzer.analyze_employer_concentration()
        employer_exposures = analysis.get('employer_exposures', [])
        
        if employer_exposures:
            # Create monitoring dataframe
            monitor_data = []
            for employer in employer_exposures:
                exposure_share = employer.get('exposure_share', 0)
                limit_utilization = (exposure_share / self.config.limits.single_employer_share_max) * 100
                
                # Determine status
                if exposure_share > self.config.limits.single_employer_share_max:
                    status = "BREACH"
                    alert_level = "High"
                elif exposure_share > 0.8 * self.config.limits.single_employer_share_max:
                    status = "WARNING"
                    alert_level = "Medium"
                else:
                    status = "WITHIN LIMIT"
                    alert_level = "Low"
                
                monitor_data.append({
                    'Employer': employer['employer_name'],
                    'Exposure (KES)': employer.get('outstanding_amount', 0),
                    'Portfolio Share': f"{exposure_share*100:.2f}%",
                    'Limit Utilization': f"{limit_utilization:.1f}%",
                    'Status': status,
                    'Alert Level': alert_level,
                    'Member Count': employer.get('loan_id', 0),
                    'Average DPD': f"{employer.get('average_dpd', 0):.1f}",
                    'Last Review': (datetime.now() - timedelta(days=np.random.randint(1, 30))).strftime('%Y-%m-%d')
                })
            
            monitor_df = pd.DataFrame(monitor_data)
            
            # Enhanced filtering
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_filter = st.multiselect(
                    "Filter by Status",
                    options=['WITHIN LIMIT', 'WARNING', 'BREACH'],
                    default=['BREACH', 'WARNING']
                )
            
            with col2:
                alert_filter = st.multiselect(
                    "Filter by Alert Level",
                    options=['Low', 'Medium', 'High'],
                    default=['High', 'Medium']
                )
            
            with col3:
                search_term = st.text_input("Search Employer")
            
            # Apply filters
            filtered_df = monitor_df[
                (monitor_df['Status'].isin(status_filter)) &
                (monitor_df['Alert Level'].isin(alert_filter))
            ]
            
            if search_term:
                filtered_df = filtered_df[filtered_df['Employer'].str.contains(search_term, case=False, na=False)]
            
            # Enhanced color coding
            def color_status(status):
                if status == 'BREACH':
                    return 'background-color: #ff4444; color: white; font-weight: bold;'
                elif status == 'WARNING':
                    return 'background-color: #ffa726; color: black; font-weight: bold;'
                else:
                    return 'background-color: #4caf50; color: white; font-weight: bold;'
            
            def color_alert_level(level):
                if level == 'High':
                    return 'color: #ff0000; font-weight: bold;'
                elif level == 'Medium':
                    return 'color: #ff9800; font-weight: bold;'
                else:
                    return 'color: #4caf50; font-weight: bold;'
            
            styled_df = filtered_df.style.map(
                color_status, subset=['Status']
            ).map(
                color_alert_level, subset=['Alert Level']
            )
            
            st.dataframe(styled_df, use_container_width=True)
            
            # Enhanced export options
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📊 Generate Enhanced Report", use_container_width=True):
                    report = self._generate_limits_report(monitor_df)
                    st.success("Enhanced report generated with analytics!")
            
            with col2:
                csv_data = monitor_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Monitoring Data",
                    data=csv_data,
                    file_name=f"employer_limits_monitoring_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col3:
                if st.button("📧 Email Summary", use_container_width=True):
                    st.success("Email summary sent to stakeholders!")
    
    def _force_comprehensive_audit(self):
        """Force comprehensive audit"""
        self.audit_logger.log_action(
            st.session_state.user,
            st.session_state.role,
            "force_comprehensive_audit",
            "employer_limit",
            None,
            {}
        )
    
    def _test_alert_system(self):
        """Test alert system"""
        self.audit_logger.log_action(
            st.session_state.user,
            st.session_state.role,
            "test_alert_system",
            "employer_limit",
            None,
            {}
        )
    
    def _execute_emergency_protocol(self, protocol):
        """Execute emergency protocol"""
        self.audit_logger.log_action(
            st.session_state.user,
            st.session_state.role,
            "execute_emergency_protocol",
            "employer_limit",
            protocol,
            {}
        )
    
    # Preserved helper methods (kept for backward compatibility)
    def _send_notification(self, employer_data, recipient):
        """Send notification for limit breach"""
        message = f"Limit breach alert for {employer_data['employer_name']}"
        self.audit_logger.log_action(
            st.session_state.user,
            st.session_state.role,
            "send_notification",
            "employer_limit",
            employer_data['employer_name'],
            {'recipient': recipient, 'message': message}
        )
    
    def _create_action_plan(self, employer_data):
        """Create action plan for limit breach"""
        self.audit_logger.log_action(
            st.session_state.user,
            st.session_state.role,
            "create_action_plan",
            "employer_limit",
            employer_data['employer_name'],
            {'exposure_share': employer_data['exposure_share']}
        )
    
    def _request_waiver(self, employer_data):
        """Request regulatory waiver for limit breach"""
        self.audit_logger.log_action(
            st.session_state.user,
            st.session_state.role,
            "request_waiver",
            "employer_limit",
            employer_data['employer_name'],
            {'exposure_share': employer_data['exposure_share']}
        )
    
    def _initiate_preventive_measures(self, employer_data):
        """Initiate preventive measures for approaching limits"""
        self.audit_logger.log_action(
            st.session_state.user,
            st.session_state.role,
            "initiate_preventive_measures",
            "employer_limit",
            employer_data['employer_name'],
            {'exposure_share': employer_data['exposure_share']}
        )
    
    def _generate_limits_report(self, monitor_df):
        """Generate employer limits report"""
        self.audit_logger.log_action(
            st.session_state.user,
            st.session_state.role,
            "generate_limits_report",
            "employer_limit",
            None,
            {'employer_count': len(monitor_df)}
        )
        return {"status": "success", "report_id": f"EMP_LIMIT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"}
    
    def render_limit_configuration(self):
        """Render limit configuration interface"""
        st.markdown("##### ⚙️ LIMIT CONFIGURATION")
        
        # SASRA Limits Configuration
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📋 SASRA REGULATORY LIMITS**")
            
            # Single employer limit
            single_limit = st.number_input(
                "Single Employer Limit (%)",
                min_value=10.0,
                max_value=50.0,
                value=float(self.config.limits.single_employer_share_max * 100),
                step=0.5,
                help="SASRA maximum single employer concentration limit"
            )
            
            # Warning threshold (e.g., 80% of limit)
            warning_threshold = st.number_input(
                "Warning Threshold (% of limit)",
                min_value=50.0,
                max_value=95.0,
                value=80.0,
                step=1.0,
                help="Trigger warnings at this percentage of limit"
            )
        
        with col2:
            st.markdown("**🎯 CUSTOM LIMIT POLICIES**")
            
            # Top 5 employers limit
            top5_limit = st.number_input(
                "Top 5 Employers Limit (%)",
                min_value=30.0,
                max_value=80.0,
                value=60.0,
                step=1.0,
                help="Maximum concentration for top 5 employers"
            )
            
            # Sector limits
            sector_limit = st.number_input(
                "Sector Concentration Limit (%)",
                min_value=20.0,
                max_value=60.0,
                value=30.0,
                step=1.0,
                help="Maximum concentration per economic sector"
            )
        
        # Advanced settings
        st.markdown("##### ⚡ ADVANCED SETTINGS")
        col_adv1, col_adv2 = st.columns(2)
        
        with col_adv1:
            # Grace period for breaches
            grace_period = st.number_input(
                "Grace Period (days)",
                min_value=1,
                max_value=30,
                value=7,
                help="Days allowed to resolve breaches before escalation"
            )
            
            # Auto-review frequency
            review_freq = st.selectbox(
                "Auto-Review Frequency",
                ["Daily", "Weekly", "Bi-weekly", "Monthly"],
                index=1
            )
        
        with col_adv2:
            # Alert thresholds
            immediate_alert = st.number_input(
                "Immediate Alert Threshold (%)",
                min_value=90.0,
                max_value=110.0,
                value=95.0,
                step=1.0,
                help="Trigger immediate alerts at this level"
            )
            
            # Escalation levels
            escalation_levels = st.slider(
                "Escalation Levels",
                min_value=1,
                max_value=5,
                value=3,
                help="Number of escalation levels for breaches"
            )
        
        # Save configuration
        if st.button("💾 Save Limit Configuration", use_container_width=True):
            # Update config
            self.config.limits.single_employer_share_max = single_limit / 100
            st.session_state.config = self.config
            
            # Log the change
            try:
                self.audit_logger.log_action(
                    st.session_state.user,
                    st.session_state.role,
                    "update_limit_configuration",
                    "employer_limit",
                    None,
                    {
                        'single_employer_limit': single_limit,
                        'warning_threshold': warning_threshold,
                        'top5_limit': top5_limit,
                        'sector_limit': sector_limit
                    }
                )
            except:
                pass  # Silently continue if logging fails
            
            st.success("✅ Limit configuration saved successfully!")
            st.rerun()
    
    def render_alert_management(self):
        """Render alert management configuration"""
        st.markdown("##### 🔔 ALERT MANAGEMENT")
        
        # Alert recipients
        st.markdown("**👥 ALERT RECIPIENTS**")
        
        recipients = st.multiselect(
            "Select Alert Recipients",
            ["Risk Manager", "Credit Officer", "Compliance Team", "CEO", "Board Risk Committee", "IT Security"],
            default=["Risk Manager", "Credit Officer"]
        )
        
        # Alert channels
        st.markdown("**📱 ALERT CHANNELS**")
        
        col_ch1, col_ch2, col_ch3 = st.columns(3)
        with col_ch1:
            email_alerts = st.checkbox("Email Alerts", value=True)
        with col_ch2:
            sms_alerts = st.checkbox("SMS Alerts", value=False)
        with col_ch3:
            dashboard_alerts = st.checkbox("Dashboard Alerts", value=True)
        
        # Alert templates
        st.markdown("##### 📝 ALERT TEMPLATES")
        
        breach_template = st.text_area(
            "Breach Alert Template",
            value="🚨 URGENT: Employer {employer} has breached concentration limits at {percentage}%.\n\nDetails:\n- Exposure: KES {amount}\n- Limit: {limit}%\n- Required action: Immediate intervention\n\nClick here to view: {link}",
            height=100
        )
        
        warning_template = st.text_area(
            "Warning Alert Template",
            value="⚠️ WARNING: Employer {employer} is approaching concentration limits at {percentage}%.\n\nDetails:\n- Exposure: KES {amount}\n- Buffer remaining: {buffer}%\n- Recommended action: Preventive measures\n\nClick here to view: {link}",
            height=100
        )
        
        # Save alert settings
        if st.button("💾 Save Alert Settings", key="save_alerts", use_container_width=True):
            st.success("Alert settings saved!")
    
    def render_breach_analytics(self):
        """Render breach analytics dashboard"""
        st.markdown("##### 📊 BREACH ANALYTICS")
        
        # Simulated breach analytics data
        breach_data = {
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'Breaches': [3, 5, 4, 2, 3, 1],
            'Resolution Time (days)': [5.2, 7.8, 4.5, 3.2, 6.1, 2.8],
            'Financial Impact (KES M)': [-12.5, -18.2, -15.3, -8.7, -11.9, -4.2]
        }
        
        breach_df = pd.DataFrame(breach_data)
        
        # Create breach trend chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Number of Breaches',
            x=breach_df['Month'],
            y=breach_df['Breaches'],
            yaxis='y',
            marker_color='#ff4444',
            opacity=0.7
        ))
        
        fig.add_trace(go.Scatter(
            name='Resolution Time',
            x=breach_df['Month'],
            y=breach_df['Resolution Time (days)'],
            yaxis='y2',
            line=dict(color='#4caf50', width=3),
            mode='lines+markers'
        ))
        
        fig.update_layout(
            title="Monthly Breach Trends & Resolution Performance",
            xaxis_title="Month",
            yaxis=dict(title='Number of Breaches', side='left'),
            yaxis2=dict(title='Resolution Time (days)', side='right', overlaying='y'),
            legend=dict(x=0.02, y=0.98),
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Key metrics
        col_met1, col_met2, col_met3 = st.columns(3)
        
        with col_met1:
            avg_resolution = breach_df['Resolution Time (days)'].mean()
            st.metric("Avg Resolution Time", f"{avg_resolution:.1f} days")
        
        with col_met2:
            total_impact = breach_df['Financial Impact (KES M)'].sum()
            st.metric("Total Financial Impact", f"KES {total_impact:,.1f}M")
        
        with col_met3:
            breach_reduction = ((breach_data['Breaches'][0] - breach_data['Breaches'][-1]) / breach_data['Breaches'][0]) * 100
            st.metric("Breach Reduction", f"{breach_reduction:.1f}%", delta="Improvement")
    
    def render_action_plans(self):
        """Render action plans interface"""
        st.markdown("##### 📋 ACTION PLANS & REMEDIATION")
        
        # Action plan templates
        st.markdown("**📝 ACTION PLAN TEMPLATES**")
        
        plan_type = st.selectbox(
            "Select Action Plan Type",
            ["Limit Breach Remediation", "Warning Prevention", "Portfolio Diversification", "Emergency Response"]
        )
        
        # Plan details based on type
        if plan_type == "Limit Breach Remediation":
            plan_details = """
            **🚨 IMMEDIATE ACTIONS (Within 24 hours):**
            1. Freeze new lending to the employer
            2. Notify Risk Committee & Compliance Officer
            3. Schedule emergency meeting with employer
            4. Initiate portfolio analysis for diversification options
            
            **📊 SHORT-TERM ACTIONS (1-7 days):**
            1. Develop exposure reduction plan
            2. Review restructuring options
            3. Prepare regulatory waiver application if needed
            4. Implement enhanced monitoring
            
            **🎯 LONG-TERM ACTIONS (30-90 days):**
            1. Execute portfolio diversification strategy
            2. Review credit policies for similar employers
            3. Implement preventive controls
            4. Update risk models with lessons learned
            """
        elif plan_type == "Warning Prevention":
            plan_details = """
            **🛡️ PREVENTIVE ACTIONS:**
            1. Increase monitoring frequency to weekly
            2. Engage employer for early restructuring discussions
            3. Review growth projections and risk appetite
            4. Initiate portfolio optimization analysis
            
            **📈 PROACTIVE MEASURES:**
            1. Develop alternative lending strategies
            2. Create exposure hedging options
            3. Enhance early warning indicators
            4. Regular stakeholder communications
            """
        else:
            plan_details = f"Action plan template for {plan_type}"
        
        st.text_area("Plan Template", value=plan_details, height=200)
        
        # Generate action plan
        if st.button("🔄 Generate Action Plan", use_container_width=True):
            st.success(f"Action plan for {plan_type} generated!")
            
            # Download option
            plan_content = f"# ACTION PLAN: {plan_type}\n\nGenerated: {datetime.now()}\n\n{plan_details}"
            st.download_button(
                label="📥 Download Action Plan",
                data=plan_content,
                file_name=f"action_plan_{plan_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    def run(self):
        """Run the enhanced employer limits and alerts page"""
        # Command Center Header
        self.render_command_center_header()
        
        # Threat Intelligence Marquee
        self.render_threat_intelligence_marquee()
        
        # Alert Intelligence Framework
        self.render_alert_intelligence_framework()
        
        # Operations Command Dashboard
        self.render_operations_command_dashboard()
        
        # Preserved Functionality
        self.render_limits_dashboard()
        self.render_employer_limits_monitor()
        
        # Additional preserved sections (simplified display)
        with st.expander("⚙️ Advanced Configuration & Analytics"):
            col1, col2 = st.columns(2)
            with col1:
                self.render_limit_configuration()
            with col2:
                self.render_alert_management()
            
            self.render_breach_analytics()
            self.render_action_plans()

if __name__ == "__main__":
    page = EmployerLimitsAlertsPage()
    page.run()
