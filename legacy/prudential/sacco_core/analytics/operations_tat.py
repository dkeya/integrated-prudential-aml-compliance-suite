# sacco_core/analytics/operations_tat.py
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TATMetrics:
    """Turnaround Time Metrics Data Class"""
    process_name: str
    total_requests: int
    average_tat: float
    median_tat: float
    p95_tat: float
    sla_compliance_rate: float
    sla_breaches: int

class OperationsTATAnalyzer:
    """Analyze Turnaround Times across SACCO operations"""
    
    def __init__(self):
        self.sla_standards = {
            'loan_application': 48,  # hours
            'loan_approval': 24,     # hours  
            'loan_disbursement': 12, # hours
            'member_registration': 4, # hours
            'complaint_resolution': 72, # hours
            'withdrawal_processing': 2, # hours
            'deposit_processing': 1,   # hours
        }
    
    def analyze_operations_tat(self) -> Dict[str, Any]:
        """
        Perform comprehensive TAT analysis across all operations
        
        Returns:
            Dictionary with TAT analysis results
        """
        try:
            # Extract operational data
            loan_data = self._extract_loan_operations_data()
            service_data = self._extract_service_requests_data()
            transaction_data = self._extract_transaction_processing_data()
            
            analysis = {
                'loan_operations': self._analyze_loan_operations_tat(loan_data),
                'service_operations': self._analyze_service_operations_tat(service_data),
                'transaction_operations': self._analyze_transaction_operations_tat(transaction_data),
                'overall_performance': self._calculate_overall_performance(loan_data, service_data, transaction_data),
                'bottleneck_analysis': self._identify_bottlenecks(loan_data, service_data, transaction_data),
                'sla_compliance': self._analyze_sla_compliance(loan_data, service_data, transaction_data),
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return analysis
        except Exception as e:
            logger.error(f"Error in operations TAT analysis: {e}")
            return self._get_fallback_analysis()
    
    def _extract_loan_operations_data(self) -> pd.DataFrame:
        """Extract loan operations data with timestamps"""
        try:
            # Simulated loan operations data
            np.random.seed(42)
            n_applications = 1000
            
            applications = []
            for i in range(n_applications):
                submission_date = datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 365))
                
                # Simulate process timings with some delays
                approval_delay = np.random.exponential(24)  # hours
                disbursement_delay = np.random.exponential(6)  # hours
                
                approval_date = submission_date + timedelta(hours=approval_delay)
                disbursement_date = approval_date + timedelta(hours=disbursement_delay)
                
                applications.append({
                    'application_id': f'APP{10000 + i}',
                    'member_id': f'M{5000 + np.random.randint(1, 1000)}',
                    'product_type': np.random.choice(['Personal Loan', 'Business Loan', 'Emergency Loan']),
                    'amount_requested': np.random.lognormal(10, 0.5),
                    'submission_date': submission_date,
                    'approval_date': approval_date,
                    'disbursement_date': disbursement_date,
                    'approval_officer': f'Officer_{np.random.randint(1, 20)}',
                    'branch': np.random.choice(['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru']),
                    'status': np.random.choice(['Approved', 'Rejected', 'Pending'], p=[0.7, 0.2, 0.1])
                })
            
            return pd.DataFrame(applications)
        except Exception as e:
            logger.error(f"Error extracting loan operations data: {e}")
            return pd.DataFrame()
    
    def _extract_service_requests_data(self) -> pd.DataFrame:
        """Extract service request and resolution data"""
        try:
            np.random.seed(42)
            n_requests = 500
            
            service_requests = []
            for i in range(n_requests):
                request_date = datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 365))
                
                # Simulate resolution time based on request type
                request_type = np.random.choice([
                    'Account Inquiry', 'Card Replacement', 'Statement Request', 
                    'Complaint', 'Information Update'
                ])
                
                resolution_hours = {
                    'Account Inquiry': np.random.exponential(2),
                    'Card Replacement': np.random.exponential(48),
                    'Statement Request': np.random.exponential(4),
                    'Complaint': np.random.exponential(24),
                    'Information Update': np.random.exponential(6)
                }
                
                resolution_date = request_date + timedelta(hours=resolution_hours[request_type])
                
                service_requests.append({
                    'request_id': f'SR{5000 + i}',
                    'member_id': f'M{5000 + np.random.randint(1, 1000)}',
                    'request_type': request_type,
                    'priority': np.random.choice(['Low', 'Medium', 'High'], p=[0.6, 0.3, 0.1]),
                    'request_date': request_date,
                    'resolution_date': resolution_date,
                    'assigned_team': np.random.choice(['Customer Service', 'Operations', 'IT Support']),
                    'sla_breach': resolution_hours[request_type] > 24  # Simple SLA check
                })
            
            return pd.DataFrame(service_requests)
        except Exception as e:
            logger.error(f"Error extracting service requests data: {e}")
            return pd.DataFrame()
    
    def _extract_transaction_processing_data(self) -> pd.DataFrame:
        """Extract transaction processing timing data"""
        try:
            np.random.seed(42)
            n_transactions = 2000
            
            transactions = []
            for i in range(n_transactions):
                submission_time = datetime(2023, 1, 1) + timedelta(
                    days=np.random.randint(0, 365),
                    hours=np.random.randint(0, 24)
                )
                
                transaction_type = np.random.choice(['Deposit', 'Withdrawal', 'Transfer', 'Payment'])
                
                # Different processing times by transaction type
                processing_times = {
                    'Deposit': np.random.exponential(0.5),  # hours
                    'Withdrawal': np.random.exponential(1),
                    'Transfer': np.random.exponential(2),
                    'Payment': np.random.exponential(3)
                }
                
                completion_time = submission_time + timedelta(hours=processing_times[transaction_type])
                
                transactions.append({
                    'transaction_id': f'TXN{20000 + i}',
                    'member_id': f'M{5000 + np.random.randint(1, 1000)}',
                    'transaction_type': transaction_type,
                    'amount': np.random.lognormal(8, 1),
                    'submission_time': submission_time,
                    'completion_time': completion_time,
                    'processing_channel': np.random.choice(['Branch', 'Mobile', 'ATM', 'Online']),
                    'status': 'Completed'
                })
            
            return pd.DataFrame(transactions)
        except Exception as e:
            logger.error(f"Error extracting transaction processing data: {e}")
            return pd.DataFrame()
    
    def _analyze_loan_operations_tat(self, loan_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze loan operations turnaround times"""
        try:
            if loan_data.empty:
                return self._get_empty_loan_analysis()
            
            # Calculate TAT for different loan processes
            approved_loans = loan_data[loan_data['status'] == 'Approved']
            
            if len(approved_loans) == 0:
                return self._get_empty_loan_analysis()
            
            # Application to approval TAT
            approved_loans = approved_loans.copy()
            approved_loans['approval_tat_hours'] = (
                approved_loans['approval_date'] - approved_loans['submission_date']
            ).dt.total_seconds() / 3600
            
            # Approval to disbursement TAT
            approved_loans['disbursement_tat_hours'] = (
                approved_loans['disbursement_date'] - approved_loans['approval_date']
            ).dt.total_seconds() / 3600
            
            # Overall TAT
            approved_loans['overall_tat_hours'] = (
                approved_loans['disbursement_date'] - approved_loans['submission_date']
            ).dt.total_seconds() / 3600
            
            # SLA compliance
            approval_sla_compliance = len(
                approved_loans[approved_loans['approval_tat_hours'] <= self.sla_standards['loan_approval']]
            ) / len(approved_loans)
            
            disbursement_sla_compliance = len(
                approved_loans[approved_loans['disbursement_tat_hours'] <= self.sla_standards['loan_disbursement']]
            ) / len(approved_loans)
            
            return {
                'application_approval_tat': {
                    'average': approved_loans['approval_tat_hours'].mean(),
                    'median': approved_loans['approval_tat_hours'].median(),
                    'p95': approved_loans['approval_tat_hours'].quantile(0.95),
                    'sla_compliance_rate': approval_sla_compliance,
                    'sla_breaches': len(approved_loans[approved_loans['approval_tat_hours'] > self.sla_standards['loan_approval']])
                },
                'approval_disbursement_tat': {
                    'average': approved_loans['disbursement_tat_hours'].mean(),
                    'median': approved_loans['disbursement_tat_hours'].median(),
                    'p95': approved_loans['disbursement_tat_hours'].quantile(0.95),
                    'sla_compliance_rate': disbursement_sla_compliance,
                    'sla_breaches': len(approved_loans[approved_loans['disbursement_tat_hours'] > self.sla_standards['loan_disbursement']])
                },
                'overall_loan_tat': {
                    'average': approved_loans['overall_tat_hours'].mean(),
                    'median': approved_loans['overall_tat_hours'].median(),
                    'p95': approved_loans['overall_tat_hours'].quantile(0.95)
                },
                'by_product': self._calculate_tat_by_product(approved_loans),
                'by_branch': self._calculate_tat_by_branch(approved_loans),
                'by_officer': self._calculate_tat_by_officer(approved_loans)
            }
        except Exception as e:
            logger.error(f"Error analyzing loan operations TAT: {e}")
            return self._get_empty_loan_analysis()
    
    def _analyze_service_operations_tat(self, service_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze service request turnaround times"""
        try:
            if service_data.empty:
                return self._get_empty_service_analysis()
            
            service_data = service_data.copy()
            service_data['resolution_tat_hours'] = (
                service_data['resolution_date'] - service_data['request_date']
            ).dt.total_seconds() / 3600
            
            # SLA compliance (using 24 hours as standard for most requests)
            sla_compliance_rate = len(
                service_data[service_data['resolution_tat_hours'] <= 24]
            ) / len(service_data)
            
            return {
                'overall_service_tat': {
                    'average': service_data['resolution_tat_hours'].mean(),
                    'median': service_data['resolution_tat_hours'].median(),
                    'p95': service_data['resolution_tat_hours'].quantile(0.95),
                    'sla_compliance_rate': sla_compliance_rate,
                    'sla_breaches': len(service_data[service_data['resolution_tat_hours'] > 24])
                },
                'by_request_type': self._calculate_tat_by_request_type(service_data),
                'by_priority': self._calculate_tat_by_priority(service_data),
                'by_team': self._calculate_tat_by_team(service_data)
            }
        except Exception as e:
            logger.error(f"Error analyzing service operations TAT: {e}")
            return self._get_empty_service_analysis()
    
    def _analyze_transaction_operations_tat(self, transaction_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze transaction processing turnaround times"""
        try:
            if transaction_data.empty:
                return self._get_empty_transaction_analysis()
            
            transaction_data = transaction_data.copy()
            transaction_data['processing_tat_hours'] = (
                transaction_data['completion_time'] - transaction_data['submission_time']
            ).dt.total_seconds() / 3600
            
            # SLA compliance (using 4 hours as standard for transactions)
            sla_compliance_rate = len(
                transaction_data[transaction_data['processing_tat_hours'] <= 4]
            ) / len(transaction_data)
            
            return {
                'overall_transaction_tat': {
                    'average': transaction_data['processing_tat_hours'].mean(),
                    'median': transaction_data['processing_tat_hours'].median(),
                    'p95': transaction_data['processing_tat_hours'].quantile(0.95),
                    'sla_compliance_rate': sla_compliance_rate,
                    'sla_breaches': len(transaction_data[transaction_data['processing_tat_hours'] > 4])
                },
                'by_transaction_type': self._calculate_tat_by_transaction_type(transaction_data),
                'by_channel': self._calculate_tat_by_channel(transaction_data)
            }
        except Exception as e:
            logger.error(f"Error analyzing transaction operations TAT: {e}")
            return self._get_empty_transaction_analysis()
    
    def _calculate_overall_performance(self, loan_data: pd.DataFrame, service_data: pd.DataFrame, transaction_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate overall TAT performance metrics"""
        try:
            # This would aggregate performance across all operations
            # For now, return simulated overall metrics
            return {
                'overall_sla_compliance': np.random.uniform(0.85, 0.95),
                'average_tat_all_operations': np.random.uniform(12, 36),
                'performance_trend': 'Improving',  # or 'Stable', 'Declining'
                'key_improvement_areas': ['Loan Approval', 'Complaint Resolution'],
                'best_performing_areas': ['Deposit Processing', 'Account Inquiries']
            }
        except Exception as e:
            logger.error(f"Error calculating overall performance: {e}")
            return {
                'overall_sla_compliance': 0.0,
                'average_tat_all_operations': 0.0,
                'performance_trend': 'Unknown',
                'key_improvement_areas': [],
                'best_performing_areas': []
            }
    
    def _identify_bottlenecks(self, loan_data: pd.DataFrame, service_data: pd.DataFrame, transaction_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify process bottlenecks"""
        try:
            bottlenecks = []
            
            # Simulated bottleneck identification
            bottlenecks.append({
                'process': 'Loan Approval',
                'bottleneck_stage': 'Credit Committee Review',
                'average_delay_hours': 18.5,
                'impact_level': 'High',
                'recommendation': 'Implement parallel processing for committee reviews'
            })
            
            bottlenecks.append({
                'process': 'Complaint Resolution', 
                'bottleneck_stage': 'Technical Investigation',
                'average_delay_hours': 36.2,
                'impact_level': 'Medium',
                'recommendation': 'Create dedicated technical support team'
            })
            
            return bottlenecks
        except Exception as e:
            logger.error(f"Error identifying bottlenecks: {e}")
            return []
    
    def _analyze_sla_compliance(self, loan_data: pd.DataFrame, service_data: pd.DataFrame, transaction_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze SLA compliance across all operations"""
        try:
            # Simulated SLA compliance analysis
            return {
                'overall_compliance_rate': 0.89,
                'monthly_trend': {
                    'Jan': 0.85, 'Feb': 0.87, 'Mar': 0.89, 'Apr': 0.91,
                    'May': 0.88, 'Jun': 0.90, 'Jul': 0.92, 'Aug': 0.89
                },
                'department_performance': {
                    'Lending': 0.87,
                    'Customer Service': 0.91,
                    'Operations': 0.93,
                    'IT Support': 0.84
                },
                'critical_sla_breaches': 12,
                'improvement_recommendations': [
                    'Automate loan application status updates',
                    'Implement SLA dashboard for real-time monitoring',
                    'Create escalation matrix for critical delays'
                ]
            }
        except Exception as e:
            logger.error(f"Error analyzing SLA compliance: {e}")
            return {
                'overall_compliance_rate': 0.0,
                'monthly_trend': {},
                'department_performance': {},
                'critical_sla_breaches': 0,
                'improvement_recommendations': []
            }
    
    # Helper methods for detailed analysis
    def _calculate_tat_by_product(self, loan_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate TAT by loan product type"""
        try:
            if loan_data.empty:
                return {}
            return loan_data.groupby('product_type')['approval_tat_hours'].agg(['mean', 'median', 'count']).to_dict()
        except Exception as e:
            logger.error(f"Error calculating TAT by product: {e}")
            return {}
    
    def _calculate_tat_by_branch(self, loan_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate TAT by branch"""
        try:
            if loan_data.empty:
                return {}
            return loan_data.groupby('branch')['approval_tat_hours'].agg(['mean', 'median', 'count']).to_dict()
        except Exception as e:
            logger.error(f"Error calculating TAT by branch: {e}")
            return {}
    
    def _calculate_tat_by_officer(self, loan_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate TAT by approval officer"""
        try:
            if loan_data.empty:
                return {}
            return loan_data.groupby('approval_officer')['approval_tat_hours'].agg(['mean', 'median', 'count']).to_dict()
        except Exception as e:
            logger.error(f"Error calculating TAT by officer: {e}")
            return {}
    
    def _calculate_tat_by_request_type(self, service_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate TAT by service request type"""
        try:
            if service_data.empty:
                return {}
            return service_data.groupby('request_type')['resolution_tat_hours'].agg(['mean', 'median', 'count']).to_dict()
        except Exception as e:
            logger.error(f"Error calculating TAT by request type: {e}")
            return {}
    
    def _calculate_tat_by_priority(self, service_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate TAT by request priority"""
        try:
            if service_data.empty:
                return {}
            return service_data.groupby('priority')['resolution_tat_hours'].agg(['mean', 'median', 'count']).to_dict()
        except Exception as e:
            logger.error(f"Error calculating TAT by priority: {e}")
            return {}
    
    def _calculate_tat_by_team(self, service_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate TAT by assigned team"""
        try:
            if service_data.empty:
                return {}
            return service_data.groupby('assigned_team')['resolution_tat_hours'].agg(['mean', 'median', 'count']).to_dict()
        except Exception as e:
            logger.error(f"Error calculating TAT by team: {e}")
            return {}
    
    def _calculate_tat_by_transaction_type(self, transaction_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate TAT by transaction type"""
        try:
            if transaction_data.empty:
                return {}
            return transaction_data.groupby('transaction_type')['processing_tat_hours'].agg(['mean', 'median', 'count']).to_dict()
        except Exception as e:
            logger.error(f"Error calculating TAT by transaction type: {e}")
            return {}
    
    def _calculate_tat_by_channel(self, transaction_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate TAT by processing channel"""
        try:
            if transaction_data.empty:
                return {}
            return transaction_data.groupby('processing_channel')['processing_tat_hours'].agg(['mean', 'median', 'count']).to_dict()
        except Exception as e:
            logger.error(f"Error calculating TAT by channel: {e}")
            return {}
    
    # Fallback methods for empty data scenarios
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Return fallback analysis when data is unavailable"""
        return {
            'loan_operations': self._get_empty_loan_analysis(),
            'service_operations': self._get_empty_service_analysis(),
            'transaction_operations': self._get_empty_transaction_analysis(),
            'overall_performance': {
                'overall_sla_compliance': 0.0,
                'average_tat_all_operations': 0.0,
                'performance_trend': 'Unknown',
                'key_improvement_areas': [],
                'best_performing_areas': []
            },
            'bottleneck_analysis': [],
            'sla_compliance': {
                'overall_compliance_rate': 0.0,
                'monthly_trend': {},
                'department_performance': {},
                'critical_sla_breaches': 0,
                'improvement_recommendations': []
            },
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _get_empty_loan_analysis(self) -> Dict[str, Any]:
        return {
            'application_approval_tat': {'average': 0, 'median': 0, 'p95': 0, 'sla_compliance_rate': 0, 'sla_breaches': 0},
            'approval_disbursement_tat': {'average': 0, 'median': 0, 'p95': 0, 'sla_compliance_rate': 0, 'sla_breaches': 0},
            'overall_loan_tat': {'average': 0, 'median': 0, 'p95': 0},
            'by_product': {},
            'by_branch': {},
            'by_officer': {}
        }
    
    def _get_empty_service_analysis(self) -> Dict[str, Any]:
        return {
            'overall_service_tat': {'average': 0, 'median': 0, 'p95': 0, 'sla_compliance_rate': 0, 'sla_breaches': 0},
            'by_request_type': {},
            'by_priority': {},
            'by_team': {}
        }
    
    def _get_empty_transaction_analysis(self) -> Dict[str, Any]:
        return {
            'overall_transaction_tat': {'average': 0, 'median': 0, 'p95': 0, 'sla_compliance_rate': 0, 'sla_breaches': 0},
            'by_transaction_type': {},
            'by_channel': {}
        }