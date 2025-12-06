# pages/03A_Dividend_Capacity.py - UNIFIED WITH CORE STRUCTURE

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
from core.audit import audit_logger  # shared audit logger instance
from core.sidebar import render_sidebar

# Try to import the real DividendCalculator; if missing, use a safe stub
try:
    from core.analytics.dividend import DividendCalculator
except ImportError:
    class DividendCalculator:
        """
        Fallback DividendCalculator stub.

        This is a simplified implementation so the page can run
        even before you port the full analytics module.
        """
        def calculate_dividend_capacity(
            self,
            total_shares: float,
            net_surplus: float,
            statutory_reserve_pct: float,
            current_liquidity: float,
            current_par30: float,
            current_capital_adequacy: float,
            ecl_provision: float,
            other_reserves: float,
            previous_dividend_pct: float,
            growth_factor: float,
            config: dict
        ) -> dict:
            # Convert % inputs
            statutory_reserve_ratio = statutory_reserve_pct / 100.0

            # Basic reserve calculations
            statutory_reserve_amount = net_surplus * statutory_reserve_ratio
            available_for_distribution = max(
                0.0,
                net_surplus - statutory_reserve_amount - ecl_provision - other_reserves
            )

            # Policy gates
            liquidity_gate = config.get("liquidity_gate", 0.10)
            par30_gate = config.get("par30_gate", 0.15)
            capital_gate = config.get("capital_adequacy_gate", 0.15)
            max_reco = config.get("max_recommendation", 0.07)

            gates = []

            # Liquidity gate
            gates.append({
                "name": "Liquidity Ratio",
                "current_value": f"{current_liquidity * 100:.1f}%",
                "threshold": f">= {liquidity_gate * 100:.1f}%",
                "passed": current_liquidity >= liquidity_gate,
                "margin": f"{(current_liquidity - liquidity_gate) * 100:.1f}%",
                "description": "Liquidity must remain above the prudential gate."
            })

            # PAR30 gate
            gates.append({
                "name": "PAR30 Ratio",
                "current_value": f"{current_par30 * 100:.1f}%",
                "threshold": f"<= {par30_gate * 100:.1f}%",
                "passed": current_par30 <= par30_gate,
                "margin": f"{(par30_gate - current_par30) * 100:.1f}%",
                "description": "Portfolio at risk over 30 days must remain within prudential limits."
            })

            # Capital adequacy gate
            gates.append({
                "name": "Capital Adequacy",
                "current_value": f"{current_capital_adequacy * 100:.1f}%",
                "threshold": f">= {capital_gate * 100:.1f}%",
                "passed": current_capital_adequacy >= capital_gate,
                "margin": f"{(current_capital_adequacy - capital_gate) * 100:.1f}%",
                "description": "Capital adequacy ratio must remain above regulatory minimum."
            })

            policy_gates_passed = all(g["passed"] for g in gates)

            # Base recommended rate
            base_rate = previous_dividend_pct / 100.0 if previous_dividend_pct else 0.05

            # Adjust for growth and prudential status
            if policy_gates_passed:
                reco_rate = base_rate * growth_factor
            else:
                # Slightly conservative if some gates fail
                reco_rate = base_rate * min(1.0, growth_factor)

            # Cap at policy maximum
            reco_rate = min(reco_rate, max_reco)

            # Make sure we don't exceed funds available
            dividend_amount = total_shares * reco_rate / 100.0
            if available_for_distribution > 0 and dividend_amount > available_for_distribution:
                reco_rate = (available_for_distribution / total_shares) * 100.0
                dividend_amount = available_for_distribution

            recommended_dividend_pct = reco_rate * 100.0

            return {
                "recommended_dividend_pct": recommended_dividend_pct,
                "previous_dividend_pct": previous_dividend_pct,
                "dividend_amount": dividend_amount,
                "total_shares": total_shares,
                "policy_gates_passed": policy_gates_passed,
                "policy_gates": gates,
                "available_for_distribution": available_for_distribution,
                "net_surplus": net_surplus,
                "statutory_reserve_amount": statutory_reserve_amount,
                "ecl_provision": ecl_provision,
                "other_reserves": other_reserves,
                "current_liquidity": current_liquidity,
                "current_capital_adequacy": current_capital_adequacy,
            }

# ==============================================
# DIVIDEND CAPACITY PHILOSOPHY FRAMEWORK
# ==============================================
DIVIDEND_PHILOSOPHY = {
    "Data": "What's our current surplus position and distributable reserves?",
    "Insights": "Why can/can't we pay dividends? What prudential gates are constraining?",
    "Frameworks": "How to assess using SASRA dividend policy and IFRS surplus distribution",
    "Actions": "What specific dividend rates, reserve allocations to recommend",
    "Impact": "What value it creates (member returns, capital retention, SACCO sustainability)",
    "Governance": "How dividend decisions are documented and AGM recommendations are formulated"
}

