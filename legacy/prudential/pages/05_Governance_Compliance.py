# pages/05_Governance_Compliance.py
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
from sacco_core.analytics.governance import GovernanceAnalyzer
from sacco_core.sidebar import render_sidebar

st.set_page_config(
    page_title="Governance & Compliance",
    page_icon="⚖️",
    layout="wide"
)

# Check authentication and render sidebar
if not st.session_state.get('authenticated', False):
    st.error("🔐 Please log in to access this page")
    st.stop()

# Render consistent sidebar and styling
render_sidebar()

class GovernanceCompliancePage:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.rbac_manager = RBACManager()
        self.audit_logger = AuditLogger()
        self.config = self.config_manager.load_settings()
        self.governance_analyzer = GovernanceAnalyzer()
        
        if not self._check_access():
            st.stop()
    
    def _check_access(self):
        if not st.session_state.get('authenticated', False):
            st.error("Please login to access this page")
            return False
        
        has_access = self.rbac_manager.check_page_access(
            "05_Governance_Compliance.py", 
            st.session_state.role, 
            self.config
        )
        
        if not has_access:
            st.error("You do not have permission to access this page")
            return False
        
        self.audit_logger.log_data_access(
            st.session_state.user, 
            st.session_state.role, 
            "governance_compliance_page"
        )
        return True
    
    def render_compliance_dashboard(self):
        """Render the main compliance dashboard"""
        st.subheader("📊 Compliance & Governance Dashboard")
        
        # Get compliance score from analyzer
        compliance_score = self.governance_analyzer.calculate_compliance_score({})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Overall Compliance Score",
                f"{compliance_score['overall_score']:.0f}%",
                "2%",
                help="Overall regulatory compliance rating"
            )
        
        with col2:
            st.metric(
                "Open Compliance Issues", 
                "12",
                "-3",
                delta_color="inverse",
                help="Number of outstanding compliance issues"
            )
        
        with col3:
            st.metric(
                "SASRA Rating",
                "Satisfactory",
                "Stable",
                help="Current SASRA supervisory rating"
            )
        
        with col4:
            st.metric(
                "Policy Updates Required",
                "4",
                "-1",
                delta_color="inverse",
                help="Policies requiring review/update"
            )
        
        # Compliance status overview
        self.render_compliance_status()
    
    def render_compliance_status(self):
        """Render compliance status by category"""
        st.markdown("#### 📋 Regulatory Compliance Status")
        
        compliance_data = pd.DataFrame({
            'Category': [
                'Capital Adequacy', 'Asset Quality', 'Management', 'Earnings', 
                'Liquidity', 'Sensitivity to Market Risk', 'Internal Controls',
                'Anti-Money Laundering', 'Data Protection', 'Consumer Protection'
            ],
            'Status': ['Compliant', 'Watch', 'Compliant', 'Compliant', 'Compliant', 
                      'Compliant', 'Watch', 'Compliant', 'Deficient', 'Compliant'],
            'Last_Audit': ['2024-01-15', '2024-01-20', '2024-02-01', '2024-01-25',
                          '2024-02-10', '2024-01-30', '2024-02-05', '2024-02-15',
                          '2024-02-08', '2024-01-28'],
            'Next_Review': ['2024-07-15', '2024-04-20', '2024-08-01', '2024-07-25',
                           '2024-08-10', '2024-07-30', '2024-04-05', '2024-08-15',
                           '2024-03-08', '2024-07-28'],
            'Issues': [0, 2, 0, 0, 0, 0, 3, 0, 5, 0]
        })
        
        # Color coding for status
        def color_status(status):
            if status == 'Compliant':
                return 'color: green; font-weight: bold'
            elif status == 'Watch':
                return 'color: orange; font-weight: bold'
            else:
                return 'color: red; font-weight: bold'
        
        styled_df = compliance_data.style.applymap(
            color_status, subset=['Status']
        )
        
        st.dataframe(styled_df, use_container_width=True)
        
        # Compliance trends
        self.render_compliance_trends()
    
    def render_compliance_trends(self):
        """Render compliance trends over time"""
        st.markdown("#### 📈 Compliance Trends")
        
        try:
            # Use the analytics module to get trend data
            trend_data = self.governance_analyzer.get_compliance_trends()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.line(
                    trend_data,
                    x='Month',
                    y=['Overall_Compliance', 'Capital_Adequacy', 'Asset_Quality', 'Liquidity'],
                    title="Compliance Scores Trend",
                    labels={'value': 'Compliance Score (%)', 'variable': 'Category'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.line(
                    trend_data,
                    x='Month',
                    y='Open_Issues',
                    title="Open Compliance Issues Trend",
                    labels={'value': 'Number of Issues'}
                )
                fig.update_traces(line=dict(color='red', width=3))
                st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            st.error(f"Error loading compliance trends: {str(e)}")
            # Fallback to simple trend display
            self._render_fallback_trends()
    
    def _render_fallback_trends(self):
        """Render fallback trends when analytics fails"""
        # Generate consistent trend data with same array lengths
        months = pd.date_range(start='2023-07-01', end='2024-02-01', freq='ME')
        n_months = len(months)
        
        trend_data = pd.DataFrame({
            'Month': months,
            'Overall_Compliance': [82, 83, 85, 84, 86, 85, 87, 87],
            'Capital_Adequacy': [88, 90, 92, 91, 93, 92, 94, 95],
            'Asset_Quality': [78, 80, 82, 81, 83, 82, 80, 82],
            'Liquidity': [85, 86, 88, 87, 89, 88, 90, 91],
            'Open_Issues': [18, 16, 15, 17, 14, 13, 12, 12]
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.line(
                trend_data,
                x='Month',
                y=['Overall_Compliance', 'Capital_Adequacy', 'Asset_Quality', 'Liquidity'],
                title="Compliance Scores Trend",
                labels={'value': 'Compliance Score (%)', 'variable': 'Category'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.line(
                trend_data,
                x='Month',
                y='Open_Issues',
                title="Open Compliance Issues Trend",
                labels={'value': 'Number of Issues'}
            )
            fig.update_traces(line=dict(color='red', width=3))
            st.plotly_chart(fig, use_container_width=True)

    def render_governance_framework(self):
        """Render governance framework overview"""
        st.markdown("---")
        st.subheader("🏛️ Governance Framework")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📋 Board & Committee Structure")
            
            governance_structure = """
            **Board of Directors (9 Members)**
            - Chairperson
            - Vice Chairperson  
            - Treasurer
            - Secretary
            - 5 Committee Chairs
            
            **Standing Committees:**
            - Audit & Risk Committee
            - Credit Committee
            - Governance & Nominations
            - IT & Digital Strategy
            - Member Services
            """
            
            st.info(governance_structure)
            
            # Board composition
            st.markdown("#### 👥 Board Composition")
            composition_data = {
                'Category': ['Executive', 'Non-Executive', 'Independent', 'Female', 'Youth'],
                'Count': [2, 5, 2, 3, 1],
                'Percentage': [22, 56, 22, 33, 11]
            }
            composition_df = pd.DataFrame(composition_data)
            st.dataframe(composition_df, use_container_width=True)
        
        with col2:
            st.markdown("#### 📅 Board Meeting Performance")
            
            meeting_data = pd.DataFrame({
                'Meeting Type': ['Board Meetings', 'Audit Committee', 'Credit Committee', 'IT Committee'],
                'Held': [6, 4, 8, 3],
                'Scheduled': [6, 4, 8, 4],
                'Attendance Rate': [92, 88, 85, 78],
                'Action Items': [45, 28, 52, 15],
                'Completed': [38, 24, 45, 12]
            })
            
            st.dataframe(meeting_data, use_container_width=True)
            
            # Meeting effectiveness
            completion_rate = (meeting_data['Completed'].sum() / meeting_data['Action Items'].sum()) * 100
            st.metric("Overall Action Completion Rate", f"{completion_rate:.1f}%")
    
    def render_policy_management(self):
        """Render policy management section"""
        st.markdown("---")
        st.subheader("📚 Policy Management")
        
        # Get policy compliance metrics
        policy_metrics = self.governance_analyzer.monitor_policy_compliance([])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📋 Policy Inventory")
            
            policies_data = pd.DataFrame({
                'Policy': [
                    'Credit Policy', 'Investment Policy', 'Liquidity Policy', 
                    'IT Security Policy', 'AML/CFT Policy', 'Data Protection Policy',
                    'Business Continuity Plan', 'Risk Management Framework'
                ],
                'Version': ['3.2', '2.1', '4.0', '1.5', '3.0', '2.2', '1.8', '3.1'],
                'Last_Review': ['2023-11-15', '2023-09-20', '2024-01-10', '2023-12-05',
                               '2024-02-01', '2023-10-30', '2023-08-15', '2024-01-25'],
                'Next_Review': ['2024-05-15', '2024-03-20', '2024-07-10', '2024-06-05',
                               '2024-08-01', '2024-04-30', '2024-02-15', '2024-07-25'],
                'Status': ['Current', 'Update Due', 'Current', 'Current', 'Current', 
                          'Update Due', 'Update Due', 'Current']
            })
            
            # Color code status
            def color_policy_status(status):
                if status == 'Current':
                    return 'color: green'
                else:
                    return 'color: red; font-weight: bold'
            
            styled_policies = policies_data.style.applymap(
                color_policy_status, subset=['Status']
            )
            
            st.dataframe(styled_policies, use_container_width=True)
        
        with col2:
            st.markdown("#### ⚠️ Policy Exceptions & Waivers")
            
            exceptions_data = pd.DataFrame({
                'Policy': ['Credit Policy', 'Investment Policy', 'Liquidity Policy'],
                'Exception_Type': ['Single Employer Limit', 'Investment Concentration', 'Liquidity Buffer'],
                'Approved_By': ['Credit Committee', 'Board', 'ALCO'],
                'Approval_Date': ['2024-01-10', '2023-12-15', '2024-02-01'],
                'Expiry_Date': ['2024-04-10', '2024-06-15', '2024-05-01'],
                'Status': ['Active', 'Active', 'Active']
            })
            
            st.dataframe(exceptions_data, use_container_width=True)
            
            # Policy compliance metrics
            st.markdown("##### 📊 Policy Compliance Metrics")
            col21, col22, col23 = st.columns(3)
            
            with col21:
                st.metric("Policies Current", "12", "15 total")
            
            with col22:
                st.metric("Update Required", "3", "-1 from last month")
            
            with col23:
                st.metric("Approval Rate", "94%", "2%")
    
    def render_risk_management(self):
        """Render risk management framework"""
        st.markdown("---")
        st.subheader("🎯 Risk Management Framework")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Risk Appetite Statement")
            
            risk_appetite = """
            **Credit Risk:** Moderate
            - PAR30: < 15%
            - NPL Ratio: < 8%
            - Single Employer: < 25%
            
            **Liquidity Risk:** Low
            - Liquidity Ratio: > 15%
            - LCR: > 100%
            - Contingency Funding: 30 days
            
            **Operational Risk:** Low
            - Internal Fraud: Zero tolerance
            - Cyber Incidents: < 2 per year
            - Business Continuity: 4hr RTO
            
            **Market Risk:** Low
            - Interest Rate Risk: ±50 bps NII impact
            - Foreign Exchange: Hedged positions only
            """
            
            st.info(risk_appetite)
        
        with col2:
            st.markdown("#### 🚨 Top Risk Register")
            
            risks_data = pd.DataFrame({
                'Risk_ID': ['RISK-001', 'RISK-002', 'RISK-003', 'RISK-004', 'RISK-005'],
                'Risk_Description': [
                    'Cyber security breach',
                    'Key employer default', 
                    'Liquidity crisis',
                    'Regulatory non-compliance',
                    'IT system failure'
                ],
                'Category': ['Operational', 'Credit', 'Liquidity', 'Compliance', 'Operational'],
                'Impact': ['High', 'High', 'High', 'Medium', 'High'],
                'Likelihood': ['Medium', 'Low', 'Low', 'Medium', 'Low'],
                'Mitigation_Status': ['In Progress', 'Completed', 'In Progress', 'Completed', 'Planned']
            })
            
            # Color code impact
            def color_impact(impact):
                if impact == 'High':
                    return 'background-color: #FFB6C1'
                elif impact == 'Medium':
                    return 'background-color: #FFE4B5'
                else:
                    return 'background-color: #90EE90'
            
            styled_risks = risks_data.style.applymap(
                color_impact, subset=['Impact']
            )
            
            st.dataframe(styled_risks, use_container_width=True)
    
    def render_audit_findings(self):
        """Render audit findings and tracking"""
        st.markdown("---")
        st.subheader("🔍 Audit Findings & Tracking")
        
        # Get audit tracking metrics
        audit_metrics = self.governance_analyzer.track_audit_findings([])
        
        audit_data = pd.DataFrame({
            'Finding_ID': ['AUD-2024-001', 'AUD-2024-002', 'AUD-2024-003', 'AUD-2024-004'],
            'Description': [
                'Inadequate IT access controls',
                'Credit file documentation gaps',
                'AML transaction monitoring weaknesses',
                'Data backup procedures not tested'
            ],
            'Severity': ['High', 'Medium', 'High', 'Medium'],
            'Audit_Date': ['2024-01-15', '2024-01-20', '2024-02-01', '2024-02-05'],
            'Due_Date': ['2024-03-15', '2024-04-20', '2024-04-01', '2024-05-05'],
            'Status': ['In Progress', 'Completed', 'In Progress', 'Not Started'],
            'Owner': ['IT Manager', 'Credit Manager', 'Compliance Officer', 'IT Manager']
        })
        
        # Severity color coding
        def color_severity(severity):
            if severity == 'High':
                return 'color: red; font-weight: bold'
            elif severity == 'Medium':
                return 'color: orange; font-weight: bold'
            else:
                return 'color: green; font-weight: bold'
        
        styled_audit = audit_data.style.applymap(
            color_severity, subset=['Severity']
        )
        
        st.dataframe(styled_audit, use_container_width=True)
        
        # Audit findings summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            high_findings = len(audit_data[audit_data['Severity'] == 'High'])
            st.metric("High Severity Findings", high_findings)
        
        with col2:
            overdue_findings = len(audit_data[audit_data['Status'] == 'Overdue'])
            st.metric("Overdue Actions", overdue_findings, delta_color="inverse")
        
        with col3:
            completion_rate = (len(audit_data[audit_data['Status'] == 'Completed']) / len(audit_data)) * 100
            st.metric("Remediation Rate", f"{completion_rate:.1f}%")
    
    def render_regulatory_reporting(self):
        """Render regulatory reporting schedule"""
        st.markdown("---")
        st.subheader("📋 Regulatory Reporting Schedule")
        
        # Get regulatory calendar
        today = datetime.now()
        start_date = today.strftime('%Y-%m-%d')
        end_date = (today + timedelta(days=180)).strftime('%Y-%m-%d')
        reporting_calendar = self.governance_analyzer.generate_regulatory_calendar(start_date, end_date)
        
        if not reporting_calendar.empty:
            st.dataframe(reporting_calendar, use_container_width=True)
        else:
            # Fallback data
            reporting_data = pd.DataFrame({
                'Report_Name': [
                    'SASRA Quarterly Returns',
                    'SASRA Annual Returns', 
                    'Central Bank AML Returns',
                    'Data Commissioner Returns',
                    'Tax Authority Returns',
                    'NCR Credit Returns'
                ],
                'Frequency': ['Quarterly', 'Annual', 'Quarterly', 'Annual', 'Monthly', 'Quarterly'],
                'Due_Date': ['2024-03-31', '2024-06-30', '2024-03-31', '2024-05-31', '2024-02-28', '2024-03-31'],
                'Status': ['Pending', 'Pending', 'Pending', 'Pending', 'Submitted', 'Pending'],
                'Responsible': ['Finance Manager', 'CEO', 'Compliance Officer', 'DPO', 'Finance Manager', 'Credit Manager']
            })
            
            # Status color coding
            def color_report_status(status):
                if status == 'Submitted':
                    return 'color: green; font-weight: bold'
                elif status == 'Overdue':
                    return 'color: red; font-weight: bold'
                else:
                    return 'color: orange; font-weight: bold'
            
            styled_reports = reporting_data.style.applymap(
                color_report_status, subset=['Status']
            )
            
            st.dataframe(styled_reports, use_container_width=True)
    
    def render_compliance_calendar(self):
        """Render compliance calendar"""
        st.markdown("---")
        st.subheader("📅 Compliance Calendar")
        
        # Generate sample calendar events
        today = datetime.now()
        events = []
        
        compliance_events = [
            ('Board Meeting', 'monthly', '2024-02-20'),
            ('Audit Committee', 'quarterly', '2024-03-05'),
            ('SASRA Quarterly Returns', 'quarterly', '2024-03-31'),
            ('Risk Committee', 'quarterly', '2024-03-15'),
            ('Policy Review - Credit', 'annual', '2024-05-15'),
            ('Internal Audit', 'semi-annual', '2024-06-30'),
            ('AML Training', 'annual', '2024-04-30'),
            ('Business Continuity Test', 'annual', '2024-07-15')
        ]
        
        for event_name, frequency, due_date in compliance_events:
            events.append({
                'Event': event_name,
                'Frequency': frequency,
                'Due_Date': due_date,
                'Days_Remaining': (datetime.strptime(due_date, '%Y-%m-%d') - today).days,
                'Status': 'Pending' if (datetime.strptime(due_date, '%Y-%m-%d') - today).days > 0 else 'Due'
            })
        
        events_df = pd.DataFrame(events)
        
        # Color code days remaining
        def color_days_remaining(days):
            if days < 0:
                return 'color: red; font-weight: bold'
            elif days <= 7:
                return 'color: orange; font-weight: bold'
            elif days <= 30:
                return 'color: #FFD700; font-weight: bold'
            else:
                return 'color: green'
        
        styled_calendar = events_df.style.applymap(
            color_days_remaining, subset=['Days_Remaining']
        )
        
        st.dataframe(styled_calendar, use_container_width=True)
    
    def render_governance_health_check(self):
        """Render governance health check"""
        st.markdown("---")
        st.subheader("❤️ Governance Health Check")
        
        health_metrics = {
            'Metric': [
                'Board Independence',
                'Committee Effectiveness', 
                'Risk Oversight',
                'Compliance Culture',
                'Policy Currency',
                'Audit Coverage',
                'Regulatory Relationship',
                'Member Engagement'
            ],
            'Score': [85, 78, 82, 75, 80, 88, 90, 72],
            'Trend': ['↑', '→', '↑', '→', '↑', '↑', '→', '↓'],
            'Rating': ['Good', 'Satisfactory', 'Good', 'Satisfactory', 'Good', 'Good', 'Excellent', 'Needs Improvement']
        }
        
        health_df = pd.DataFrame(health_metrics)
        
        # Create radar chart for governance health
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=health_df['Score'],
            theta=health_df['Metric'],
            fill='toself',
            name='Governance Health'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=False,
            title="Governance Health Radar Chart"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Overall governance score
        overall_score = health_df['Score'].mean()
        st.metric("Overall Governance Score", f"{overall_score:.1f}%", "Good")
    
    def run(self):
        """Run the governance and compliance page"""
        st.title("⚖️ Governance & Compliance")
        
        st.markdown("""
        Comprehensive governance framework, regulatory compliance monitoring, and risk management 
        oversight to ensure the SACCO operates with integrity and in compliance with all regulatory requirements.
        """)
        
        self.render_compliance_dashboard()
        self.render_governance_framework()
        self.render_policy_management()
        self.render_risk_management()
        self.render_audit_findings()
        self.render_regulatory_reporting()
        self.render_compliance_calendar()
        self.render_governance_health_check()

if __name__ == "__main__":
    page = GovernanceCompliancePage()
    page.run()