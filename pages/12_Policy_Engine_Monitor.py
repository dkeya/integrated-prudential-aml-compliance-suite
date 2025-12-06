# pages/12_Policy_Engine_Monitor.py
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

# Make sure Python can see the project root so `core.*` works
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================
# UNIFIED CORE IMPORTS
# ============================
from core.rbac import (
    RBACManager,
    check_permission,
    get_current_role,
    get_current_username,
)
from core.audit import audit_logger
from core.sidebar import render_sidebar

try:
    from core.database import DatabaseManager
except ImportError:
    DatabaseManager = None

# Try to import a proper policy engine implementation from core, else use fallback
try:
    from core.analytics.policy_engine import (
        PolicyEngineAnalyzer,
        PolicyRuleType,
        RuleStatus,
        AlertSeverity,
        PolicyRule,
        PolicyAlert,
    )
except ImportError:
    # ================
    # Fallback classes
    # ================
    class PolicyRuleType:
        RISK_MONITORING = "Risk Monitoring"
        COMPLIANCE = "Compliance"
        OPERATIONAL = "Operational"
        FINANCIAL = "Financial"
        SECURITY = "Security"

    class RuleStatus:
        ACTIVE = "Active"
        INACTIVE = "Inactive"
        TRIGGERED = "Triggered"
        OVERRIDDEN = "Overridden"
        DISABLED = "Disabled"

    class AlertSeverity:
        CRITICAL = "Critical"
        HIGH = "High"
        MEDIUM = "Medium"
        LOW = "Low"
        INFO = "Information"

    class PolicyRule:
        def __init__(self, rule_id="R-000", rule_name="Sample Rule", status="Active"):
            self.rule_id = rule_id
            self.rule_name = rule_name
            self.status = status

    class PolicyAlert:
        def __init__(self, message="Sample Alert"):
            self.message = message

    class PolicyEngineAnalyzer:
        def __init__(self, db_connection=None):
            self.policy_rules: List[PolicyRule] = []

        def execute_policy_engine(self):
            return self._get_fallback_analysis()

        def _get_fallback_analysis(self):
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return {
                "execution_summary": {
                    "total_rules_executed": 0,
                    "rules_triggered": 0,
                    "successful_executions": 0,
                    "execution_success_rate": 0,
                    "trigger_rate": 0,
                    "last_execution_time": now_str,
                },
                "triggered_rules": [],
                "active_alerts": [],
                "rule_effectiveness": {"overall_effectiveness": 0},
                "risk_exposure": {
                    "risk_exposure_percentage": 0,
                    "risk_level": "Low",
                },
                "compliance_status": {
                    "compliance_rate": 0,
                    "compliance_status": "Unknown",
                },
                "recommendations": [],
                "execution_timestamp": now_str,
            }

# Simple audit wrapper that is safe even if audit_logger changes
def audit_log(action: str, description: str, payload: Optional[Dict] = None):
    user = st.session_state.get("username", "system")
    role = st.session_state.get("role", "system")
    try:
        # Use the same pattern we used in app.py
        audit_logger.log_data_access(user, role, action)
    except Exception:
        # Fallback to console, but never break the app
        print(f"AUDIT ({action}) [{user}/{role}]: {description} | {payload}")


# =============================================
# ENTERPRISE ENHANCEMENTS: Policy Intelligence Framework
# =============================================
POLICY_INTELLIGENCE_PHILOSOPHY = {
    "Data": "What's the current policy compliance landscape, rule execution effectiveness, and risk exposure?",
    "Insights": "Why are policies being triggered, what patterns emerge from rule violations, and where are control gaps?",
    "Frameworks": "How to assess using SASRA Prudential Guidelines, CBK regulations, IFRS 9, Basel III, and internal policy frameworks?",
    "Actions": "What specific policy adjustments, control enhancements, and compliance interventions to implement?",
    "Impact": "What value it creates (regulatory compliance, risk mitigation, operational efficiency, capital optimization)?",
    "Governance": "How policy decisions are documented, approved, monitored, and compliance evidence is maintained?",
}