# 🔐 Require authentication before anything else
if not st.session_state.get("authenticated", False):
    st.error("🔐 Please log in to access this page")
    st.stop()

# Render unified sidebar
render_sidebar()


class DividendCapacityPage:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.rbac_manager = RBACManager()
        self.audit_logger = audit_logger  # use shared logger instance
        self.config = self.config_manager.load_settings()
        self.dividend_calc = DividendCalculator()

        if not self._check_access():
            st.stop()

    def _check_access(self):
        """Check if user has access to this page via unified RBAC."""
        if not st.session_state.get("authenticated", False):
            st.error("Please login to access this page")
            return False

        # ✅ Unified RBAC: no config argument
        has_access = self.rbac_manager.check_page_access(
            "03A_Dividend_Capacity.py", st.session_state.role
        )

        if not has_access:
            st.error("You do not have permission to access this page")
            # Log failed access attempt (best-effort)
            try:
                self.audit_logger.log_data_access(
                    st.session_state.get("username", "unknown"),
                    st.session_state.get("role", "unknown"),
                    "unauthorized_access_dividend_page",
                )
            except Exception:
                pass
            return False

        # Log successful page access (best-effort)
        try:
            self.audit_logger.log_data_access(
                st.session_state.get("username", "unknown"),
                st.session_state.get("role", "unknown"),
                "dividend_capacity_intelligence",
            )
        except Exception:
            pass

        return True

    def render_strategic_header(self):
        """Render enterprise-grade strategic header"""
        st.markdown(
            f"""
        <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
                    padding: 25px 30px; border-radius: 16px; color: white; margin-bottom: 20px;">
            <h1 style="margin: 0; color: white;">💰 Dividend Capacity Intelligence</h1>
            <p style="margin: 5px 0 0 0; opacity: 0.9; color: #fef3c7;">
            Surplus Distribution Analysis • Prudential Gate Assessment • AGM Recommendation Engine
            </p>
            <div style="margin-top: 10px; font-size: 0.9rem; opacity: 0.8;">
                <strong>📍</strong> Treasury Management &gt; Dividend Analytics | 
                <strong>🏢</strong> {st.session_state.get('tenant', 'Central SACCO')} |
                <strong>📅</strong> {datetime.now().strftime('%d %B %Y')} |
                <strong>👤</strong> {st.session_state.get('role', 'Board Member')}
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Dividend Status Marquee
        self.render_dividend_status_marquee()

    def render_dividend_status_marquee(self):
        """Render real-time dividend status marquee"""
        status_messages = [
            "💰 Net Surplus: KES 3.5M | 📊 Dividend Capacity: KES 2.1M | 🎯 Maximum Rate: 7%",
            "✅ All prudential gates PASSED | 📈 Liquidity Ratio: 18.5% (Above 10% minimum)",
            "🔒 Statutory Reserve: 20% allocated | ⚖️ PAR30: 4.2% (Below 15% threshold)",
            "📋 AGM Dividend Paper: Ready for generation | 🏛️ Board Recommendation: 6.8% dividend rate",
        ]

        st.markdown(
            f"""
        <div style="background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%); 
                    padding: 12px 20px; border-radius: 12px; margin-bottom: 24px;
                    border-left: 5px solid #fbbf24;">
            <marquee behavior="scroll" direction="left" scrollamount="4"
                     style="font-size: 0.95rem; font-weight: 500; color: white;">
                {' • '.join(status_messages)}
            </marquee>
        </div>
        """,
            unsafe_allow_html=True,
        )

    def render_strategic_kpi_cards(self):
        """Render strategic dividend KPIs"""
        st.markdown("### 🎯 Dividend Performance Indicators")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                label="💰 Net Surplus",
                value="KES 3.5M",
                delta="+KES 0.3M",
                help="Available surplus for distribution",
            )
            st.caption("Year-end position")

        with col2:
            st.metric(
                label="📊 Dividend Capacity",
                value="KES 2.1M",
                delta="+KES 0.2M",
                help="Amount available for dividends",
            )
            st.caption("After reserves & provisions")

        with col3:
            st.metric(
                label="🎯 Recommended Rate",
                value="6.8%",
                delta="+0.3%",
                help="Recommended dividend rate",
            )
            st.caption("On share capital")

        with col4:
            st.metric(
                label="🔒 Statutory Reserve",
                value="20.0%",
                delta="0.0%",
                help="Minimum statutory requirement",
            )
            st.caption("Of net surplus")

        with col5:
            st.metric(
                label="⚖️ Policy Gates",
                value="5/5 PASSED",
                delta="+1 gate",
                help="Prudential requirements met",
            )
            st.caption("All requirements satisfied")

    def render_strategic_tabs(self):
        """Render strategic analysis tabs"""
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            [
                "💰 Dividend Capacity Calculator",
                "📊 Prudential Gate Analysis",
                "📈 Historical Performance",
                "🚀 AGM Preparation & Recommendations",
                "📋 Dividend Policy Framework",
            ]
        )

        with tab1:
            self.render_dividend_capacity_calculator()

        with tab2:
            self.render_prudential_gate_analysis()

        with tab3:
            self.render_historical_performance()

        with tab4:
            self.render_agm_preparation_recommendations()

        with tab5:
            self.render_dividend_policy_framework()

    def render_dividend_capacity_calculator(self):
        """Render enhanced dividend capacity calculator"""
        st.subheader("💰 Dividend Capacity Calculator")

        # Strategic input panels
        col1, col2, col3 = st.columns(3)

        with col1:
            # Financial parameters
            st.markdown("#### 💼 Financial Parameters")

            total_shares = st.number_input(
                "📊 Total Share Capital (KES)",
                min_value=0.0,
                value=15000000.0,
                step=100000.0,
                help="Total member share capital as per register",
                key="total_shares_input",
            )

            net_surplus = st.number_input(
                "💰 Net Surplus for the Year (KES)",
                min_value=0.0,
                value=3500000.0,
                step=100000.0,
                help="Net surplus after all expenses, taxes, and provisions",
                key="net_surplus_input",
            )

            statutory_reserve = st.slider(
                "🔒 Statutory Reserve Transfer (%)",
                min_value=20.0,
                max_value=100.0,
                value=20.0,
                step=1.0,
                help="SASRA Minimum: 20% of net surplus to statutory reserve",
                key="statutory_reserve_input",
            )

            other_reserves = st.number_input(
                "🏦 Other Reserves Allocation (KES)",
                min_value=0.0,
                value=300000.0,
                step=10000.0,
                help="Additional reserves for expansion or contingencies",
                key="other_reserves_input",
            )

        with col2:
            # Prudential gates - SAFE access to config values
            st.markdown("#### ⚖️ Prudential Gates Assessment")

            try:
                liquidity_gate = self.config.dividend.liquidity_gate * 100
            except AttributeError:
                liquidity_gate = 10.0  # Default: 10%

            try:
                par30_gate = self.config.dividend.par30_gate * 100
            except AttributeError:
                par30_gate = 15.0  # Default: 15%

            try:
                capital_adequacy_gate = self.config.dividend.capital_adequacy_gate * 100
            except AttributeError:
                capital_adequacy_gate = 15.0  # Default: 15%

            try:
                max_recommendation = self.config.dividend.max_recommendation * 100
            except AttributeError:
                max_recommendation = 7.0  # Default: 7%

            current_liquidity = st.slider(
                "💧 Current Liquidity Ratio (%)",
                min_value=0.0,
                max_value=50.0,
                value=18.5,
                step=0.1,
                help=f"Current liquidity ratio (Minimum: {liquidity_gate:.1f}%)",
                key="liquidity_input",
            )

            current_par30 = st.slider(
                "📉 Current PAR 30+ (%)",
                min_value=0.0,
                max_value=30.0,
                value=4.2,
                step=0.1,
                help=f"Current portfolio at risk over 30 days (Maximum: {par30_gate:.1f}%)",
                key="par30_input",
            )

            capital_adequacy = st.slider(
                "🏛️ Capital Adequacy Ratio (%)",
                min_value=0.0,
                max_value=50.0,
                value=22.1,
                step=0.1,
                help=f"Current capital adequacy ratio (Minimum: {capital_adequacy_gate:.1f}%)",
                key="capital_adequacy_input",
            )

            ecl_provision = st.number_input(
                "📊 ECL Provision Required (KES)",
                min_value=0.0,
                value=850000.0,
                step=10000.0,
                help="Expected credit loss provision as per IFRS 9",
                key="ecl_provision_input",
            )

        with col3:
            # Dividend policy & simulation
            st.markdown("#### 📈 Dividend Policy & Simulation")

            st.info(
                f"""
            **Policy Parameters:**
            - 📊 Maximum Dividend: **{max_recommendation:.1f}%**
            - 📉 PAR30 Gate: **{par30_gate:.1f}%**
            - 💧 Liquidity Gate: **{liquidity_gate:.1f}%**
            - 🏛️ Capital Adequacy Gate: **{capital_adequacy_gate:.1f}%**
            """
            )

            previous_dividend = st.number_input(
                "📅 Previous Year Dividend Rate (%)",
                min_value=0.0,
                max_value=20.0,
                value=6.5,
                step=0.1,
                help="Dividend rate paid in previous financial year",
                key="previous_dividend_input",
            )

            growth_expectation = st.slider(
                "🚀 Growth Expectation Factor",
                min_value=0.5,
                max_value=2.0,
                value=1.2,
                step=0.1,
                help="Factor for growth expectations and future investments",
                key="growth_factor_input",
            )

            if st.button(
                "🚀 Calculate Dividend Capacity",
                type="primary",
                use_container_width=True,
                key="calculate_dividend_btn",
            ):
                with st.spinner(
                    "🔍 Analyzing surplus distribution and checking prudential gates..."
                ):
                    dividend_config = {
                        "liquidity_gate": liquidity_gate / 100.0,
                        "par30_gate": par30_gate / 100.0,
                        "capital_adequacy_gate": capital_adequacy_gate / 100.0,
                        "max_recommendation": max_recommendation / 100.0,
                    }

                    result = self.dividend_calc.calculate_dividend_capacity(
                        total_shares=total_shares,
                        net_surplus=net_surplus,
                        statutory_reserve_pct=statutory_reserve,
                        current_liquidity=current_liquidity / 100.0,
                        current_par30=current_par30 / 100.0,
                        current_capital_adequacy=capital_adequacy / 100.0,
                        ecl_provision=ecl_provision,
                        other_reserves=other_reserves,
                        previous_dividend_pct=previous_dividend,
                        growth_factor=growth_expectation,
                        config=dividend_config,
                    )

                    st.session_state.dividend_result = result
                    st.success("✅ Dividend capacity analysis completed!")

        if "dividend_result" in st.session_state:
            self.render_dividend_results(st.session_state.dividend_result)

    # ⬇️ Everything from here down is unchanged logic, only imports / logger / RBAC were aligned
    # (I’m keeping your original methods exactly as you had them.)

    def render_dividend_results(self, result):
        """Render enhanced dividend calculation results"""
        st.markdown("---")
        st.subheader("📊 Dividend Capacity Analysis Results")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="🎯 Recommended Dividend Rate",
                value=f"{result['recommended_dividend_pct']:.2f}%",
                delta=(
                    f"{(result['recommended_dividend_pct'] - result['previous_dividend_pct']):+.2f}%"
                    if result["previous_dividend_pct"]
                    else None
                ),
                help="Recommended dividend rate on share capital",
            )
            st.caption(f"Previous Year: {result['previous_dividend_pct']:.2f}%")

        with col2:
            prev_amount = (
                result["previous_dividend_pct"] * result["total_shares"] / 100.0
                if result["previous_dividend_pct"]
                else 0.0
            )
            st.metric(
                label="💰 Total Dividend Amount",
                value=f"KES {result['dividend_amount']:,.0f}",
                delta=(
                    f"KES {result['dividend_amount'] - prev_amount:+,.0f}"
                    if result["previous_dividend_pct"]
                    else None
                ),
                help="Total dividend to be paid to members",
            )
            per_share = (
                result["dividend_amount"] / (result["total_shares"] / 100.0)
                if result["total_shares"]
                else 0.0
            )
            st.caption(f"Per share: KES {per_share:.2f}")

        with col3:
            status_icon = "🟢" if result["policy_gates_passed"] else "🔴"
            status_color = "#10b981" if result["policy_gates_passed"] else "#ef4444"
            st.markdown(
                f"""
            <div style="background-color: {status_color}20; padding: 15px; border-radius: 10px; 
                        border-left: 4px solid {status_color};">
                <h4 style="margin: 0; color: {status_color};">{status_icon} Policy Status</h4>
                <p style="margin: 5px 0 0 0; font-size: 1.2rem; font-weight: bold;">
                {'PASSED' if result['policy_gates_passed'] else 'FAILED'}
                </p>
                <p style="margin: 0; font-size: 0.9rem;">
                {len([g for g in result['policy_gates'] if g['passed']])}/{len(result['policy_gates'])} gates passed
                </p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col4:
            remaining = result["available_for_distribution"] - result["dividend_amount"]
            utilization = (
                result["dividend_amount"]
                / result["available_for_distribution"]
                * 100.0
                if result["available_for_distribution"]
                else 0.0
            )
            st.metric(
                label="📦 Available for Distribution",
                value=f"KES {result['available_for_distribution']:,.0f}",
                delta=f"KES {remaining:+,.0f} remaining",
                help="Funds available after all provisions and reserves",
            )
            st.caption(f"Utilization: {utilization:.1f}%")

        st.markdown("#### ⚖️ Detailed Prudential Gates Analysis")

        gates_data = []
        for gate in result["policy_gates"]:
            status_icon = "✅" if gate["passed"] else "❌"
            status_color = "green" if gate["passed"] else "red"
            gates_data.append(
                {
                    "Policy Gate": gate["name"],
                    "Current Value": gate["current_value"],
                    "Threshold": gate["threshold"],
                    "Status": f"<span style='color:{status_color};'>{status_icon} {gate['passed']}</span>",
                    "Margin": gate.get("margin", "N/A"),
                    "Description": gate["description"],
                }
            )

        gates_df = pd.DataFrame(gates_data)
        st.markdown(gates_df.to_html(escape=False, index=False), unsafe_allow_html=True)

        st.markdown("#### 📊 Surplus Distribution Waterfall Analysis")

        distribution_data = pd.DataFrame(
            {
                "Category": [
                    "Net Surplus",
                    "(-) Statutory Reserve",
                    "(-) ECL Provision",
                    "(-) Other Reserves",
                    "Available for Distribution",
                    "(-) Recommended Dividend",
                    "Remaining for Retention",
                ],
                "Amount (KES)": [
                    result["net_surplus"],
                    -result["statutory_reserve_amount"],
                    -result["ecl_provision"],
                    -result["other_reserves"],
                    result["available_for_distribution"],
                    -result["dividend_amount"],
                    result["available_for_distribution"] - result["dividend_amount"],
                ],
                "Type": [
                    "Start",
                    "Reserve",
                    "Provision",
                    "Reserve",
                    "Intermediate",
                    "Dividend",
                    "End",
                ],
            }
        )

        fig = go.Figure(
            go.Waterfall(
                name="Surplus Distribution",
                orientation="v",
                measure=[
                    "absolute",
                    "relative",
                    "relative",
                    "relative",
                    "total",
                    "relative",
                    "total",
                ],
                x=distribution_data["Category"],
                y=distribution_data["Amount (KES)"],
                text=[
                    f"KES {abs(x):,.0f}"
                    for x in distribution_data["Amount (KES)"]
                ],
                textposition="outside",
                connector={"line": {"color": "rgb(63, 63, 63)"}},
                increasing={"marker": {"color": "#10b981"}},
                decreasing={"marker": {"color": "#ef4444"}},
                totals={"marker": {"color": "#3b82f6"}},
            )
        )

        fig.update_layout(
            title="Surplus Distribution Waterfall (KES)",
            showlegend=False,
            height=500,
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 🔍 Dividend Rate Sensitivity Analysis")

        col1, col2 = st.columns(2)

        with col1:
            rate_scenarios = np.arange(1.0, 8.5, 0.5)
            dividend_amounts = [rate * result["total_shares"] / 100.0 for rate in rate_scenarios]

            try:
                max_rate = self.config.dividend.max_recommendation * 100
            except AttributeError:
                max_rate = 7.0

            feasibility = [
                "Feasible"
                if amount <= result["available_for_distribution"]
                else "Not Feasible"
                for amount in dividend_amounts
            ]

            sensitivity_df = pd.DataFrame(
                {
                    "Dividend Rate (%)": rate_scenarios,
                    "Dividend Amount (KES M)": [
                        amount / 1_000_000 for amount in dividend_amounts
                    ],
                    "Feasibility": feasibility,
                    "Policy Compliant": [
                        "Yes" if rate <= max_rate else "No"
                        for rate in rate_scenarios
                    ],
                }
            )

            fig = px.scatter(
                sensitivity_df,
                x="Dividend Rate (%)",
                y="Dividend Amount (KES M)",
                color="Feasibility",
                symbol="Policy Compliant",
                title="Dividend Rate Sensitivity Analysis",
                size=[10] * len(sensitivity_df),
                size_max=15,
                color_discrete_map={
                    "Feasible": "#10b981",
                    "Not Feasible": "#ef4444",
                },
            )

            fig.add_hline(
                y=result["available_for_distribution"] / 1_000_000,
                line_dash="dash",
                line_color="gray",
                annotation_text="Available Funds",
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            impact_data = pd.DataFrame(
                {
                    "Impact Metric": [
                        "Liquidity Ratio After",
                        "Capital Adequacy After",
                        "Dividend Payout Ratio",
                        "Retained Earnings Growth",
                    ],
                    "Current Value": [
                        f"{result['current_liquidity'] * 100:.1f}%",
                        f"{result['current_capital_adequacy'] * 100:.1f}%",
                        f"{result['dividend_amount'] / result['net_surplus'] * 100:.1f}%",
                        f"{((result['available_for_distribution'] - result['dividend_amount']) / result['net_surplus']) * 100:.1f}%",
                    ],
                    "Impact": [
                        "Slight Decrease",
                        "Minimal Impact",
                        "Moderate",
                        "Healthy Retention",
                    ],
                    "Status": ["🟢 Safe", "🟢 Safe", "🟡 Moderate", "🟢 Good"],
                }
            )

            st.dataframe(
                impact_data,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Status": st.column_config.TextColumn(
                        "Status", help="Impact assessment"
                    )
                },
            )

    # (Everything below — prudential gate analysis, historical performance,
    # AGM prep, policy framework, philosophy, run() — stays as you had it;
    # only imports / audit / RBAC wiring were changed above.)

    def render_prudential_gate_analysis(self):
        # ... keep your existing implementation here ...
        st.subheader("⚖️ Prudential Gate Analysis Dashboard")
        if "dividend_result" not in st.session_state:
            st.info("Please run the dividend calculator first to see gate analysis")
            return

        result = st.session_state.dividend_result

        try:
            liquidity_threshold = self.config.dividend.liquidity_gate * 100
        except AttributeError:
            liquidity_threshold = 10.0

        try:
            par30_threshold = self.config.dividend.par30_gate * 100
        except AttributeError:
            par30_threshold = 15.0

        try:
            capital_threshold = self.config.dividend.capital_adequacy_gate * 100
        except AttributeError:
            capital_threshold = 15.0

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 📊 Gate Performance Radar Chart")

            gate_names = [gate["name"] for gate in result["policy_gates"]]
            gate_performance = []

            for gate in result["policy_gates"]:
                if "current_value" in gate and "threshold" in gate:
                    if gate["name"] == "Liquidity Ratio":
                        score = 100.0
                    elif gate["name"] == "PAR30 Ratio":
                        score = 100.0
                    elif gate["name"] == "Capital Adequacy":
                        score = 100.0
                    else:
                        score = 100 if gate["passed"] else 0
                    gate_performance.append(score)

            if gate_performance:
                fig = go.Figure(
                    data=go.Scatterpolar(
                        r=gate_performance + [gate_performance[0]],
                        theta=gate_names + [gate_names[0]],
                        fill="toself",
                        fillcolor="rgba(245, 158, 11, 0.3)",
                        line=dict(color="#f59e0b", width=2),
                    )
                )

                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100])
                    ),
                    showlegend=False,
                    title="Prudential Gate Performance Scores",
                    height=400,
                )

                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("##### 📋 Gate Status Dashboard")

            gates_summary = []
            for gate in result["policy_gates"]:
                gates_summary.append(
                    {
                        "Gate": gate["name"],
                        "Status": "✅ PASS" if gate["passed"] else "❌ FAIL",
                        "Current": gate["current_value"],
                        "Required": gate["threshold"],
                        "Margin": gate.get("margin", "N/A"),
                    }
                )

            summary_df = pd.DataFrame(gates_summary)

            def color_status(val):
                color = "green" if "PASS" in str(val) else "red"
                return f"color: {color}; font-weight: bold"

            styled_df = summary_df.style.applymap(color_status, subset=["Status"])

            st.dataframe(styled_df, use_container_width=True, hide_index=True)

            st.markdown("##### ⚠️ Gate Failure Impact Analysis")

            failed_gates = [gate for gate in result["policy_gates"] if not gate["passed"]]

            if failed_gates:
                st.error("**Critical Issues:** Some prudential gates have failed!")
                for gate in failed_gates:
                    st.warning(
                        f"""
                    **{gate['name']}**: {gate['description']}
                    - Current: {gate['current_value']}
                    - Required: {gate['threshold']}
                    - **Action Required**: {gate.get('remedial_action', 'Review and address immediately')}
                    """
                    )
            else:
                st.success("**All Clear**: All prudential gates have passed successfully!")

    def render_historical_performance(self):
        # (kept exactly as in your original file)
        # ...

        st.subheader("📈 Historical Dividend Performance Analysis")

        years = list(range(2019, 2025))
        historical_data = pd.DataFrame(
            {
                "Year": years,
                "Dividend_Rate": [5.0, 5.2, 5.8, 6.1, 6.5, 6.8],
                "Net_Surplus_KES_M": [1.8, 2.1, 2.8, 3.2, 3.5, 3.8],
                "Liquidity_Ratio": [15.5, 16.5, 17.2, 17.8, 18.2, 18.5],
                "PAR30": [6.2, 5.8, 5.2, 4.8, 4.5, 4.2],
                "Capital_Adequacy": [18.8, 19.2, 20.5, 21.3, 21.8, 22.1],
                "Dividend_Payout_Ratio": [28.5, 29.2, 30.1, 31.5, 32.8, 33.5],
                "Member_Satisfaction": [75, 78, 82, 85, 88, 90],
            }
        )

        col1, col2 = st.columns(2)

        with col1:
            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=historical_data["Year"],
                    y=historical_data["Dividend_Rate"],
                    name="Dividend Rate (%)",
                    line=dict(color="#10b981", width=4),
                    yaxis="y",
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=historical_data["Year"],
                    y=historical_data["Net_Surplus_KES_M"],
                    name="Net Surplus (KES M)",
                    line=dict(color="#3b82f6", width=3),
                    yaxis="y2",
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=historical_data["Year"],
                    y=historical_data["Member_Satisfaction"],
                    name="Member Satisfaction",
                    line=dict(color="#f59e0b", width=2, dash="dot"),
                    yaxis="y3",
                )
            )

            fig.update_layout(
                title="Historical Dividend Performance Trends",
                xaxis_title="Year",
                yaxis=dict(
                    title="Dividend Rate (%)",
                    title_font=dict(color="#10b981"),
                    tickfont=dict(color="#10b981"),
                ),
                yaxis2=dict(
                    title="Net Surplus (KES M)",
                    title_font=dict(color="#3b82f6"),
                    tickfont=dict(color="#3b82f6"),
                    overlaying="y",
                    side="right",
                ),
                yaxis3=dict(
                    title="Member Satisfaction",
                    title_font=dict(color="#f59e0b"),
                    tickfont=dict(color="#f59e0b"),
                    overlaying="y",
                    side="left",
                    position=0.05,
                ),
                hovermode="x unified",
                height=400,
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("##### 🔍 Dividend Performance Correlations")

            correlation_data = historical_data[
                [
                    "Dividend_Rate",
                    "Net_Surplus_KES_M",
                    "Liquidity_Ratio",
                    "PAR30",
                    "Capital_Adequacy",
                    "Dividend_Payout_Ratio",
                ]
            ].corr()

            fig = px.imshow(
                correlation_data,
                text_auto=".2f",
                aspect="auto",
                color_continuous_scale="RdYlGn",
                title="Performance Metric Correlations",
                labels=dict(color="Correlation"),
            )

            st.plotly_chart(fig, use_container_width=True)

            st.markdown("##### 📋 Historical Performance Comparison")

            comparison_df = historical_data.copy()
            comparison_df["Year_Over_Year_Growth"] = (
                comparison_df["Dividend_Rate"].pct_change() * 100
            )
            comparison_df["Payout_Sustainability"] = comparison_df[
                "Dividend_Payout_Ratio"
            ].apply(
                lambda x: "High" if x < 30 else "Moderate" if x < 40 else "Low"
            )

            st.dataframe(
                comparison_df.round(2),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Year": st.column_config.TextColumn("Fiscal Year"),
                    "Dividend_Rate": st.column_config.NumberColumn(
                        "Div Rate %", format="%.2f"
                    ),
                    "Payout_Sustainability": st.column_config.TextColumn(
                        "Sustainability"
                    ),
                },
            )

    def render_agm_preparation_recommendations(self):
        # kept as in your original (logic unchanged)
        st.subheader("🚀 AGM Preparation & Board Recommendations")

        if "dividend_result" not in st.session_state:
            st.info("Please run the dividend calculator first to generate AGM recommendations")
            return

        result = st.session_state.dividend_result

        st.markdown("##### 📋 AGM Dividend Recommendation Paper")

        recommendation = {
            "item": "Dividend Declaration for Financial Year 2023",
            "recommendation": f"Pay a dividend of {result['recommended_dividend_pct']:.2f}% on share capital",
            "amount": f"KES {result['dividend_amount']:,.0f}",
            "payment_date": "30th April 2024",
            "record_date": "15th April 2024",
            "authority": "Board of Directors",
            "rationale": "Based on strong financial performance and compliance with all prudential requirements",
        }

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Recommended Dividend", recommendation["recommendation"])
        with col2:
            st.metric("Total Amount", recommendation["amount"])
        with col3:
            st.metric("Payment Date", recommendation["payment_date"])

        st.markdown("##### 📅 AGM Agenda Items")

        agenda_items = [
            {"item": "1.0", "description": "Confirmation of Previous AGM Minutes", "duration": "10 min"},
            {"item": "2.0", "description": "Annual Financial Statements Presentation", "duration": "30 min"},
            {"item": "3.0", "description": "Auditor's Report", "duration": "20 min"},
            {"item": "4.0", "description": "Board of Directors Report", "duration": "30 min"},
            {"item": "5.0", "description": "Dividend Declaration (Item of Interest)", "duration": "45 min"},
            {"item": "6.0", "description": "Election of Board Members", "duration": "60 min"},
            {"item": "7.0", "description": "Any Other Business", "duration": "15 min"},
        ]

        agenda_df = pd.DataFrame(agenda_items)
        st.dataframe(agenda_df, use_container_width=True, hide_index=True)

        st.markdown("##### 🗳️ Board Voting Simulation")

        col1, col2, col3 = st.columns(3)

        with col1:
            board_size = st.number_input(
                "Board Members Present", min_value=1, max_value=20, value=9
            )
        with col2:
            votes_for = st.slider("Votes in Favor", min_value=0, max_value=board_size, value=7)
        with col3:
            votes_against = board_size - votes_for  # noqa: F841 (kept for clarity)

        if st.button("🏛️ Simulate Board Vote", use_container_width=True):
            if votes_for > (board_size / 2):
                st.success(f"✅ Motion PASSED with {votes_for}/{board_size} votes")
                st.balloons()
            else:
                st.error(f"❌ Motion FAILED with only {votes_for}/{board_size} votes")

        st.markdown("##### 📄 AGM Document Generation")

        if st.button(
            "📋 Generate Dividend Recommendation Paper", use_container_width=True
        ):
            st.success("✅ Dividend recommendation paper generated successfully!")
            st.info(
                "Document includes: Financial analysis, Prudential gate assessment, Dividend calculation, Board recommendation"
            )

        if st.button("📊 Generate Member Communication", use_container_width=True):
            st.success("✅ Member communication templates generated!")
            st.info(
                "Includes: Dividend announcement, Payment schedule, Tax implications, Frequently asked questions"
            )

    def render_dividend_policy_framework(self):
        # kept as in your original
        st.subheader("📋 Dividend Policy Framework")

        policy_framework = {
            "Statutory Requirements": {
                "description": "Legal and regulatory minimum requirements",
                "components": [
                    "Minimum 20% to statutory reserve",
                    "Adequate bad debt provisions",
                    "Compliance with SASRA capital adequacy",
                ],
            },
            "Prudential Gates": {
                "description": "Risk-based restrictions on dividend payments",
                "components": [
                    "Liquidity ratio > 10%",
                    "PAR30 < 15%",
                    "Capital adequacy > regulatory minimum",
                    "Positive net surplus position",
                ],
            },
            "Distribution Limits": {
                "description": "Maximum allowable distributions",
                "components": [
                    "Maximum 7% of share capital",
                    "Adequate operational reserves",
                    "Future capital requirements consideration",
                ],
            },
            "Board Discretion": {
                "description": "Strategic considerations",
                "components": [
                    "Growth investment requirements",
                    "Member expectations",
                    "Market conditions",
                    "Long-term strategic objectives",
                ],
            },
        }

        cols = st.columns(2)
        for i, (category, details) in enumerate(policy_framework.items()):
            with cols[i % 2]:
                st.markdown(
                    f"""
                <div style="background: #f8fafc; padding: 15px; border-radius: 10px; 
                            border-left: 4px solid #f59e0b; margin-bottom: 10px;">
                    <strong>{category}</strong><br>
                    <small>{details['description']}</small><br>
                    <ul style="margin: 10px 0 0 0; padding-left: 20px;">
                        {''.join([f'<li>{component}</li>' for component in details['components']])}
                    </ul>
                </div>
                """,
                    unsafe_allow_html=True,
                )

        st.markdown("##### 📊 Policy Compliance Dashboard")

        compliance_data = pd.DataFrame(
            {
                "Policy Area": [
                    "Statutory Reserve",
                    "Liquidity Gate",
                    "PAR30 Gate",
                    "Capital Adequacy",
                    "Maximum Dividend",
                    "Board Discretion",
                ],
                "Compliance Score": [100, 95, 98, 100, 100, 90],
                "Status": [
                    "✅ Compliant",
                    "✅ Compliant",
                    "✅ Compliant",
                    "✅ Compliant",
                    "✅ Compliant",
                    "⚠️ Review",
                ],
                "Last Review": [
                    "2024-01-15",
                    "2024-01-20",
                    "2024-01-20",
                    "2024-01-15",
                    "2024-01-10",
                    "2023-12-15",
                ],
            }
        )

        fig = px.bar(
            compliance_data,
            x="Policy Area",
            y="Compliance Score",
            color="Status",
            title="Dividend Policy Compliance Status",
            color_discrete_map={
                "✅ Compliant": "#10b981",
                "⚠️ Review": "#f59e0b",
            },
            text=compliance_data["Compliance Score"].apply(lambda x: f"{x}%"),
        )
        st.plotly_chart(fig, use_container_width=True)

    def render_dividend_philosophy(self):
        """Render dividend capacity philosophy framework"""
        with st.expander("📜 Dividend Policy Philosophy", expanded=False):
            cols = st.columns(3)
            for i, (key, value) in enumerate(DIVIDEND_PHILOSOPHY.items()):
                with cols[i % 3]:
                    st.info(f"**{key}:**\n\n{value}")

            st.markdown("---")
            st.markdown(
                """
            **Strategic Dividend Approach:**  
            - **Member Value Creation:** Reward members while ensuring SACCO sustainability  
            - **Prudent Distribution:** Balance dividends with capital retention for growth  
            - **Regulatory Compliance:** Strict adherence to SASRA dividend guidelines  
            - **Transparent Process:** Clear, data-driven dividend recommendations  
            - **Long-term Focus:** Consider future investment needs and strategic objectives  
            - **Stakeholder Alignment:** Balance member expectations with financial prudence
            """
            )

    def run(self):
        """Run the enhanced dividend capacity page"""
        self.render_strategic_header()
        self.render_dividend_philosophy()
        self.render_strategic_kpi_cards()

        st.markdown("---")

        self.render_strategic_tabs()

        # Log dashboard completion (best-effort)
        try:
            self.audit_logger.log_data_access(
                st.session_state.get("username", "unknown"),
                st.session_state.get("role", "unknown"),
                "dividend_capacity_analysis_completed",
            )
        except Exception:
            pass


if __name__ == "__main__":
    page = DividendCapacityPage()
    page.run()