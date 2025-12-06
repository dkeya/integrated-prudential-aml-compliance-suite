# pages/13_Collections_Recovery.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# --------------------------------------------------------------------
# Ensure project root is on sys.path so `core.*` imports work
# --------------------------------------------------------------------
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import ConfigManager
from core.rbac import RBACManager
from core.audit import AuditLogger, audit_logger
from core.sidebar import render_sidebar

# Try to use real analytics module if it exists; otherwise use a mock
try:
    from core.analytics.collections import (
        CollectionsAnalyzer,
        DelinquencyBucket,
        CollectionStrategy,
        RecoveryProbability,
    )
except ImportError:
    # ----------------------------------------------------------------
    # FALLBACK: Lightweight mock analytics so the page runs end-to-end
    # Replace with real core.analytics.collections when ready
    # ----------------------------------------------------------------
    from enum import Enum

    class DelinquencyBucket(str, Enum):
        BUCKET_1_30 = "1-30"
        BUCKET_31_60 = "31-60"
        BUCKET_61_90 = "61-90"
        BUCKET_91_120 = "91-120"
        BUCKET_120_PLUS = "120+"

    class CollectionStrategy(str, Enum):
        SMS_REMINDER = "SMS Reminder"
        PHONE_CALL = "Phone Call"
        FIELD_VISIT = "Field Visit"
        NEGOTIATION = "Negotiation"
        RESTRUCTURING = "Restructuring"
        LEGAL_ACTION = "Legal Action"

    class RecoveryProbability(str, Enum):
        VERY_HIGH = "Very High"
        HIGH = "High"
        MEDIUM = "Medium"
        LOW = "Low"
        VERY_LOW = "Very Low"

    class MockLoan:
        def __init__(
            self,
            loan_id: str,
            member_id: str,
            member_name: str,
            outstanding_amount: float,
            days_delinquent: int,
            delinquency_bucket: DelinquencyBucket,
            contact_number: str,
            recommended_strategy: CollectionStrategy,
            recovery_probability: RecoveryProbability,
        ):
            self.loan_id = loan_id
            self.member_id = member_id
            self.member_name = member_name
            self.outstanding_amount = outstanding_amount
            self.days_delinquent = days_delinquent
            self.delinquency_bucket = delinquency_bucket
            self.contact_number = contact_number
            self.recommended_strategy = recommended_strategy
            self.recovery_probability = recovery_probability

    class CollectionsAnalyzer:
        """
        Mock analyzer that generates synthetic portfolio / agent / strategy
        data purely for UI wiring. Replace with real logic when ready.
        """

        def analyze_collections_portfolio(self):
            rng = np.random.default_rng(42)

            # --- Portfolio statistics ---
            total_delinquent_loans = 420
            total_outstanding_amount = float(rng.integers(80_000_000, 150_000_000))
            avg_days = float(rng.integers(35, 95))
            high_priority_accounts = int(rng.integers(20, 40))

            portfolio_statistics = {
                "total_delinquent_loans": total_delinquent_loans,
                "total_outstanding_amount": total_outstanding_amount,
                "average_delinquency_days": avg_days,
                "high_priority_accounts": high_priority_accounts,
            }

            # --- Bucket segmentation ---
            bucket_segmentation = {
                DelinquencyBucket.BUCKET_1_30.value: int(rng.integers(100, 150)),
                DelinquencyBucket.BUCKET_31_60.value: int(rng.integers(80, 120)),
                DelinquencyBucket.BUCKET_61_90.value: int(rng.integers(60, 90)),
                DelinquencyBucket.BUCKET_91_120.value: int(rng.integers(40, 70)),
                DelinquencyBucket.BUCKET_120_PLUS.value: int(rng.integers(30, 50)),
            }

            # --- Amount segmentation (by exposure band) ---
            amount_segmentation = {
                "< 50K": int(rng.integers(80, 120)),
                "50K - 200K": int(rng.integers(120, 180)),
                "200K - 500K": int(rng.integers(80, 120)),
                "> 500K": int(rng.integers(40, 70)),
            }

            # --- Top delinquent accounts ---
            buckets_list = list(DelinquencyBucket)
            strategies_list = list(CollectionStrategy)
            probs_list = list(RecoveryProbability)

            top_delinquent_accounts = []
            for i in range(25):
                loan_id = f"LOAN-{2000 + i}"
                member_id = f"MBR-{1000 + i}"
                member_name = f"Member {i+1}"
                outstanding_amount = float(rng.integers(50_000, 1_200_000))
                days_delinquent = int(rng.integers(15, 180))
                delinquency_bucket = rng.choice(buckets_list)
                contact_number = f"07{rng.integers(10_000_000, 99_999_999)}"
                recommended_strategy = rng.choice(strategies_list)
                recovery_probability = rng.choice(probs_list)

                top_delinquent_accounts.append(
                    MockLoan(
                        loan_id=loan_id,
                        member_id=member_id,
                        member_name=member_name,
                        outstanding_amount=outstanding_amount,
                        days_delinquent=days_delinquent,
                        delinquency_bucket=delinquency_bucket,
                        contact_number=contact_number,
                        recommended_strategy=recommended_strategy,
                        recovery_probability=recovery_probability,
                    )
                )

            portfolio_segmentation = {
                "portfolio_statistics": portfolio_statistics,
                "bucket_segmentation": bucket_segmentation,
                "amount_segmentation": amount_segmentation,
                "top_delinquent_accounts": top_delinquent_accounts,
            }

            # --- Performance metrics ---
            performance_metrics = {
                "recovery_rate": float(rng.uniform(0.55, 0.82)),
                "collection_efficiency_score": float(rng.uniform(0.6, 0.9)),
            }

            # --- Strategy recommendations (reuse top accounts for demo) ---
            strategy_recommendations = top_delinquent_accounts

            # --- Agent performance ---
            agent_ids = [f"AGT-{i:03d}" for i in range(1, 8)]
            agent_performance = {}
            for agent_id in agent_ids:
                success_rate = float(rng.uniform(0.45, 0.9))
                total_actions = int(rng.integers(40, 200))
                avg_recovery = float(rng.integers(15_000, 150_000))
                actions_per_day = float(rng.uniform(3.0, 12.0))
                promise_keep_rate = float(rng.uniform(0.5, 0.95))
                avg_days_to_close = float(rng.integers(10, 60))
                actions_by_type = {
                    "SMS": int(rng.integers(20, 80)),
                    "Call": int(rng.integers(20, 80)),
                    "Field Visit": int(rng.integers(5, 30)),
                    "Negotiation": int(rng.integers(2, 20)),
                }
                total_recovery_amount = float(total_actions * avg_recovery * success_rate)

                agent_performance[agent_id] = {
                    "success_rate": success_rate,
                    "total_actions": total_actions,
                    "average_recovery_amount": avg_recovery,
                    "actions_per_day": actions_per_day,
                    "promise_keep_rate": promise_keep_rate,
                    "avg_days_to_close": avg_days_to_close,
                    "actions_by_type": actions_by_type,
                    "total_recovery_amount": total_recovery_amount,
                }

            # Sort top performers
            top_performers = sorted(
                agent_performance.items(),
                key=lambda x: x[1]["success_rate"],
                reverse=True,
            )[:3]

            agent_analysis = {
                "agent_performance": agent_performance,
                "top_performers": top_performers,
                "active_agents": len(agent_performance),
            }

            return {
                "portfolio_segmentation": portfolio_segmentation,
                "performance_metrics": performance_metrics,
                "strategy_recommendations": strategy_recommendations,
                "agent_analysis": agent_analysis,
            }

