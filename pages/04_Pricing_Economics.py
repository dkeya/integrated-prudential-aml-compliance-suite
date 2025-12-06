# pages/04_Pricing_Economics.py - ENHANCED WITH ENTERPRISE FEATURES
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

# 🔽 LOCAL / PROJECT IMPORTS (unified core)
from core.config import ConfigManager
from core.rbac import RBACManager
from core.audit import audit_logger
from core.sidebar import render_sidebar

# ==============================================
# PRICING ECONOMICS PHILOSOPHY FRAMEWORK
# ==============================================
PRICING_PHILOSOPHY = {
    "Data": "What are our current margins, costs, and market positions across products?",
    "Insights": "Why are certain products under/over performing? What drives pricing elasticity?",
    "Frameworks": "How to optimize using risk-based pricing, value-based pricing, and competitor benchmarking",
    "Actions": "What specific rate adjustments, product repositioning, promotional strategies to implement",
    "Impact": "What value it creates (improved margins, market share growth, member value optimization)",
    "Governance": "How pricing decisions are documented and rate card changes are approved"
}

# 🔐 Guard: must be authenticated to view this page
if not st.session_state.get("authenticated", False):
    st.error("🔐 Please log in to access this page")
    st.stop()

# Render unified sidebar
render_sidebar()


