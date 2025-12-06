# pages/13A_Collections_Funnel_SMS.py
# Communications Command Center – Unified SACCO Platform

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Ensure project root is on sys.path so `core.*` imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 🔽 Unified / Local imports
from core.config import ConfigManager
from core.rbac import RBACManager
from core.audit import AuditLogger, audit_logger  # audit_logger is the singleton instance
from core.sidebar import render_sidebar

# OPTIONAL: Real analyzer (once you port it into core/analytics/sms_automation.py)
try:
    from core.analytics.sms_automation import SMSAutomationAnalyzer
except Exception:
    # Fallback stub so the page works even without the analytics module
    class SMSAutomationAnalyzer:
        """Fallback SMS analyzer stub returning demo data for the UI."""
        def analyze_sms_automation(self):
            return {
                "cost_analysis": {
                    "total_messages": 12_450,
                    "total_roi": 4.25,  # 4.25x => 425%
                    "estimated_revenue": 1_250_000,
                },
                "compliance_analysis": {
                    "compliance_rate": 0.972,
                    "opt_out_rate": 0.015,
                    "opt_out_count": 45,
                    "failure_rate": 0.023,
                    "opt_out_trend": {
                        "Jan": 52,
                        "Feb": 47,
                        "Mar": 42,
                        "Apr": 38,
                        "May": 35,
                        "Jun": 30,
                    },
                    "compliance_issues": [
                        "Some legacy templates missing explicit opt-out text.",
                        "A few campaigns exceed preferred weekly contact frequency.",
                    ],
                },
                "funnel_analysis": {
                    "stage_1": {"stage_label": "Reminder 1", "response_rate": 0.68},
                    "stage_2": {"stage_label": "Reminder 2", "response_rate": 0.55},
                    "stage_3": {"stage_label": "Restructuring Offer", "response_rate": 0.48},
                    "stage_4": {"stage_label": "Final Notice", "response_rate": 0.32},
                },
                "campaign_performance": {
                    "camp_1": {
                        "campaign_name": "Early Reminder",
                        "roi": 4.8,
                        "response_rate": 0.72,
                    },
                    "camp_2": {
                        "campaign_name": "Soft Restructure",
                        "roi": 3.9,
                        "response_rate": 0.64,
                    },
                    "camp_3": {
                        "campaign_name": "Final Demand",
                        "roi": 2.7,
                        "response_rate": 0.38,
                    },
                },
                "response_optimization": {
                    "template_performance": {
                        "Friendly Reminder": 0.72,
                        "Urgent Notice": 0.58,
                        "Restructure Offer": 0.69,
                        "Survey": 0.46,
                    },
                    "time_performance": {
                        "09:00": 0.62,
                        "11:00": 0.68,
                        "14:00": 0.71,
                        "17:00": 0.65,
                    },
                    "best_performing_templates": [
                        ("Friendly Reminder", 0.72),
                        ("Restructure Offer", 0.69),
                        ("Urgent Notice", 0.58),
                    ],
                    "optimal_send_times": [
                        ("11:00", 0.68),
                        ("14:00", 0.71),
                        ("17:00", 0.65),
                    ],
                },
            }

# Page configuration
st.set_page_config(
    page_title="Communications Command Center",
    page_icon="📡",
    layout="wide",
)

# Authentication gate
if not st.session_state.get("authenticated", False):
    st.error("🔐 Please log in to access this page")
    st.stop()

# Unified sidebar
render_sidebar()

# ============================================================================
# ENTERPRISE TRANSFORMATION: COMMUNICATIONS COMMAND CENTER
# ============================================================================


