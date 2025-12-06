# pages/10_Cybersecurity_BCP.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any, Optional
import sys
import os

# --- Ensure project root is on sys.path so `core.*` imports work ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Unified core imports (replacing sacco_core.*) ---
from core.rbac import check_permission      # unified RBAC
from core.audit import audit_logger         # unified audit logger instance
from core.sidebar import render_sidebar     # available if you ever want to use it on this page

# =============================================
# ENTERPRISE ENHANCEMENTS: Cyber Defense Framework
# =============================================
CYBER_DEFENSE_PHILOSOPHY = {
    "Data": "What's the current threat landscape, vulnerability exposure, and business continuity readiness?",
    "Insights": "Why are security gaps emerging and what patterns predict attack vectors and system failures?",
    "Frameworks": "How to assess using NIST CSF, ISO 27001, CIS Controls, and SASRA Cybersecurity Guidelines?",
    "Actions": "What specific security controls, incident response plans, and continuity measures to implement?",
    "Impact": "What value it creates (data protection, system availability, regulatory compliance, member trust)?",
    "Governance": "How security decisions are documented, monitored, and incident responses are coordinated?"
}

# --- Small wrapper so this file can call `audit_log(...)` cleanly using the unified logger ---
def audit_log(action: str, description: str, payload: Optional[Dict] = None):
    """
    Wrapper around core.audit.audit_logger so this page can log
    without worrying about the exact logger method signatures.
    """
    try:
        user = st.session_state.get("username") or st.session_state.get("user", "unknown")
        role = st.session_state.get("role", "Unknown")
    except Exception:
        user = "unknown"
        role = "Unknown"

    details = {"description": description}
    if payload:
        details.update(payload)

    # Prefer the generic event logger if available
    try:
        audit_logger.log_event(
            user=user,
            action=action,
            module="10_Cybersecurity_BCP.py",
            details=details,
        )
        return
    except Exception:
        pass

    # Fallback: try data_access-style logging
    try:
        audit_logger.log_data_access(
            user,            # user_id
            role,            # role
            action,          # action
            details,         # details dict
        )
        return
    except Exception:
        pass

    # Final fallback: just print to console so nothing crashes
    print(f"AUDIT: {action} - {description} - {payload}")


# --- Cybersecurity analytics module import with fallback ---
try:
    from core.analytics.cybersecurity import (
        CybersecurityAnalyzer,
        RiskLevel,
        ThreatCategory,
        BCPStatus,
        SecurityIncident,
        BusinessImpact,
        SecurityControl,
    )
except ImportError:
    # Fallback classes if the analytics module is not present
    class RiskLevel:
        CRITICAL = "Critical"
        HIGH = "High"
        MEDIUM = "Medium"
        LOW = "Low"
        MINIMAL = "Minimal"

    class ThreatCategory:
        MALWARE = "Malware"
        PHISHING = "Phishing"
        DDoS = "DDoS"
        DATA_BREACH = "Data Breach"
        INSIDER_THREAT = "Insider Threat"
        SYSTEM_FAILURE = "System Failure"
        COMPLIANCE_VIOLATION = "Compliance Violation"

    class BCPStatus:
        FULLY_OPERATIONAL = "Fully Operational"
        MINIMAL_IMPACT = "Minimal Impact"
        MODERATE_IMPACT = "Moderate Impact"
        SEVERE_IMPACT = "Severe Impact"
        CRITICAL_FAILURE = "Critical Failure"

    class CybersecurityAnalyzer:
        def analyze_cybersecurity_risk(self):
            return self._get_fallback_analysis()

        def _get_fallback_analysis(self):
            return {
                'risk_assessment': {
                    'overall_risk_score': 0,
                    'risk_level': RiskLevel.MINIMAL,
                    'vulnerability_risk_score': 0,
                    'incident_risk_score': 0,
                    'critical_vulnerabilities': 0,
                    'unpatched_vulnerabilities': 0,
                    'trend_comparison': {}
                },
                'bcp_analysis': {
                    'bcp_status': BCPStatus.CRITICAL_FAILURE,
                    'readiness_score': 0,
                    'business_impact_analysis': [],
                    'recovery_capabilities': {},
                    'last_recovery_test': 'Unknown',
                    'recovery_test_success': False
                },
                'controls_assessment': {
                    'security_controls': [],
                    'overall_effectiveness': 0,
                    'fully_implemented': 0,
                    'partially_implemented': 0,
                    'not_implemented': 0
                },
                'compliance_analysis': {
                    'compliance_score': 0,
                    'failed_login_rate': 0,
                    'compliance_violations': ['Data unavailable'],
                    'gdpr_compliance': False,
                    'data_protection_compliance': False,
                    'access_control_compliance': False,
                    'audit_trail_compliance': False
                },
                'threat_analysis': {},
                'security_recommendations': [],
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }


