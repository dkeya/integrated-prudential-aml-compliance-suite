# sacco_core/analytics/dq_scans.py
"""
Data Quality Scanning Analytics Module
Automated scanning, monitoring, and alerting for SACCO Pro
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
from dataclasses import dataclass
import time

from sacco_core.db import DatabaseManager
from sacco_core.config import ConfigManager
from sacco_core.analytics.dq import DataQualityAnalyzer


@dataclass
class ScanResult:
    """Data quality scan result"""
    scan_id: str
    scan_type: str
    timestamp: datetime
    tables_scanned: List[str]
    issues_found: int
    overall_score: float
    duration: float
    status: str  # Completed, Failed, Running


@dataclass
class ScanConfiguration:
    """Scan configuration"""
    name: str
    frequency: str
    tables: List[str]
    checks: List[str]
    enabled: bool
    last_run: Optional[datetime]
    next_run: Optional[datetime]


class DataQualityScanner:
    """Automated data quality scanning and monitoring"""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        self.config_manager = config_manager or ConfigManager()
        self.db = DatabaseManager()
        self.dq_analyzer = DataQualityAnalyzer()
        self.config = self.config_manager.load_settings()
        
        # Initialize scan storage
        self.scan_results = {}
        self.scheduled_scans = {}
        self.custom_rules = {}
        self.alert_settings = {}
        
        self._initialize_defaults()
    
    def _initialize_defaults(self):
        """Initialize default configurations"""
        # Default scheduled scans
        self.scheduled_scans = {
            'daily_core_scan': {
                'name': 'Daily Core Tables Scan',
                'frequency': 'Daily',
                'time': '02:00 AM',
                'tables': ['members', 'loans', 'employers'],
                'checks': ['completeness', 'accuracy', 'consistency'],
                'status': 'Active',
                'last_run': datetime.now() - timedelta(days=1),
                'next_run': datetime.now() + timedelta(days=1)
            },
            'weekly_full_scan': {
                'name': 'Weekly Full Scan',
                'frequency': 'Weekly',
                'time': 'Sunday 03:00 AM',
                'tables': ['members', 'loans', 'employers', 'deposits', 'transactions'],
                'checks': ['completeness', 'accuracy', 'consistency', 'timeliness', 'uniqueness'],
                'status': 'Active',
                'last_run': datetime.now() - timedelta(days=7),
                'next_run': datetime.now() + timedelta(days=7)
            }
        }
        
        # Default custom rules
        self.custom_rules = {
            'CUST001': {
                'id': 'CUST001',
                'name': 'Loan Amount Validation',
                'description': 'Ensure loan amounts are within reasonable limits',
                'table': 'loans',
                'condition': 'loan_amount BETWEEN 1000 AND 1000000',
                'severity': 'High',
                'status': 'Active'
            },
            'CUST002': {
                'id': 'CUST002',
                'name': 'Member Age Validation',
                'description': 'Ensure member ages are realistic',
                'table': 'members',
                'condition': 'age BETWEEN 18 AND 100',
                'severity': 'Medium',
                'status': 'Active'
            }
        }
        
        # Default alert settings
        self.alert_settings = {
            'email': {
                'enabled': True,
                'critical_issues': True,
                'high_issues': True,
                'medium_issues': False,
                'low_issues': False,
                'daily_summary': True,
                'recipients': ['admin@sacco.com', 'data-team@sacco.com']
            },
            'sms': {
                'enabled': False,
                'recipients': [],
                'critical_only': True
            },
            'thresholds': {
                'critical': 1,
                'high': 5
            }
        }
    
    def get_scan_statistics(self) -> Dict[str, Any]:
        """Get overall scan statistics"""
        # Calculate statistics from scan results
        total_scans = len(self.scan_results)
        active_scans = len([s for s in self.scheduled_scans.values() if s['status'] == 'Active'])
        
        # Calculate total issues from recent scans
        recent_scans = self._get_recent_scans(days=7)
        total_issues = sum(scan.get('issues_found', 0) for scan in recent_scans)
        
        # Calculate coverage (percentage of tables covered by active scans)
        all_tables = ['members', 'loans', 'employers', 'deposits', 'transactions']
        covered_tables = set()
        for scan in self.scheduled_scans.values():
            if scan['status'] == 'Active':
                covered_tables.update(scan['tables'])
        coverage = int((len(covered_tables) / len(all_tables)) * 100)
        
        return {
            'active_scans': active_scans,
            'new_scans_week': 2,  # Mock data
            'total_issues': total_issues,
            'issues_change': -5,  # Mock data
            'coverage': coverage,
            'coverage_change': 5,  # Mock data
            'avg_scan_time': 2.3,  # Mock data
            'time_change': -0.4   # Mock data
        }
    
    def get_scan_trends(self, days: int = 30) -> pd.DataFrame:
        """Get scan trends over time"""
        dates = pd.date_range(start=datetime.now() - timedelta(days=days), 
                             end=datetime.now(), freq='D')
        
        # Generate realistic trend data
        base_success = np.random.uniform(85, 99, len(dates))
        critical_issues = np.random.poisson(2, len(dates))
        high_issues = np.random.poisson(5, len(dates))
        medium_issues = np.random.poisson(10, len(dates))
        
        return pd.DataFrame({
            'date': dates,
            'success_rate': base_success,
            'critical_issues': critical_issues,
            'high_issues': high_issues,
            'medium_issues': medium_issues,
            'scans_completed': np.random.randint(8, 15, len(dates))
        })
    
    def run_comprehensive_scan(self) -> Dict[str, Any]:
        """Run comprehensive data quality scan"""
        start_time = time.time()
        
        try:
            # Run data quality assessment
            assessment = self.dq_analyzer.comprehensive_data_quality_assessment()
            
            # Run data profiling
            profiling = self.dq_analyzer.comprehensive_data_profiling()
            
            # Detect issues
            issues_report = self.dq_analyzer.detect_data_quality_issues()
            
            duration = time.time() - start_time
            
            # Create scan result
            scan_id = f"SCAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            scan_result = {
                'scan_id': scan_id,
                'scan_type': 'Comprehensive Scan',
                'timestamp': datetime.now(),
                'tables_scanned': ['members', 'loans', 'employers', 'deposits', 'transactions'],
                'issues_found': len(issues_report.get('critical_issues', [])) + len(issues_report.get('quality_warnings', [])),
                'overall_score': assessment.get('overall_score', 0) * 100,
                'duration': duration,
                'status': 'Completed',
                'assessment': assessment,
                'profiling': profiling,
                'issues': issues_report
            }
            
            # Store result
            self.scan_results[scan_id] = scan_result
            
            # Check alert thresholds
            self._check_alert_thresholds(scan_result)
            
            return scan_result
            
        except Exception as e:
            return {
                'scan_id': f"SCAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'scan_type': 'Comprehensive Scan',
                'timestamp': datetime.now(),
                'status': 'Failed',
                'error': str(e)
            }
    
    def run_data_profiling_scan(self) -> Dict[str, Any]:
        """Run data profiling scan"""
        start_time = time.time()
        
        try:
            profiling = self.dq_analyzer.comprehensive_data_profiling()
            duration = time.time() - start_time
            
            scan_id = f"PROF_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            scan_result = {
                'scan_id': scan_id,
                'scan_type': 'Data Profiling',
                'timestamp': datetime.now(),
                'duration': duration,
                'status': 'Completed',
                'profiling': profiling
            }
            
            self.scan_results[scan_id] = scan_result
            return scan_result
            
        except Exception as e:
            return {
                'scan_id': f"PROF_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'scan_type': 'Data Profiling',
                'timestamp': datetime.now(),
                'status': 'Failed',
                'error': str(e)
            }
    
    def run_validation_scan(self) -> Dict[str, Any]:
        """Run validation rules scan"""
        start_time = time.time()
        
        try:
            issues_report = self.dq_analyzer.detect_data_quality_issues()
            duration = time.time() - start_time
            
            scan_id = f"VAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            scan_result = {
                'scan_id': scan_id,
                'scan_type': 'Validation Scan',
                'timestamp': datetime.now(),
                'duration': duration,
                'status': 'Completed',
                'validation_results': issues_report.get('validation_rules', []),
                'issues_found': len(issues_report.get('critical_issues', [])) + len(issues_report.get('quality_warnings', []))
            }
            
            self.scan_results[scan_id] = scan_result
            return scan_result
            
        except Exception as e:
            return {
                'scan_id': f"VAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'scan_type': 'Validation Scan',
                'timestamp': datetime.now(),
                'status': 'Failed',
                'error': str(e)
            }
    
    def run_data_cleaning_scan(self) -> Dict[str, Any]:
        """Run data cleaning scan"""
        start_time = time.time()
        
        try:
            # Simulate data cleaning operations
            time.sleep(1)
            
            duration = time.time() - start_time
            
            scan_id = f"CLEAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            scan_result = {
                'scan_id': scan_id,
                'scan_type': 'Data Cleaning',
                'timestamp': datetime.now(),
                'duration': duration,
                'status': 'Completed',
                'cleaning_results': {
                    'records_processed': 12500,
                    'issues_fixed': 342,
                    'quality_improvement': 15.2
                }
            }
            
            self.scan_results[scan_id] = scan_result
            return scan_result
            
        except Exception as e:
            return {
                'scan_id': f"CLEAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'scan_type': 'Data Cleaning',
                'timestamp': datetime.now(),
                'status': 'Failed',
                'error': str(e)
            }
    
    def get_scheduled_scans(self) -> List[Dict[str, Any]]:
        """Get all scheduled scans"""
        return list(self.scheduled_scans.values())
    
    def run_scheduled_scan(self, scan_name: str) -> Dict[str, Any]:
        """Run a scheduled scan immediately"""
        scan_config = next((s for s in self.scheduled_scans.values() if s['name'] == scan_name), None)
        
        if not scan_config:
            return {'success': False, 'error': 'Scan not found'}
        
        try:
            # Update last run time
            scan_config['last_run'] = datetime.now()
            
            # Run the scan based on scan type
            if 'comprehensive' in scan_name.lower():
                result = self.run_comprehensive_scan()
            elif 'profiling' in scan_name.lower():
                result = self.run_data_profiling_scan()
            else:
                result = self.run_validation_scan()
            
            return {'success': True, 'result': result}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def pause_scan(self, scan_name: str) -> bool:
        """Pause a scheduled scan"""
        scan_config = next((s for s in self.scheduled_scans.values() if s['name'] == scan_name), None)
        
        if scan_config:
            scan_config['status'] = 'Inactive'
            return True
        return False
    
    def activate_scan(self, scan_name: str) -> bool:
        """Activate a scheduled scan"""
        scan_config = next((s for s in self.scheduled_scans.values() if s['name'] == scan_name), None)
        
        if scan_config:
            scan_config['status'] = 'Active'
            return True
        return False
    
    def save_scheduled_scan(self, scan_config: Dict[str, Any]) -> bool:
        """Save a new scheduled scan"""
        try:
            scan_id = f"scan_{len(self.scheduled_scans) + 1:03d}"
            
            self.scheduled_scans[scan_id] = {
                'name': scan_config['name'],
                'frequency': scan_config['frequency'],
                'time': '02:00 AM',  # Default time
                'tables': scan_config['tables'],
                'checks': ['completeness', 'accuracy'],  # Default checks
                'status': 'Active' if scan_config['enabled'] else 'Inactive',
                'last_run': None,
                'next_run': datetime.now() + timedelta(days=1)
            }
            
            return True
        except Exception:
            return False
    
    def get_custom_rules(self) -> List[Dict[str, Any]]:
        """Get all custom rules"""
        return list(self.custom_rules.values())
    
    def test_custom_rule(self, rule_id: str) -> Dict[str, Any]:
        """Test a custom rule"""
        rule = self.custom_rules.get(rule_id)
        
        if not rule:
            return {'success': False, 'message': 'Rule not found'}
        
        try:
            # Simulate rule testing
            time.sleep(0.5)
            
            # Mock test results
            test_passed = np.random.choice([True, False], p=[0.8, 0.2])
            
            if test_passed:
                return {'success': True, 'message': 'Rule test passed - no issues found'}
            else:
                return {'success': False, 'message': 'Rule test failed - issues detected'}
                
        except Exception as e:
            return {'success': False, 'message': f'Test error: {str(e)}'}
    
    def deactivate_rule(self, rule_id: str) -> bool:
        """Deactivate a custom rule"""
        if rule_id in self.custom_rules:
            self.custom_rules[rule_id]['status'] = 'Inactive'
            return True
        return False
    
    def activate_rule(self, rule_id: str) -> bool:
        """Activate a custom rule"""
        if rule_id in self.custom_rules:
            self.custom_rules[rule_id]['status'] = 'Active'
            return True
        return False
    
    def save_custom_rule(self, rule_config: Dict[str, Any]) -> Dict[str, Any]:
        """Save a new custom rule"""
        try:
            rule_id = f"CUST{len(self.custom_rules) + 1:03d}"
            
            self.custom_rules[rule_id] = {
                'id': rule_id,
                'name': rule_config['name'],
                'description': rule_config['description'],
                'table': rule_config['table'],
                'condition': rule_config['condition'],
                'severity': rule_config['severity'],
                'status': 'Active' if rule_config['active'] else 'Inactive'
            }
            
            return {'success': True, 'rule_id': rule_id}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_alert_settings(self) -> Dict[str, Any]:
        """Get current alert settings"""
        return self.alert_settings
    
    def save_alert_settings(self, settings: Dict[str, Any]) -> bool:
        """Save alert settings"""
        try:
            self.alert_settings = settings
            return True
        except Exception:
            return False
    
    def get_scan_templates(self) -> List[Dict[str, Any]]:
        """Get available scan templates"""
        return [
            {
                'name': 'Comprehensive Scan',
                'description': 'Full data quality assessment across all dimensions',
                'checks': ['Completeness', 'Accuracy', 'Consistency', 'Timeliness', 'Uniqueness'],
                'tables': 'All Tables',
                'duration': '5-10 minutes'
            },
            {
                'name': 'Quick Health Check',
                'description': 'Rapid assessment of critical data quality metrics',
                'checks': ['Completeness', 'Accuracy'],
                'tables': ['members', 'loans'],
                'duration': '1-2 minutes'
            },
            {
                'name': 'Compliance Scan',
                'description': 'Focus on regulatory and compliance requirements',
                'checks': ['Accuracy', 'Consistency', 'Validation Rules'],
                'tables': ['members', 'transactions'],
                'duration': '3-5 minutes'
            }
        ]
    
    def apply_scan_template(self, template_name: str) -> Dict[str, Any]:
        """Apply a scan template"""
        templates = self.get_scan_templates()
        template = next((t for t in templates if t['name'] == template_name), None)
        
        if not template:
            return {'success': False, 'error': 'Template not found'}
        
        # Create a scheduled scan based on template
        scan_config = {
            'name': f"Template: {template_name}",
            'frequency': 'Weekly',
            'tables': template['tables'],
            'enabled': True
        }
        
        if self.save_scheduled_scan(scan_config):
            return {'success': True, 'message': f"Template '{template_name}' applied successfully"}
        else:
            return {'success': False, 'error': 'Failed to create scheduled scan from template'}
    
    def get_scan_history(self, days: int = 30) -> pd.DataFrame:
        """Get scan history"""
        # Generate sample scan history
        scan_ids = [f'SCAN_{i:04d}' for i in range(1, 21)]
        timestamps = pd.date_range('2024-02-01', periods=20, freq='D')
        
        return pd.DataFrame({
            'scan_id': scan_ids,
            'timestamp': timestamps,
            'scan_type': np.random.choice(['Full Scan', 'Quick Scan', 'Scheduled Scan'], 20),
            'tables_scanned': np.random.randint(3, 8, 20),
            'issues_found': np.random.randint(0, 25, 20),
            'success_rate': np.random.uniform(80, 100, 20),
            'duration_seconds': np.random.uniform(30, 300, 20),
            'status': np.random.choice(['Completed', 'Failed', 'Running'], 20, p=[0.85, 0.1, 0.05])
        })
    
    def get_scan_details(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed scan results"""
        # Check if we have the scan in results
        if scan_id in self.scan_results:
            return self.scan_results[scan_id]
        
        # Generate sample details for mock scans
        return self._generate_sample_scan_details(scan_id)
    
    def implement_recommendation(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Implement a scan recommendation"""
        try:
            # Simulate implementation
            time.sleep(1)
            
            return {
                'success': True,
                'message': f"Successfully implemented: {recommendation['description']}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_recent_scans(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent scans (mock implementation)"""
        return [
            {
                'scan_id': f'SCAN_{i:04d}',
                'timestamp': datetime.now() - timedelta(days=np.random.randint(0, days)),
                'issues_found': np.random.randint(0, 25)
            }
            for i in range(1, 11)
        ]
    
    def _check_alert_thresholds(self, scan_result: Dict[str, Any]):
        """Check if scan results exceed alert thresholds"""
        critical_issues = scan_result.get('issues', {}).get('critical_issues', [])
        high_issues = scan_result.get('issues', {}).get('quality_warnings', [])
        
        critical_threshold = self.alert_settings.get('thresholds', {}).get('critical', 1)
        high_threshold = self.alert_settings.get('thresholds', {}).get('high', 5)
        
        if len(critical_issues) >= critical_threshold:
            self._trigger_alert('critical', len(critical_issues))
        
        if len(high_issues) >= high_threshold:
            self._trigger_alert('high', len(high_issues))
    
    def _trigger_alert(self, severity: str, count: int):
        """Trigger an alert (mock implementation)"""
        print(f"ALERT: {severity.upper()} - {count} issues detected")
        # In production, this would send emails, SMS, etc.
    
    def _generate_sample_scan_details(self, scan_id: str) -> Dict[str, Any]:
        """Generate sample scan details for mock scans"""
        return {
            'summary': {
                'score': np.random.randint(85, 98),
                'issues_found': np.random.randint(5, 25),
                'tables_scanned': np.random.randint(3, 8),
                'duration': np.random.randint(45, 180)
            },
            'table_scores': [
                {'table': 'members', 'score': 95},
                {'table': 'loans', 'score': 88},
                {'table': 'employers', 'score': 92},
                {'table': 'deposits', 'score': 96},
                {'table': 'transactions', 'score': 84}
            ],
            'issues': [
                {
                    'table': 'loans',
                    'column': 'interest_rate',
                    'issue_type': 'Out of Range',
                    'severity': 'High',
                    'affected_records': 12,
                    'description': 'Interest rate outside expected range'
                }
            ],
            'validations': [
                {
                    'rule_id': 'VAL001',
                    'rule_name': 'National ID Format',
                    'status': 'Pass',
                    'error_count': 0
                }
            ],
            'recommendations': [
                {
                    'type': 'Data Cleaning',
                    'description': 'Standardize phone number formats in members table',
                    'impact': 'High'
                }
            ]
        }