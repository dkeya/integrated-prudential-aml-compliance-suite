# sacco_core/analytics/governance.py
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from datetime import datetime, timedelta

class GovernanceAnalyzer:
    """Analyze governance and compliance metrics"""
    
    def __init__(self):
        self.compliance_framework = self._initialize_compliance_framework()
    
    def _initialize_compliance_framework(self) -> Dict[str, Dict]:
        """Initialize regulatory compliance framework"""
        return {
            'capital_adequacy': {
                'requirement': 'Minimum 10% capital adequacy ratio',
                'frequency': 'Quarterly',
                'threshold': 0.10,
                'weight': 0.15
            },
            'asset_quality': {
                'requirement': 'NPL ratio below 8%',
                'frequency': 'Monthly', 
                'threshold': 0.08,
                'weight': 0.20
            },
            'liquidity': {
                'requirement': 'Minimum 15% liquidity ratio',
                'frequency': 'Monthly',
                'threshold': 0.15,
                'weight': 0.15
            },
            'management': {
                'requirement': 'Board governance effectiveness',
                'frequency': 'Annual',
                'threshold': 0.80,  # Score out of 100%
                'weight': 0.15
            },
            'earnings': {
                'requirement': 'Positive and sustainable earnings',
                'frequency': 'Quarterly',
                'threshold': 0.0,  # Positive earnings
                'weight': 0.10
            },
            'sensitivity': {
                'requirement': 'Market risk sensitivity limits',
                'frequency': 'Quarterly',
                'threshold': 0.05,  # Maximum NII impact
                'weight': 0.10
            },
            'internal_controls': {
                'requirement': 'Effective internal control system',
                'frequency': 'Annual',
                'threshold': 0.85,  # Control effectiveness score
                'weight': 0.15
            }
        }
    
    def calculate_compliance_score(self, current_metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate overall compliance score
        
        Args:
            current_metrics: Dictionary of current metric values
            
        Returns:
            Dictionary with compliance scoring results
        """
        total_score = 0
        component_scores = {}
        status_summary = {}
        
        for component, framework in self.compliance_framework.items():
            current_value = current_metrics.get(component, 0)
            threshold = framework['threshold']
            weight = framework['weight']
            
            # Calculate component score (0-100)
            if component in ['management', 'internal_controls']:
                # For score-based metrics
                component_score = min(current_value * 100, 100)
            else:
                # For threshold-based metrics
                if current_value >= threshold:
                    component_score = 100
                else:
                    # Linear interpolation below threshold
                    component_score = max((current_value / threshold) * 100, 0)
            
            weighted_score = component_score * weight
            total_score += weighted_score
            
            component_scores[component] = {
                'score': component_score,
                'weighted_score': weighted_score,
                'status': 'Compliant' if component_score >= 80 else 'Watch' if component_score >= 60 else 'Deficient'
            }
        
        # Overall status
        if total_score >= 90:
            overall_status = 'Excellent'
        elif total_score >= 80:
            overall_status = 'Good'
        elif total_score >= 70:
            overall_status = 'Satisfactory'
        elif total_score >= 60:
            overall_status = 'Needs Improvement'
        else:
            overall_status = 'Poor'
        
        return {
            'overall_score': total_score,
            'overall_status': overall_status,
            'component_scores': component_scores,
            'calculation_date': datetime.now().strftime('%Y-%m-%d')
        }
    
    def get_compliance_trends(self, months: int = 8) -> pd.DataFrame:
        """
        Get compliance trends over time
        
        Args:
            months: Number of months of trend data to generate
            
        Returns:
            DataFrame with compliance trend data
        """
        try:
            # Generate consistent date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months*30)
            dates = pd.date_range(start=start_date, end=end_date, freq='M')
            
            n_months = len(dates)
            
            # Generate realistic trend data with consistent array lengths
            base_compliance = np.linspace(82, 87, n_months)
            compliance_noise = np.random.normal(0, 2, n_months)
            
            trend_data = {
                'Month': [d.strftime('%b %Y') for d in dates],
                'Overall_Compliance': (base_compliance + compliance_noise).clip(75, 95).round(1).tolist(),
                'Capital_Adequacy': (base_compliance + 6 + np.random.normal(0, 1.5, n_months)).clip(80, 98).round(1).tolist(),
                'Asset_Quality': (base_compliance - 4 + np.random.normal(0, 2, n_months)).clip(70, 90).round(1).tolist(),
                'Liquidity': (base_compliance + 3 + np.random.normal(0, 1, n_months)).clip(80, 96).round(1).tolist(),
                'Open_Issues': (np.linspace(18, 12, n_months) + np.random.normal(0, 1, n_months)).clip(8, 25).round(0).astype(int).tolist()
            }
            
            # Verify all arrays have the same length
            array_lengths = {k: len(v) for k, v in trend_data.items()}
            if len(set(array_lengths.values())) != 1:
                raise ValueError(f"Array length mismatch: {array_lengths}")
            
            return pd.DataFrame(trend_data)
            
        except Exception as e:
            # Fallback to consistent mock data
            months_list = ['Jul 2023', 'Aug 2023', 'Sep 2023', 'Oct 2023', 'Nov 2023', 'Dec 2023', 'Jan 2024', 'Feb 2024']
            n = len(months_list)
            
            return pd.DataFrame({
                'Month': months_list,
                'Overall_Compliance': [82, 83, 85, 84, 86, 85, 87, 87],
                'Capital_Adequacy': [88, 90, 92, 91, 93, 92, 94, 95],
                'Asset_Quality': [78, 80, 82, 81, 83, 82, 80, 82],
                'Liquidity': [85, 86, 88, 87, 89, 88, 90, 91],
                'Open_Issues': [18, 16, 15, 17, 14, 13, 12, 12]
            })
    
    def generate_risk_heat_map(self, risks_data: List[Dict]) -> pd.DataFrame:
        """
        Generate risk heat map data
        
        Args:
            risks_data: List of risk dictionaries
            
        Returns:
            DataFrame formatted for heat map visualization
        """
        risk_categories = ['Strategic', 'Operational', 'Financial', 'Compliance', 'Reputational']
        impact_levels = ['Low', 'Medium', 'High', 'Very High']
        likelihood_levels = ['Rare', 'Unlikely', 'Possible', 'Likely', 'Almost Certain']
        
        # Initialize heat map data
        heat_data = []
        for impact in impact_levels:
            for likelihood in likelihood_levels:
                count = len([r for r in risks_data 
                           if r.get('impact') == impact and r.get('likelihood') == likelihood])
                heat_data.append({
                    'Impact': impact,
                    'Likelihood': likelihood,
                    'Count': count
                })
        
        return pd.DataFrame(heat_data)
    
    def track_audit_findings(self, findings_data: List[Dict]) -> Dict[str, Any]:
        """
        Track audit findings and remediation progress
        
        Args:
            findings_data: List of audit finding dictionaries
            
        Returns:
            Dictionary with audit tracking metrics
        """
        total_findings = len(findings_data)
        
        # Categorize by severity
        high_severity = len([f for f in findings_data if f.get('severity') == 'High'])
        medium_severity = len([f for f in findings_data if f.get('severity') == 'Medium'])
        low_severity = len([f for f in findings_data if f.get('severity') == 'Low'])
        
        # Track remediation status
        completed = len([f for f in findings_data if f.get('status') == 'Completed'])
        in_progress = len([f for f in findings_data if f.get('status') == 'In Progress'])
        not_started = len([f for f in findings_data if f.get('status') == 'Not Started'])
        overdue = len([f for f in findings_data if f.get('status') == 'Overdue'])
        
        # Calculate metrics with zero division protection
        completion_rate = (completed / total_findings) * 100 if total_findings > 0 else 0
        overdue_rate = (overdue / total_findings) * 100 if total_findings > 0 else 0
        
        # Calculate health score with zero division protection
        if total_findings > 0:
            incomplete_penalty = ((total_findings - completed) / total_findings) * 50
        else:
            incomplete_penalty = 0
            
        health_score = max(100 - (overdue_rate * 2) - incomplete_penalty, 0)
        
        return {
            'total_findings': total_findings,
            'severity_breakdown': {
                'high': high_severity,
                'medium': medium_severity,
                'low': low_severity
            },
            'remediation_status': {
                'completed': completed,
                'in_progress': in_progress,
                'not_started': not_started,
                'overdue': overdue
            },
            'completion_rate': completion_rate,
            'overdue_rate': overdue_rate,
            'health_score': health_score
        }
    
    def monitor_policy_compliance(self, policies_data: List[Dict]) -> Dict[str, Any]:
        """
        Monitor policy compliance and currency
        
        Args:
            policies_data: List of policy dictionaries
            
        Returns:
            Dictionary with policy compliance metrics
        """
        total_policies = len(policies_data)
        
        # Analyze review status
        current_policies = len([p for p in policies_data if p.get('status') == 'Current'])
        update_due = len([p for p in policies_data if p.get('status') == 'Update Due'])
        expired = len([p for p in policies_data if p.get('status') == 'Expired'])
        
        # Calculate average days since last review
        today = datetime.now()
        days_since_review = []
        
        for policy in policies_data:
            last_review = policy.get('last_review')
            if last_review:
                review_date = datetime.strptime(last_review, '%Y-%m-%d')
                days = (today - review_date).days
                days_since_review.append(days)
        
        avg_days_since_review = np.mean(days_since_review) if days_since_review else 0
        
        # Policy health score with zero division protection
        currency_score = (current_policies / total_policies) * 100 if total_policies > 0 else 100
        review_score = max(100 - (avg_days_since_review / 365 * 100), 0)  # Penalize older reviews
        
        overall_health = (currency_score + review_score) / 2
        
        return {
            'total_policies': total_policies,
            'currency_status': {
                'current': current_policies,
                'update_due': update_due,
                'expired': expired
            },
            'avg_days_since_review': avg_days_since_review,
            'currency_score': currency_score,
            'review_score': review_score,
            'overall_health': overall_health
        }
    
    def generate_regulatory_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Generate regulatory reporting calendar
        
        Args:
            start_date: Start date for calendar (YYYY-MM-DD)
            end_date: End date for calendar (YYYY-MM-DD)
            
        Returns:
            DataFrame with regulatory reporting schedule
        """
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        regulatory_reports = [
            {
                'report': 'SASRA Quarterly Returns',
                'frequency': 'quarterly',
                'due_day': 31,  # Last day of quarter
                'responsible': 'Finance Manager'
            },
            {
                'report': 'SASRA Annual Returns', 
                'frequency': 'annual',
                'due_day': 183,  # June 30th (day 183)
                'responsible': 'CEO'
            },
            {
                'report': 'Central Bank AML Returns',
                'frequency': 'quarterly', 
                'due_day': 31,
                'responsible': 'Compliance Officer'
            },
            {
                'report': 'Data Commissioner Returns',
                'frequency': 'annual',
                'due_day': 151,  # May 31st (day 151)
                'responsible': 'Data Protection Officer'
            }
        ]
        
        calendar_events = []
        
        current_date = start
        while current_date <= end:
            for report in regulatory_reports:
                if report['frequency'] == 'quarterly':
                    # Last day of each quarter
                    quarter_end = self._get_quarter_end(current_date)
                    if quarter_end >= start and quarter_end <= end:
                        calendar_events.append({
                            'report': report['report'],
                            'due_date': quarter_end.strftime('%Y-%m-%d'),
                            'responsible': report['responsible'],
                            'status': 'Pending'
                        })
                elif report['frequency'] == 'annual':
                    # Specific day of year
                    annual_date = datetime(current_date.year, 6, 30)  # June 30th
                    if annual_date >= start and annual_date <= end:
                        calendar_events.append({
                            'report': report['report'],
                            'due_date': annual_date.strftime('%Y-%m-%d'),
                            'responsible': report['responsible'],
                            'status': 'Pending'
                        })
            
            # Move to next month
            if current_date.month == 12:
                current_date = datetime(current_date.year + 1, 1, 1)
            else:
                current_date = datetime(current_date.year, current_date.month + 1, 1)
        
        return pd.DataFrame(calendar_events)
    
    def _get_quarter_end(self, date: datetime) -> datetime:
        """Get quarter end date for given date"""
        quarter = (date.month - 1) // 3 + 1
        if quarter == 1:
            return datetime(date.year, 3, 31)
        elif quarter == 2:
            return datetime(date.year, 6, 30)
        elif quarter == 3:
            return datetime(date.year, 9, 30)
        else:
            return datetime(date.year, 12, 31)