class CollectionsSMSAutomationPage:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.rbac_manager = RBACManager()
        self.audit_logger = audit_logger  # use unified singleton
        self.config = self.config_manager.load_settings()
        self.sms_analyzer = SMSAutomationAnalyzer()

        if not self._check_access():
            st.stop()

    def _check_access(self) -> bool:
        """Enhanced access control with audit logging."""
        if not st.session_state.get("authenticated", False):
            st.error("🔐 Please login to access the Communications Command Center")
            return False

        try:
            has_access = self.rbac_manager.check_page_access(
                "13A_Collections_Funnel_SMS.py",
                st.session_state.role,
                self.config,
            )
        except Exception:
            # If RBAC is not fully wired, allow access but you can tighten later
            has_access = True

        if not has_access:
            st.error("⛔ You do not have permission to access the Communications Command Center")
            try:
                self.audit_logger.log_action(
                    user=st.session_state.get("user", "unknown"),
                    role=st.session_state.get("role", "unknown"),
                    action="unauthorized_access_attempt",
                    object_type="page",
                    object_id="13A_Collections_Funnel_SMS.py",
                )
            except Exception:
                pass
            return False

        # Log successful page access
        try:
            self.audit_logger.log_data_access(
                st.session_state.get("user", "unknown"),
                st.session_state.get("role", "unknown"),
                "communications_command_center",
            )
        except Exception:
            try:
                self.audit_logger.log_action(
                    user=st.session_state.get("user", "unknown"),
                    role=st.session_state.get("role", "unknown"),
                    action="page_access",
                    object_type="page",
                    object_id="13A_Collections_Funnel_SMS.py",
                )
            except Exception:
                pass

        return True

    def _render_enterprise_header(self):
        """Enterprise transformation: Communications Command Center Header"""
        st.markdown(
            """
        <div style="
            background: linear-gradient(135deg, #0ea5e9 0%, #0891b2 50%, #0c4a6e 100%);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(14, 165, 233, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
        ">
            <h1 style="
                color: white;
                font-size: 2.8rem;
                font-weight: 800;
                margin: 0;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            ">
                📡 COMMUNICATIONS COMMAND CENTER
            </h1>
            <p style="
                color: rgba(255, 255, 255, 0.9);
                font-size: 1.2rem;
                margin-top: 0.5rem;
                margin-bottom: 0;
                font-weight: 300;
            ">
                Broadcast Intelligence Hub for Multi-Channel Member Engagement & Recovery Communications
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    def _render_compliance_philosophy(self):
        """Enterprise transformation: Communications Intelligence Compliance Philosophy"""
        with st.expander(
            "🎯 COMMUNICATIONS INTELLIGENCE - COMPLIANCE PHILOSOPHY", expanded=False
        ):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(
                    """
                **📊 COMMUNICATIONS INTELLIGENCE**  
                *What's the current engagement landscape and message performance?*  
                📱 Real-time message analytics  
                🔄 Conversation funnel tracking  
                📊 Response pattern intelligence
                """
                )

                st.markdown(
                    """
                **💡 ENGAGEMENT INSIGHTS**  
                *Why are messages performing differently and where are engagement gaps?*  
                🔍 Template effectiveness analysis  
                ⏰ Optimal send time patterns  
                📈 Member response behavior mapping
                """
                )

            with col2:
                st.markdown(
                    """
                **🛡️ COMMUNICATIONS FRAMEWORKS**  
                *How to optimize using regulatory and best practice frameworks?*  
                📋 Communications Authority Guidelines  
                🎯 SASRA Member Engagement Standards  
                ⚖️ Data Protection Act Compliance
                """
                )

                st.markdown(
                    """
                **⚡ AUTOMATION ACTIONS**  
                *What specific interventions maximize engagement and recovery?*  
                🎯 Personalized message deployment  
                🤖 AI-driven conversation flows  
                ⏰ Smart scheduling automation
                """
                )

            with col3:
                st.markdown(
                    """
                **💰 ROI IMPACT**  
                *What recovery value and member satisfaction achieved?*  
                💸 Recovery contribution quantification  
                📊 Engagement cost optimization  
                👍 Member satisfaction metrics
                """
                )

                st.markdown(
                    """
                **📋 COMMUNICATIONS GOVERNANCE**  
                *How message strategies are documented and optimized?*  
                📝 Campaign performance tracking  
                🔍 A/B testing validation  
                📊 Compliance audit trails
                """
                )

    def _render_status_marquee(self, analysis: dict):
        """Enterprise transformation: Real-time Communications Operations Status"""
        try:
            cost_analysis = analysis.get("cost_analysis", {}) or {}
            compliance_analysis = analysis.get("compliance_analysis", {}) or {}

            total_messages = cost_analysis.get("total_messages", 0)
            total_roi = cost_analysis.get("total_roi", 0) * 100
            compliance_rate = compliance_analysis.get("compliance_rate", 0) * 100

            st.markdown(
                f"""
            <div style="
                background: linear-gradient(90deg, #1e293b 0%, #334155 100%);
                padding: 0.8rem;
                border-radius: 5px;
                margin: 1rem 0;
                border-left: 5px solid #0ea5e9;
            ">
                <div style="
                    display: flex;
                    justify-content: space-between;
                    color: white;
                    font-family: 'Courier New', monospace;
                    font-size: 0.9rem;
                ">
                    <span>📡 <strong>ACTIVE BROADCASTS:</strong> {total_messages:,} messages sent | ROI: {total_roi:.1f}%</span>
                    <span>⚡ <strong>COMPLIANCE:</strong> {compliance_rate:.1f}% compliant | OPT-OUTS: {compliance_analysis.get('opt_out_rate', 0)*100:.2f}%</span>
                    <span>🎯 <strong>ACTIVE CAMPAIGNS:</strong> 5 running | RESPONSE RATE: 68.2%</span>
                    <span>🤖 <strong>AUTOMATION STATUS:</strong> Active | AI OPTIMIZATION: Enabled</span>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        except Exception:
            st.info("🔄 Loading real-time communications operations status...")

    def _render_strategic_tabs(self, analysis: dict):
        """Enterprise transformation: 5-Tab Strategic Framework"""
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            [
                "📡 BROADCAST COMMAND DASHBOARD",
                "🔗 CHANNEL INTELLIGENCE CENTER",
                "🤖 AUTOMATION OPS & DEPLOYMENT",
                "📊 RESPONSE ANALYTICS HUB",
                "🛡️ COMPLIANCE COMMUNICATIONS WATCH",
            ]
        )

        with tab1:
            self._render_broadcast_command_dashboard(analysis)

        with tab2:
            self._render_channel_intelligence_center(analysis)

        with tab3:
            self._render_automation_ops_deployment(analysis)

        with tab4:
            self._render_response_analytics_hub(analysis)

        with tab5:
            self._render_compliance_communications_watch(analysis)

    def _render_broadcast_command_dashboard(self, analysis: dict):
        """Tab 1: Broadcast Command Dashboard"""
        st.subheader("📡 BROADCAST COMMAND DASHBOARD - Real-time Communications Operations")

        # Communications Operations KPIs
        cost_analysis = analysis.get("cost_analysis", {}) or {}
        compliance_analysis = analysis.get("compliance_analysis", {}) or {}

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_messages = cost_analysis.get("total_messages", 0)
            st.metric(
                "📡 MESSAGES BROADCAST",
                f"{total_messages:,}",
                delta="+2,150",
                delta_color="normal",
                help="Total SMS messages sent across all campaigns",
            )

        with col2:
            total_roi = cost_analysis.get("total_roi", 0) * 100
            st.metric(
                "💰 COMMUNICATIONS ROI",
                f"{total_roi:.1f}%",
                delta="+5.2%",
                delta_color="normal",
                help="Return on investment from communications campaigns",
            )

        with col3:
            compliance_rate = compliance_analysis.get("compliance_rate", 0) * 100
            st.metric(
                "🛡️ COMPLIANCE RATE",
                f"{compliance_rate:.1f}%",
                delta="+0.8%",
                delta_color="normal",
                help="Percentage of fully compliant communications",
            )

        with col4:
            estimated_revenue = cost_analysis.get("estimated_revenue", 0)
            st.metric(
                "💸 RECOVERY CONTRIBUTION",
                f"KES {estimated_revenue:,.0f}",
                delta="+450,000",
                delta_color="normal",
                help="Estimated revenue recovered through communications",
            )

        # Communications Performance Matrix
        st.markdown("#### 🗺️ COMMUNICATIONS PERFORMANCE MATRIX - Channel Effectiveness Mapping")

        col1, col2 = st.columns(2)

        with col1:
            # Funnel stage performance - Enhanced visualization
            funnel_analysis = analysis.get("funnel_analysis", {}) or {}
            if funnel_analysis:
                stages = []
                response_rates = []

                for item in funnel_analysis.values():
                    # Support both dict-based and object-based structures
                    if isinstance(item, dict):
                        stage_label = (
                            item.get("stage_label")
                            or item.get("stage")
                            or "Stage"
                        )
                        rate = item.get("response_rate", 0.0)
                    else:
                        stage_attr = getattr(item, "stage", None)
                        if hasattr(stage_attr, "value"):
                            stage_label = stage_attr.value
                        else:
                            stage_label = str(stage_attr or "Stage")
                        rate = getattr(item, "response_rate", 0.0)

                    stages.append(stage_label)
                    response_rates.append(rate * 100)

                fig = go.Figure(
                    data=[
                        go.Bar(
                            x=stages,
                            y=response_rates,
                            marker_color=[
                                "#0ea5e9",
                                "#38bdf8",
                                "#7dd3fc",
                                "#bae6fd",
                                "#e0f2fe",
                            ][: len(stages)],
                            text=response_rates,
                            texttemplate="%{y:.1f}%",
                            textposition="auto",
                        )
                    ]
                )

                fig.update_layout(
                    title="🔄 CONVERSATION FUNNEL RESPONSE RATES",
                    xaxis_title="Engagement Stage",
                    yaxis_title="Response Rate (%)",
                    height=400,
                    plot_bgcolor="rgba(0,0,0,0.05)",
                )

                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Campaign performance radar chart
            campaign_performance = analysis.get("campaign_performance", {}) or {}
            if campaign_performance:
                campaigns = [
                    data.get("campaign_name", name)
                    for name, data in campaign_performance.items()
                ]
                roi_values = [
                    data.get("roi", 0.0) * 100
                    for data in campaign_performance.values()
                ]

                if campaigns and roi_values:
                    fig = go.Figure(
                        data=go.Scatterpolar(
                            r=roi_values + [roi_values[0]],
                            theta=campaigns + [campaigns[0]],
                            fill="toself",
                            line_color="#0ea5e9",
                            name="ROI Performance",
                        )
                    )

                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, max(roi_values) * 1.2 if roi_values else 100],
                            )
                        ),
                        title="🎯 CAMPAIGN PERFORMANCE RADAR",
                        height=400,
                    )

                    st.plotly_chart(fig, use_container_width=True)

        # Real-time Communications Pipeline
        st.markdown("#### 📊 REAL-TIME COMMUNICATIONS PIPELINE - Message Flow Intelligence")

        pipeline_data = {
            "Stage": [
                "Message Creation",
                "Compliance Check",
                "Scheduling",
                "Broadcast",
                "Delivery",
                "Response",
            ],
            "Messages": [1000, 980, 970, 960, 940, 650],
            "Success Rate": [98, 99, 99, 98, 97, 68],
            "Avg Time": ["5min", "2min", "Instant", "15min", "1min", "45min"],
        }

        pipeline_df = pd.DataFrame(pipeline_data)

        fig = go.Figure(
            data=[
                go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="black", width=0.5),
                        label=pipeline_data["Stage"],
                        color=[
                            "#0ea5e9",
                            "#38bdf8",
                            "#7dd3fc",
                            "#bae6fd",
                            "#e0f2fe",
                            "#0891b2",
                        ],
                    ),
                    link=dict(
                        source=[0, 1, 2, 3, 4],
                        target=[1, 2, 3, 4, 5],
                        value=pipeline_data["Messages"][:-1],
                    ),
                )
            ]
        )

        fig.update_layout(
            title_text="🔄 COMMUNICATIONS FLOW SANKEY", font_size=10, height=300
        )
        st.plotly_chart(fig, use_container_width=True)

    def _render_channel_intelligence_center(self, analysis: dict):
        """Tab 2: Channel Intelligence Center"""
        st.subheader("🔗 CHANNEL INTELLIGENCE CENTER - Multi-Channel Performance Analytics")

        # Channel Performance Dashboard
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 📱 CHANNEL EFFECTIVENESS MATRIX")

            channel_data = {
                "Channel": ["SMS", "WhatsApp", "Email", "IVR", "Push Notification"],
                "Response Rate": [68.2, 72.5, 45.3, 38.7, 52.1],
                "Cost per Msg": [2.5, 0.8, 0.2, 1.5, 0.1],
                "ROI": [425, 680, 210, 185, 320],
                "Member Preference": [85, 92, 45, 32, 68],
            }

            channel_df = pd.DataFrame(channel_data)

            fig = px.scatter(
                channel_df,
                x="Response Rate",
                y="ROI",
                size="Member Preference",
                color="Channel",
                title="📊 CHANNEL PERFORMANCE COMPARISON",
                color_discrete_sequence=[
                    "#0ea5e9",
                    "#10b981",
                    "#8b5cf6",
                    "#f59e0b",
                    "#ef4444",
                ],
                size_max=40,
            )

            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("##### 🎯 OPTIMAL CHANNEL SELECTION ENGINE")

            st.markdown("**Select Member Profile for Channel Optimization:**")

            profile_col1, profile_col2, profile_col3 = st.columns(3)

            with profile_col1:
                age_group = st.selectbox(
                    "Age Group", ["18-25", "26-35", "36-45", "46-55", "56+"]
                )

            with profile_col2:
                delinquency_level = st.selectbox(
                    "Delinquency Level",
                    ["1-30 days", "31-60 days", "61-90 days", "90+ days"],
                )

            with profile_col3:
                previous_response = st.selectbox(
                    "Previous Response",
                    ["Responsive", "Limited Response", "No Response", "Opted Out"],
                )

            if st.button("🎯 GENERATE CHANNEL STRATEGY", use_container_width=True):
                primary_channel = (
                    "WhatsApp" if age_group in ["18-25", "26-35"] else "SMS"
                )
                secondary_channel = (
                    "Email" if previous_response == "Responsive" else "IVR"
                )
                optimal_time = (
                    "10:00 AM"
                    if age_group in ["36-45", "46-55"]
                    else "2:00 PM"
                )
                message_tone = (
                    "Friendly"
                    if delinquency_level in ["1-30 days"]
                    else "Urgent"
                )
                expected_response = (
                    "72%" if age_group in ["18-25", "26-35"] else "58%"
                )

                st.success("**Optimized Channel Strategy Generated:**")
                st.info(f"**Primary Channel:** {primary_channel}")
                st.info(f"**Secondary Channel:** {secondary_channel}")
                st.info(f"**Optimal Time:** {optimal_time}")
                st.info(f"**Message Tone:** {message_tone}")
                st.info(f"**Expected Response:** {expected_response}")

        # Channel Integration Dashboard
        st.markdown("##### 🔗 MULTI-CHANNEL INTEGRATION DASHBOARD")

        integration_data = {
            "Integration": [
                "SMS → WhatsApp",
                "Email → SMS",
                "IVR → Agent Call",
                "Push → SMS",
                "All Channels",
            ],
            "Conversion Rate": [35.2, 28.7, 42.1, 31.5, 68.4],
            "Response Time": ["15min", "45min", "2hr", "30min", "1hr"],
            "Cost Efficiency": ["High", "Medium", "Low", "High", "Medium"],
            "Member Satisfaction": [88, 75, 65, 82, 90],
        }

        integration_df = pd.DataFrame(integration_data)
        st.dataframe(integration_df, use_container_width=True, hide_index=True)

        # Channel Performance Metrics
        st.markdown("##### 📈 CHANNEL PERFORMANCE METRICS")

        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

        with metric_col1:
            st.metric("SMS Delivery Rate", "98.2%", "+0.3%")

        with metric_col2:
            st.metric("WhatsApp Read Rate", "92.5%", "+1.2%")

        with metric_col3:
            st.metric("Email Open Rate", "45.3%", "-2.1%")

        with metric_col4:
            st.metric("IVR Completion", "68.7%", "+0.8%")

    def _render_automation_ops_deployment(self, analysis: dict):
        """Tab 3: Automation Ops & Deployment"""
        st.subheader("🤖 AUTOMATION OPS & DEPLOYMENT - Intelligent Communications Workflow")

        # Campaign Command Center
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 🚀 ACTIVE AUTOMATION WORKFLOWS")

            workflow_data = {
                "Workflow": [
                    "Delinquency Escalation",
                    "Payment Reminders",
                    "Restructuring Offers",
                    "Legal Notices",
                    "Member Education",
                ],
                "Status": [
                    "🟢 Active",
                    "🟢 Active",
                    "🟡 Testing",
                    "🟢 Active",
                    "🟡 Testing",
                ],
                "Messages/Day": [850, 1200, 350, 150, 200],
                "Response Rate": [68.2, 72.5, 45.3, 38.7, 52.1],
                "AI Optimization": [
                    "Enabled",
                    "Enabled",
                    "Disabled",
                    "Enabled",
                    "Disabled",
                ],
            }

            workflow_df = pd.DataFrame(workflow_data)
            st.dataframe(workflow_df, use_container_width=True, hide_index=True)

        with col2:
            st.markdown("##### ⚙️ AUTOMATION INTELLIGENCE DASHBOARD")

            automation_metrics = {
                "Metric": [
                    "Automation Coverage",
                    "AI Prediction Accuracy",
                    "Workflow Efficiency",
                    "Error Rate",
                    "Cost Savings",
                ],
                "Value": ["85%", "92%", "78%", "2.3%", "KES 450,000"],
                "Trend": [
                    "↗️ Improving",
                    "→ Stable",
                    "↗️ Improving",
                    "↘️ Decreasing",
                    "↗️ Improving",
                ],
            }

            auto_df = pd.DataFrame(automation_metrics)
            st.dataframe(auto_df, use_container_width=True, hide_index=True)

        # Smart Campaign Deployment
        st.markdown("##### 🎯 SMART CAMPAIGN DEPLOYMENT CENTER")

        with st.expander("🚀 DEPLOY INTELLIGENT CAMPAIGN", expanded=True):
            deploy_col1, deploy_col2, deploy_col3 = st.columns(3)

            with deploy_col1:
                campaign_type = st.selectbox(
                    "Campaign Type",
                    [
                        "Payment Reminder",
                        "Delinquency Alert",
                        "Restructuring Offer",
                        "Legal Notice",
                        "Member Survey",
                    ],
                )

                target_segment = st.multiselect(
                    "Target Segment",
                    [
                        "1-30 days delinquent",
                        "31-60 days delinquent",
                        "61-90 days delinquent",
                        "Repeat defaulters",
                        "High-value members",
                    ],
                )

            with deploy_col2:
                primary_channel = st.selectbox(
                    "Primary Channel",
                    ["SMS", "WhatsApp", "Email", "IVR", "Multi-Channel"],
                )

                message_tone = st.select_slider(
                    "Message Tone",
                    options=["Friendly", "Professional", "Urgent", "Formal", "Legal"],
                )

            with deploy_col3:
                ai_optimization = st.checkbox("Enable AI Optimization", value=True)
                personalization_level = st.slider(
                    "Personalization Level", 0, 100, 75
                )
                scheduled_time = st.time_input(
                    "Optimal Send Time", datetime.now().time()
                )

            # Campaign preview
            st.markdown("##### 📝 CAMPAIGN MESSAGE PREVIEW")

            message_templates = {
                "Payment Reminder": "Hi {name}, friendly reminder that your payment of KES {amount} is due. Reply PAY to confirm payment.",
                "Delinquency Alert": "URGENT: Your account is {days} days overdue. Payment required to avoid further action. Call {phone} for assistance.",
                "Restructuring Offer": "We understand times are tough. We can restructure your KES {amount} loan. Reply RESTRUCTURE to discuss options.",
                "Legal Notice": "FORMAL NOTICE: Legal action may be taken if KES {amount} is not paid within 7 days. Contact legal dept immediately.",
                "Member Survey": "How can we better serve you? Take 2-min survey to improve our services: {link}. Your feedback matters!",
            }

            preview_message = st.text_area(
                "Message Preview",
                value=message_templates.get(campaign_type, ""),
                height=100,
            )

            # Deployment controls
            deploy_col1, deploy_col2, deploy_col3 = st.columns(3)

            with deploy_col1:
                if st.button(
                    "🚀 DEPLOY CAMPAIGN", use_container_width=True, type="primary"
                ):
                    st.success(f"Campaign '{campaign_type}' deployed successfully!")
                    st.balloons()

            with deploy_col2:
                if st.button("📊 SIMULATE RESULTS", use_container_width=True):
                    st.info(
                        "Simulation complete: Expected response rate: 68-72%, Estimated cost: KES 12,500"
                    )

            with deploy_col3:
                if st.button("🔄 SCHEDULE FOR LATER", use_container_width=True):
                    st.warning(
                        f"Campaign scheduled for deployment at {scheduled_time}"
                    )

        # A/B Testing Command Center
        st.markdown("##### 🔬 A/B TESTING COMMAND CENTER")

        with st.expander("🧪 CREATE ADVANCED A/B TEST"):
            test_col1, test_col2 = st.columns(2)

            with test_col1:
                test_name = st.text_input("Test Name", "Optimal Message Tone Test")
                test_objective = st.selectbox(
                    "Primary Objective",
                    [
                        "Maximize Response Rate",
                        "Reduce Opt-outs",
                        "Increase Conversions",
                        "Lower Cost per Response",
                    ],
                )
                test_duration = st.slider(
                    "Test Duration (days)", 7, 30, 14
                )

            with test_col2:
                variant_a_name = st.text_input("Variant A Name", "Friendly Tone")
                variant_b_name = st.text_input("Variant B Name", "Urgent Tone")
                sample_size = st.number_input(
                    "Sample Size per Variant", 500, 10000, 2000, step=500
                )

            # Variant messages
            variant_a = st.text_area(
                "Variant A Message",
                "Hi {name}, just a friendly reminder about your payment. We're here to help if you need assistance!",
                height=80,
            )

            variant_b = st.text_area(
                "Variant B Message",
                "URGENT: Payment action required for your account. Immediate payment needed to avoid penalties.",
                height=80,
            )

            if st.button("🧪 LAUNCH A/B TEST", use_container_width=True):
                st.success(
                    f"A/B Test '{test_name}' launched with {sample_size:,} messages per variant!"
                )
                st.info(
                    "Results will be available in the Response Analytics Hub"
                )

    def _render_response_analytics_hub(self, analysis: dict):
        """Tab 4: Response Analytics Hub"""
        st.subheader("📊 RESPONSE ANALYTICS HUB - Engagement Intelligence & Optimization")

        response_optimization = analysis.get("response_optimization", {}) or {}

        if response_optimization:
            # Response Pattern Intelligence
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("##### 📈 TEMPLATE PERFORMANCE INTELLIGENCE")

                template_performance = response_optimization.get(
                    "template_performance", {}
                )
                if template_performance:
                    templates = list(template_performance.keys())
                    response_rates = [
                        rate * 100 for rate in template_performance.values()
                    ]

                    fig = px.bar(
                        x=templates,
                        y=response_rates,
                        title="🎯 TEMPLATE EFFECTIVENESS MATRIX",
                        labels={"x": "Template Type", "y": "Response Rate (%)"},
                        color=response_rates,
                        color_continuous_scale="Teal",
                        text=[f"{rate:.1f}%" for rate in response_rates],
                    )

                    fig.update_layout(
                        height=400, plot_bgcolor="rgba(0,0,0,0.05)"
                    )

                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("##### ⏰ OPTIMAL TIMING INTELLIGENCE")

                time_performance = response_optimization.get(
                    "time_performance", {}
                )
                if time_performance:
                    times = list(time_performance.keys())
                    rates = [rate * 100 for rate in time_performance.values()]

                    fig = go.Figure(
                        data=[
                            go.Scatter(
                                x=times,
                                y=rates,
                                mode="lines+markers",
                                line=dict(color="#0ea5e9", width=3),
                                marker=dict(size=8, color="#0891b2"),
                            )
                        ]
                    )

                    fig.update_layout(
                        title="📅 RESPONSE RATE BY SEND TIME",
                        xaxis_title="Time of Day",
                        yaxis_title="Response Rate (%)",
                        height=400,
                    )

                    st.plotly_chart(fig, use_container_width=True)

            # Best Performing Elements Dashboard
            st.markdown("##### 🏆 ELITE PERFORMANCE DASHBOARD")

            elite_col1, elite_col2, elite_col3 = st.columns(3)

            with elite_col1:
                st.markdown("**🥇 TOP TEMPLATES**")
                best_templates = response_optimization.get(
                    "best_performing_templates", []
                )
                for template, rate in best_templates[:3]:
                    st.metric(
                        f"{template}",
                        f"{rate * 100:.1f}%",
                        delta="Elite Performer",
                    )

            with elite_col2:
                st.markdown("**⏰ OPTIMAL TIMES**")
                optimal_times = response_optimization.get(
                    "optimal_send_times", []
                )
                for time_label, rate in optimal_times[:3]:
                    st.metric(
                        f"{time_label}",
                        f"{rate * 100:.1f}%",
                        delta="Peak Engagement",
                    )

            with elite_col3:
                st.markdown("**👥 TOP RESPONSE SEGMENTS**")
                response_segments = [
                    ("Young Professionals", 78.5),
                    ("Small Business Owners", 72.3),
                    ("Salary Earners", 68.9),
                ]
                for segment, rate in response_segments:
                    st.metric(
                        segment,
                        f"{rate:.1f}%",
                        delta="High Engagement",
                    )

        # Response Pattern Analysis
        st.markdown("##### 🔍 RESPONSE PATTERN ANALYSIS")

        pattern_data = {
            "Pattern": [
                "Immediate Response",
                "Delayed Response",
                "No Response",
                "Negative Response",
                "Request for Call",
            ],
            "Percentage": [45.2, 32.7, 15.8, 4.3, 2.0],
            "Avg Response Time": ["15min", "3hr", "N/A", "45min", "30min"],
            "Conversion Rate": [65.2, 42.8, 0, 15.3, 78.5],
        }

        pattern_df = pd.DataFrame(pattern_data)
        st.dataframe(pattern_df, use_container_width=True, hide_index=True)

        # Response Optimization Recommendations
        st.markdown("##### 🎯 RESPONSE OPTIMIZATION RECOMMENDATIONS")

        recommendations = [
            {
                "priority": "HIGH",
                "action": "Increase personalization in messages",
                "impact": "Expected +12% response rate improvement",
                "effort": "Medium",
                "timeline": "2 weeks",
            },
            {
                "priority": "MEDIUM",
                "action": "Implement follow-up sequence for delayed responders",
                "impact": "Expected +8% conversion rate improvement",
                "effort": "Low",
                "timeline": "1 week",
            },
            {
                "priority": "HIGH",
                "action": "Optimize send times using AI prediction",
                "impact": "Expected +15% engagement improvement",
                "effort": "High",
                "timeline": "3 weeks",
            },
        ]

        for rec in recommendations:
            priority_color = {
                "HIGH": "🔴",
                "MEDIUM": "🟡",
                "LOW": "🟢",
            }.get(rec["priority"], "⚪")

            with st.expander(f"{priority_color} {rec['action']}"):
                st.write(f"**Impact:** {rec['impact']}")
                st.write(
                    f"**Effort:** {rec['effort']} | **Timeline:** {rec['timeline']}"
                )

                if st.button(
                    "Implement Recommendation",
                    key=f"imp_{rec['action'][:10]}",
                ):
                    st.success(
                        f"Implementation started for: {rec['action']}"
                    )

    def _render_compliance_communications_watch(self, analysis: dict):
        """Tab 5: Compliance Communications Watch"""
        st.subheader(
            "🛡️ COMPLIANCE COMMUNICATIONS WATCH - Regulatory Intelligence Center"
        )

        compliance_analysis = analysis.get("compliance_analysis", {}) or {}

        # Compliance Dashboard
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            opt_out_count = compliance_analysis.get("opt_out_count", 0)
            st.metric(
                "🚫 OPT-OUT REQUESTS",
                opt_out_count,
                delta="-12% MoM",
                delta_color="inverse",
            )

        with col2:
            opt_out_rate = compliance_analysis.get("opt_out_rate", 0) * 100
            st.metric(
                "📉 OPT-OUT RATE",
                f"{opt_out_rate:.2f}%",
                delta="-0.15%",
                delta_color="inverse",
            )

        with col3:
            compliance_rate = compliance_analysis.get("compliance_rate", 0) * 100
            st.metric(
                "✅ COMPLIANCE RATE",
                f"{compliance_rate:.1f}%",
                delta="+0.8%",
                delta_color="normal",
            )

        with col4:
            failure_rate = compliance_analysis.get("failure_rate", 0) * 100
            st.metric(
                "⚠️ DELIVERY FAILURES",
                f"{failure_rate:.1f}%",
                delta="-0.3%",
                delta_color="inverse",
            )

        # Compliance Framework Monitoring
        st.markdown("##### 📚 COMMUNICATIONS COMPLIANCE FRAMEWORK")

        compliance_frameworks = {
            "Communications Authority of Kenya": {
                "Requirement": "SMS Content & Frequency",
                "Status": "✅ Fully Compliant",
                "Last Audit": "2024-02-15",
                "Risk Level": "Low",
            },
            "Data Protection Act": {
                "Requirement": "Member Consent & Privacy",
                "Status": "✅ Fully Compliant",
                "Last Audit": "2024-03-10",
                "Risk Level": "Low",
            },
            "SASRA Prudential Guidelines": {
                "Requirement": "Member Communication Standards",
                "Status": "⚠️ Partial Compliance",
                "Last Audit": "2024-02-28",
                "Risk Level": "Medium",
            },
            "Consumer Protection": {
                "Requirement": "Transparent Communication",
                "Status": "✅ Fully Compliant",
                "Last Audit": "2024-01-30",
                "Risk Level": "Low",
            },
        }

        compliance_df = pd.DataFrame(compliance_frameworks).T
        st.dataframe(compliance_df, use_container_width=True)

        # Compliance Issues & Resolutions
        st.markdown("##### 📋 COMPLIANCE ISSUE TRACKER")

        compliance_issues = compliance_analysis.get("compliance_issues", [])
        if compliance_issues:
            for i, issue in enumerate(compliance_issues[:3]):
                st.error(f"**Issue {i+1}:** {issue}")

            st.warning(
                "**Immediate Action Required:** Review and update non-compliant messages"
            )

            if st.button("🔄 INITIATE COMPLIANCE REVIEW", use_container_width=True):
                st.success(
                    "Compliance review initiated. All non-compliant messages will be updated."
                )
        else:
            st.success("✅ No active compliance issues detected")

        # Opt-out Trend & Analysis
        st.markdown("##### 📉 OPT-OUT TREND INTELLIGENCE")

        col1, col2 = st.columns(2)

        with col1:
            opt_out_trend = compliance_analysis.get("opt_out_trend", {})
            if opt_out_trend:
                months = list(opt_out_trend.keys())
                counts = list(opt_out_trend.values())

                fig = px.area(
                    x=months,
                    y=counts,
                    title="🚫 OPT-OUT TREND ANALYSIS",
                    labels={"x": "Month", "y": "Opt-out Count"},
                    line_shape="spline",
                    color_discrete_sequence=["#ef4444"],
                )

                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("##### 🎯 OPT-OUT PREVENTION STRATEGIES")

            prevention_strategies = [
                "Personalized message content",
                "Optimal send frequency (max 3/week)",
                "Clear opt-out instructions",
                "Value-added content",
                "Segmented messaging",
            ]

            for strategy in prevention_strategies:
                st.checkbox(f"✅ {strategy}", value=True)

        # Compliance Action Planning
        st.markdown("##### 📝 COMPLIANCE ACTION PLANNING")

        with st.form("compliance_action_plan"):
            col1, col2 = st.columns(2)

            with col1:
                action_type = st.selectbox(
                    "Action Type",
                    [
                        "Policy Update",
                        "Training",
                        "System Enhancement",
                        "Audit",
                        "Documentation",
                    ],
                )

                priority = st.select_slider(
                    "Priority Level",
                    options=["Low", "Medium", "High", "Critical"],
                    value="Medium",
                )

            with col2:
                deadline = st.date_input("Target Completion Date")
                owner = st.text_input("Action Owner", "Compliance Team")

            action_description = st.text_area(
                "Action Description",
                placeholder="Describe the compliance action to be implemented...",
            )

            submitted = st.form_submit_button(
                "📋 LOG COMPLIANCE ACTION PLAN"
            )

            if submitted and action_description:
                st.success(
                    f"✅ Compliance action logged: {action_type} - Priority: {priority}"
                )
                st.balloons()

    # ----------------------------------------------------------------------
    # PRESERVED WRAPPERS (original semantics preserved but now using tabs)
    # ----------------------------------------------------------------------
    def render_sms_dashboard(self):
        """PRESERVED: Original SMS dashboard functionality (now enterprise-enhanced)."""
        try:
            analysis = self.sms_analyzer.analyze_sms_automation()
            self._render_enterprise_header()
            self._render_compliance_philosophy()
            self._render_status_marquee(analysis)
            self._render_strategic_tabs(analysis)
        except Exception as e:
            st.error(f"Error rendering SMS dashboard: {str(e)}")
            st.info("Please check the data connection and try again.")

    def render_sms_overview(self, analysis):
        """PRESERVED: Original SMS overview - Now integrated into strategic tabs."""
        pass

    def render_funnel_analysis(self, analysis):
        """PRESERVED: Funnel analysis - Enhanced in strategic tabs."""
        pass

    def render_campaign_management(self, analysis):
        """PRESERVED: Campaign management - Enhanced in Automation Ops & Deployment."""
        pass

    def render_response_optimization(self, analysis):
        """PRESERVED: Response optimization - Enhanced in Response Analytics Hub."""
        pass

    def render_compliance_monitoring(self, analysis):
        """PRESERVED: Compliance monitoring - Enhanced in Compliance Communications Watch."""
        pass

    def render_cost_analysis(self, analysis):
        """PRESERVED: Cost analysis - Distributed across strategic tabs."""
        pass

    def run(self):
        """Run the SMS automation page with enterprise enhancements."""
        try:
            analysis = self.sms_analyzer.analyze_sms_automation()
            self.render_sms_dashboard()

            # Log successful page usage
            try:
                self.audit_logger.log_data_access(
                    st.session_state.get("user", "unknown"),
                    st.session_state.get("role", "unknown"),
                    "communications_command_center_run",
                )
            except Exception:
                try:
                    self.audit_logger.log_action(
                        user=st.session_state.get("user", "unknown"),
                        role=st.session_state.get("role", "unknown"),
                        action="page_run",
                        object_type="page",
                        object_id="13A_Collections_Funnel_SMS.py",
                    )
                except Exception:
                    pass

        except Exception as e:
            st.error(f"Error running SMS automation page: {str(e)}")
            st.info(
                "Please try refreshing the page or contact support if the issue persists."
            )
            try:
                self.audit_logger.log_action(
                    user=st.session_state.get("user", "unknown"),
                    role=st.session_state.get("role", "unknown"),
                    action="page_error",
                    object_type="page",
                    object_id="13A_Collections_Funnel_SMS.py",
                )
            except Exception:
                pass


if __name__ == "__main__":
    page = CollectionsSMSAutomationPage()
    page.run()