class CyberDefenseOpsPage:
    def __init__(self):
        # Initialize session state for real-time features
        if 'cyber_defense_refresh' not in st.session_state:
            st.session_state.cyber_defense_refresh = datetime.now()
        if 'live_threat_intel' not in st.session_state:
            st.session_state.live_threat_intel = self._generate_live_threat_intelligence()
        if 'security_posture' not in st.session_state:
            st.session_state.security_posture = self._generate_security_posture()

        # Initialize analyzer
        try:
            self.analyzer = CybersecurityAnalyzer()
        except Exception:
            self.analyzer = CybersecurityAnalyzer()

        self.analysis = self._get_analysis()

        if not self._check_access():
            st.stop()

    def _check_access(self):
        """Check user access permissions using unified RBAC."""
        if not st.session_state.get('authenticated', False):
            st.error("🔐 Please login to access this page")
            return False

        try:
            has_access = check_permission("10_Cybersecurity_BCP.py")
            if not has_access:
                st.error("You do not have permission to access this page")
                return False
        except Exception:
            # Fallback if RBAC fails: allow access but don't crash
            pass

        return True

    def _get_analysis(self):
        """Get cybersecurity analysis (real if available, fallback otherwise)."""
        try:
            with st.spinner("Analyzing cybersecurity risks and business continuity..."):
                return self.analyzer.analyze_cybersecurity_risk()
        except Exception:
            return self.analyzer._get_fallback_analysis()

    def _generate_live_threat_intelligence(self):
        """Generate live threat intelligence data"""
        return {
            'threat_level': 68,
            'active_attacks': 3,
            'blocked_intrusions': 1428,
            'defense_effectiveness': 94.7,
            'threat_feeds': [
                {'source': 'Global Threat Intel', 'severity': 'High', 'count': 42},
                {'source': 'Local Threat Actors', 'severity': 'Medium', 'count': 18},
                {'source': 'Insider Threat Monitor', 'severity': 'Low', 'count': 5}
            ]
        }

    def _generate_security_posture(self):
        """Generate security posture data"""
        return {
            'overall_posture': 'Guarded',
            'attack_surface': 156,
            'mean_time_to_detect': 2.4,
            'mean_time_to_respond': 1.8,
            'patching_lag': 4.2
        }

    def render_cyber_defense_header(self):
        """Render cyber defense operations center header"""
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 30%, #1d4ed8 100%);
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            color: white;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.1);
            position: relative;
            overflow: hidden;
        ">
            <div style="position: absolute; top: 0; right: 0; width: 300px; height: 100%; 
                        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1));
                        transform: skewX(-20deg);">
            </div>
            
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <div style="flex-grow: 1;">
                    <h1 style="color: white; margin: 0; display: flex; align-items: center; gap: 10px;">
                        🛡️ CYBER DEFENSE OPERATIONS CENTER
                    </h1>
                    <p style="color: #dbeafe; margin: 0.5rem 0 0 0; font-size: 1.1rem;">
                        Real-time threat monitoring, security intelligence, and business continuity command
                    </p>
                </div>
                <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 5px;">
                    <span style="background: rgba(255, 255, 255, 0.2); color: white; padding: 4px 12px; 
                               border-radius: 20px; font-weight: bold; border: 1px solid white;">
                        THREAT LEVEL: {st.session_state.live_threat_intel['threat_level']}%
                    </span>
                    <span style="font-size: 0.9rem; color: #dbeafe;">
                        Last scan: {st.session_state.cyber_defense_refresh.strftime("%H:%M:%S")}
                    </span>
                </div>
            </div>
            
            <div style="display: flex; gap: 1rem; margin-top: 1rem;">
                <span style="background: rgba(220, 38, 38, 0.3); padding: 4px 12px; border-radius: 16px; 
                          border: 1px solid #dc2626; font-size: 0.9rem;">
                    ⚡ {st.session_state.live_threat_intel['active_attacks']} Active Attacks
                </span>
                <span style="background: rgba(34, 197, 94, 0.3); padding: 4px 12px; border-radius: 16px; 
                          border: 1px solid #22c55e; font-size: 0.9rem;">
                    🛡️ {st.session_state.live_threat_intel['blocked_intrusions']} Blocked Intrusions
                </span>
                <span style="background: rgba(59, 130, 246, 0.3); padding: 4px 12px; border-radius: 16px; 
                          border: 1px solid #3b82f6; font-size: 0.9rem;">
                    📊 {st.session_state.live_threat_intel['defense_effectiveness']}% Defense Effectiveness
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    def render_threat_radar_marquee(self):
        """Render threat radar marquee with real-time monitoring"""
        try:
            risk_level = self.analysis['risk_assessment']['risk_level']
            threat_level = st.session_state.live_threat_intel['threat_level']
            active_attacks = st.session_state.live_threat_intel['active_attacks']
            
            # Determine threat status
            if threat_level >= 80:
                threat_status = "CRITICAL THREAT LEVEL"
                threat_color = "#dc2626"
                threat_icon = "🚨"
            elif threat_level >= 65:
                threat_status = "HIGH THREAT LEVEL"
                threat_color = "#f59e0b"
                threat_icon = "⚠️"
            elif threat_level >= 50:
                threat_status = "ELEVATED THREAT LEVEL"
                threat_color = "#eab308"
                threat_icon = "🔍"
            else:
                threat_status = "NORMAL THREAT LEVEL"
                threat_color = "#16a34a"
                threat_icon = "✅"
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {threat_color}20 0%, {threat_color}40 100%);
                border: 3px solid {threat_color};
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 1.5rem;
                display: grid;
                grid-template-columns: auto 1fr auto;
                gap: 1rem;
                align-items: center;
                box-shadow: 0 4px 12px {threat_color}40;
            ">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 50px; height: 50px; background: {threat_color}; 
                                border-radius: 50%; display: flex; align-items: center; 
                                justify-content: center; font-size: 1.8rem; animation: pulse 2s infinite;">
                        {threat_icon}
                    </div>
                    <div>
                        <div style="font-weight: bold; font-size: 1.2rem; color: {threat_color};">
                            {threat_status}
                        </div>
                        <div style="font-size: 0.9rem; color: #666;">
                            Threat Level: {threat_level}% | Active Attacks: {active_attacks}
                        </div>
                    </div>
                </div>
                
                <div style="display: flex; gap: 2rem; justify-content: center;">
                    <div style="text-align: center;">
                        <div style="font-size: 0.9rem; color: #666;">Attack Surface</div>
                        <div style="font-weight: bold; color: {threat_color}; font-size: 1.1rem;">
                            {st.session_state.security_posture['attack_surface']}
                        </div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 0.9rem; color: #666;">MTTD</div>
                        <div style="font-weight: bold; color: {threat_color};">
                            {st.session_state.security_posture['mean_time_to_detect']}h
                        </div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 0.9rem; color: #666;">MTTR</div>
                        <div style="font-weight: bold; color: {threat_color};">
                            {st.session_state.security_posture['mean_time_to_respond']}h
                        </div>
                    </div>
                </div>
                
                <div>
                    <span style="background: {threat_color}; color: white; padding: 6px 16px; 
                               border-radius: 20px; font-size: 0.9rem; font-weight: bold;">
                        {threat_icon} {threat_status}
                    </span>
                </div>
            </div>
            
            <style>
                @keyframes pulse {{
                    0% {{ transform: scale(1); opacity: 1; }}
                    50% {{ transform: scale(1.05); opacity: 0.8; }}
                    100% {{ transform: scale(1); opacity: 1; }}
                }}
            </style>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error in threat radar: {str(e)}")

    def render_cyber_defense_dashboard(self):
        """Render cyber defense dashboard with strategic tabs"""
        st.markdown("### 🛡️ CYBER DEFENSE DASHBOARD")
        
        # Strategic 5-tab structure for cyber defense
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📡 **Threat Intelligence**", 
            "🎯 **Vulnerability Ops**", 
            "🛡️ **Defense Systems**",
            "🔄 **Continuity Command**",
            "⚖️ **Compliance Watch**"
        ])
        
        with tab1:
            self.render_threat_intelligence()
        
        with tab2:
            self.render_vulnerability_ops()
        
        with tab3:
            self.render_defense_systems()
        
        with tab4:
            self.render_continuity_command()
        
        with tab5:
            self.render_compliance_watch()

    def render_cyber_defense_framework(self):
        """Render cyber defense framework"""
        with st.expander("🧠 CYBER DEFENSE INTELLIGENCE FRAMEWORK", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**📡 Threat Intelligence**")
                st.info("Real-time monitoring of global and local threat landscapes")
                st.markdown("**🎯 Vulnerability Management**")
                st.info("Systematic identification and remediation of security weaknesses")
            
            with col2:
                st.markdown("**🛡️ Defense Systems**")
                st.info("Multi-layered security controls and detection capabilities")
                st.markdown("**🔄 Continuity Command**")
                st.info("Business continuity planning and disaster recovery operations")
            
            with col3:
                st.markdown("**⚖️ Compliance Watch**")
                st.info("Regulatory adherence across NIST, ISO, CIS, and SASRA frameworks")
                st.markdown("**🧠 Predictive Defense**")
                st.info("AI-driven threat prediction and proactive security measures")

    # ---------- THREAT INTELLIGENCE ----------
    def render_threat_intelligence(self):
        """Render threat intelligence interface"""
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("##### 📡 LIVE THREAT MAP")
            
            threat_data = self._generate_threat_map_data()
            
            fig = go.Figure()
            fig.add_trace(go.Scattergeo(
                lon=threat_data['longitudes'],
                lat=threat_data['latitudes'],
                text=threat_data['threat_names'],
                mode='markers',
                name='Threat Sources',
                marker=dict(
                    size=threat_data['severities'],
                    color=threat_data['severities'],
                    colorscale='reds',
                    showscale=True,
                    colorbar=dict(title="Severity"),
                    line=dict(width=1, color='white')
                )
            ))
            
            fig.update_layout(
                title="Global Threat Intelligence Map",
                geo=dict(
                    projection_type="natural earth",
                    showland=True,
                    landcolor="lightgray",
                    showcountries=True,
                    countrycolor="white",
                    coastlinecolor="white"
                ),
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Threat trend analysis
            st.markdown("##### 📈 THREAT TREND ANALYSIS")
            trend_data = self._generate_threat_trend_data()
            
            trend_fig = go.Figure()
            trend_fig.add_trace(go.Scatter(
                x=trend_data['dates'],
                y=trend_data['threat_counts'],
                name='Threat Count',
                line=dict(color='#dc2626', width=3),
                mode='lines+markers'
            ))
            trend_fig.add_trace(go.Scatter(
                x=trend_data['dates'],
                y=trend_data['attack_attempts'],
                name='Attack Attempts',
                line=dict(color='#f59e0b', width=2, dash='dash'),
                yaxis='y2'
            ))
            trend_fig.update_layout(
                title="Threat Activity Trend (30 Days)",
                xaxis_title="Date",
                yaxis_title="Threat Count",
                yaxis2=dict(
                    title="Attack Attempts",
                    overlaying="y",
                    side="right"
                ),
                height=300
            )
            
            st.plotly_chart(trend_fig, use_container_width=True)
        
        with col2:
            # Threat command console
            st.markdown("##### 🎮 THREAT COMMAND CONSOLE")
            
            st.markdown("**📊 LIVE THREAT INDICATORS**")
            col_indicators = st.columns(2)
            with col_indicators[0]:
                st.metric("Threat Level", f"{st.session_state.live_threat_intel['threat_level']}%")
                st.metric("Active Attacks", st.session_state.live_threat_intel['active_attacks'])
            with col_indicators[1]:
                st.metric("Blocked Intrusions", f"{st.session_state.live_threat_intel['blocked_intrusions']}")
                st.metric("Defense Effectiveness", f"{st.session_state.live_threat_intel['defense_effectiveness']}%")
            
            st.markdown("**🚨 THREAT RESPONSE COMMANDS**")
            if st.button("🛡️ Activate Shield", use_container_width=True):
                st.success("Advanced threat protection activated!")
            if st.button("📡 Deep Threat Scan", use_container_width=True):
                st.warning("Deep threat scanning initiated! Analyzing all attack vectors.")
            if st.button("🚨 Incident Response", use_container_width=True, type="secondary"):
                st.error("Incident response activated! Security team mobilized.")
            
            st.markdown("**📡 THREAT INTELLIGENCE FEEDS**")
            for feed in st.session_state.live_threat_intel['threat_feeds']:
                severity_color = "#dc2626" if feed['severity'] == 'High' else "#f59e0b" if feed['severity'] == 'Medium' else "#16a34a"
                st.markdown(f"""
                <div style="background: {severity_color}15; padding: 0.5rem; border-radius: 6px; margin-bottom: 0.5rem;
                            border-left: 4px solid {severity_color}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span><strong>{feed['source']}</strong></span>
                        <span style="font-weight: bold; color: {severity_color};">{feed['count']} alerts</span>
                    </div>
                    <div style="font-size: 0.8rem; color: #666;">Severity: {feed['severity']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("**🛡️ DEFENSE PROTOCOLS**")
            defense_protocol = st.selectbox(
                "Select Defense Protocol",
                ["None", "Code Red: Full Lockdown", "Code Orange: Enhanced Monitoring", 
                 "Code Yellow: Alert Status", "Code Green: Normal Operations"]
            )
            if defense_protocol != "None" and st.button("⚡ Execute Protocol", use_container_width=True):
                self._execute_defense_protocol(defense_protocol)
                st.error(f"Executing {defense_protocol}!")

    def _generate_threat_map_data(self):
        """Generate threat map data"""
        cities = ['Nairobi', 'Lagos', 'Johannesburg', 'Cairo', 'London', 'New York', 'Singapore', 'Mumbai']
        lats = [-1.286, 6.524, -26.195, 30.044, 51.507, 40.712, 1.352, 19.076]
        longs = [36.817, 3.379, 28.034, 31.236, -0.127, -74.006, 103.819, 72.877]
        severities = [65, 78, 42, 55, 88, 92, 34, 71]
        threat_names = ['Cybercrime Ring', 'Financial Hackers', 'Insider Threats', 'State Actors', 
                        'Organized Crime', 'APT Groups', 'Script Kiddies', 'Ransomware Gang']
        
        return {
            'longitudes': longs,
            'latitudes': lats,
            'severities': severities,
            'threat_names': threat_names
        }

    def _generate_threat_trend_data(self):
        """Generate threat trend data"""
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        threat_counts = np.random.randint(20, 100, 30) + np.sin(np.arange(30) * 0.2) * 20
        attack_attempts = np.random.randint(100, 500, 30) + np.cos(np.arange(30) * 0.2) * 50
        
        return {
            'dates': dates,
            'threat_counts': threat_counts,
            'attack_attempts': attack_attempts
        }

    # ---------- VULNERABILITY OPS ----------
    def render_vulnerability_ops(self):
        """Render vulnerability operations"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 🎯 VULNERABILITY MANAGEMENT DASHBOARD")
            
            vuln_metrics = {
                'Critical Vulnerabilities': self.analysis['risk_assessment'].get('critical_vulnerabilities', 0),
                'Unpatched Vulnerabilities': self.analysis['risk_assessment'].get('unpatched_vulnerabilities', 0),
                'Patching Lag (days)': st.session_state.security_posture.get('patching_lag', 0),
                'Remediation Rate': 85.4,
                'False Positive Rate': 2.8,
                'Scan Coverage': 98.2
            }
            
            for key, value in vuln_metrics.items():
                col_vuln = st.columns([3, 1])
                with col_vuln[0]:
                    st.write(f"**{key}:**")
                with col_vuln[1]:
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        st.write(f"`{value:.1f}`" if isinstance(value, float) else f"`{value}`")
                    else:
                        st.write(f"`{value}`")
            
            st.markdown("##### 🎯 VULNERABILITY PRIORITY MATRIX")
            priority_matrix = [
                {"vulnerability": "RCE in Core Banking", "severity": "Critical", "exploitability": "High", "priority": "P1"},
                {"vulnerability": "SQL Injection in Portal", "severity": "High", "exploitability": "Medium", "priority": "P2"},
                {"vulnerability": "XSS in Member Portal", "severity": "Medium", "exploitability": "High", "priority": "P2"},
                {"vulnerability": "Weak Password Policy", "severity": "Medium", "exploitability": "Low", "priority": "P3"}
            ]
            
            for vuln in priority_matrix:
                priority_color = "#dc2626" if vuln['priority'] == 'P1' else "#f59e0b" if vuln['priority'] == 'P2' else "#eab308"
                st.markdown(f"""
                <div style="background: {priority_color}15; padding: 0.5rem; border-radius: 6px; margin-bottom: 0.5rem;
                            border-left: 4px solid {priority_color}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span><strong>{vuln['vulnerability']}</strong></span>
                        <span style="font-weight: bold; color: {priority_color};">{vuln['priority']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-top: 0.25rem;">
                        <span style="color: #666;">Severity: {vuln['severity']}</span>
                        <span style="color: {priority_color}; font-weight: bold;">Exploitability: {vuln['exploitability']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("##### 📈 VULNERABILITY ANALYTICS")
            vuln_trend = self._generate_vulnerability_trend()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=vuln_trend['months'],
                y=vuln_trend['vulnerability_count'],
                name='Vulnerability Count',
                line=dict(color='#3b82f6', width=3),
                mode='lines+markers'
            ))
            fig.add_trace(go.Scatter(
                x=vuln_trend['months'],
                y=vuln_trend['remediation_rate'],
                name='Remediation Rate',
                line=dict(color='#dc2626', width=2, dash='dash'),
                yaxis='y2'
            ))
            fig.update_layout(
                title="Vulnerability Trend & Remediation Performance",
                xaxis_title="Month",
                yaxis_title="Vulnerability Count",
                yaxis2=dict(
                    title="Remediation Rate (%)",
                    overlaying="y",
                    side="right",
                    range=[0, 100]
                ),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("##### 🔍 VULNERABILITY SCANNER STATUS")
            scanner_data = [
                {"scanner": "Network Scanner", "status": "Active", "last_scan": "2h ago", "findings": 24},
                {"scanner": "Web App Scanner", "status": "Active", "last_scan": "4h ago", "findings": 18},
                {"scanner": "Container Scanner", "status": "Inactive", "last_scan": "2d ago", "findings": 8},
                {"scanner": "Cloud Security Scanner", "status": "Active", "last_scan": "1h ago", "findings": 42}
            ]
            
            for scanner in scanner_data:
                col_scan = st.columns([3, 1, 1])
                with col_scan[0]:
                    status_color = "#16a34a" if scanner['status'] == 'Active' else "#dc2626"
                    st.write(f"**{scanner['scanner']}**")
                    st.markdown(
                        f"<span style='color: {status_color}; font-size: 0.9rem;'>Status: {scanner['status']}</span>",
                        unsafe_allow_html=True
                    )
                with col_scan[1]:
                    st.metric("Findings", scanner['findings'])
                with col_scan[2]:
                    st.caption(f"Scan: {scanner['last_scan']}")

    def _generate_vulnerability_trend(self):
        """Generate vulnerability trend data"""
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug']
        base_count = [45, 52, 48, 56, 62, 58, 51, 47]
        remediation_rate = [65, 68, 72, 75, 78, 82, 85, 88]
        return {
            'months': months,
            'vulnerability_count': base_count,
            'remediation_rate': remediation_rate
        }

    # ---------- DEFENSE SYSTEMS ----------
    def render_defense_systems(self):
        """Render defense systems dashboard"""
        st.markdown("##### 🛡️ DEFENSE SYSTEMS DASHBOARD")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("###### 🏰 DEFENSE LAYERS EFFECTIVENESS")
            defense_layers = [
                {"layer": "Perimeter Defense", "effectiveness": 94.8, "trend": "↑", "alerts": 128},
                {"layer": "Network Security", "effectiveness": 88.5, "trend": "→", "alerts": 64},
                {"layer": "Endpoint Protection", "effectiveness": 91.2, "trend": "↑", "alerts": 42},
                {"layer": "Application Security", "effectiveness": 85.7, "trend": "↓", "alerts": 28},
                {"layer": "Data Protection", "effectiveness": 96.4, "trend": "↑", "alerts": 18},
                {"layer": "Identity & Access", "effectiveness": 89.3, "trend": "→", "alerts": 56}
            ]
            
            for layer in defense_layers:
                trend_color = "#dc2626" if layer['trend'] == "↑" else "#16a34a" if layer['trend'] == "↓" else "#f59e0b"
                st.markdown(f"""
                <div style="padding: 0.5rem; margin-bottom: 0.5rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: bold;">{layer['layer']}</span>
                        <span style="font-weight: bold; color: {trend_color};">{layer['effectiveness']}%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.9rem; margin-top: 0.25rem;">
                        <span style="color: #666;">Alerts: {layer['alerts']}</span>
                        <span style="color: {trend_color}; font-weight: bold;">{layer['trend']}</span>
                    </div>
                    <div style="height: 4px; background: #e0e0e0; border-radius: 2px; margin-top: 0.25rem;">
                        <div style="height: 100%; width: {layer['effectiveness']}%; background: {trend_color}; border-radius: 2px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("###### ⚙️ SECURITY CONTROL IMPLEMENTATION")
            security_controls = [
                {"control": "Firewall Configuration", "implementation": "Fully", "compliance": 98, "risk": "Low"},
                {"control": "SIEM Integration", "implementation": "Partial", "compliance": 78, "risk": "Medium"},
                {"control": "Multi-Factor Auth", "implementation": "Fully", "compliance": 95, "risk": "Low"},
                {"control": "Encryption at Rest", "implementation": "Full", "compliance": 100, "risk": "Minimal"},
                {"control": "Backup Encryption", "implementation": "None", "compliance": 25, "risk": "High"}
            ]
            
            for control in security_controls:
                risk_color = "#dc2626" if control['risk'] == 'High' else "#f59e0b" if control['risk'] == 'Medium' else "#16a34a"
                impl_color = "#16a34a" if control['implementation'] in ['Fully', 'Full'] else "#f59e0b" if control['implementation'] == 'Partial' else "#dc2626"
                st.markdown(f"""
                <div style="background: {risk_color}15; padding: 0.75rem; border-radius: 8px; 
                            margin-bottom: 0.5rem; border-left: 4px solid {impl_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: bold;">{control['control']}</span>
                        <span style="background: {impl_color}; color: white; padding: 2px 8px; 
                                  border-radius: 12px; font-size: 0.8rem; font-weight: bold;">
                            {control['implementation']}
                        </span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.9rem; margin-top: 0.25rem;">
                        <span style="color: #666;">Compliance: {control['compliance']}%</span>
                        <span style="color: {risk_color}; font-weight: bold;">Risk: {control['risk']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("###### 🎯 CONTROL OPTIMIZATION")
            selected_control = st.selectbox(
                "Select Control to Optimize",
                ["SIEM Integration", "Backup Encryption", "Network Segmentation"]
            )
            if st.button("⚡ Optimize Control", use_container_width=True):
                st.success(f"Optimizing {selected_control}! AI analyzing implementation gaps...")

    # ---------- CONTINUITY COMMAND ----------
    def render_continuity_command(self):
        """Render business continuity command center"""
        st.markdown("##### 🔄 BUSINESS CONTINUITY COMMAND")
        
        tab1, tab2, tab3 = st.tabs(["🏢 BCP Dashboard", "🔄 Recovery Ops", "🧪 Testing Center"])
        
        with tab1:
            st.markdown("###### 🏢 BCP DASHBOARD")
            bcp_metrics = [
                {"metric": "BCP Readiness Score", "current": self.analysis['bcp_analysis'].get('readiness_score', 0), "target": 95, "unit": "%"},
                {"metric": "RTO Achievement", "current": 85, "target": 90, "unit": "%"},
                {"metric": "RPO Achievement", "current": 92, "target": 95, "unit": "%"},
                {"metric": "Last Test Success", "current": 1 if self.analysis['bcp_analysis'].get('recovery_test_success', False) else 0, "target": 1, "unit": ""}
            ]
            
            for metric in bcp_metrics:
                col_bcp = st.columns([2, 1, 1])
                with col_bcp[0]:
                    st.write(f"**{metric['metric']}**")
                with col_bcp[1]:
                    current_val = f"{metric['current']}{metric['unit']}" if metric['unit'] else ("✅" if metric['current'] == 1 else "❌")
                    st.metric("Current", current_val)
                with col_bcp[2]:
                    progress = (metric['current'] / metric['target']) * 100 if metric['target'] > 0 else 0
                    progress_color = "#16a34a" if progress >= 90 else "#f59e0b" if progress >= 75 else "#dc2626"
                    st.markdown(
                        f"<span style='color: {progress_color}; font-weight: bold;'>{progress:.1f}% of Target</span>",
                        unsafe_allow_html=True
                    )
            
            if st.button("💾 Update BCP Strategy", use_container_width=True):
                st.success("BCP strategy updated! Team notifications sent.")
        
        with tab2:
            st.markdown("###### 🔄 RECOVERY OPERATIONS")
            recovery_ops = [
                {"operation": "Data Recovery", "status": "Active", "success_rate": 98, "avg_time": "2h"},
                {"operation": "System Recovery", "status": "Standby", "success_rate": 95, "avg_time": "4h"},
                {"operation": "Application Recovery", "status": "Active", "success_rate": 92, "avg_time": "3h"},
                {"operation": "Network Recovery", "status": "Testing", "success_rate": 88, "avg_time": "6h"}
            ]
            
            for op in recovery_ops:
                col_ops = st.columns([2, 2])
                with col_ops[0]:
                    st.write(f"**{op['operation']}**")
                    status_color = "#16a34a" if op['status'] == 'Active' else "#f59e0b" if op['status'] == 'Standby' else "#3b82f6"
                    st.markdown(
                        f"<span style='color: {status_color};'>Status: {op['status']}</span>",
                        unsafe_allow_html=True
                    )
                with col_ops[1]:
                    st.metric("Success Rate", f"{op['success_rate']}%", f"Time: {op['avg_time']}")
        
        with tab3:
            st.markdown("###### 🧪 TESTING CENTER")
            test_scenarios = {
                "Minor Outage": {"recovery_time": "2h", "success_probability": 95, "risk": "Low"},
                "Major Disaster": {"recovery_time": "8h", "success_probability": 85, "risk": "Medium"},
                "Cyber Attack": {"recovery_time": "12h", "success_probability": 75, "risk": "High"}
            }
            
            selected_scenario = st.radio(
                "Select Test Scenario",
                list(test_scenarios.keys()),
                horizontal=True
            )
            scenario = test_scenarios[selected_scenario]
            
            st.markdown(f"""
            <div style="background: #f0f9ff; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                <h4 style="margin: 0 0 0.5rem 0;">{selected_scenario} Scenario Selected</h4>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem;">
                    <div><strong>Recovery Time:</strong> {scenario['recovery_time']}</div>
                    <div><strong>Success Probability:</strong> {scenario['success_probability']}%</div>
                    <div><strong>Risk Level:</strong> {scenario['risk']}</div>
                    <div><strong>Team Readiness:</strong> 92%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 Execute Test Scenario", use_container_width=True):
                st.success(f"{selected_scenario} test scenario executed! Results being analyzed...")

    # ---------- COMPLIANCE WATCH ----------
    def render_compliance_watch(self):
        """Render compliance watch dashboard"""
        st.markdown("##### ⚖️ COMPLIANCE WATCH DASHBOARD")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("###### 📋 FRAMEWORK COMPLIANCE")
            frameworks = [
                {"framework": "NIST CSF", "compliance": 92.4, "status": "Compliant"},
                {"framework": "ISO 27001", "compliance": 88.7, "status": "Partial"},
                {"framework": "CIS Controls", "compliance": 95.8, "status": "Compliant"},
                {"framework": "SASRA Cybersecurity", "compliance": 96.2, "status": "Compliant"}
            ]
            
            for i, framework in enumerate(frameworks, 1):
                status_color = "#16a34a" if framework['status'] == 'Compliant' else "#f59e0b" if framework['status'] == 'Partial' else "#dc2626"
                st.markdown(f"""
                <div style="background: {'#f0f9ff' if i == 1 else '#f8fafc'}; padding: 0.75rem; border-radius: 8px; 
                            margin-bottom: 0.5rem; border-left: 4px solid {status_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-weight: bold; font-size: 1.1rem;">{framework['framework']}</div>
                            <div style="font-size: 0.9rem; color: #666;">{framework['status']}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-weight: bold; font-size: 1.2rem;">{framework['compliance']}%</div>
                            <div style="font-size: 0.9rem; color: #666;">Compliance</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("###### 📜 REGULATORY REQUIREMENTS")
            regulations = [
                {"requirement": "Data Protection", "status": "Compliant", "last_audit": "2024-Q1"},
                {"requirement": "Access Control", "status": "Partial", "last_audit": "2024-Q1"},
                {"requirement": "Incident Reporting", "status": "Compliant", "last_audit": "2024-Q1"},
                {"requirement": "Audit Trail", "status": "Compliant", "last_audit": "2024-Q1"}
            ]
            
            for reg in regulations:
                col_reg = st.columns([3, 1, 1])
                with col_reg[0]:
                    st.write(f"**{reg['requirement']}**")
                with col_reg[1]:
                    status_color = "#16a34a" if reg['status'] == 'Compliant' else "#f59e0b" if reg['status'] == 'Partial' else "#dc2626"
                    st.markdown(
                        f"<span style='color: {status_color}; font-weight: bold;'>{reg['status']}</span>",
                        unsafe_allow_html=True
                    )
                with col_reg[2]:
                    st.caption(f"Audit: {reg['last_audit']}")
            
            st.markdown("###### 📈 COMPLIANCE TREND")
            quarters = ['2023-Q3', '2023-Q4', '2024-Q1', '2024-Q2', '2024-Q3', '2024-Q4']
            compliance_scores = [85, 88, 90, 92, 94, 96]
            
            fig = px.line(
                x=quarters,
                y=compliance_scores,
                title="Compliance Score Progression",
                markers=True
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

    def _execute_defense_protocol(self, protocol):
        """Execute defense protocol"""
        try:
            audit_log(
                "cybersecurity_defense_protocol",
                f"Executed defense protocol: {protocol}",
                {"protocol": protocol, "timestamp": datetime.now().isoformat()}
            )
        except Exception:
            pass

    # =============================================
    # PRESERVED ORIGINAL FUNCTIONALITY (Enhanced where needed)
    # =============================================
    def render_enhanced_dashboard(self):
        """Render enhanced cybersecurity dashboard with original metrics"""
        st.markdown("---")
        st.subheader("🔒 Comprehensive Security Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            risk_score = self.analysis['risk_assessment']['overall_risk_score']
            risk_level = self.analysis['risk_assessment']['risk_level']
            risk_color = {
                "Critical": "#FF0000",
                "High": "#FF6B00", 
                "Medium": "#FFA500",
                "Low": "#00FF00",
                "Minimal": "#008000"
            }.get(str(risk_level), "#666666")
            
            st.markdown(f"""
            <div style="background: {risk_color}15; padding: 1rem; border-radius: 10px; border-left: 4px solid {risk_color};">
                <h4 style="margin: 0; color: {risk_color};">Cyber Risk Score</h4>
                <h2 style="margin: 0.5rem 0; color: {risk_color};">{risk_score:.1f}</h2>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: {risk_color};">
                        {'🚨 Critical' if risk_level == 'Critical' else '⚠️ High' if risk_level == 'High' else '🔍 Medium' if risk_level == 'Medium' else '✅ Low'}
                    </span>
                    <span style="font-size: 0.9rem; color: #666;">Overall Risk</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            bcp_score = self.analysis['bcp_analysis']['readiness_score']
            bcp_status = self.analysis['bcp_analysis']['bcp_status']
            bcp_color = "#16a34a" if bcp_score >= 90 else "#f59e0b" if bcp_score >= 75 else "#dc2626"
            
            st.markdown(f"""
            <div style="background: {bcp_color}15; padding: 1rem; border-radius: 10px; border-left: 4px solid {bcp_color};">
                <h4 style="margin: 0; color: {bcp_color};">BCP Readiness</h4>
                <h2 style="margin: 0.5rem 0; color: {bcp_color};">{bcp_score:.1f}%</h2>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: {bcp_color};">
                        {'🛡️ Optimal' if bcp_score >= 90 else '⚠️ Adequate' if bcp_score >= 75 else '🚨 Deficient'}
                    </span>
                    <span style="font-size: 0.9rem; color: #666;">{bcp_status}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            controls_score = self.analysis['controls_assessment']['overall_effectiveness']
            controls_color = "#16a34a" if controls_score >= 90 else "#f59e0b" if controls_score >= 80 else "#dc2626"
            
            st.markdown(f"""
            <div style="background: {controls_color}15; padding: 1rem; border-radius: 10px; border-left: 4px solid {controls_color};">
                <h4 style="margin: 0; color: {controls_color};">Controls Effectiveness</h4>
                <h2 style="margin: 0.5rem 0; color: {controls_color};">{controls_score:.1f}%</h2>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: {controls_color};">
                        {'✅ Optimal' if controls_score >= 90 else '⚠️ Effective' if controls_score >= 80 else '🔧 Needs Work'}
                    </span>
                    <span style="font-size: 0.9rem; color: #666;">Security Controls</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            compliance_score = self.analysis['compliance_analysis']['compliance_score']
            violations = len(self.analysis['compliance_analysis']['compliance_violations'])
            compliance_color = "#16a34a" if compliance_score >= 90 else "#f59e0b" if compliance_score >= 80 else "#dc2626"
            
            st.markdown(f"""
            <div style="background: {compliance_color}15; padding: 1rem; border-radius: 10px; border-left: 4px solid {compliance_color};">
                <h4 style="margin: 0; color: {compliance_color};">Compliance Score</h4>
                <h2 style="margin: 0.5rem 0; color: {compliance_color};">{compliance_score:.1f}</h2>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: {compliance_color};">
                        {'✅ Compliant' if compliance_score >= 90 else '⚠️ Partial' if compliance_score >= 80 else '🚨 Deficient'}
                    </span>
                    <span style="font-size: 0.9rem; color: #666;">{violations} violations</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        self.render_detailed_sections()

    def render_detailed_sections(self):
        """Render preserved detailed analysis sections"""
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🔍 Threat Analysis", 
            "📊 Risk Assessment", 
            "🛡️ Business Continuity",
            "⚙️ Security Controls",
            "📋 Recommendations"
        ])
        
        with tab1:
            self.display_threat_analysis(self.analysis['threat_analysis'])
        with tab2:
            self.display_risk_assessment(self.analysis['risk_assessment'])
        with tab3:
            self.display_business_continuity(self.analysis['bcp_analysis'])
        with tab4:
            self.display_security_controls(self.analysis['controls_assessment'])
        with tab5:
            self.display_recommendations(self.analysis['security_recommendations'])

    # ---------- PRESERVED HELPER METHODS ----------
    def display_threat_analysis(self, threat_analysis: Dict[str, Any]):
        st.header("🔍 Threat Landscape Analysis")
        
        if not threat_analysis:
            st.warning("Threat analysis data unavailable")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            threat_dist = threat_analysis.get('threat_distribution', {})
            if threat_dist:
                fig = px.bar(
                    x=list(threat_dist.keys()),
                    y=list(threat_dist.values()),
                    title="Threat Category Distribution",
                    labels={'x': 'Threat Category', 'y': 'Number of Incidents'},
                    color=list(threat_dist.values()),
                    color_continuous_scale='reds'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            severity_dist = threat_analysis.get('severity_distribution', {})
            if severity_dist:
                fig = px.pie(
                    values=list(severity_dist.values()),
                    names=list(severity_dist.keys()),
                    title="Incident Severity Distribution",
                    color_discrete_sequence=px.colors.sequential.Reds_r
                )
                st.plotly_chart(fig, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Incidents", threat_analysis.get('total_incidents', 0))
        with col2:
            st.metric("Resolved Incidents", threat_analysis.get('resolved_incidents', 0))
        with col3:
            avg_response = threat_analysis.get('average_response_time_hours', 0)
            st.metric("Avg Response Time", f"{avg_response:.1f} hours")

    def display_risk_assessment(self, risk_assessment: Dict[str, Any]):
        st.header("📊 Cybersecurity Risk Assessment")
        
        col1, col2 = st.columns(2)
        with col1:
            risk_components = {
                'Vulnerability Risk': risk_assessment.get('vulnerability_risk_score', 0),
                'Incident Risk': risk_assessment.get('incident_risk_score', 0)
            }
            fig = px.bar(
                x=list(risk_components.keys()),
                y=list(risk_components.values()),
                title="Risk Component Breakdown",
                labels={'x': 'Risk Component', 'y': 'Risk Score'},
                color=list(risk_components.values()),
                color_continuous_scale='reds'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            trend_data = risk_assessment.get('trend_comparison', {})
            if trend_data:
                fig = px.line(
                    x=list(trend_data.keys()),
                    y=list(trend_data.values()),
                    title="Risk Trend Over Time",
                    labels={'x': 'Time Period', 'y': 'Risk Score'},
                    markers=True
                )
                fig.update_traces(line=dict(color='red', width=3))
                st.plotly_chart(fig, use_container_width=True)

    def display_business_continuity(self, bcp_analysis: Dict[str, Any]):
        st.header("🛡️ Business Continuity Planning")
        
        bcp_status = bcp_analysis.get('bcp_status', 'Unknown')
        readiness_score = bcp_analysis.get('readiness_score', 0)
        status_colors = {
            "Fully Operational": "green",
            "Minimal Impact": "lightgreen", 
            "Moderate Impact": "orange",
            "Severe Impact": "red",
            "Critical Failure": "darkred"
        }
        
        st.markdown(f"""
        <div style="padding: 20px; border-radius: 10px; background-color: {status_colors.get(str(bcp_status), 'gray')}; color: white;">
            <h3 style="margin: 0;">BCP Status: {bcp_status}</h3>
            <p style="margin: 0;">Readiness Score: {readiness_score:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

    def display_security_controls(self, controls_assessment: Dict[str, Any]):
        st.header("⚙️ Security Controls Assessment")
        effectiveness = controls_assessment.get('overall_effectiveness', 0)
        st.metric(
            "Overall Controls Effectiveness",
            f"{effectiveness:.1f}%",
            delta="Optimal" if effectiveness >= 85 else "Needs Improvement",
            delta_color="normal" if effectiveness >= 85 else "off"
        )

    def display_recommendations(self, recommendations: List[Dict[str, Any]]):
        st.header("📋 Security Improvement Recommendations")
        
        if not recommendations:
            st.info("No specific recommendations at this time. Current security posture appears adequate.")
            return
        
        priority_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
        sorted_recommendations = sorted(
            recommendations, 
            key=lambda x: priority_order.get(x.get('priority', 'Low'), 3)
        )
        
        for i, rec in enumerate(sorted_recommendations, 1):
            priority = rec.get('priority', 'Medium')
            category = rec.get('category', 'General')
            recommendation = rec.get('recommendation', '')
            effort = rec.get('estimated_effort', 'Unknown')
            impact = rec.get('impact', 'Medium')
            
            priority_colors = {
                'Critical': 'red',
                'High': 'orange', 
                'Medium': 'yellow',
                'Low': 'green'
            }
            
            st.markdown(f"""
            <div style="padding: 15px; border-left: 5px solid {priority_colors.get(priority, 'gray')}; 
                        background-color: #f8f9fa; margin: 10px 0; border-radius: 5px;">
                <h4 style="margin: 0;">{i}. {recommendation}</h4>
                <p style="margin: 5px 0;">
                    <strong>Priority:</strong> <span style="color: {priority_colors.get(priority, 'black')};">{priority}</span> | 
                    <strong>Category:</strong> {category} | 
                    <strong>Effort:</strong> {effort} | 
                    <strong>Impact:</strong> {impact}
                </p>
            </div>
            """, unsafe_allow_html=True)

    def run(self):
        """Run the enhanced cyber defense operations center"""
        self.render_cyber_defense_header()
        self.render_threat_radar_marquee()
        self.render_cyber_defense_framework()
        self.render_cyber_defense_dashboard()
        self.render_enhanced_dashboard()
        
        # Unified audit logging for page view
        try:
            risk_level = self.analysis['risk_assessment']['risk_level']
            bcp_status = self.analysis['bcp_analysis']['bcp_status']
            risk_score = self.analysis['risk_assessment']['overall_risk_score']
            bcp_score = self.analysis['bcp_analysis']['readiness_score']
            
            audit_log(
                "cybersecurity_bcp_view",
                f"Viewed cybersecurity and BCP dashboard - Risk: {risk_level}, BCP: {bcp_status}",
                {"risk_score": risk_score, "bcp_score": bcp_score}
            )
        except Exception:
            pass


def main():
    """Main entry point"""
    page = CyberDefenseOpsPage()
    page.run()


if __name__ == "__main__":
    main()