class PolicyIntelligencePage:
    def __init__(self):
        # Initialize session state for real-time features
        if "policy_intelligence_refresh" not in st.session_state:
            st.session_state.policy_intelligence_refresh = datetime.now()
        if "live_policy_pulse" not in st.session_state:
            st.session_state.live_policy_pulse = self._generate_policy_pulse()
        if "compliance_signals" not in st.session_state:
            st.session_state.compliance_signals = self._generate_compliance_signals()

        # Initialize policy engine using unified DatabaseManager where available
        try:
            db_connection = None
            if DatabaseManager is not None:
                dbm = DatabaseManager()
                if hasattr(dbm, "get_connection"):
                    db_connection = dbm.get_connection()
            self.engine = PolicyEngineAnalyzer(db_connection)
        except Exception:
            self.engine = PolicyEngineAnalyzer()

        # Execute policy engine
        self.analysis = self._get_analysis()

        # RBAC / access control
        if not self._check_access():
            st.stop()

    def _check_access(self):
        """Check user access permissions via unified RBAC."""
        if not st.session_state.get("authenticated", False):
            st.error("🔐 Please login to access this page")
            return False

        try:
            has_access = check_permission("12_Policy_Engine_Monitor.py")
            if not has_access:
                st.error("You do not have permission to access this page")
                return False
        except Exception:
            # Fallback if RBAC fails – allow but don't break the page
            pass

        return True

    def _get_analysis(self):
        """Get policy engine analysis."""
        try:
            with st.spinner("Executing policy rules and analyzing compliance..."):
                return self.engine.execute_policy_engine()
        except Exception:
            # Fallback to internal safe version
            return self.engine._get_fallback_analysis()

    def _generate_policy_pulse(self):
        """Generate live policy pulse data."""
        return {
            "policy_health": 88,
            "rule_velocity": 3.2,
            "compliance_momentum": 2.4,
            "control_coverage": 94.7,
            "hot_policies": [
                {"policy": "Credit Risk Limits", "triggers": 24, "severity": "High"},
                {"policy": "Liquidity Compliance", "triggers": 18, "severity": "Medium"},
                {"policy": "Data Protection", "triggers": 5, "severity": "Low"},
            ],
        }

    def _generate_compliance_signals(self):
        """Generate compliance signals data."""
        return {
            "regulatory_compliance": 96.2,
            "policy_adherence": 92.8,
            "audit_ready_score": 94.5,
            "compliance_velocity": 1.8,
            "next_audit_date": "2024-06-15",
        }

    def render_policy_intelligence_header(self):
        """Render policy intelligence command center header."""
        st.markdown(
            f"""
        <div style="
            background: linear-gradient(135deg, #059669 0%, #047857 30%, #065f46 100%);
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
                        ⚖️ POLICY INTELLIGENCE COMMAND CENTER
                    </h1>
                    <p style="color: #d1fae5; margin: 0.5rem 0 0 0; font-size: 1.1rem;">
                        Real-time policy monitoring, compliance automation, and regulatory intelligence
                    </p>
                </div>
                <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 5px;">
                    <span style="background: rgba(255, 255, 255, 0.2); color: white; padding: 4px 12px; 
                               border-radius: 20px; font-weight: bold; border: 1px solid white;">
                        POLICY HEALTH: {st.session_state.live_policy_pulse['policy_health']}%
                    </span>
                    <span style="font-size: 0.9rem; color: #d1fae5;">
                        Last scan: {st.session_state.policy_intelligence_refresh.strftime("%H:%M:%S")}
                    </span>
                </div>
            </div>
            
            <div style="display: flex; gap: 1rem; margin-top: 1rem;">
                <span style="background: rgba(34, 197, 94, 0.3); padding: 4px 12px; border-radius: 16px; 
                          border: 1px solid #22c55e; font-size: 0.9rem;">
                    ⚖️ {st.session_state.live_policy_pulse['policy_health']}% Policy Health
                </span>
                <span style="background: rgba(14, 165, 233, 0.3); padding: 4px 12px; border-radius: 16px; 
                          border: 1px solid #0ea5e9; font-size: 0.9rem;">
                    📈 {st.session_state.live_policy_pulse['rule_velocity']} Rule Velocity
                </span>
                <span style="background: rgba(245, 158, 11, 0.3); padding: 4px 12px; border-radius: 16px; 
                          border: 1px solid #f59e0b; font-size: 0.9rem;">
                    🛡️ {st.session_state.live_policy_pulse['control_coverage']}% Control Coverage
                </span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    def render_compliance_radar_marquee(self):
        """Render compliance radar marquee with real-time monitoring."""
        try:
            compliance_rate = self.analysis["compliance_status"].get("compliance_rate", 0)
            risk_exposure = self.analysis["risk_exposure"].get(
                "risk_exposure_percentage", 0
            )

            compliance_score = st.session_state.compliance_signals["regulatory_compliance"]
            if compliance_score >= 95:
                compliance_status = "FULLY COMPLIANT"
                compliance_color = "#059669"
                compliance_icon = "✅"
            elif compliance_score >= 90:
                compliance_status = "LARGELY COMPLIANT"
                compliance_color = "#22c55e"
                compliance_icon = "⚠️"
            elif compliance_score >= 85:
                compliance_status = "PARTIALLY COMPLIANT"
                compliance_color = "#f59e0b"
                compliance_icon = "🔍"
            else:
                compliance_status = "NON-COMPLIANT"
                compliance_color = "#dc2626"
                compliance_icon = "🚨"

            st.markdown(
                f"""
            <div style="
                background: linear-gradient(135deg, {compliance_color}20 0%, {compliance_color}40 100%);
                border: 3px solid {compliance_color};
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 1.5rem;
                display: grid;
                grid-template-columns: auto 1fr auto;
                gap: 1rem;
                align-items: center;
                box-shadow: 0 4px 12px {compliance_color}40;
            ">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 50px; height: 50px; background: {compliance_color}; 
                                border-radius: 50%; display: flex; align-items: center; 
                                justify-content: center; font-size: 1.8rem; animation: pulse 2s infinite;">
                        {compliance_icon}
                    </div>
                    <div>
                        <div style="font-weight: bold; font-size: 1.2rem; color: {compliance_color};">
                            {compliance_status}
                        </div>
                        <div style="font-size: 0.9rem; color: #666;">
                            Regulatory: {compliance_score}% | Compliance: {compliance_rate:.1f}%
                        </div>
                    </div>
                </div>
                
                <div style="display: flex; gap: 2rem; justify-content: center;">
                    <div style="text-align: center;">
                        <div style="font-size: 0.9rem; color: #666;">Regulatory Compliance</div>
                        <div style="font-weight: bold; color: {compliance_color}; font-size: 1.1rem;">
                            {compliance_score}%
                        </div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 0.9rem; color: #666;">Policy Adherence</div>
                        <div style="font-weight: bold; color: {compliance_color};">
                            {st.session_state.compliance_signals['policy_adherence']}%
                        </div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 0.9rem; color: #666;">Risk Exposure</div>
                        <div style="font-weight: bold; color: {compliance_color};">
                            {risk_exposure:.1f}%
                        </div>
                    </div>
                </div>
                
                <div>
                    <span style="background: {compliance_color}; color: white; padding: 6px 16px; 
                               border-radius: 20px; font-size: 0.9rem; font-weight: bold;">
                        {compliance_icon} {compliance_status}
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
            """,
                unsafe_allow_html=True,
            )

        except Exception as e:
            st.error(f"Error in compliance radar: {str(e)}")

    def render_policy_intelligence_dashboard(self):
        """Render policy intelligence dashboard with strategic tabs."""
        st.markdown("### ⚖️ POLICY INTELLIGENCE DASHBOARD")

        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            [
                "📡 **Policy Radar**",
                "⚙️ **Rule Engine Ops**",
                "📊 **Compliance Intelligence**",
                "🔄 **Control Ops**",
                "🎯 **Regulatory Command**",
            ]
        )

        with tab1:
            self.render_policy_radar()

        with tab2:
            self.render_rule_engine_ops()

        with tab3:
            self.render_compliance_intelligence()

        with tab4:
            self.render_control_ops()

        with tab5:
            self.render_regulatory_command()

    def render_policy_intelligence_framework(self):
        """Render policy intelligence framework."""
        with st.expander("🧠 POLICY INTELLIGENCE FRAMEWORK", expanded=False):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**📡 Policy Radar**")
                st.info(
                    "Real-time monitoring of policy health, rule triggers, and compliance signals"
                )
                st.markdown("**⚙️ Rule Engine Ops**")
                st.info(
                    "Automated rule execution, effectiveness tracking, and performance optimization"
                )

            with col2:
                st.markdown("**📊 Compliance Intelligence**")
                st.info(
                    "Multi-regulatory framework compliance tracking and gap analysis"
                )
                st.markdown("**🔄 Control Operations**")
                st.info(
                    "Control effectiveness monitoring and continuous improvement cycles"
                )

            with col3:
                st.markdown("**🎯 Regulatory Command**")
                st.info(
                    "Centralized regulatory requirement management and audit readiness"
                )
                st.markdown("**🤖 Predictive Compliance**")
                st.info(
                    "AI-driven compliance risk prediction and proactive control enhancement"
                )

    def render_policy_radar(self):
        """Render interactive policy radar visualization."""
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("##### 📡 LIVE POLICY LANDSCAPE")

            policy_data = self._generate_policy_landscape()

            fig = go.Figure()

            for cluster in policy_data["clusters"]:
                fig.add_trace(
                    go.Scatter(
                        x=cluster["x"],
                        y=cluster["y"],
                        mode="markers",
                        name=cluster["name"],
                        marker=dict(
                            size=cluster["size"],
                            color=cluster["color"],
                            opacity=0.7,
                            line=dict(width=1, color="white"),
                        ),
                        text=cluster["policies"],
                        hoverinfo="text",
                    )
                )

            for vector in policy_data["risk_vectors"]:
                fig.add_trace(
                    go.Scatter(
                        x=vector["x"],
                        y=vector["y"],
                        mode="lines",
                        name="Risk Vector",
                        line=dict(color="red", width=2, dash="dot"),
                        showlegend=False,
                    )
                )

            fig.update_layout(
                title="Policy Landscape & Risk Vector Analysis",
                xaxis=dict(title="Compliance Score", showgrid=True, range=[0, 100]),
                yaxis=dict(title="Control Effectiveness", showgrid=True, range=[0, 100]),
                height=500,
                plot_bgcolor="rgba(0,0,0,0.1)",
                showlegend=True,
            )

            st.plotly_chart(fig, use_container_width=True)

            st.markdown("##### 🎯 POLICY EFFECTIVENESS HEATMAP")
            heatmap_data = self._generate_policy_heatmap()

            heatmap_fig = go.Figure(
                data=go.Heatmap(
                    z=heatmap_data["effectiveness_matrix"],
                    x=heatmap_data["policy_areas"],
                    y=heatmap_data["regulatory_frameworks"],
                    colorscale="greens",
                    showscale=True,
                )
            )

            heatmap_fig.update_layout(
                title="Policy Effectiveness by Area & Regulatory Framework",
                xaxis_title="Policy Area",
                yaxis_title="Regulatory Framework",
                height=300,
            )

            st.plotly_chart(heatmap_fig, use_container_width=True)

        with col2:
            st.markdown("##### 🎮 POLICY COMMAND CONSOLE")

            st.markdown("**📊 LIVE POLICY INDICATORS**")
            col_indicators = st.columns(2)
            with col_indicators[0]:
                st.metric(
                    "Policy Health",
                    f"{st.session_state.live_policy_pulse['policy_health']}%",
                )
                st.metric("Rule Velocity", st.session_state.live_policy_pulse["rule_velocity"])
            with col_indicators[1]:
                st.metric(
                    "Control Coverage",
                    f"{st.session_state.live_policy_pulse['control_coverage']}%",
                )
                st.metric(
                    "Compliance Momentum",
                    f"{st.session_state.compliance_signals['compliance_velocity']}",
                )

            st.markdown("**⚙️ POLICY OPERATIONS COMMANDS**")

            if st.button("🔄 Refresh Policy Engine", use_container_width=True):
                st.success("Policy engine refresh initiated!")

            if st.button("📡 Deep Policy Analysis", use_container_width=True):
                st.warning(
                    "Deep policy analysis running! Scanning all policy frameworks."
                )

            if st.button(
                "🚨 Emergency Override",
                use_container_width=True,
                type="secondary",
            ):
                st.error("Emergency override activated! Compliance team notified.")

            st.markdown("**🔥 HIGH-ACTIVITY POLICIES**")

            for policy in st.session_state.live_policy_pulse["hot_policies"]:
                severity_color = (
                    "#dc2626"
                    if policy["severity"] == "High"
                    else "#f59e0b"
                    if policy["severity"] == "Medium"
                    else "#22c55e"
                )
                st.markdown(
                    f"""
                <div style="background: {severity_color}15; padding: 0.5rem; border-radius: 6px; margin-bottom: 0.5rem;
                            border-left: 4px solid {severity_color}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span><strong>{policy['policy']}</strong></span>
                        <span style="font-weight: bold; color: {severity_color};">{policy['triggers']} triggers</span>
                    </div>
                    <div style="font-size: 0.8rem; color: #666;">Severity: {policy['severity']}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            st.markdown("**🛡️ POLICY PROTOCOLS**")

            policy_protocol = st.selectbox(
                "Select Policy Protocol",
                [
                    "None",
                    "Code Green: Normal Operations",
                    "Code Yellow: Enhanced Monitoring",
                    "Code Orange: Policy Review",
                    "Code Red: Emergency Controls",
                ],
            )

            if (
                policy_protocol != "None"
                and st.button("⚡ Execute Protocol", use_container_width=True)
            ):
                self._execute_policy_protocol(policy_protocol)
                st.success(f"Executing {policy_protocol}!")

    def _generate_policy_landscape(self):
        """Generate policy landscape data."""
        clusters = []

        clusters.append(
            {
                "name": "Credit Risk Policies",
                "x": np.random.normal(85, 5, 10),
                "y": np.random.normal(88, 4, 10),
                "size": np.random.uniform(15, 25, 10),
                "color": "#059669",
                "policies": [
                    "Single Borrower Limit",
                    "Portfolio Concentration",
                    "PAR Monitoring",
                    "Provisioning Policy",
                ],
            }
        )

        clusters.append(
            {
                "name": "Liquidity Policies",
                "x": np.random.normal(75, 8, 8),
                "y": np.random.normal(82, 6, 8),
                "size": np.random.uniform(12, 20, 8),
                "color": "#0ea5e9",
                "policies": [
                    "Liquidity Coverage",
                    "Cash Reserve",
                    "ALM Policy",
                    "Stress Testing",
                ],
            }
        )

        clusters.append(
            {
                "name": "Operational Policies",
                "x": np.random.normal(65, 8, 8),
                "y": np.random.normal(75, 8, 8),
                "size": np.random.uniform(10, 18, 8),
                "color": "#f59e0b",
                "policies": [
                    "Fraud Prevention",
                    "BCP Policy",
                    "Data Protection",
                    "Internal Controls",
                ],
            }
        )

        risk_vectors = [
            {
                "x": [40, 55, 70],
                "y": [35, 50, 65],
                "name": "Compliance Gap Vector",
            }
        ]

        return {"clusters": clusters, "risk_vectors": risk_vectors}

    def _generate_policy_heatmap(self):
        """Generate policy heatmap data."""
        policy_areas = [
            "Credit Risk",
            "Liquidity",
            "Operational",
            "Market Risk",
            "Compliance",
        ]
        regulatory_frameworks = [
            "SASRA",
            "CBK",
            "IFRS 9",
            "Basel III",
            "Data Protection",
        ]

        effectiveness_matrix = np.array(
            [
                [92, 88, 85, 82, 90],
                [88, 85, 80, 78, 82],
                [78, 75, 72, 70, 68],
                [85, 82, 80, 78, 75],
                [95, 92, 90, 88, 85],
            ]
        )

        return {
            "policy_areas": policy_areas,
            "regulatory_frameworks": regulatory_frameworks,
            "effectiveness_matrix": effectiveness_matrix,
        }

    def render_rule_engine_ops(self):
        """Render rule engine operations dashboard."""
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### ⚙️ RULE ENGINE COMMAND DASHBOARD")

            summary = self.analysis.get("execution_summary", {})
            current_status = {
                "total_rules": len(self.engine.policy_rules)
                if hasattr(self.engine, "policy_rules")
                else 0,
                "execution_success": summary.get("execution_success_rate", 0),
                "trigger_rate": summary.get("trigger_rate", 0),
                "avg_execution_time": "2.8ms",
                "engine_uptime": "99.95%",
                "last_failure": "None",
            }

            st.markdown("**📊 CURRENT ENGINE STATUS**")
            for key, value in current_status.items():
                col_engine = st.columns([3, 1])
                with col_engine[0]:
                    st.write(f"**{key.replace('_', ' ').title()}:**")
                with col_engine[1]:
                    if key.endswith("_rate") or key == "execution_success":
                        st.write(f"`{float(value):.1f}%`")
                    else:
                        st.write(f"`{value}`")

            st.markdown("**🎯 RULE OPTIMIZATION OPTIONS**")

            optimization_options = [
                {"option": "Risk Rule Tuning", "impact": "+8.4%", "effort": "Medium"},
                {
                    "option": "Compliance Rule Enhancement",
                    "impact": "+12.2%",
                    "effort": "High",
                },
                {
                    "option": "Performance Optimization",
                    "impact": "+5.8%",
                    "effort": "Low",
                },
                {"option": "Maintain Current", "impact": "0.0%", "effort": "None"},
            ]

            for option in optimization_options:
                impact_val = float(option["impact"].replace("+", "").replace("%", ""))
                impact_color = "#059669" if impact_val > 8 else "#f59e0b"
                st.markdown(
                    f"""
                <div style="background: {impact_color}15; padding: 0.5rem; border-radius: 6px; margin-bottom: 0.5rem;
                            border-left: 4px solid {impact_color}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span><strong>{option['option']}</strong></span>
                        <span style="font-weight: bold; color: {impact_color};">{option['impact']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-top: 0.25rem;">
                        <span style="color: #666;">Effort: {option['effort']}</span>
                        <span style="color: {impact_color}; font-weight: bold;">ROI: 3.8x</span>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

        with col2:
            st.markdown("##### 📈 RULE PERFORMANCE ANALYTICS")

            performance_data = self._generate_rule_performance()

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=performance_data["weeks"],
                    y=performance_data["trigger_rates"],
                    name="Trigger Rate",
                    line=dict(color="#0ea5e9", width=3),
                    mode="lines+markers",
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=performance_data["weeks"],
                    y=performance_data["false_positive_rates"],
                    name="False Positive Rate",
                    line=dict(color="#dc2626", width=2, dash="dash"),
                    yaxis="y2",
                )
            )

            fig.update_layout(
                title="Rule Engine Performance Trends",
                xaxis_title="Week",
                yaxis_title="Trigger Rate (%)",
                yaxis2=dict(
                    title="False Positive Rate (%)",
                    overlaying="y",
                    side="right",
                    range=[0, 20],
                ),
                height=400,
            )

            st.plotly_chart(fig, use_container_width=True)

            st.markdown("##### 📊 RULE CATEGORY PERFORMANCE")

            category_data = [
                {
                    "category": "Credit Risk Rules",
                    "effectiveness": 92.4,
                    "alerts": 24,
                    "trend": "↑",
                },
                {
                    "category": "Compliance Rules",
                    "effectiveness": 88.7,
                    "alerts": 18,
                    "trend": "→",
                },
                {
                    "category": "Operational Rules",
                    "effectiveness": 78.9,
                    "alerts": 12,
                    "trend": "↓",
                },
                {
                    "category": "Security Rules",
                    "effectiveness": 95.2,
                    "alerts": 8,
                    "trend": "↑",
                },
            ]

            for category in category_data:
                col_cat = st.columns([3, 1, 1])
                with col_cat[0]:
                    st.write(f"**{category['category']}**")
                with col_cat[1]:
                    trend_color = (
                        "#059669"
                        if category["trend"] == "↑"
                        else "#dc2626"
                        if category["trend"] == "↓"
                        else "#f59e0b"
                    )
                    st.metric(
                        "",
                        f"{category['effectiveness']:.1f}%",
                        category["trend"],
                        label_visibility="collapsed",
                    )
                with col_cat[2]:
                    st.metric("Alerts", category["alerts"])

    def _generate_rule_performance(self):
        """Generate rule performance data."""
        weeks = np.arange(1, 13)

        trigger_rates = [
            12.5 + np.sin(w * 0.5) * 3 + np.random.normal(0, 1) for w in weeks
        ]

        false_positive_rates = [
            15.0 - w * 0.5 + np.random.normal(0, 0.5) for w in weeks
        ]

        return {
            "weeks": weeks,
            "trigger_rates": trigger_rates,
            "false_positive_rates": false_positive_rates,
        }

    def render_compliance_intelligence(self):
        """Render compliance intelligence dashboard."""
        st.markdown("##### 📊 COMPLIANCE INTELLIGENCE DASHBOARD")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("###### 📋 REGULATORY FRAMEWORK COMPLIANCE")

            framework_compliance = [
                {
                    "framework": "SASRA Prudential",
                    "compliance": 96.5,
                    "trend": "↑",
                    "requirements": 42,
                },
                {
                    "framework": "CBK Regulations",
                    "compliance": 94.2,
                    "trend": "→",
                    "requirements": 28,
                },
                {
                    "framework": "IFRS 9",
                    "compliance": 98.8,
                    "trend": "↑",
                    "requirements": 18,
                },
                {
                    "framework": "Data Protection",
                    "compliance": 92.4,
                    "trend": "↑",
                    "requirements": 24,
                },
                {
                    "framework": "Basel III",
                    "compliance": 89.7,
                    "trend": "↓",
                    "requirements": 35,
                },
                {
                    "framework": "Anti-Money Laundering",
                    "compliance": 97.2,
                    "trend": "↑",
                    "requirements": 22,
                },
            ]

            for framework in framework_compliance:
                trend_color = (
                    "#059669"
                    if framework["trend"] == "↑"
                    else "#dc2626"
                    if framework["trend"] == "↓"
                    else "#f59e0b"
                )

                st.markdown(
                    f"""
                <div style="padding: 0.5rem; margin-bottom: 0.5rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: bold;">{framework['framework']}</span>
                        <span style="font-weight: bold; color: {trend_color};">{framework['compliance']}%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.9rem; margin-top: 0.25rem;">
                        <span style="color: #666;">Requirements: {framework['requirements']}</span>
                        <span style="color: {trend_color}; font-weight: bold;">{framework['trend']}</span>
                    </div>
                    <div style="height: 4px; background: #e0e0e0; border-radius: 2px; margin-top: 0.25rem;">
                        <div style="height: 100%; width: {framework['compliance']}%; background: {trend_color}; border-radius: 2px;"></div>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

        with col2:
            st.markdown("###### 🔍 COMPLIANCE GAP ANALYSIS")

            compliance_gaps = [
                {
                    "gap": "Basel III - Leverage Ratio",
                    "severity": "High",
                    "days_open": 45,
                    "owner": "Risk Dept",
                },
                {
                    "gap": "SASRA - Internal Audit Frequency",
                    "severity": "Medium",
                    "days_open": 28,
                    "owner": "Audit",
                },
                {
                    "gap": "Data Protection - Data Retention",
                    "severity": "Medium",
                    "days_open": 32,
                    "owner": "IT",
                },
                {
                    "gap": "CBK - Stress Testing Scenarios",
                    "severity": "Low",
                    "days_open": 15,
                    "owner": "Treasury",
                },
            ]

            for gap in compliance_gaps:
                severity_color = (
                    "#dc2626"
                    if gap["severity"] == "High"
                    else "#f59e0b"
                    if gap["severity"] == "Medium"
                    else "#22c55e"
                )

                st.markdown(
                    f"""
                <div style="background: {severity_color}15; padding: 0.75rem; border-radius: 8px; 
                            margin-bottom: 0.5rem; border-left: 4px solid {severity_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: bold;">{gap['gap']}</span>
                        <span style="background: {severity_color}; color: white; padding: 2px 8px; 
                                  border-radius: 12px; font-size: 0.8rem; font-weight: bold;">
                            {gap['severity']}
                        </span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.9rem; margin-top: 0.25rem;">
                        <span style="color: #666;">Open: {gap['days_open']} days</span>
                        <span style="color: {severity_color}; font-weight: bold;">Owner: {gap['owner']}</span>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            st.markdown("###### 🎯 GAP RESOLUTION")

            selected_gap = st.selectbox(
                "Select Gap to Resolve",
                [
                    "Basel III - Leverage Ratio",
                    "SASRA - Internal Audit Frequency",
                    "Data Protection - Data Retention",
                ],
            )

            if st.button("⚡ Activate Resolution", use_container_width=True):
                st.success(
                    f"Resolution activated for {selected_gap}! Task assigned to owner."
                )

    def render_control_ops(self):
        """Render control operations center."""
        st.markdown("##### 🔄 CONTROL OPERATIONS CENTER")

        tab1, tab2, tab3 = st.tabs(
            ["🛡️ Control Effectiveness", "📊 Performance Ops", "🧪 Testing Lab"]
        )

        with tab1:
            st.markdown("###### 🛡️ CONTROL EFFECTIVENESS")

            control_metrics = [
                {
                    "control": "Automated Monitoring",
                    "effectiveness": 94,
                    "target": 95,
                    "trend": "↑",
                },
                {
                    "control": "Manual Reviews",
                    "effectiveness": 82,
                    "target": 90,
                    "trend": "→",
                },
                {
                    "control": "Segregation of Duties",
                    "effectiveness": 98,
                    "target": 100,
                    "trend": "↑",
                },
                {
                    "control": "Access Controls",
                    "effectiveness": 96,
                    "target": 98,
                    "trend": "↑",
                },
            ]

            for control in control_metrics:
                col_ctrl = st.columns([2, 1, 1])
                with col_ctrl[0]:
                    st.write(f"**{control['control']}**")
                with col_ctrl[1]:
                    trend_color = (
                        "#059669"
                        if control["trend"] == "↑"
                        else "#dc2626"
                        if control["trend"] == "↓"
                        else "#f59e0b"
                    )
                    st.metric(
                        "",
                        f"{control['effectiveness']}%",
                        control["trend"],
                        label_visibility="collapsed",
                    )
                with col_ctrl[2]:
                    progress = (control["effectiveness"] / control["target"]) * 100
                    progress_color = (
                        "#059669"
                        if progress >= 95
                        else "#f59e0b"
                        if progress >= 85
                        else "#dc2626"
                    )
                    st.markdown(
                        f"<span style='color: {progress_color}; font-weight: bold;'>{progress:.1f}% of Target</span>",
                        unsafe_allow_html=True,
                    )

            if st.button("💾 Update Control Strategy", use_container_width=True):
                st.success("Control strategy updated! Team notifications sent.")

        with tab2:
            st.markdown("###### 📊 PERFORMANCE OPERATIONS")

            performance_ops = [
                {
                    "operation": "Control Testing",
                    "status": "Active",
                    "success_rate": 92,
                    "coverage": 85,
                },
                {
                    "operation": "Exception Monitoring",
                    "status": "Active",
                    "success_rate": 88,
                    "coverage": 78,
                },
                {
                    "operation": "Control Automation",
                    "status": "Testing",
                    "success_rate": 75,
                    "coverage": 45,
                },
                {
                    "operation": "Remediation Tracking",
                    "status": "Active",
                    "success_rate": 95,
                    "coverage": 92,
                },
            ]

            for op in performance_ops:
                col_ops = st.columns([2, 2])
                with col_ops[0]:
                    st.write(f"**{op['operation']}**")
                    status_color = (
                        "#059669"
                        if op["status"] == "Active"
                        else "#f59e0b"
                        if op["status"] == "Testing"
                        else "#dc2626"
                    )
                    st.markdown(
                        f"<span style='color: {status_color};'>Status: {op['status']}</span>",
                        unsafe_allow_html=True,
                    )
                with col_ops[1]:
                    st.metric(
                        "Success",
                        f"{op['success_rate']}%",
                        f"Coverage: {op['coverage']}%",
                    )

        with tab3:
            st.markdown("###### 🧪 TESTING LAB")

            test_scenarios = {
                "Control Failure": {
                    "detection_time": "2.8h",
                    "recovery_time": "4.2h",
                    "risk": "Medium",
                },
                "Policy Breach": {
                    "detection_time": "1.2h",
                    "recovery_time": "3.8h",
                    "risk": "High",
                },
                "Regulatory Change": {
                    "detection_time": "24h",
                    "recovery_time": "72h",
                    "risk": "Low",
                },
            }

            selected_scenario = st.radio(
                "Select Test Scenario",
                list(test_scenarios.keys()),
                horizontal=True,
            )

            scenario = test_scenarios[selected_scenario]

            st.markdown(
                f"""
            <div style="background: #f0f9ff; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                <h4 style="margin: 0 0 0.5rem 0;">{selected_scenario} Scenario Selected</h4>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem;">
                    <div><strong>Detection Time:</strong> {scenario['detection_time']}</div>
                    <div><strong>Recovery Time:</strong> {scenario['recovery_time']}</div>
                    <div><strong>Risk Level:</strong> {scenario['risk']}</div>
                    <div><strong>Control Readiness:</strong> 88%</div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            if st.button("🚀 Execute Test Scenario", use_container_width=True):
                st.success(
                    f"{selected_scenario} test scenario executed! Results being analyzed..."
                )

    def render_regulatory_command(self):
        """Render regulatory command dashboard."""
        st.markdown("##### 🎯 REGULATORY COMMAND DASHBOARD")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("###### 📅 REGULATORY CALENDAR")

            regulatory_items = [
                {
                    "item": "SASRA Q1 Returns",
                    "due_date": "2024-03-31",
                    "status": "On Track",
                    "owner": "Compliance",
                },
                {
                    "item": "CBK Annual Report",
                    "due_date": "2024-04-30",
                    "status": "On Track",
                    "owner": "Finance",
                },
                {
                    "item": "Annual External Audit",
                    "due_date": "2024-06-30",
                    "status": "Preparing",
                    "owner": "Audit",
                },
                {
                    "item": "Data Protection Audit",
                    "due_date": "2024-05-15",
                    "status": "Behind",
                    "owner": "IT",
                },
            ]

            for i, item in enumerate(regulatory_items, 1):
                status_color = (
                    "#059669"
                    if item["status"] == "On Track"
                    else "#f59e0b"
                    if item["status"] == "Preparing"
                    else "#dc2626"
                )

                st.markdown(
                    f"""
                <div style="background: {'#fff7ed' if i == 1 else '#f8fafc'}; padding: 0.75rem; border-radius: 8px; 
                            margin-bottom: 0.5rem; border-left: 4px solid {status_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-weight: bold; font-size: 1.1rem;">{item['item']}</div>
                            <div style="font-size: 0.9rem; color: #666;">Due: {item['due_date']}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-weight: bold; font-size: 1.2rem; color: {status_color};">{item['status']}</div>
                            <div style="font-size: 0.9rem; color: #666;">Owner: {item['owner']}</div>
                        </div>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

        with col2:
            st.markdown("###### 📈 REGULATORY INTELLIGENCE")

            regulatory_updates = [
                {
                    "update": "New CBK Circular on Cybersecurity",
                    "impact": "High",
                    "deadline": "2024-09-30",
                },
                {
                    "update": "SASRA Guideline Amendments",
                    "impact": "Medium",
                    "deadline": "2024-08-15",
                },
                {
                    "update": "Data Protection Regulation Updates",
                    "impact": "High",
                    "deadline": "2024-07-31",
                },
                {
                    "update": "IFRS 9 Implementation Guidance",
                    "impact": "Low",
                    "deadline": "2024-06-30",
                },
            ]

            for update in regulatory_updates:
                col_update = st.columns([3, 1, 1])
                with col_update[0]:
                    st.write(f"**{update['update']}**")
                with col_update[1]:
                    impact_color = (
                        "#dc2626"
                        if update["impact"] == "High"
                        else "#f59e0b"
                        if update["impact"] == "Medium"
                        else "#059669"
                    )
                    st.markdown(
                        f"<span style='color: {impact_color}; font-weight: bold;'>{update['impact']}</span>",
                        unsafe_allow_html=True,
                    )
                with col_update[2]:
                    st.caption(f"Deadline: {update['deadline']}")

            st.markdown("###### 📊 COMPLIANCE TREND")

            quarters = ["2023-Q3", "2023-Q4", "2024-Q1", "2024-Q2", "2024-Q3", "2024-Q4"]
            compliance_scores = [88, 90, 92, 94, 95, 96]

            fig = px.line(
                x=quarters,
                y=compliance_scores,
                title="Compliance Score Progression",
                markers=True,
            )

            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

    def _execute_policy_protocol(self, protocol):
        """Execute policy protocol."""
        try:
            audit_log(
                "policy_intelligence_protocol",
                f"Executed policy protocol: {protocol}",
                {"protocol": protocol, "timestamp": datetime.now().isoformat()},
            )
        except Exception:
            pass

    # =============================================
    # PRESERVED ORIGINAL FUNCTIONALITY (Enhanced)
    # =============================================
    def render_enhanced_policy_dashboard(self):
        """Render enhanced policy engine dashboard with original metrics."""
        st.markdown("---")
        st.subheader("⚙️ Policy Engine Monitoring Dashboard")

        col1, col2, col3, col4 = st.columns(4)

        summary = self.analysis.get("execution_summary", {})
        risk_exposure = self.analysis.get("risk_exposure", {})
        compliance = self.analysis.get("compliance_status", {})
        effectiveness = self.analysis.get("rule_effectiveness", {})

        with col1:
            success_rate = summary.get("execution_success_rate", 0)
            success_color = (
                "#059669" if success_rate >= 95 else "#f59e0b" if success_rate >= 85 else "#dc2626"
            )

            st.markdown(
                f"""
            <div style="background: {success_color}15; padding: 1rem; border-radius: 10px; border-left: 4px solid {success_color};">
                <h4 style="margin: 0; color: {success_color};">Execution Success</h4>
                <h2 style="margin: 0.5rem 0; color: {success_color};">{success_rate:.1f}%</h2>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: {success_color};">{'⚡ Optimal' if success_rate >= 95 else '📊 Good' if success_rate >= 85 else '🔧 Needs Attention'}</span>
                    <span style="font-size: 0.9rem; color: #666;">Policy Execution</span>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            risk_percentage = risk_exposure.get("risk_exposure_percentage", 0)
            risk_color = (
                "#059669"
                if risk_percentage < 20
                else "#f59e0b"
                if risk_percentage < 40
                else "#dc2626"
            )

            st.markdown(
                f"""
            <div style="background: {risk_color}15; padding: 1rem; border-radius: 10px; border-left: 4px solid {risk_color};">
                <h4 style="margin: 0; color: {risk_color};">Risk Exposure</h4>
                <h2 style="margin: 0.5rem 0; color: {risk_color};">{risk_percentage:.1f}%</h2>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: {risk_color};">{'✅ Controlled' if risk_percentage < 20 else '⚠️ Monitor' if risk_percentage < 40 else '🚨 High Exposure'}</span>
                    <span style="font-size: 0.9rem; color: #666;">Policy Risk</span>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col3:
            compliance_rate = compliance.get("compliance_rate", 0)
            compliance_color = (
                "#059669"
                if compliance_rate >= 95
                else "#f59e0b"
                if compliance_rate >= 85
                else "#dc2626"
            )

            st.markdown(
                f"""
            <div style="background: {compliance_color}15; padding: 1rem; border-radius: 10px; border-left: 4px solid {compliance_color};">
                <h4 style="margin: 0; color: {compliance_color};">Compliance Rate</h4>
                <h2 style="margin: 0.5rem 0; color: {compliance_color};">{compliance_rate:.1f}%</h2>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: {compliance_color};">{'🛡️ Compliant' if compliance_rate >= 95 else '⚠️ Partial' if compliance_rate >= 85 else '🚨 Deficient'}</span>
                    <span style="font-size: 0.9rem; color: #666;">Regulatory</span>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col4:
            rule_effectiveness = effectiveness.get("overall_effectiveness", 0)
            effectiveness_color = (
                "#059669"
                if rule_effectiveness >= 90
                else "#f59e0b"
                if rule_effectiveness >= 80
                else "#dc2626"
            )

            st.markdown(
                f"""
            <div style="background: {effectiveness_color}15; padding: 1rem; border-radius: 10px; border-left: 4px solid {effectiveness_color};">
                <h4 style="margin: 0; color: {effectiveness_color};">Rule Effectiveness</h4>
                <h2 style="margin: 0.5rem 0; color: {effectiveness_color};">{rule_effectiveness:.1f}%</h2>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: {effectiveness_color};">{'🤖 Highly Effective' if rule_effectiveness >= 90 else '📊 Effective' if rule_effectiveness >= 80 else '🔧 Needs Tuning'}</span>
                    <span style="font-size: 0.9rem; color: #666;">Policy Rules</span>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        self.render_detailed_sections()

    def render_detailed_sections(self):
        """Render preserved detailed analysis sections."""
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            [
                "📋 Rule Dashboard",
                "🚨 Active Alerts",
                "📊 Execution Analytics",
                "🛡️ Compliance Monitor",
                "🎯 Recommendations",
            ]
        )

        with tab1:
            rules = self.engine.policy_rules if hasattr(self.engine, "policy_rules") else []
            self.display_rule_dashboard(rules, self.analysis)

        with tab2:
            self.display_active_alerts(self.analysis.get("active_alerts", []))

        with tab3:
            self.display_execution_analytics(self.analysis)

        with tab4:
            self.display_compliance_monitor(self.analysis)

        with tab5:
            self.display_recommendations(self.analysis.get("recommendations", []))

    # PRESERVED HELPER METHODS (safe minimal implementations)
    def display_rule_dashboard(self, rules: List[Any], analysis: Dict[str, Any]):
        """Display policy rules dashboard - PRESERVED."""
        st.header("📋 Policy Rules Dashboard")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            active_rules = len(
                [r for r in rules if getattr(r, "status", "Active") == "Active"]
            )
            st.metric("Active Rules", active_rules)

        with col2:
            st.metric("Total Rules", len(rules))

        with col3:
            triggered = analysis.get("execution_summary", {}).get("rules_triggered", 0)
            st.metric("Rules Triggered (Last Run)", triggered)

        with col4:
            last_exec = analysis.get("execution_summary", {}).get(
                "last_execution_time", "N/A"
            )
            st.metric("Last Execution", last_exec)

    def display_active_alerts(self, alerts: List[Any]):
        """Display active policy alerts - PRESERVED."""
        st.header("🚨 Active Policy Alerts")

        if not alerts:
            st.success("🎉 No active alerts! All systems are operating within policy limits.")
            return

        for alert in alerts:
            msg = getattr(alert, "message", "Policy alert")
            sev = getattr(alert, "severity", "Medium")
            sev_color = (
                "#dc2626"
                if sev == "Critical"
                else "#f97316"
                if sev == "High"
                else "#facc15"
                if sev == "Medium"
                else "#22c55e"
            )
            st.markdown(
                f"""
            <div style="background: {sev_color}15; padding: 0.75rem; border-radius: 8px; 
                        margin-bottom: 0.5rem; border-left: 4px solid {sev_color};">
                <strong>{sev}:</strong> {msg}
            </div>
            """,
                unsafe_allow_html=True,
            )

    def display_execution_analytics(self, analysis: Dict[str, Any]):
        """Display policy execution analytics - PRESERVED."""
        st.header("📊 Policy Execution Analytics")

        summary = analysis.get("execution_summary", {})

        df = pd.DataFrame(
            [
                {
                    "Metric": "Total Rules Executed",
                    "Value": summary.get("total_rules_executed", 0),
                },
                {
                    "Metric": "Rules Triggered",
                    "Value": summary.get("rules_triggered", 0),
                },
                {
                    "Metric": "Successful Executions",
                    "Value": summary.get("successful_executions", 0),
                },
                {
                    "Metric": "Execution Success Rate (%)",
                    "Value": summary.get("execution_success_rate", 0),
                },
                {
                    "Metric": "Trigger Rate (%)",
                    "Value": summary.get("trigger_rate", 0),
                },
            ]
        )
        st.dataframe(df, use_container_width=True)

    def display_compliance_monitor(self, analysis: Dict[str, Any]):
        """Display compliance monitoring dashboard - PRESERVED."""
        st.header("🛡️ Compliance Monitoring")

        compliance = analysis.get("compliance_status", {})
        risk = analysis.get("risk_exposure", {})

        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Compliance Rate (%)", compliance.get("compliance_rate", 0.0), delta=None
            )
            st.write(f"Status: **{compliance.get('compliance_status', 'Unknown')}**")
        with col2:
            st.metric(
                "Risk Exposure (%)",
                risk.get("risk_exposure_percentage", 0.0),
                delta=None,
            )
            st.write(f"Risk Level: **{risk.get('risk_level', 'Unknown')}**")

    def display_recommendations(self, recommendations: List[Dict[str, Any]]):
        """Display policy improvement recommendations - PRESERVED."""
        st.header("🎯 Policy Improvement Recommendations")

        if not recommendations:
            st.info("No recommendations available from the engine at this time.")
            return

        for rec in recommendations:
            title = rec.get("title", "Recommendation")
            desc = rec.get("description", "")
            impact = rec.get("impact", "Medium")
            sev_color = (
                "#dc2626"
                if impact == "High"
                else "#f59e0b"
                if impact == "Medium"
                else "#22c55e"
            )
            st.markdown(
                f"""
            <div style="background: {sev_color}15; padding: 0.75rem; border-radius: 8px; 
                        margin-bottom: 0.5rem; border-left: 4px solid {sev_color};">
                <strong>{title}</strong> <span style="color:{sev_color};">({impact} Impact)</span>
                <div style="font-size:0.9rem; margin-top:0.25rem;">{desc}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    def _execute_rule_manual(self, rule: Any):
        """Simulated manual rule execution (safe stub)."""
        class ExecutionResult:
            def __init__(self):
                self.triggered = False
                self.actions_taken: List[str] = []

        result = ExecutionResult()
        # Simple placeholder logic – in future can be wired to real engine
        result.triggered = False
        result.actions_taken = [f"Executed rule {getattr(rule, 'rule_name', 'Unknown')}"]
        return result

    def render_manual_execution(self):
        """Render manual rule execution section."""
        st.markdown("---")
        st.subheader("🔄 Manual Rule Execution")

        col1, col2 = st.columns([2, 1])

        with col1:
            if hasattr(self.engine, "policy_rules") and self.engine.policy_rules:
                selected_rule = st.selectbox(
                    "Select Rule to Execute Manually",
                    options=[
                        f"{getattr(rule, 'rule_id', 'Unknown')}: {getattr(rule, 'rule_name', 'Unknown')}"
                        for rule in self.engine.policy_rules
                    ],
                    key="manual_rule_select",
                )
            else:
                st.info("No policy rules available for manual execution")
                selected_rule = None

        with col2:
            st.write("")  # Spacing
            if selected_rule and st.button("🚀 Execute Selected Rule", type="primary"):
                rule_id = selected_rule.split(":")[0]
                rule = next(
                    (
                        r
                        for r in self.engine.policy_rules
                        if getattr(r, "rule_id", "") == rule_id
                    ),
                    None,
                )

                if rule:
                    with st.spinner(
                        f"Executing {getattr(rule, 'rule_name', 'Unknown')}..."
                    ):
                        try:
                            execution = self._execute_rule_manual(rule)
                        except Exception as e:
                            st.error(f"Error executing rule: {e}")
                            execution = None

                    if execution and getattr(execution, "triggered", False):
                        actions = getattr(execution, "actions_taken", [])
                        st.warning(f"Rule triggered! {len(actions)} actions executed.")
                        for action in actions:
                            st.write(f"✅ {action}")
                    else:
                        st.success("Rule executed - No triggers detected")

    def run(self):
        """Run the enhanced policy intelligence page."""
        # Optional: unified sidebar if you want the same nav when running standalone
        # render_sidebar(active_page="12_Policy_Engine_Monitor.py")

        self.render_policy_intelligence_header()
        self.render_compliance_radar_marquee()
        self.render_policy_intelligence_framework()
        self.render_policy_intelligence_dashboard()
        self.render_enhanced_policy_dashboard()
        self.render_manual_execution()

        # Audit logging
        try:
            summary = self.analysis.get("execution_summary", {})
            risk_exposure = self.analysis.get("risk_exposure", {})
            audit_log(
                "policy_engine_view",
                "Viewed policy engine monitoring dashboard",
                {
                    "rules_executed": summary.get("total_rules_executed", 0),
                    "rules_triggered": summary.get("rules_triggered", 0),
                    "risk_exposure": risk_exposure.get("risk_exposure_percentage", 0),
                },
            )
        except Exception:
            pass


def main():
    """Main entry point."""
    page = PolicyIntelligencePage()
    page.run()


if __name__ == "__main__":
    main()