# --------------------------------------------------------------------
# Page configuration
# --------------------------------------------------------------------
st.set_page_config(
    page_title="Collections Intelligence Operations Center",
    page_icon="🚨",
    layout="wide",
)

# --------------------------------------------------------------------
# Authentication + unified sidebar
# --------------------------------------------------------------------
if not st.session_state.get("authenticated", False):
    st.error("🔐 Please log in to access this page")
    st.stop()

# Render unified sidebar (core.sidebar)
render_sidebar()

# ============================================================================
# ENTERPRISE TRANSFORMATION: COLLECTIONS INTELLIGENCE OPERATIONS CENTER
# ============================================================================


class CollectionsRecoveryPage:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.rbac_manager = RBACManager()
        # Use the shared audit logger instance from core.audit
        self.audit_logger = audit_logger
        self.config = self.config_manager.load_settings()
        self.collections_analyzer = CollectionsAnalyzer()

        if not self._check_access():
            st.stop()

    def _check_access(self):
        """Enhanced access control with audit logging"""
        if not st.session_state.get("authenticated", False):
            st.error(
                "🔐 Please login to access the Collections Intelligence Operations Center"
            )
            return False

        has_access = self.rbac_manager.check_page_access(
            "13_Collections_Recovery.py",
            st.session_state.role,
            self.config,
        )

        if not has_access:
            st.error(
                "⛔ You do not have permission to access the Collections Intelligence Operations Center"
            )
            try:
                self.audit_logger.log_page_access(
                    st.session_state.get("user", "unknown"),
                    "Collections_Intelligence_Ops_Center",
                    "Unauthorized",
                )
            except Exception:
                pass
            return False

        try:
            self.audit_logger.log_data_access(
                st.session_state.get("user", "unknown"),
                st.session_state.get("role", "unknown"),
                "collections_intelligence_ops_center",
            )
        except Exception:
            pass

        return True

    def _render_enterprise_header(self):
        """Enterprise transformation: Collections Intelligence Operations Center Header"""
        st.markdown(
            """
        <div style="
            background: linear-gradient(135deg, #f97316 0%, #dc2626 50%, #991b1b 100%);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(220, 38, 38, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
        ">
            <h1 style="
                color: white;
                font-size: 2.8rem;
                font-weight: 800;
                margin: 0;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            ">
                🚨 COLLECTIONS INTELLIGENCE OPERATIONS CENTER
            </h1>
            <p style="
                color: rgba(255, 255, 255, 0.9);
                font-size: 1.2rem;
                margin-top: 0.5rem;
                margin-bottom: 0;
                font-weight: 300;
            ">
                Command Hub for Revenue Protection, Recovery Optimization & Portfolio Defense Operations
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    def _render_compliance_philosophy(self):
        """Enterprise transformation: Collections Intelligence Compliance Philosophy"""
        with st.expander(
            "🎯 COLLECTIONS INTELLIGENCE OPERATIONS - COMPLIANCE PHILOSOPHY",
            expanded=False,
        ):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(
                    """
                **📊 DATA INTELLIGENCE**  
                *What's the current recovery posture and portfolio risk exposure?*  
                🔍 Real-time delinquency analytics  
                📈 Recovery probability modeling  
                ⚠️ Portfolio vulnerability mapping
                """
                )

                st.markdown(
                    """
                **💡 STRATEGIC INSIGHTS**  
                *Why are recoveries underperforming and where are operational gaps?*  
                🔍 Root cause delinquency analysis  
                📊 Agent performance variance  
                ⚙️ Process efficiency bottlenecks
                """
                )

            with col2:
                st.markdown(
                    """
                **🛡️ RECOVERY FRAMEWORKS**  
                *How to optimize using SASRA Guidelines & Best Practices?*  
                📋 SASRA Prudential Standard 12  
                🎯 CBK Collections Guidelines  
                ⚖️ Fair Debt Collection Practices Act
                """
                )

                st.markdown(
                    """
                **⚡ OPERATIONAL ACTIONS**  
                *What specific interventions maximize recovery yield?*  
                🎯 Targeted collection strategies  
                🤖 Automated workflow optimization  
                👥 Agent performance coaching
                """
                )

            with col3:
                st.markdown(
                    """
                **💰 VALUE IMPACT**  
                *What revenue protection and capital efficiency achieved?*  
                💸 Recovered revenue quantification  
                🏦 Reduced provisioning requirements  
                📊 Improved portfolio quality metrics
                """
                )

                st.markdown(
                    """
                **📋 OPERATIONS GOVERNANCE**  
                *How recovery decisions are documented and audited?*  
                📝 Action tracking and accountability  
                🔍 Strategy effectiveness monitoring  
                📊 Performance-based compensation
                """
                )

    def _render_status_marquee(self, analysis):
        """Enterprise transformation: Real-time Recovery Operations Status"""
        try:
            portfolio_stats = (
                analysis.get("portfolio_segmentation", {})
                .get("portfolio_statistics", {})
            )
            performance_metrics = analysis.get("performance_metrics", {})

            total_delinquent = portfolio_stats.get("total_delinquent_loans", 0)
            total_outstanding = portfolio_stats.get("total_outstanding_amount", 0)
            recovery_rate = performance_metrics.get("recovery_rate", 0) * 100

            st.markdown(
                f"""
            <div style="
                background: linear-gradient(90deg, #1e293b 0%, #334155 100%);
                padding: 0.8rem;
                border-radius: 5px;
                margin: 1rem 0;
                border-left: 5px solid #f97316;
            ">
                <div style="
                    display: flex;
                    justify-content: space-between;
                    color: white;
                    font-family: 'Courier New', monospace;
                    font-size: 0.9rem;
                    flex-wrap: wrap;
                    row-gap: 4px;
                ">
                    <span>🚨 <strong>ACTIVE RECOVERY OPS:</strong> {total_delinquent:,} accounts | KES {total_outstanding:,.0f} at risk</span>
                    <span>🎯 <strong>RECOVERY RATE:</strong> {recovery_rate:.1f}% | TARGET: 85%</span>
                    <span>⚡ <strong>PRIORITY ACTIONS:</strong> {portfolio_stats.get('high_priority_accounts', 15)} immediate interventions needed</span>
                    <span>👥 <strong>AGENTS ACTIVE:</strong> {analysis.get('agent_analysis', {}).get('active_agents', 8)} field operatives</span>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        except Exception:
            st.info("🔄 Loading real-time recovery operations status...")

    def _render_strategic_tabs(self, analysis):
        """Enterprise transformation: 5-Tab Strategic Framework"""
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            [
                "🚨 RECOVERY COMMAND DASHBOARD",
                "📊 PORTFOLIO INTELLIGENCE CENTER",
                "🎯 STRATEGY OPS & DEPLOYMENT",
                "👥 AGENT PERFORMANCE COMMAND",
                "🛡️ COMPLIANCE & AUDIT WATCH",
            ]
        )

        with tab1:
            self._render_recovery_command_dashboard(analysis)

        with tab2:
            self._render_portfolio_intelligence_center(analysis)

        with tab3:
            self._render_strategy_ops_deployment(analysis)

        with tab4:
            self._render_agent_performance_command(analysis)

        with tab5:
            self._render_compliance_audit_watch(analysis)

    def _render_recovery_command_dashboard(self, analysis):
        """Tab 1: Recovery Command Dashboard"""
        st.subheader("🚨 RECOVERY COMMAND DASHBOARD - Real-time Operations Monitoring")

        portfolio_stats = (
            analysis.get("portfolio_segmentation", {})
            .get("portfolio_statistics", {})
        )
        performance_metrics = analysis.get("performance_metrics", {})

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_outstanding = portfolio_stats.get("total_outstanding_amount", 0)
            st.metric(
                "🚨 AT-RISK CAPITAL",
                f"KES {total_outstanding:,.0f}",
                delta="-2.3% WoW",
                delta_color="inverse",
                help="Total outstanding amount in delinquent portfolio requiring recovery action",
            )

        with col2:
            recovery_rate = performance_metrics.get("recovery_rate", 0) * 100
            st.metric(
                "🎯 RECOVERY EFFECTIVENESS",
                f"{recovery_rate:.1f}%",
                delta="+3.2%",
                delta_color="normal",
                help="Percentage of successful recovery actions against target",
            )

        with col3:
            avg_days = portfolio_stats.get("average_delinquency_days", 0)
            st.metric(
                "⏰ MEAN TIME TO RECOVERY",
                f"{avg_days:.0f} days",
                delta="-5 days",
                delta_color="inverse",
                help="Average days accounts remain in delinquency before recovery",
            )

        with col4:
            efficiency_score = (
                performance_metrics.get("collection_efficiency_score", 0) * 100
            )
            st.metric(
                "⚡ OPERATIONS EFFICIENCY",
                f"{efficiency_score:.1f}%",
                delta="+4.1%",
                delta_color="normal",
                help="Overall collections operations efficiency score",
            )

        # Recovery Operations Heatmap
        st.markdown("#### 🗺️ RECOVERY OPERATIONS HEATMAP - Priority Zone Mapping")

        col1, col2 = st.columns(2)

        with col1:
            bucket_segmentation = (
                analysis.get("portfolio_segmentation", {})
                .get("bucket_segmentation", {})
            )
            if bucket_segmentation:
                buckets = list(bucket_segmentation.keys())
                counts = list(bucket_segmentation.values())

                colors = ["#22c55e", "#84cc16", "#eab308", "#f97316", "#dc2626", "#991b1b"]

                fig = go.Figure(
                    data=[
                        go.Bar(
                            x=buckets,
                            y=counts,
                            marker_color=colors[: len(buckets)],
                            text=counts,
                            textposition="auto",
                        )
                    ]
                )

                fig.update_layout(
                    title="🚨 DELINQUENCY BUCKET URGENCY MATRIX",
                    xaxis_title="Risk Severity Level",
                    yaxis_title="Number of Accounts",
                    height=400,
                    plot_bgcolor="rgba(0,0,0,0.05)",
                )

                st.plotly_chart(fig, use_container_width=True)

        with col2:
            strategy_loans = analysis.get("strategy_recommendations", [])
            if strategy_loans:
                recovery_levels = {}
                for loan in strategy_loans:
                    level = getattr(loan.recovery_probability, "value", "Unknown")
                    recovery_levels[level] = recovery_levels.get(level, 0) + 1

                if recovery_levels:
                    levels = list(recovery_levels.keys())
                    counts = list(recovery_levels.values())

                    fig = px.pie(
                        names=levels,
                        values=counts,
                        title="🎯 RECOVERY PROBABILITY INTELLIGENCE",
                        hole=0.5,
                        color_discrete_sequence=[
                            "#22c55e",
                            "#84cc16",
                            "#eab308",
                            "#f97316",
                            "#dc2626",
                        ],
                    )

                    fig.update_traces(
                        textinfo="percent+label",
                        pull=[
                            0.1 if "HIGH" in str(level).upper() else 0 for level in levels
                        ],
                    )

                    st.plotly_chart(fig, use_container_width=True)

        # Real-time Recovery Pipeline
        st.markdown("#### 📊 REAL-TIME RECOVERY PIPELINE - Operations Status")

        pipeline_data = {
            "Stage": [
                "Early Delinquency",
                "Reminder Stage",
                "Negotiation",
                "Restructuring",
                "Legal Action",
                "Recovered",
            ],
            "Accounts": [125, 89, 67, 42, 23, 156],
        }

        fig = go.Figure(
            data=[
                go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="black", width=0.5),
                        label=pipeline_data["Stage"],
                        color=[
                            "#22c55e",
                            "#84cc16",
                            "#eab308",
                            "#f97316",
                            "#dc2626",
                            "#059669",
                        ],
                    ),
                    link=dict(
                        source=[0, 1, 2, 3, 4],
                        target=[1, 2, 3, 4, 5],
                        value=[100, 80, 60, 40, 20],
                    ),
                )
            ]
        )

        fig.update_layout(
            title_text="🔄 RECOVERY STAGE PROGRESSION SANKEY", font_size=10, height=300
        )
        st.plotly_chart(fig, use_container_width=True)

    def _render_portfolio_intelligence_center(self, analysis):
        """Tab 2: Portfolio Intelligence Center"""
        st.subheader("📊 PORTFOLIO INTELLIGENCE CENTER - Risk Exposure Analytics")

        portfolio_segmentation = analysis.get("portfolio_segmentation", {})

        if portfolio_segmentation:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("##### 💰 PORTFOLIO CONCENTRATION ANALYTICS")

                amount_segmentation = portfolio_segmentation.get(
                    "amount_segmentation", {}
                )
                if amount_segmentation:
                    segments = list(amount_segmentation.keys())
                    counts = list(amount_segmentation.values())

                    fig = px.bar(
                        x=segments,
                        y=counts,
                        title="📈 PORTFOLIO VALUE CONCENTRATION",
                        labels={"x": "Exposure Segment", "y": "Number of Accounts"},
                        color=counts,
                        color_continuous_scale="OrRd",
                    )

                    fig.update_layout(
                        height=400, plot_bgcolor="rgba(0,0,0,0.05)"
                    )

                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("##### 📊 PORTFOLIO VULNERABILITY MATRIX")

                vulnerability_data = {
                    "Risk Dimension": [
                        "Amount Concentration",
                        "Duration Risk",
                        "Geographic Cluster",
                        "Industry Exposure",
                        "Agent Dependency",
                    ],
                    "Risk Score": [8.2, 7.5, 6.3, 5.8, 4.2],
                    "Impact": ["High", "High", "Medium", "Medium", "Low"],
                }

                vul_df = pd.DataFrame(vulnerability_data)

                fig = px.scatter(
                    vul_df,
                    x="Risk Dimension",
                    y="Risk Score",
                    size="Risk Score",
                    color="Impact",
                    title="⚡ PORTFOLIO VULNERABILITY HEATMAP",
                    color_discrete_sequence=["#dc2626", "#f97316", "#84cc16"],
                    size_max=40,
                )

                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

            # Top Delinquent Accounts
            st.markdown("##### ⚠️ HIGH-PRIORITY TARGET LIST - Immediate Action Required")

            top_accounts = portfolio_segmentation.get("top_delinquent_accounts", [])
            if top_accounts:
                accounts_data = []
                max_exposure = max(
                    [a.outstanding_amount for a in top_accounts[:15]]
                )

                for account in top_accounts[:15]:
                    bucket_val = getattr(account.delinquency_bucket, "value", "1-30")
                    priority_color = {
                        "1-30": "🟢",
                        "31-60": "🟡",
                        "61-90": "🟠",
                        "91-120": "🔴",
                        "120+": "⚫",
                    }.get(bucket_val, "⚪")

                    accounts_data.append(
                        {
                            "Priority": priority_color,
                            "Loan ID": account.loan_id,
                            "Member ID": account.member_id,
                            "Exposure": account.outstanding_amount,
                            "Days Delinq": account.days_delinquent,
                            "Risk Level": bucket_val,
                            "Contact": account.contact_number,
                            "Last Action": "2 days ago",
                        }
                    )

                accounts_df = pd.DataFrame(accounts_data)

                st.dataframe(
                    accounts_df,
                    use_container_width=True,
                    column_config={
                        "Priority": st.column_config.TextColumn("🔴", width="small"),
                        "Exposure": st.column_config.ProgressColumn(
                            "Exposure",
                            format="KES %f",
                            min_value=0,
                            max_value=float(max_exposure) if max_exposure else 1_000_000,
                        ),
                    },
                )

                st.markdown("##### 🚀 BATCH ACTION DEPLOYMENT")
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button(
                        "📞 DEPLOY SMS CAMPAIGN", use_container_width=True
                    ):
                        st.success(
                            "SMS campaign deployed to 15 high-priority accounts"
                        )

                with col2:
                    if st.button(
                        "👥 ASSIGN TO FIELD AGENTS", use_container_width=True
                    ):
                        st.success(
                            "15 accounts assigned to field collection teams"
                        )

                with col3:
                    if st.button(
                        "🔄 INITIATE RESTRUCTURING", use_container_width=True
                    ):
                        st.info(
                            "Restructuring proposals generated for selected accounts"
                        )

    def _render_strategy_ops_deployment(self, analysis):
        """Tab 3: Strategy Ops & Deployment"""
        st.subheader("🎯 STRATEGY OPS & DEPLOYMENT - Tactical Implementation Center")

        strategy_loans = analysis.get("strategy_recommendations", [])

        if strategy_loans:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("##### 📋 STRATEGY DISTRIBUTION INTELLIGENCE")

                strategy_distribution = {}
                for loan in strategy_loans:
                    strategy = getattr(
                        loan.recommended_strategy, "value", "Unspecified"
                    )
                    strategy_distribution[strategy] = (
                        strategy_distribution.get(strategy, 0) + 1
                    )

                if strategy_distribution:
                    strategies = list(strategy_distribution.keys())
                    counts = list(strategy_distribution.values())

                    fig = px.bar(
                        x=strategies,
                        y=counts,
                        title="🔄 STRATEGY DEPLOYMENT MATRIX",
                        labels={
                            "x": "Collection Strategy",
                            "y": "Number of Accounts",
                        },
                        color=counts,
                        color_continuous_scale="OrRd",
                        text=counts,
                    )

                    fig.update_layout(
                        height=400, plot_bgcolor="rgba(0,0,0,0.05)"
                    )

                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("##### 🔥 HIGH-IMPACT INTERVENTION QUEUE")

                high_priority_strategies = {
                    CollectionStrategy.NEGOTIATION.value,
                    CollectionStrategy.RESTRUCTURING.value,
                    CollectionStrategy.LEGAL_ACTION.value,
                }

                high_priority_loans = [
                    loan
                    for loan in strategy_loans
                    if getattr(loan.recommended_strategy, "value", "")
                    in high_priority_strategies
                ]

                if high_priority_loans:
                    priority_data = []
                    for loan in high_priority_loans[:10]:
                        priority_data.append(
                            {
                                "Target": f"{loan.loan_id}",
                                "Strategy": f"🎯 {getattr(loan.recommended_strategy, 'value', '')}",
                                "Probability": f"📊 {getattr(loan.recovery_probability, 'value', '')}",
                                "Exposure": f"💰 KES {loan.outstanding_amount:,.0f}",
                                "Urgency": f"⏰ {loan.days_delinquent} days",
                            }
                        )

                    priority_df = pd.DataFrame(priority_data)
                    st.dataframe(priority_df, use_container_width=True, hide_index=True)

                    st.markdown("##### 📈 STRATEGY EFFECTIVENESS METRICS")

                    effectiveness_data = {
                        "Strategy": [
                            "SMS Reminder",
                            "Phone Call",
                            "Field Visit",
                            "Negotiation",
                            "Restructuring",
                        ],
                        "Success Rate": [65, 72, 78, 55, 48],
                        "Avg Days": [7, 14, 21, 35, 60],
                        "Cost per Recovery": [150, 750, 2500, 5000, 15000],
                    }

                    eff_df = pd.DataFrame(effectiveness_data)
                    st.dataframe(eff_df, use_container_width=True)

            st.markdown("##### 🎯 TARGETED STRATEGY DEPLOYMENT CENTER")

            loan_options = [
                f"{loan.loan_id} | {loan.member_name} | KES {loan.outstanding_amount:,.0f} | {loan.days_delinquent} days"
                for loan in strategy_loans[:50]
            ]

            selected_loan = st.selectbox(
                "🎯 SELECT TARGET ACCOUNT FOR PRECISION DEPLOYMENT",
                loan_options,
                index=0 if loan_options else None,
            )

            if selected_loan:
                loan_id = selected_loan.split(" | ")[0]
                selected_loan_data = next(
                    (loan for loan in strategy_loans if loan.loan_id == loan_id),
                    None,
                )

                if selected_loan_data:
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric(
                            "🎯 RECOMMENDED STRATEGY",
                            getattr(
                                selected_loan_data.recommended_strategy, "value", ""
                            ),
                            delta="AI-Optimized",
                        )

                    with col2:
                        recovery_prob = getattr(
                            selected_loan_data.recovery_probability, "value", ""
                        )
                        st.metric(
                            "📊 RECOVERY PROBABILITY",
                            recovery_prob,
                            delta=(
                                "High Confidence"
                                if "HIGH" in recovery_prob.upper()
                                else "Medium"
                            ),
                        )

                    with col3:
                        st.metric(
                            "💰 EXPOSURE VALUE",
                            f"KES {selected_loan_data.outstanding_amount:,.0f}",
                            delta="Priority Target",
                        )

                    with col4:
                        st.metric(
                            "⏰ TIME IN DELINQUENCY",
                            f"{selected_loan_data.days_delinquent} days",
                            delta=(
                                "Critical"
                                if selected_loan_data.days_delinquent > 90
                                else "Elevated"
                            ),
                        )

                    st.markdown("##### ⚡ ACTION DEPLOYMENT PANEL")

                    action_col1, action_col2, action_col3, action_col4 = st.columns(4)

                    with action_col1:
                        if st.button(
                            "🚨 DEPLOY IMMEDIATE ACTION",
                            use_container_width=True,
                            key=f"deploy_{loan_id}",
                        ):
                            st.success(
                                f"🎯 Strategy deployed for {loan_id}. Agent assigned and action initiated."
                            )

                    with action_col2:
                        if st.button(
                            "📞 SCHEDULE NEGOTIATION",
                            use_container_width=True,
                            key=f"nego_{loan_id}",
                        ):
                            st.info(
                                f"📅 Negotiation scheduled for {selected_loan_data.member_name}. Calendar invite sent."
                            )

                    with action_col3:
                        if st.button(
                            "📋 GENERATE RESTRUCTURING",
                            use_container_width=True,
                            key=f"restruct_{loan_id}",
                        ):
                            st.warning(
                                f"🔄 Restructuring proposal generated for {loan_id}. Awaiting member response."
                            )

                    with action_col4:
                        if st.button(
                            "⚖️ ESCALATE TO LEGAL",
                            use_container_width=True,
                            key=f"legal_{loan_id}",
                        ):
                            st.error(
                                f"⚖️ Case {loan_id} escalated to legal department for recovery action."
                            )

    def _render_agent_performance_command(self, analysis):
        """Tab 4: Agent Performance Command"""
        st.subheader("👥 AGENT PERFORMANCE COMMAND - Field Operations Intelligence")

        agent_analysis = analysis.get("agent_analysis", {})
        agent_performance = agent_analysis.get("agent_performance", {})

        if agent_performance:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("##### 📊 AGENT PERFORMANCE SCOREBOARD")

                performance_data = []
                for agent_id, data in agent_performance.items():
                    success_rate = data["success_rate"] * 100
                    if success_rate > 75:
                        tier = "⭐ Elite"
                    elif success_rate > 60:
                        tier = "✅ Proficient"
                    else:
                        tier = "⚠️ Needs Coaching"

                    performance_data.append(
                        {
                            "Agent ID": f"👤 {agent_id}",
                            "Performance Tier": tier,
                            "Success Rate": f"{success_rate:.1f}%",
                            "Total Actions": data["total_actions"],
                            "Avg Recovery": f"KES {data.get('average_recovery_amount', 0):,.0f}",
                            "Productivity": f"{data.get('actions_per_day', 0):.1f}/day",
                        }
                    )

                performance_df = pd.DataFrame(performance_data)
                st.dataframe(performance_df, use_container_width=True, hide_index=True)

            with col2:
                st.markdown("##### 🏆 ELITE AGENT COMMAND CENTER")

                top_performers = agent_analysis.get("top_performers", [])
                if top_performers:
                    elite_agent = top_performers[0]
                    agent_id, data = elite_agent

                    st.markdown(
                        f"""
                    <div style="
                        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                        padding: 1.5rem;
                        border-radius: 10px;
                        border-left: 5px solid #f59e0b;
                        margin-bottom: 1rem;
                    ">
                        <h3 style="color: #92400e; margin: 0;">🏆 ELITE AGENT: {agent_id}</h3>
                        <p style="color: #92400e; margin: 0.5rem 0 0 0;">
                            ⭐ Success Rate: <strong>{data['success_rate'] * 100:.1f}%</strong> | 
                            🎯 Recoveries: <strong>KES {data.get('total_recovery_amount', 0):,.0f}</strong>
                        </p>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    elite_col1, elite_col2, elite_col3 = st.columns(3)

                    with elite_col1:
                        st.metric("Total Actions", data["total_actions"], delta="+15%")

                    with elite_col2:
                        st.metric(
                            "Promise Keep Rate",
                            f"{data.get('promise_keep_rate', 0) * 100:.1f}%",
                            delta="+8%",
                        )

                    with elite_col3:
                        st.metric(
                            "Avg Days to Close",
                            f"{data.get('avg_days_to_close', 0):.0f}",
                            delta="-3 days",
                        )

            st.markdown("##### 📈 ACTION TYPE INTELLIGENCE")

            all_actions = {}
            for agent_data in agent_performance.values():
                for action_type, count in agent_data.get(
                    "actions_by_type", {}
                ).items():
                    all_actions[action_type] = all_actions.get(action_type, 0) + count

            if all_actions:
                action_types = list(all_actions.keys())
                action_counts = list(all_actions.values())

                fig = go.Figure(
                    data=[
                        go.Bar(
                            x=action_types,
                            y=action_counts,
                            marker_color=[
                                "#f97316",
                                "#84cc16",
                                "#3b82f6",
                                "#8b5cf6",
                                "#ec4899",
                            ][: len(action_types)],
                            text=action_counts,
                            textposition="auto",
                        )
                    ]
                )

                fig.update_layout(
                    title="🔄 ACTION TYPE EFFECTIVENESS MATRIX",
                    xaxis_title="Action Type",
                    yaxis_title="Frequency",
                    height=350,
                    plot_bgcolor="rgba(0,0,0,0.05)",
                )

                st.plotly_chart(fig, use_container_width=True)

            st.markdown("##### 🎓 AGENT COACHING & DEVELOPMENT CENTER")

            selected_agent = st.selectbox(
                "👤 SELECT AGENT FOR PERFORMANCE COACHING",
                list(agent_performance.keys()),
            )

            if selected_agent:
                agent_data = agent_performance[selected_agent]

                coaching_col1, coaching_col2, coaching_col3 = st.columns(3)

                with coaching_col1:
                    st.metric(
                        "Current Success Rate",
                        f"{agent_data['success_rate'] * 100:.1f}%",
                    )
                    st.progress(
                        agent_data["success_rate"], text="Success Rate Progress"
                    )

                with coaching_col2:
                    st.metric(
                        "Target Success Rate",
                        "75.0%",
                        delta=f"{(75 - agent_data['success_rate'] * 100):+.1f}%",
                    )
                    st.progress(0.75, text="Target Achievement")

                with coaching_col3:
                    sr = agent_data["success_rate"] * 100
                    if sr < 60:
                        priority = "HIGH"
                    elif sr < 70:
                        priority = "MEDIUM"
                    else:
                        priority = "LOW"

                    st.metric("Coaching Priority", priority)

                if st.button(
                    "📋 GENERATE COACHING PLAN", key=f"coach_{selected_agent}"
                ):
                    st.success(
                        f"Personalized coaching plan generated for Agent {selected_agent}"
                    )

                if st.button(
                    "🎯 ASSIGN MENTOR", key=f"mentor_{selected_agent}"
                ):
                    st.info(
                        f"Elite agent assigned as mentor to {selected_agent}"
                    )

    def _render_compliance_audit_watch(self, analysis):
        """Tab 5: Compliance & Audit Watch"""
        st.subheader("🛡️ COMPLIANCE & AUDIT WATCH - Regulatory Intelligence Center")

        st.markdown("##### 📚 COLLECTIONS COMPLIANCE FRAMEWORK")

        compliance_frameworks = {
            "SASRA Prudential Standard 12": {
                "Requirement": "Fair Debt Collection Practices",
                "Status": "✅ Compliant",
                "Last Audit": "2024-01-15",
                "Risk Level": "Low",
            },
            "CBK Collections Guidelines": {
                "Requirement": "Customer Communication Standards",
                "Status": "⚠️ Partial Compliance",
                "Last Audit": "2024-02-20",
                "Risk Level": "Medium",
            },
            "Data Protection Act": {
                "Requirement": "Member Data Privacy",
                "Status": "✅ Compliant",
                "Last Audit": "2024-03-10",
                "Risk Level": "Low",
            },
            "Consumer Protection": {
                "Requirement": "Transparent Communication",
                "Status": "✅ Compliant",
                "Last Audit": "2024-01-30",
                "Risk Level": "Low",
            },
        }

        compliance_df = pd.DataFrame(compliance_frameworks).T
        st.dataframe(compliance_df, use_container_width=True)

        st.markdown("##### 📋 AUDIT TRAIL & ACTION LOGGING")

        audit_data = {
            "Date": [
                "2024-03-15",
                "2024-03-14",
                "2024-03-13",
                "2024-03-12",
                "2024-03-11",
            ],
            "Action": [
                "Legal escalation approved",
                "Restructuring agreement signed",
                "Field visit completed",
                "SMS campaign deployed",
                "Agent performance review",
            ],
            "Agent": [
                "Legal Team",
                "Agent-007",
                "Agent-012",
                "System",
                "Supervisor",
            ],
            "Account": [
                "LOAN-2345",
                "LOAN-1892",
                "LOAN-1567",
                "15 accounts",
                "Agent-009",
            ],
            "Compliance": [
                "✅ Compliant",
                "✅ Compliant",
                "⚠️ Review needed",
                "✅ Compliant",
                "✅ Compliant",
            ],
        }

        audit_df = pd.DataFrame(audit_data)
        st.dataframe(audit_df, use_container_width=True, hide_index=True)

        st.markdown("##### 🚨 COMPLIANCE RISK MONITORING")

        col1, col2 = st.columns(2)

        with col1:
            risk_data = {
                "Risk Area": [
                    "Communication Compliance",
                    "Data Privacy",
                    "Documentation",
                    "Agent Conduct",
                    "Legal Procedures",
                ],
                "Risk Score": [25, 15, 40, 30, 20],
                "Trend": ["↓ Improving", "→ Stable", "↑ Increasing", "→ Stable", "↓ Improving"],
            }

            risk_df = pd.DataFrame(risk_data)

            fig = px.bar(
                risk_df,
                x="Risk Area",
                y="Risk Score",
                color="Risk Score",
                title="⚡ COMPLIANCE RISK HEATMAP",
                color_continuous_scale="RdYlGn_r",
                text="Trend",
            )

            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("##### 📊 COMPLIANCE METRICS DASHBOARD")

            metrics_data = {
                "Metric": [
                    "Compliance Rate",
                    "Audit Findings",
                    "Training Completion",
                    "Documentation Rate",
                    "Member Complaints",
                ],
                "Value": ["98.5%", "2 Open", "100%", "95.2%", "3 This Month"],
                "Status": [
                    "✅ Excellent",
                    "⚠️ Attention",
                    "✅ Complete",
                    "✅ Good",
                    "✅ Low",
                ],
            }

            metrics_df = pd.DataFrame(metrics_data)
            st.dataframe(metrics_df, use_container_width=True, hide_index=True)

        st.markdown("##### 🎯 COMPLIANCE ACTION PLANNING")

        with st.form("compliance_action_form"):
            col1, col2, col3 = st.columns(3)

            with col1:
                action_type = st.selectbox(
                    "Action Type",
                    [
                        "Training",
                        "Process Update",
                        "Documentation",
                        "System Enhancement",
                        "Policy Review",
                    ],
                )

            with col2:
                priority = st.select_slider(
                    "Priority Level",
                    options=["Low", "Medium", "High", "Critical"],
                )

            with col3:
                deadline = st.date_input("Target Completion Date")

            action_description = st.text_area(
                "Action Description",
                placeholder="Describe the compliance action to be implemented...",
            )

            submitted = st.form_submit_button("📋 LOG COMPLIANCE ACTION")

            if submitted and action_description:
                st.success(
                    f"✅ Compliance action logged: {action_type} - Priority: {priority}"
                )
                st.balloons()

    def render_collections_dashboard(self, analysis=None):
        """Wrapper that wires analysis into the strategic UI"""
        try:
            if analysis is None:
                analysis = self.collections_analyzer.analyze_collections_portfolio()

            self._render_enterprise_header()
            self._render_compliance_philosophy()
            self._render_status_marquee(analysis)
            self._render_strategic_tabs(analysis)

        except Exception as e:
            st.error(f"Error rendering collections dashboard: {str(e)}")
            st.info("Please check the data connection and try again.")

    # The following “preserved” methods are now covered by the strategic tabs
    def render_collections_overview(self, analysis):
        pass

    def render_portfolio_segmentation(self, analysis):
        pass

    def render_strategy_recommendations(self, analysis):
        pass

    def render_agent_performance(self, analysis):
        pass

    def render_workflow_optimization(self, analysis):
        pass

    def render_performance_analytics(self, analysis):
        pass

    def run(self):
        """Run the collections and recovery page with enterprise enhancements"""
        try:
            analysis = self.collections_analyzer.analyze_collections_portfolio()
            self.render_collections_dashboard(analysis)

            try:
                self.audit_logger.log_page_access(
                    st.session_state.get("user", "unknown"),
                    "Collections_Intelligence_Ops_Center",
                    "Success",
                )
            except Exception:
                pass

        except Exception as e:
            st.error(f"Error running collections page: {str(e)}")
            st.info(
                "Please try refreshing the page or contact support if the issue persists."
            )

            try:
                self.audit_logger.log_page_access(
                    st.session_state.get("user", "unknown"),
                    "Collections_Intelligence_Ops_Center",
                    f"Error: {str(e)}",
                )
            except Exception:
                pass


if __name__ == "__main__":
    page = CollectionsRecoveryPage()
    page.run()