class PricingEconomicsPage:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.rbac_manager = RBACManager()
        # Use shared unified audit logger instance
        self.audit_logger = audit_logger

        try:
            self.config = self.config_manager.load_settings()
        except Exception:
            # Fallback if config manager fails
            self.config = {}

        if not self._check_access():
            st.stop()

    def _check_access(self):
        """Basic RBAC check – fails open if RBAC config is minimal."""
        if not st.session_state.get("authenticated", False):
            st.error("Please login to access this page")
            return False

        has_access = True
        try:
            # If RBAC supports page-level access, use it
            has_access = self.rbac_manager.check_page_access(
                "04_Pricing_Economics.py",
                st.session_state.role,
                self.config,
            )
        except Exception:
            # If method not available, allow access but still log
            has_access = True

        if not has_access:
            st.error("You do not have permission to access this page")
            return False

        # Safe logging
        try:
            self.audit_logger.log_data_access(
                st.session_state.get("username", st.session_state.get("user", "unknown_user")),
                st.session_state.get("role", "Unknown Role"),
                "pricing_economics_intelligence",
            )
        except Exception:
            pass

        return True

    def render_strategic_header(self):
        """Render enterprise-grade strategic header"""
        st.markdown(
            f"""
        <div style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
                    padding: 25px 30px; border-radius: 16px; color: white; margin-bottom: 20px;">
            <h1 style="margin: 0; color: white;">💳 Pricing Intelligence & Economics</h1>
            <p style="margin: 5px 0 0 0; opacity: 0.9; color: #ede9fe;">
            Risk-Based Pricing • Margin Optimization • Competitive Intelligence • Value Creation
            </p>
            <div style="margin-top: 10px; font-size: 0.9rem; opacity: 0.8;">
                <strong>📍</strong> Commercial Strategy > Pricing Analytics | 
                <strong>🏢</strong> {st.session_state.get('tenant', 'Central SACCO')} |
                <strong>📅</strong> {datetime.now().strftime('%d %B %Y')} |
                <strong>👤</strong> {st.session_state.get('role', 'Commercial Manager')}
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Pricing Status Marquee
        self.render_pricing_status_marquee()

    def render_pricing_status_marquee(self):
        """Render real-time pricing status marquee"""
        status_messages = [
            "💰 Net Interest Margin: 8.4% (Target: 8.5%) | 📊 Average Loan Yield: 14.2% | 🏦 Deposit Cost: 5.8%",
            "🎯 Pricing Efficiency: 86% | ⚡ Most Profitable Product: Business Loans (4.1% margin)",
            "📈 Market Position: Competitive in 4/5 products | 🔍 Underperforming: Personal Loans vs market",
            "🚀 Next Review: Loan pricing optimization due 15 Feb | 📋 Strategy: Risk-based pricing implementation",
        ]

        st.markdown(
            f"""
        <div style="background: linear-gradient(90deg, #8b5cf6 0%, #7c3aed 100%); 
                    padding: 12px 20px; border-radius: 12px; margin-bottom: 24px;
                    border-left: 5px solid #a78bfa;">
            <marquee behavior="scroll" direction="left" scrollamount="4"
                     style="font-size: 0.95rem; font-weight: 500; color: white;">
                {' • '.join(status_messages)}
            </marquee>
        </div>
        """,
            unsafe_allow_html=True,
        )

    def render_strategic_kpi_cards(self):
        """Render strategic pricing KPIs"""
        st.markdown("### 🎯 Pricing Performance Indicators")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                label="💰 Net Interest Margin",
                value="8.4%",
                delta="+0.2%",
                help="Net interest income / earning assets",
            )
            st.caption("Target: 8.5%")

        with col2:
            st.metric(
                label="📊 Average Loan Yield",
                value="14.2%",
                delta="+0.3%",
                help="Weighted average loan yield",
            )
            st.caption("Risk-adjusted: 15.1%")

        with col3:
            st.metric(
                label="🏦 Average Deposit Cost",
                value="5.8%",
                delta="-0.1%",
                delta_color="inverse",
                help="Weighted average deposit cost",
            )
            st.caption("Market: 6.2%")

        with col4:
            st.metric(
                label="🎯 Pricing Efficiency",
                value="86%",
                delta="+2%",
                help="Actual vs optimal pricing ratio",
            )
            st.caption("Improvement needed")

        with col5:
            st.metric(
                label="📈 Market Competitiveness",
                value="4/5 products",
                delta="+1 product",
                help="Products with competitive rates",
            )
            st.caption("Competitive positioning")

    def render_strategic_tabs(self):
        """Render strategic analysis tabs"""
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            [
                "💳 Current Pricing Intelligence",
                "🎯 Risk-Based Pricing Optimizer",
                "🏆 Competitive Intelligence",
                "💰 Deposit Pricing Strategy",
                "🚀 Strategic Pricing Roadmap",
            ]
        )

        with tab1:
            self.render_current_pricing_intelligence()

        with tab2:
            self.render_risk_based_pricing_optimizer()

        with tab3:
            self.render_competitive_intelligence()

        with tab4:
            self.render_deposit_pricing_strategy()

        with tab5:
            self.render_strategic_pricing_roadmap()

    def render_current_pricing_intelligence(self):
        """Render comprehensive current pricing analysis"""
        st.subheader("💳 Current Pricing Intelligence Dashboard")

        # Enhanced product pricing data
        products_data = pd.DataFrame(
            {
                "Product": [
                    "Personal Loans",
                    "Business Loans",
                    "Asset Finance",
                    "Emergency Loans",
                    "School Fees",
                ],
                "Current_Rate": [13.5, 15.2, 12.8, 18.5, 10.5],
                "Risk_Adjusted_Rate": [14.1, 16.8, 13.2, 20.2, 10.8],
                "Market_Average": [14.5, 16.0, 13.5, 19.0, 11.0],
                "Volume_KES_M": [85.2, 92.5, 45.3, 12.8, 9.9],
                "Profit_Margin": [3.2, 4.1, 2.8, 5.2, 1.8],
                "Market_Share": [18.5, 22.1, 15.8, 8.2, 12.5],
                "Growth_Rate": [12.5, 15.3, 10.8, 25.1, 8.7],
                "Customer_Satisfaction": [88, 85, 90, 82, 92],
                "Risk_Category": ["Medium", "High", "Low", "Very High", "Low"],
            }
        )

        # Strategic filters
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        with col_filter1:
            view_type = st.selectbox(
                "Analysis View",
                ["Rates & Margins", "Volume & Growth", "Market Position", "Customer Value"],
                key="pricing_view",
            )
        with col_filter2:
            sort_by = st.selectbox(
                "Sort By",
                ["Profit Margin", "Volume", "Market Gap", "Growth Rate"],
                key="pricing_sort",
            )
        with col_filter3:
            risk_filter = st.multiselect(
                "Risk Category",
                products_data["Risk_Category"].unique(),
                default=products_data["Risk_Category"].unique(),
                key="risk_filter",
            )

        # Filter data
        filtered_data = products_data[products_data["Risk_Category"].isin(risk_filter)]

        col1, col2 = st.columns(2)

        with col1:
            # Enhanced pricing comparison
            st.markdown("##### 📊 Pricing Strategy Matrix")

            fig = px.scatter(
                filtered_data,
                x="Current_Rate",
                y="Profit_Margin",
                size="Volume_KES_M",
                color="Risk_Category",
                hover_name="Product",
                title="Profitability vs Rate Analysis (Size = Volume, Color = Risk)",
                size_max=50,
                color_discrete_sequence=["#10b981", "#f59e0b", "#ef4444", "#7c3aed"],
                labels={
                    "Current_Rate": "Current Rate (%)",
                    "Profit_Margin": "Profit Margin (%)",
                    "Volume_KES_M": "Portfolio Volume (KES M)",
                    "Risk_Category": "Risk Level",
                },
            )

            # Add optimal zone
            fig.add_shape(
                type="rect",
                x0=12,
                x1=16,
                y0=3,
                y1=5,
                line=dict(color="green", width=1, dash="dot"),
                fillcolor="rgba(0, 255, 0, 0.1)",
            )
            fig.add_annotation(
                x=14,
                y=4,
                text="Optimal Zone",
                showarrow=False,
                font=dict(color="green", size=10),
            )

            st.plotly_chart(fig, use_container_width=True)

            # Rate gap analysis
            st.markdown("##### ⚖️ Rate Gap Analysis")

            filtered_data["Rate_Gap_vs_Market"] = (
                filtered_data["Current_Rate"] - filtered_data["Market_Average"]
            )
            filtered_data["Rate_Gap_vs_Risk_Adjusted"] = (
                filtered_data["Current_Rate"] - filtered_data["Risk_Adjusted_Rate"]
            )

            fig = go.Figure(
                data=[
                    go.Bar(
                        name="vs Market",
                        x=filtered_data["Product"],
                        y=filtered_data["Rate_Gap_vs_Market"],
                        marker_color=[
                            "red" if x < 0 else "green"
                            for x in filtered_data["Rate_Gap_vs_Market"]
                        ],
                    ),
                    go.Bar(
                        name="vs Risk Adjusted",
                        x=filtered_data["Product"],
                        y=filtered_data["Rate_Gap_vs_Risk_Adjusted"],
                        marker_color=[
                            "red" if x < 0 else "green"
                            for x in filtered_data["Rate_Gap_vs_Risk_Adjusted"]
                        ],
                    ),
                ]
            )

            fig.update_layout(
                title="Rate Gap Analysis (Negative = Below Optimal)",
                xaxis_title="Product",
                yaxis_title="Rate Gap (%)",
                barmode="group",
                xaxis_tickangle=-45,
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Portfolio performance metrics
            st.markdown("##### 📈 Portfolio Performance Dashboard")

            performance_metrics = []

            for _, product in filtered_data.iterrows():
                # Calculate performance score (0-100)
                score = (
                    (product["Profit_Margin"] / filtered_data["Profit_Margin"].max() * 30)
                    + (product["Growth_Rate"] / filtered_data["Growth_Rate"].max() * 25)
                    + (product["Customer_Satisfaction"] / 100 * 25)
                    + (
                        (product["Current_Rate"] - product["Risk_Adjusted_Rate"])
                        / 5
                        * 20
                    )
                )

                performance_metrics.append(
                    {
                        "Product": product["Product"],
                        "Profit Margin": f"{product['Profit_Margin']:.1f}%",
                        "Growth Rate": f"{product['Growth_Rate']:.1f}%",
                        "Customer Satisfaction": f"{product['Customer_Satisfaction']}/100",
                        "Rate Alignment": (
                            "Optimal"
                            if abs(
                                product["Current_Rate"]
                                - product["Risk_Adjusted_Rate"]
                            )
                            < 0.5
                            else "High"
                            if product["Current_Rate"]
                            > product["Risk_Adjusted_Rate"]
                            else "Low"
                        ),
                        "Performance Score": min(100, max(0, score)),
                    }
                )

            performance_df = pd.DataFrame(performance_metrics)

            # Sort by selected criteria
            if sort_by == "Profit Margin":
                performance_df = performance_df.sort_values(
                    "Performance Score", ascending=False
                )
            elif sort_by == "Volume":
                performance_df = performance_df.merge(
                    filtered_data[["Product", "Volume_KES_M"]], on="Product"
                )
                performance_df = performance_df.sort_values(
                    "Volume_KES_M", ascending=False
                )

            def color_rate_alignment(val):
                if val == "Optimal":
                    return "background-color: #bbf7d0"
                elif val == "High":
                    return "background-color: #fecaca"
                else:
                    return "background-color: #fed7aa"

            styled_df = performance_df.style.applymap(
                color_rate_alignment, subset=["Rate Alignment"]
            )

            st.dataframe(
                styled_df, use_container_width=True, hide_index=True, height=400
            )

            # Performance distribution
            st.markdown("##### 📊 Performance Distribution")

            fig = px.box(
                filtered_data,
                y=["Current_Rate", "Profit_Margin", "Growth_Rate"],
                title="Product Performance Distribution",
                points="all",
                color_discrete_sequence=["#8b5cf6", "#10b981", "#f59e0b"],
            )

            fig.update_layout(yaxis_title="Percentage (%)", showlegend=False)

            st.plotly_chart(fig, use_container_width=True)

    # ------------- INTERNAL PRICING ENGINE (replaces external PricingOptimizer) -------------
    def _calculate_comprehensive_pricing(
        self,
        product_type: str,
        loan_amount: float,
        loan_term: int,
        risk_category: str,
        credit_score: int,
        debt_to_income: float,
        collateral_coverage: float,
        cost_of_funds: float,
        operating_cost: float,
        target_roa: float,
        capital_charge: float,
        risk_premium: float,
        market_rate: float,
        competitive_positioning: str,
    ) -> dict:
        """
        Simple, transparent risk-based pricing engine that mirrors the structure
        of the previous PricingOptimizer output, but is self-contained.
        All rates are decimals (e.g. 0.145 for 14.5%).
        """

        # Base risk provision by category (aligned with later sensitivity logic)
        base_provisions = {"Low": 0.005, "Medium": 0.015, "High": 0.030, "Very High": 0.050}
        risk_provision = base_provisions.get(risk_category, 0.015)

        # Core building blocks
        break_even_rate = cost_of_funds + operating_cost + capital_charge + risk_provision
        base_rate = break_even_rate + target_roa  # risk-neutral target
        cost_plus_risk = break_even_rate + target_roa + risk_premium

        # Start from cost-plus-risk as internal baseline
        recommended_rate = cost_plus_risk

        # Positioning vs market
        if competitive_positioning == "Price Leader":
            # Try to sit slightly below market but never below break-even+small margin
            target_rate = min(market_rate - 0.005, recommended_rate)
            min_safe = break_even_rate + 0.002
            recommended_rate = max(target_rate, min_safe)
        elif competitive_positioning == "Premium Position":
            # Ensure a small premium over market
            target_rate = max(market_rate + 0.005, recommended_rate)
            recommended_rate = max(target_rate, break_even_rate + target_roa)
        else:  # Market Match
            # Blend cost-plus view with market reference
            target_rate = max(break_even_rate + 0.005, market_rate)
            recommended_rate = 0.6 * recommended_rate + 0.4 * target_rate

        strategic_adjustment = recommended_rate - cost_plus_risk

        # Risk-adjusted return (after risk premium & provisions)
        risk_adjusted_return = (
            recommended_rate
            - cost_of_funds
            - operating_cost
            - capital_charge
            - risk_provision
            - risk_premium
        )

        # Market competitiveness flag
        market_competitive = abs(recommended_rate - market_rate) <= 0.01

        # Monthly payment (standard amortization)
        monthly_rate = recommended_rate / 12
        n = max(int(loan_term), 1)

        if monthly_rate > 0:
            monthly_payment = loan_amount * (
                monthly_rate * (1 + monthly_rate) ** n
            ) / ((1 + monthly_rate) ** n - 1)
        else:
            monthly_payment = loan_amount / n

        return {
            "product_type": product_type,
            "loan_amount": loan_amount,
            "loan_term": loan_term,
            "risk_category": risk_category,
            "credit_score": credit_score,
            "debt_to_income": debt_to_income,
            "collateral_coverage": collateral_coverage,
            "cost_of_funds": cost_of_funds,
            "operating_cost": operating_cost,
            "target_roa": target_roa,
            "capital_charge": capital_charge,
            "risk_premium": risk_premium,
            "risk_provision": risk_provision,
            "break_even_rate": break_even_rate,
            "base_rate": base_rate,
            "recommended_rate": recommended_rate,
            "market_rate": market_rate,
            "competitive_positioning": competitive_positioning,
            "strategic_adjustment": strategic_adjustment,
            "risk_adjusted_return": risk_adjusted_return,
            "market_competitive": market_competitive,
            "monthly_payment": monthly_payment,
        }

    # -------------------------------------------------------------------------
    # RISK-BASED PRICING OPTIMIZER UI
    # -------------------------------------------------------------------------
    def render_risk_based_pricing_optimizer(self):
        """Render enhanced risk-based pricing optimizer"""
        st.subheader("🎯 Risk-Based Pricing Optimizer")

        col1, col2 = st.columns(2)

        with col1:
            # Enhanced loan parameters
            st.markdown("#### 📝 Loan Parameters")

            product_type = st.selectbox(
                "Product Type",
                [
                    "Personal Loan",
                    "Business Loan",
                    "Asset Finance",
                    "Emergency Loan",
                    "School Fees",
                ],
                help="Select the loan product to price",
                key="pricing_product_type",
            )

            loan_amount = st.number_input(
                "Loan Amount (KES)",
                min_value=10000.0,
                value=500000.0,
                step=10000.0,
                help="Requested loan amount",
                key="pricing_loan_amount",
            )

            loan_term = st.slider(
                "Loan Term (Months)",
                min_value=1,
                max_value=84,
                value=24,
                help="Loan repayment period in months",
                key="pricing_loan_term",
            )

            # Enhanced risk assessment
            st.markdown("#### ⚠️ Risk Assessment")

            risk_category = st.select_slider(
                "Risk Category",
                options=["Low", "Medium", "High", "Very High"],
                value="Medium",
                help="Borrower risk assessment category",
                key="pricing_risk_category",
            )

            credit_score = st.slider(
                "Credit Score",
                min_value=300,
                max_value=850,
                value=650,
                step=10,
                help="Borrower credit score",
                key="pricing_credit_score",
            )

            debt_to_income = st.slider(
                "Debt-to-Income Ratio (%)",
                min_value=0.0,
                max_value=100.0,
                value=35.0,
                step=1.0,
                help="Borrower's debt to income ratio",
                key="pricing_dti",
            )

            collateral_coverage = st.slider(
                "Collateral Coverage (%)",
                min_value=0.0,
                max_value=200.0,
                value=120.0,
                step=5.0,
                help="Collateral value as percentage of loan amount",
                key="pricing_collateral",
            )

        with col2:
            # Enhanced cost parameters
            st.markdown("#### ⚙️ Cost & Margin Parameters")

            cost_of_funds = st.slider(
                "Cost of Funds (%)",
                min_value=1.0,
                max_value=10.0,
                value=5.8,
                step=0.1,
                help="Weighted average cost of funds",
                key="pricing_cof",
            )

            operating_cost = st.slider(
                "Operating Cost (%)",
                min_value=0.5,
                max_value=5.0,
                value=2.2,
                step=0.1,
                help="Operating cost as percentage of loan amount",
                key="pricing_opex",
            )

            target_roa = st.slider(
                "Target Return on Assets (%)",
                min_value=0.5,
                max_value=5.0,
                value=1.8,
                step=0.1,
                help="Desired return on assets",
                key="pricing_roa",
            )

            capital_charge = st.slider(
                "Capital Charge (%)",
                min_value=0.5,
                max_value=3.0,
                value=1.5,
                step=0.1,
                help="Cost of regulatory capital",
                key="pricing_capital",
            )

            # Dynamic risk premium (based on helper methods below)
            base_risk_premium = self._get_risk_premium(risk_category)
            credit_adjustment = self._get_credit_adjustment(credit_score)
            dti_adjustment = self._get_dti_adjustment(debt_to_income)
            collateral_adjustment = self._get_collateral_adjustment(collateral_coverage)

            total_risk_premium = (
                base_risk_premium
                + credit_adjustment
                + dti_adjustment
                + collateral_adjustment
            )

            st.markdown("#### 🎯 Calculated Risk Premium")

            risk_premium_breakdown = pd.DataFrame(
                {
                    "Component": [
                        "Base Risk",
                        "Credit Score",
                        "DTI Ratio",
                        "Collateral",
                        "Total",
                    ],
                    "Premium (%)": [
                        base_risk_premium,
                        credit_adjustment,
                        dti_adjustment,
                        collateral_adjustment,
                        total_risk_premium,
                    ],
                }
            )

            st.dataframe(
                risk_premium_breakdown.style.format({"Premium (%)": "{:.1f}%"}),
                use_container_width=True,
                hide_index=True,
            )

            # Market alignment
            st.markdown("#### 🌍 Market Alignment")

            market_rate = st.slider(
                "Market Reference Rate (%)",
                min_value=5.0,
                max_value=25.0,
                value=14.5,
                step=0.1,
                help="Competitive market rate for similar product",
                key="pricing_market_rate",
            )

            competitive_positioning = st.select_slider(
                "Desired Competitive Position",
                options=["Price Leader", "Market Match", "Premium Position"],
                value="Market Match",
                help="Strategic positioning relative to competitors",
                key="pricing_position",
            )

        # Calculate optimal pricing
        col_calc1, col_calc2, col_calc3 = st.columns([2, 1, 2])
        with col_calc2:
            if st.button(
                "🚀 Calculate Optimal Pricing",
                type="primary",
                use_container_width=True,
                key="calculate_pricing_btn",
            ):
                with st.spinner("🔍 Calculating risk-based optimal pricing..."):
                    pricing_result = self._calculate_comprehensive_pricing(
                        product_type=product_type,
                        loan_amount=loan_amount,
                        loan_term=loan_term,
                        risk_category=risk_category,
                        credit_score=credit_score,
                        debt_to_income=debt_to_income / 100,
                        collateral_coverage=collateral_coverage / 100,
                        cost_of_funds=cost_of_funds / 100,
                        operating_cost=operating_cost / 100,
                        target_roa=target_roa / 100,
                        capital_charge=capital_charge / 100,
                        risk_premium=total_risk_premium / 100,
                        market_rate=market_rate / 100,
                        competitive_positioning=competitive_positioning,
                    )

                    st.session_state.pricing_result = pricing_result
                    st.success("✅ Optimal pricing calculated successfully!")

        # Display pricing results if available
        if "pricing_result" in st.session_state:
            self.render_pricing_results(st.session_state.pricing_result)

    def _get_risk_premium(self, risk_category: str) -> float:
        """Get base risk premium based on category (in % points)."""
        premiums = {
            "Low": 1.5,
            "Medium": 3.0,
            "High": 6.0,
            "Very High": 9.0,
        }
        return premiums.get(risk_category, 3.0)

    def _get_credit_adjustment(self, credit_score: int) -> float:
        """Get credit score adjustment (in % points)."""
        if credit_score >= 750:
            return -1.5
        elif credit_score >= 700:
            return -0.5
        elif credit_score >= 650:
            return 0.0
        elif credit_score >= 600:
            return 1.0
        else:
            return 2.5

    def _get_dti_adjustment(self, dti: float) -> float:
        """Get DTI ratio adjustment (in % points)."""
        if dti <= 30:
            return -0.5
        elif dti <= 40:
            return 0.0
        elif dti <= 50:
            return 1.0
        else:
            return 2.0

    def _get_collateral_adjustment(self, collateral: float) -> float:
        """Get collateral coverage adjustment (in % points)."""
        if collateral >= 150:
            return -2.0
        elif collateral >= 120:
            return -1.0
        elif collateral >= 100:
            return 0.0
        elif collateral >= 80:
            return 1.0
        else:
            return 2.5

    def render_pricing_results(self, result: dict):
        """Render enhanced pricing calculation results"""
        st.markdown("---")
        st.subheader("💰 Optimal Pricing Results")

        # Key metrics dashboard
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="🎯 Recommended Rate",
                value=f"{result['recommended_rate'] * 100:.2f}%",
                delta=f"{result['recommended_rate'] * 100 - result['market_rate'] * 100:.2f}% vs market",
                help="Optimal risk-based interest rate",
            )
            st.caption(f"Strategy: {result.get('competitive_positioning', 'Market Match')}")

        with col2:
            st.metric(
                label="📊 Base Break-even Rate",
                value=f"{result['break_even_rate'] * 100:.2f}%",
                help="Minimum rate to cover all costs",
            )
            st.caption(
                f"Margin: {(result['recommended_rate'] - result['break_even_rate']) * 100:.2f}%"
            )

        with col3:
            st.metric(
                label="⚡ Risk-Adjusted Return",
                value=f"{result['risk_adjusted_return'] * 100:.2f}%",
                help="Expected return after risk adjustments",
            )
            st.caption(f"Target: {result['target_roa'] * 100:.2f}%")

        with col4:
            competitiveness = result.get("market_competitive", False)
            status_color = "#10b981" if competitiveness else "#ef4444"
            status_text = "✅ Competitive" if competitiveness else "⚠️ Review Needed"
            st.markdown(
                f"""
            <div style="background-color: {status_color}20; padding: 15px; border-radius: 10px; 
                        border-left: 4px solid {status_color};">
                <h4 style="margin: 0; color: {status_color};">🏆 Market Position</h4>
                <p style="margin: 5px 0 0 0; font-size: 1.2rem; font-weight: bold;">
                {status_text}
                </p>
                <p style="margin: 0; font-size: 0.9rem;">
                vs Market: {result['market_rate'] * 100:.2f}%
                </p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Enhanced pricing breakdown
        st.markdown("#### 📊 Comprehensive Pricing Breakdown")

        col_break1, col_break2 = st.columns(2)

        with col_break1:
            # Component breakdown bar chart
            components_data = pd.DataFrame(
                {
                    "Component": [
                        "Cost of Funds",
                        "Operating Cost",
                        "Capital Charge",
                        "Risk Provision",
                        "Target Return",
                        "Risk Premium",
                        "Strategic Adjustment",
                    ],
                    "Percentage": [
                        result["cost_of_funds"] * 100,
                        result["operating_cost"] * 100,
                        result.get("capital_charge", 0) * 100,
                        result.get("risk_provision", 0) * 100,
                        result["target_roa"] * 100,
                        result["risk_premium"] * 100,
                        result.get("strategic_adjustment", 0) * 100,
                    ],
                }
            )

            fig = px.bar(
                components_data,
                x="Component",
                y="Percentage",
                title="Interest Rate Component Breakdown",
                color="Component",
                color_discrete_sequence=px.colors.qualitative.Set3,
                text=components_data["Percentage"].apply(lambda x: f"{x:.1f}%"),
            )

            fig.update_layout(xaxis_tickangle=-45, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with col_break2:
            # Loan affordability analysis
            st.markdown("##### 💰 Loan Affordability Analysis")

            monthly_payment = result.get("monthly_payment", 0)
            annual_income = st.number_input(
                "Estimated Annual Income (KES)",
                min_value=0.0,
                value=1_200_000.0,
                step=10_000.0,
                help="Borrower's annual income",
                key="affordability_income",
            )

            if annual_income > 0:
                monthly_income = annual_income / 12
                payment_ratio = (monthly_payment / monthly_income) * 100

                fig = go.Figure(
                    go.Indicator(
                        mode="gauge+number",
                        value=payment_ratio,
                        title={"text": "Payment-to-Income Ratio"},
                        gauge={
                            "axis": {"range": [None, 50]},
                            "bar": {"color": "darkblue"},
                            "steps": [
                                {"range": [0, 20], "color": "lightgreen"},
                                {"range": [20, 35], "color": "yellow"},
                                {"range": [35, 50], "color": "red"},
                            ],
                            "threshold": {
                                "line": {"color": "red", "width": 4},
                                "thickness": 0.75,
                                "value": 35,
                            },
                        },
                    )
                )

                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)

                if payment_ratio > 35:
                    st.error("⚠️ **High Risk**: Payment exceeds 35% of income")
                elif payment_ratio > 20:
                    st.warning("⚠️ **Moderate Risk**: Payment 20-35% of income")
                else:
                    st.success("✅ **Low Risk**: Payment below 20% of income")

        # Sensitivity analysis
        st.markdown("#### 📈 Advanced Sensitivity Analysis")

        sensitivity_tab1, sensitivity_tab2, sensitivity_tab3 = st.tabs(
            ["Cost Sensitivity", "Risk Sensitivity", "Market Sensitivity"]
        )

        # --- Cost Sensitivity (single, cleaned block – no PricingOptimizer dependency) ---
        with sensitivity_tab1:
            col_sens1, col_sens2 = st.columns(2)

            with col_sens1:
                # Cost of funds sensitivity
                cof_range = np.linspace(4.0, 8.0, 9)
                rates_cof = []
                for cof in cof_range:
                    new_rate = result["recommended_rate"] + (
                        cof / 100 - result["cost_of_funds"]
                    )
                    rates_cof.append(new_rate * 100)

                fig = px.line(
                    x=cof_range,
                    y=rates_cof,
                    title="Sensitivity to Cost of Funds",
                    labels={"x": "Cost of Funds (%)", "y": "Adjusted Rate (%)"},
                )
                fig.add_vline(
                    x=result["cost_of_funds"] * 100, line_dash="dash", line_color="red"
                )
                fig.add_annotation(
                    x=result["cost_of_funds"] * 100,
                    y=rates_cof[len(rates_cof) // 2],
                    text=f"Current: {result['cost_of_funds']*100:.2f}%",
                    showarrow=False,
                    font=dict(color="red"),
                )
                st.plotly_chart(fig, use_container_width=True)

            with col_sens2:
                # Operating cost sensitivity
                opex_range = np.linspace(1.5, 3.5, 9)
                rates_opex = []
                for opex in opex_range:
                    new_rate = result["recommended_rate"] + (
                        opex / 100 - result["operating_cost"]
                    )
                    rates_opex.append(new_rate * 100)

                fig = px.line(
                    x=opex_range,
                    y=rates_opex,
                    title="Sensitivity to Operating Costs",
                    labels={"x": "Operating Cost (%)", "y": "Adjusted Rate (%)"},
                )
                fig.add_vline(
                    x=result["operating_cost"] * 100,
                    line_dash="dash",
                    line_color="red",
                )
                fig.add_annotation(
                    x=result["operating_cost"] * 100,
                    y=rates_opex[len(rates_opex) // 2],
                    text=f"Current: {result['operating_cost']*100:.2f}%",
                    showarrow=False,
                    font=dict(color="red"),
                )
                st.plotly_chart(fig, use_container_width=True)

        # --- Risk Sensitivity ---
        with sensitivity_tab2:
            col_sens3, col_sens4 = st.columns(2)

            with col_sens3:
                # Risk premium sensitivity
                risk_range = np.linspace(-0.05, 0.05, 11)  # ±5%
                rates_risk = []

                for risk_change in risk_range:
                    adjusted_rate = result["recommended_rate"] + risk_change
                    rates_risk.append(adjusted_rate * 100)

                fig = px.line(
                    x=risk_range * 100,  # Convert to percentage
                    y=rates_risk,
                    title="Sensitivity to Risk Premium Changes",
                    labels={
                        "x": "Risk Premium Change (%)",
                        "y": "Adjusted Rate (%)",
                    },
                )
                fig.add_vline(x=0, line_dash="dash", line_color="red")
                fig.add_annotation(
                    x=0,
                    y=rates_risk[len(rates_risk) // 2],
                    text=f"Base: {result['risk_premium']*100:.2f}%",
                    showarrow=False,
                    font=dict(color="red"),
                )
                st.plotly_chart(fig, use_container_width=True)

            with col_sens4:
                # Credit score sensitivity
                credit_scores = np.linspace(300, 850, 11)
                rates_credit = []

                for score in credit_scores:
                    if score >= 750:
                        adjustment = -0.015
                    elif score >= 700:
                        adjustment = -0.005
                    elif score >= 650:
                        adjustment = 0.000
                    elif score >= 600:
                        adjustment = 0.010
                    else:
                        adjustment = 0.025

                    adjusted_rate = result["recommended_rate"] + adjustment
                    rates_credit.append(adjusted_rate * 100)

                fig = px.line(
                    x=credit_scores,
                    y=rates_credit,
                    title="Sensitivity to Credit Score Changes",
                    labels={"x": "Credit Score", "y": "Adjusted Rate (%)"},
                )
                fig.add_vline(
                    x=result["credit_score"], line_dash="dash", line_color="red"
                )
                fig.add_annotation(
                    x=result["credit_score"],
                    y=rates_credit[len(rates_credit) // 2],
                    text=f"Current: {result['credit_score']:.0f}",
                    showarrow=False,
                    font=dict(color="red"),
                )
                st.plotly_chart(fig, use_container_width=True)

            # Risk category impact
            st.markdown("##### ⚠️ Risk Category Impact Analysis")

            risk_categories = ["Low", "Medium", "High", "Very High"]
            risk_rates = []

            for category in risk_categories:
                base_provisions = {
                    "Low": 0.005,
                    "Medium": 0.015,
                    "High": 0.030,
                    "Very High": 0.050,
                }
                base_provision = base_provisions.get(category, 0.015)

                # Credit score adjustment (using current credit score)
                if result["credit_score"] < 600:
                    credit_adjustment = 0.020
                elif result["credit_score"] < 650:
                    credit_adjustment = 0.010
                elif result["credit_score"] < 700:
                    credit_adjustment = 0.005
                elif result["credit_score"] < 750:
                    credit_adjustment = 0.000
                else:
                    credit_adjustment = -0.005

                total_risk = base_provision + credit_adjustment
                adjusted_rate = (
                    result["base_rate"]
                    + total_risk
                    + result.get("strategic_adjustment", 0)
                )
                risk_rates.append(adjusted_rate * 100)

            fig = px.bar(
                x=risk_categories,
                y=risk_rates,
                title="Rate Variation by Risk Category",
                labels={"x": "Risk Category", "y": "Interest Rate (%)"},
                color=risk_rates,
                color_continuous_scale="RdYlGn_r",
            )

            # Highlight current risk category
            current_idx = risk_categories.index(result["risk_category"])
            fig.add_shape(
                type="rect",
                x0=current_idx - 0.4,
                x1=current_idx + 0.4,
                y0=0,
                y1=max(risk_rates) * 1.1,
                line=dict(color="gold", width=2),
                fillcolor="rgba(255, 215, 0, 0.1)",
            )

            st.plotly_chart(fig, use_container_width=True)

        # --- Market Sensitivity ---
        with sensitivity_tab3:
            col_sens5, col_sens6 = st.columns(2)

            with col_sens5:
                # Market rate sensitivity
                market_range = np.linspace(-0.03, 0.03, 11)  # ±3%
                rates_market = []

                for market_change in market_range:
                    new_market = result["market_rate"] + market_change

                    if result["competitive_positioning"] == "Price Leader":
                        adjustment = max(
                            new_market - 0.005 - result["recommended_rate"], 0
                        )
                    elif result["competitive_positioning"] == "Premium Position":
                        adjustment = (
                            new_market + 0.005 - result["recommended_rate"]
                        )
                    else:  # Market Match
                        if abs(result["recommended_rate"] - new_market) > 0.01:
                            adjustment = new_market - result["recommended_rate"]
                        else:
                            adjustment = 0

                    adjusted_rate = result["recommended_rate"] + adjustment
                    rates_market.append(adjusted_rate * 100)

                fig = px.line(
                    x=market_range * 100,
                    y=rates_market,
                    title="Sensitivity to Market Rate Changes",
                    labels={"x": "Market Rate Change (%)", "y": "Adjusted Rate (%)"},
                )
                fig.add_vline(x=0, line_dash="dash", line_color="red")
                fig.add_annotation(
                    x=0,
                    y=rates_market[len(rates_market) // 2],
                    text=f"Base Market: {result['market_rate']*100:.2f}%",
                    showarrow=False,
                    font=dict(color="red"),
                )
                st.plotly_chart(fig, use_container_width=True)

            with col_sens6:
                # Competitive positioning sensitivity
                positions = ["Price Leader", "Market Match", "Premium Position"]
                rates_position = []

                for position in positions:
                    if position == "Price Leader":
                        adjustment = max(
                            result["market_rate"] - 0.005 - result["recommended_rate"],
                            0,
                        )
                    elif position == "Premium Position":
                        adjustment = (
                            result["market_rate"] + 0.005 - result["recommended_rate"]
                        )
                    else:  # Market Match
                        if abs(result["recommended_rate"] - result["market_rate"]) > 0.01:
                            adjustment = (
                                result["market_rate"] - result["recommended_rate"]
                            )
                        else:
                            adjustment = 0

                    adjusted_rate = result["recommended_rate"] + adjustment
                    rates_position.append(adjusted_rate * 100)

                fig = px.bar(
                    x=positions,
                    y=rates_position,
                    title="Impact of Competitive Positioning",
                    labels={
                        "x": "Positioning Strategy",
                        "y": "Adjusted Rate (%)",
                    },
                    color=rates_position,
                    color_continuous_scale="RdYlGn_r",
                )

                # Add current position highlight
                current_idx = positions.index(
                    result.get("competitive_positioning", "Market Match")
                )
                fig.add_shape(
                    type="rect",
                    x0=current_idx - 0.4,
                    x1=current_idx + 0.4,
                    y0=0,
                    y1=max(rates_position) * 1.1,
                    line=dict(color="gold", width=2),
                    fillcolor="rgba(255, 215, 0, 0.1)",
                )

                st.plotly_chart(fig, use_container_width=True)

            # Market competitiveness gauge
            st.markdown("##### 🏆 Market Competitiveness Analysis")

            competitiveness_score = 100 - abs(
                result["recommended_rate"] - result["market_rate"]
            ) * 1000
            competitiveness_score = max(0, min(100, competitiveness_score))

            col_gauge1, col_gauge2 = st.columns([2, 1])

            with col_gauge1:
                fig = go.Figure(
                    go.Indicator(
                        mode="gauge+number",
                        value=competitiveness_score,
                        title={"text": "Competitiveness Score"},
                        gauge={
                            "axis": {"range": [None, 100]},
                            "bar": {"color": "darkblue"},
                            "steps": [
                                {"range": [0, 50], "color": "red"},
                                {"range": [50, 75], "color": "yellow"},
                                {"range": [75, 100], "color": "green"},
                            ],
                            "threshold": {
                                "line": {"color": "black", "width": 4},
                                "thickness": 0.75,
                                "value": 75,
                            },
                        },
                    )
                )

                fig.update_layout(height=250)
                st.plotly_chart(fig, use_container_width=True)

            with col_gauge2:
                st.markdown("#### 📊 Gap Analysis")

                gap_data = {
                    "Metric": [
                        "Rate vs Market",
                        "Risk Premium",
                        "Strategic Adjustment",
                        "Total Gap",
                    ],
                    "Value": [
                        f"{(result['recommended_rate'] - result['market_rate'])*100:+.2f}%",
                        f"{result['risk_premium']*100:.2f}%",
                        f"{result.get('strategic_adjustment', 0)*100:+.2f}%",
                        f"{(result['recommended_rate'] - result['break_even_rate'])*100:.2f}%",
                    ],
                    "Status": [
                        "✅ Competitive"
                        if abs(result["recommended_rate"] - result["market_rate"])
                        <= 0.01
                        else "⚠️ Review",
                        "✅ Appropriate"
                        if 0.01 <= result["risk_premium"] <= 0.05
                        else "⚠️ Review",
                        "✅ Optimal"
                        if abs(result.get("strategic_adjustment", 0)) <= 0.005
                        else "⚠️ Adjust",
                        "✅ Profitable"
                        if result["recommended_rate"] > result["break_even_rate"]
                        else "❌ Loss",
                    ],
                }

                gap_df = pd.DataFrame(gap_data)
                st.dataframe(gap_df, use_container_width=True, hide_index=True)

            # Strategic recommendations
            st.markdown("##### 💡 Strategic Recommendations")

            recommendations = []

            # Market position recommendation
            market_gap = result["recommended_rate"] - result["market_rate"]
            if market_gap > 0.02:
                recommendations.append(
                    "📉 **Consider rate reduction**: Rate is >2% above market"
                )
            elif market_gap < -0.02:
                recommendations.append(
                    "📈 **Consider rate increase**: Rate is >2% below market"
                )
            else:
                recommendations.append(
                    "✅ **Maintain current positioning**: Rate is within market range"
                )

            # Risk premium recommendation
            if result["risk_premium"] > 0.05:
                recommendations.append(
                    "⚡ **Review risk premium**: Premium >5% may reduce competitiveness"
                )
            elif result["risk_premium"] < 0.01:
                recommendations.append(
                    "⚠️ **Increase risk coverage**: Premium <1% may not cover risks"
                )

            # Profitability check
            if result["recommended_rate"] < result["break_even_rate"]:
                recommendations.append(
                    "🚨 **CRITICAL**: Rate below break-even - Immediate action required"
                )

            for rec in recommendations:
                st.info(rec)

    # -------------------------------------------------------------------------
    # COMPETITIVE INTELLIGENCE
    # -------------------------------------------------------------------------
    def render_competitive_intelligence(self):
        """Render comprehensive competitive intelligence"""
        st.subheader("🏆 Competitive Intelligence Dashboard")

        competitors = [
            "SACCO A",
            "SACCO B",
            "Commercial Bank",
            "Microfinance",
            "Fintech",
            "Market Average",
            "Our SACCO",
        ]
        products = [
            "Personal Loan",
            "Business Loan",
            "Asset Finance",
            "Emergency Loan",
            "School Fees Loan",
        ]

        competitor_data = []
        for competitor in competitors:
            for product in products:
                base_rates = {
                    "Personal Loan": 14.0,
                    "Business Loan": 16.0,
                    "Asset Finance": 13.0,
                    "Emergency Loan": 19.0,
                    "School Fees Loan": 11.0,
                }

                base_rate = base_rates[product]

                if competitor == "Our SACCO":
                    our_rates = {
                        "Personal Loan": 13.5,
                        "Business Loan": 15.2,
                        "Asset Finance": 12.8,
                        "Emergency Loan": 18.5,
                        "School Fees Loan": 10.5,
                    }
                    rate = our_rates[product]
                elif competitor == "Market Average":
                    rate = base_rate
                else:
                    variation = {
                        "SACCO A": np.random.uniform(-1.0, 1.0),
                        "SACCO B": np.random.uniform(-0.5, 1.5),
                        "Commercial Bank": np.random.uniform(-2.0, 0.5),
                        "Microfinance": np.random.uniform(1.0, 3.0),
                        "Fintech": np.random.uniform(-3.0, 0.0),
                    }.get(competitor, 0)

                    rate = max(base_rate + variation, 5.0)

                competitor_data.append(
                    {
                        "Competitor": competitor,
                        "Product": product,
                        "Rate": rate,
                        "Market Position": "Leader"
                        if rate < base_rate
                        else "Follower",
                        "Risk Profile": "Aggressive"
                        if rate < base_rate - 1
                        else "Conservative"
                        if rate > base_rate + 1
                        else "Neutral",
                    }
                )

        competitor_df = pd.DataFrame(competitor_data)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 🔥 Competitive Rate Heatmap")

            pivot_df = competitor_df.pivot(index="Competitor", columns="Product", values="Rate")

            fig = px.imshow(
                pivot_df,
                text_auto=".1f",
                aspect="auto",
                color_continuous_scale="RdYlGn_r",
                title="Competitor Pricing Heatmap (Lower = More Competitive)",
                labels=dict(color="Interest Rate (%)"),
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("##### 🎯 Market Positioning Analysis")

            positioning_data = []
            for product in products:
                our_rate = competitor_df[
                    (competitor_df["Competitor"] == "Our SACCO")
                    & (competitor_df["Product"] == product)
                ]["Rate"].iloc[0]
                market_avg = competitor_df[
                    (competitor_df["Competitor"] == "Market Average")
                    & (competitor_df["Product"] == product)
                ]["Rate"].iloc[0]

                positioning_data.append(
                    {
                        "Product": product,
                        "Our Rate": our_rate,
                        "Market Average": market_avg,
                        "Gap": our_rate - market_avg,
                        "Position": "Leader"
                        if our_rate < market_avg
                        else "Follower",
                    }
                )

            positioning_df = pd.DataFrame(positioning_data)

            fig = px.bar(
                positioning_df,
                x="Product",
                y="Gap",
                color="Position",
                title="Our Rate vs Market Average (Negative = More Competitive)",
                color_discrete_map={"Leader": "#10b981", "Follower": "#ef4444"},
                text=positioning_df["Gap"].apply(lambda x: f"{x:+.1f}%"),
            )

            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("##### 📊 Competitive Strategy Matrix")

        strategy_data = competitor_df[competitor_df["Competitor"] != "Market Average"].copy()
        strategy_data["Competitive_Index"] = strategy_data.groupby("Product")["Rate"].rank(
            method="dense", ascending=True
        )

        fig = px.scatter(
            strategy_data,
            x="Product",
            y="Rate",
            color="Competitor",
            size="Competitive_Index",
            title="Competitive Landscape by Product (Size = Competitiveness Rank)",
            size_max=20,
            hover_data=["Market Position", "Risk Profile"],
        )

        st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------------------------------
    # DEPOSIT PRICING STRATEGY
    # -------------------------------------------------------------------------
    def render_deposit_pricing_strategy(self):
        """Render comprehensive deposit pricing strategy"""
        st.subheader("💰 Deposit Pricing Strategy")

        deposit_products = pd.DataFrame(
            {
                "Product": [
                    "Savings Account",
                    "Fixed Deposit 30D",
                    "Fixed Deposit 90D",
                    "Fixed Deposit 180D",
                    "Fixed Deposit 1Y",
                    "Youth Account",
                    "Senior Citizen Account",
                    "Premium Savings",
                ],
                "Current_Rate": [3.5, 5.2, 6.8, 7.5, 8.2, 4.0, 4.5, 5.0],
                "Market_Average": [3.8, 5.5, 7.0, 7.8, 8.5, 4.2, 4.8, 5.5],
                "Balance_KES_M": [45.2, 28.5, 35.8, 42.1, 38.9, 12.3, 18.7, 25.4],
                "Growth_Rate": [5.2, 3.8, 4.5, 6.2, 5.8, 8.5, 7.2, 9.1],
                "Cost_of_Funds": [3.5, 5.2, 6.8, 7.5, 8.2, 4.0, 4.5, 5.0],
                "Net_Interest_Margin": [1.8, 2.1, 2.5, 2.8, 3.0, 2.2, 2.5, 2.8],
                "Stability_Score": [85, 75, 80, 85, 90, 70, 88, 82],
            }
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 📊 Deposit Cost & Margin Analysis")

            fig = go.Figure()

            fig.add_trace(
                go.Bar(
                    name="Current Rate",
                    x=deposit_products["Product"],
                    y=deposit_products["Current_Rate"],
                    marker_color="lightblue",
                    text=deposit_products["Current_Rate"].apply(lambda x: f"{x:.1f}%"),
                    textposition="outside",
                )
            )

            fig.add_trace(
                go.Bar(
                    name="Cost of Funds",
                    x=deposit_products["Product"],
                    y=deposit_products["Cost_of_Funds"],
                    marker_color="lightcoral",
                    text=deposit_products["Cost_of_Funds"].apply(lambda x: f"{x:.1f}%"),
                    textposition="outside",
                )
            )

            fig.add_trace(
                go.Scatter(
                    name="Net Margin",
                    x=deposit_products["Product"],
                    y=deposit_products["Net_Interest_Margin"],
                    mode="lines+markers",
                    line=dict(color="green", width=3),
                    yaxis="y2",
                )
            )

            fig.update_layout(
                title="Deposit Rate vs Cost Analysis",
                xaxis_title="Product",
                yaxis_title="Rate (%)",
                yaxis2=dict(
                    title="Net Margin (%)", overlaying="y", side="right"
                ),
                xaxis_tickangle=-45,
                showlegend=True,
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("##### 🎯 Deposit Strategy Optimization")

            deposit_products["Rate_Gap"] = (
                deposit_products["Current_Rate"] - deposit_products["Market_Average"]
            )
            deposit_products["Growth_Potential"] = (
                deposit_products["Growth_Rate"]
                * deposit_products["Stability_Score"]
                / 100
            )

            fig = px.scatter(
                deposit_products,
                x="Rate_Gap",
                y="Growth_Potential",
                size="Balance_KES_M",
                color="Net_Interest_Margin",
                hover_name="Product",
                title="Deposit Strategy Matrix (Size = Balance, Color = Margin)",
                size_max=50,
                color_continuous_scale="RdYlGn",
                labels={
                    "Rate_Gap": "Rate Gap vs Market (%)",
                    "Growth_Potential": "Growth Potential Score",
                    "Balance_KES_M": "Balance (KES M)",
                    "Net_Interest_Margin": "Net Margin (%)",
                },
            )

            fig.add_hline(
                y=deposit_products["Growth_Potential"].median(),
                line_dash="dash",
                line_color="gray",
            )
            fig.add_vline(x=0, line_dash="dash", line_color="gray")

            fig.add_annotation(
                x=1,
                y=8,
                text="⭐ Stars",
                showarrow=False,
                font=dict(color="green", size=12),
            )
            fig.add_annotation(
                x=-1,
                y=8,
                text="📈 Growth Focus",
                showarrow=False,
                font=dict(color="blue", size=12),
            )
            fig.add_annotation(
                x=1,
                y=4,
                text="💰 Profit Focus",
                showarrow=False,
                font=dict(color="orange", size=12),
            )
            fig.add_annotation(
                x=-1,
                y=4,
                text="🔍 Review Needed",
                showarrow=False,
                font=dict(color="red", size=12),
            )

            st.plotly_chart(fig, use_container_width=True)

        st.markdown("##### 💡 Deposit Pricing Recommendations")

        recommendations = []
        for _, product in deposit_products.iterrows():
            if product["Rate_Gap"] < -0.3:
                action = (
                    f"Increase to {product['Market_Average']:.1f}% "
                    f"(+{abs(product['Rate_Gap']):.1f}%)"
                )
                priority = "High"
            elif product["Rate_Gap"] > 0.3:
                action = f"Consider reducing to {product['Market_Average']:.1f}%"
                priority = "Medium"
            else:
                action = "Maintain current rate"
                priority = "Low"

            recommendations.append(
                {
                    "Product": product["Product"],
                    "Current Rate": f"{product['Current_Rate']:.1f}%",
                    "Market Average": f"{product['Market_Average']:.1f}%",
                    "Gap": f"{product['Rate_Gap']:+.1f}%",
                    "Recommended Action": action,
                    "Priority": priority,
                }
            )

        recommendations_df = pd.DataFrame(recommendations)

        def color_priority(priority):
            if priority == "High":
                return "background-color: #fecaca"
            elif priority == "Medium":
                return "background-color: #fed7aa"
            else:
                return "background-color: #bbf7d0"

        styled_recs = recommendations_df.style.applymap(
            color_priority, subset=["Priority"]
        )

        st.dataframe(styled_recs, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # STRATEGIC PRICING ROADMAP
    # -------------------------------------------------------------------------
    def render_strategic_pricing_roadmap(self):
        """Render strategic pricing roadmap"""
        st.subheader("🚀 Strategic Pricing Roadmap")

        roadmap_phases = [
            {
                "phase": "Immediate (0-30 days)",
                "initiatives": [
                    "Implement risk-based pricing for personal loans",
                    "Adjust savings account rates to market levels",
                    "Launch premium savings product",
                    "Update rate cards and disclosure documents",
                ],
                "owner": "Pricing Committee",
                "kpis": [
                    "NIM: 8.5%",
                    "Pricing efficiency: 90%",
                    "Market competitiveness: 5/5 products",
                ],
                "budget": "KES 500K",
            },
            {
                "phase": "Short-term (1-3 months)",
                "initiatives": [
                    "Roll out dynamic pricing for business loans",
                    "Implement competitor monitoring dashboard",
                    "Develop customer segmentation for pricing",
                    "Train staff on new pricing framework",
                ],
                "owner": "Commercial Department",
                "kpis": [
                    "Risk-adjusted returns: +1%",
                    "Customer satisfaction: 90%",
                    "Market share: +2%",
                ],
                "budget": "KES 1.2M",
            },
            {
                "phase": "Medium-term (3-6 months)",
                "initiatives": [
                    "Implement advanced pricing analytics platform",
                    "Develop AI-driven pricing recommendations",
                    "Integrate pricing with CRM system",
                    "Launch promotional pricing campaigns",
                ],
                "owner": "Technology & Commercial",
                "kpis": [
                    "Automated pricing: 80%",
                    "Response time: <24 hours",
                    "ROI on pricing: 15%",
                ],
                "budget": "KES 2.5M",
            },
            {
                "phase": "Long-term (6-12 months)",
                "initiatives": [
                    "Establish real-time pricing engine",
                    "Implement predictive pricing models",
                    "Develop pricing governance framework",
                    "Achieve market leadership in 3 products",
                ],
                "owner": "Executive Committee",
                "kpis": [
                    "Market leadership: 3 products",
                    "Pricing innovation index: 85%",
                    "Strategic alignment: 95%",
                ],
                "budget": "KES 3.8M",
            },
        ]

        for phase in roadmap_phases:
            with st.expander(
                f"📅 {phase['phase']} - Budget: {phase['budget']}", expanded=False
            ):
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Owner", phase["owner"])
                with col2:
                    st.metric("Budget", phase["budget"])
                with col3:
                    st.metric("Duration", phase["phase"].split("(")[1].split(")")[0])
                with col4:
                    progress = st.slider(
                        "Progress %",
                        min_value=0,
                        max_value=100,
                        value=20 if "Immediate" in phase["phase"] else 10,
                        key=f"progress_{phase['phase']}",
                    )

                st.markdown("**Key Initiatives:**")
                for initiative in phase["initiatives"]:
                    st.markdown(f"• {initiative}")

                st.markdown("**Success Metrics:**")
                for kpi in phase["kpis"]:
                    st.markdown(f"📊 {kpi}")

        st.markdown("##### 🎯 Strategic Alignment Dashboard")

        alignment_data = pd.DataFrame(
            {
                "Strategic Objective": [
                    "Maximize Profitability",
                    "Increase Market Share",
                    "Enhance Member Value",
                    "Optimize Risk-Return",
                    "Improve Competitive Position",
                ],
                "Current Alignment": [85, 78, 92, 88, 75],
                "Target Alignment": [95, 90, 95, 95, 90],
                "Pricing Contribution": ["High", "Medium", "High", "High", "Medium"],
            }
        )

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                name="Current Alignment",
                x=alignment_data["Strategic Objective"],
                y=alignment_data["Current Alignment"],
                marker_color="lightblue",
                text=alignment_data["Current Alignment"].apply(lambda x: f"{x}%"),
                textposition="outside",
            )
        )

        fig.add_trace(
            go.Bar(
                name="Target Alignment",
                x=alignment_data["Strategic Objective"],
                y=alignment_data["Target Alignment"],
                marker_color="lightgreen",
                text=alignment_data["Target Alignment"].apply(lambda x: f"{x}%"),
                textposition="outside",
            )
        )

        fig.update_layout(
            title="Strategic Alignment of Pricing Initiatives",
            xaxis_title="Strategic Objective",
            yaxis_title="Alignment Score (%)",
            barmode="group",
            xaxis_tickangle=-45,
        )

        st.plotly_chart(fig, use_container_width=True)

    def render_pricing_philosophy(self):
        """Render pricing economics philosophy framework"""
        with st.expander("📜 Pricing Economics Philosophy", expanded=False):
            cols = st.columns(3)
            for i, (key, value) in enumerate(PRICING_PHILOSOPHY.items()):
                with cols[i % 3]:
                    st.info(f"**{key}:**\n\n{value}")

            st.markdown("---")
            st.markdown(
                """
            **Strategic Pricing Approach:**  
            - **Value-Based:** Price based on customer value, not just costs  
            - **Risk-Adjusted:** Differentiate pricing based on risk profiles  
            - **Market-Responsive:** Adapt to competitive dynamics while maintaining margins  
            - **Data-Driven:** Use analytics to optimize pricing decisions  
            - **Member-Centric:** Balance profitability with member value creation  
            - **Regulatory Compliant:** Ensure pricing transparency and fairness
            """
            )

    def run(self):
        """Run the enhanced pricing economics page"""
        # Strategic Header
        self.render_strategic_header()

        # Pricing Philosophy
        self.render_pricing_philosophy()

        # Strategic KPI Cards
        self.render_strategic_kpi_cards()

        st.markdown("---")

        # Strategic Analysis Tabs
        self.render_strategic_tabs()

        # Log dashboard completion (safe, non-breaking)
        try:
            self.audit_logger.log_action(
                user=st.session_state.get(
                    "username", st.session_state.get("user", "unknown_user")
                ),
                role=st.session_state.get("role", "Unknown Role"),
                action="pricing_economics_analysis_completed",
                object_type="dashboard",
                object_id="04_Pricing_Economics.py",
            )
        except Exception:
            # Don't let logging failures crash the app
            pass


if __name__ == "__main__":
    page = PricingEconomicsPage()
    page.run()
