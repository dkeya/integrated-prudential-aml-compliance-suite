# sacco_core/analytics/cybersecurity.py
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Cybersecurity Risk Levels"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    MINIMAL = "Minimal"

class ThreatCategory(Enum):
    """Cybersecurity Threat Categories"""
    MALWARE = "Malware"
    PHISHING = "Phishing"
    DDoS = "DDoS"
    DATA_BREACH = "Data Breach"
    INSIDER_THREAT = "Insider Threat"
    SYSTEM_FAILURE = "System Failure"
    COMPLIANCE_VIOLATION = "Compliance Violation"

class BCPStatus(Enum):
    """Business Continuity Plan Status"""
    FULLY_OPERATIONAL = "Fully Operational"
    MINIMAL_IMPACT = "Minimal Impact"
    MODERATE_IMPACT = "Moderate Impact"
    SEVERE_IMPACT = "Severe Impact"
    CRITICAL_FAILURE = "Critical Failure"

@dataclass
class SecurityIncident:
    """Security Incident Record"""
    incident_id: str
    threat_category: ThreatCategory
    severity: RiskLevel
    detection_time: datetime
    resolution_time: Optional[datetime]
    affected_systems: List[str]
    description: str
    response_actions: List[str]
    status: str

@dataclass
class BusinessImpact:
    """Business Impact Analysis Result"""
    business_process: str
    recovery_time_objective: int  # hours
    recovery_point_objective: int  # hours
    maximum_tolerable_downtime: int  # hours
    financial_impact_per_hour: float
    operational_impact: str
    criticality: RiskLevel

@dataclass
class SecurityControl:
    """Security Control Implementation"""
    control_id: str
    control_name: str
    category: str
    implementation_status: str
    effectiveness_score: float
    last_test_date: datetime
    next_test_date: datetime

class CybersecurityAnalyzer:
    """Cybersecurity Risk and Business Continuity Analysis"""
    
    def __init__(self):
        self.security_parameters = {
            'max_login_attempts': 5,
            'session_timeout_minutes': 30,
            'password_expiry_days': 90,
            'mfa_required': True,
            'data_encryption_required': True,
            'backup_frequency_hours': 24
        }
        
        self.threat_intelligence = self._initialize_threat_intelligence()
    
    def analyze_cybersecurity_risk(self) -> Dict[str, Any]:
        """
        Perform comprehensive cybersecurity risk analysis
        
        Returns:
            Dictionary with cybersecurity and BCP analysis results
        """
        try:
            # Extract security data
            security_events = self._extract_security_events()
            system_vulnerabilities = self._extract_vulnerabilities()
            access_logs = self._extract_access_logs()
            backup_status = self._extract_backup_status()
            
            # Threat analysis
            threat_analysis = self._analyze_threat_landscape(security_events)
            
            # Risk assessment
            risk_assessment = self._assess_cybersecurity_risk(system_vulnerabilities, security_events)
            
            # Business continuity analysis
            bcp_analysis = self._analyze_business_continuity(backup_status)
            
            # Security controls assessment
            controls_assessment = self._assess_security_controls()
            
            # Compliance monitoring
            compliance_analysis = self._monitor_compliance(access_logs, security_events)
            
            analysis = {
                'threat_analysis': threat_analysis,
                'risk_assessment': risk_assessment,
                'bcp_analysis': bcp_analysis,
                'controls_assessment': controls_assessment,
                'compliance_analysis': compliance_analysis,
                'incident_response': self._analyze_incident_response(security_events),
                'recovery_capability': self._assess_recovery_capability(backup_status),
                'security_recommendations': self._generate_security_recommendations(risk_assessment, controls_assessment),
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in cybersecurity risk analysis: {e}")
            return self._get_fallback_analysis()
    
    def _extract_security_events(self) -> List[SecurityIncident]:
        """Extract security events and incidents"""
        try:
            np.random.seed(42)
            n_incidents = 150
            
            incidents = []
            for i in range(n_incidents):
                detection_time = datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 365))
                
                # Simulate incident resolution
                resolution_delay = timedelta(hours=np.random.exponential(48))
                resolution_time = detection_time + resolution_delay if np.random.random() > 0.2 else None
                
                incidents.append(SecurityIncident(
                    incident_id=f'SEC-INCIDENT-{50000 + i}',
                    threat_category=np.random.choice(list(ThreatCategory)),
                    severity=np.random.choice(list(RiskLevel), p=[0.05, 0.15, 0.30, 0.40, 0.10]),
                    detection_time=detection_time,
                    resolution_time=resolution_time,
                    affected_systems=np.random.choice(['Core Banking', 'Mobile App', 'Database', 'API Gateway', 'Network'], 
                                                    size=np.random.randint(1, 4), replace=False).tolist(),
                    description=f"Security incident {i} detected and handled",
                    response_actions=['Isolated system', 'Patched vulnerability', 'Reset credentials'][:np.random.randint(1, 3)],
                    status='Resolved' if resolution_time else 'Investigating'
                ))
            
            return incidents
        except Exception as e:
            logger.error(f"Error extracting security events: {e}")
            return []
    
    def _extract_vulnerabilities(self) -> pd.DataFrame:
        """Extract system vulnerabilities"""
        try:
            np.random.seed(42)
            n_vulnerabilities = 85
            
            vulnerabilities = []
            for i in range(n_vulnerabilities):
                vulnerabilities.append({
                    'vulnerability_id': f'VULN-{60000 + i}',
                    'system_component': np.random.choice(['Web Server', 'Database', 'API', 'Mobile App', 'Network']),
                    'severity': np.random.choice(['Critical', 'High', 'Medium', 'Low'], p=[0.1, 0.2, 0.5, 0.2]),
                    'cvss_score': np.random.uniform(0, 10),
                    'discovery_date': datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 300)),
                    'patch_status': np.random.choice(['Patched', 'In Progress', 'Not Started'], p=[0.6, 0.3, 0.1]),
                    'exploit_available': np.random.choice([True, False], p=[0.3, 0.7]),
                    'affected_versions': f"Version {np.random.randint(1, 5)}.{np.random.randint(0, 10)}"
                })
            
            return pd.DataFrame(vulnerabilities)
        except Exception as e:
            logger.error(f"Error extracting vulnerabilities: {e}")
            return pd.DataFrame()
    
    def _extract_access_logs(self) -> pd.DataFrame:
        """Extract system access logs"""
        try:
            np.random.seed(42)
            n_logs = 10000
            
            access_logs = []
            for i in range(n_logs):
                access_time = datetime(2023, 1, 1) + timedelta(
                    days=np.random.randint(0, 365),
                    hours=np.random.randint(0, 24)
                )
                
                access_logs.append({
                    'log_id': f'ACCESS-{70000 + i}',
                    'user_id': f'USER{np.random.randint(1000, 5000)}',
                    'ip_address': f"192.168.{np.random.randint(1, 255)}.{np.random.randint(1, 255)}",
                    'action': np.random.choice(['Login', 'Logout', 'Data Access', 'Configuration Change']),
                    'resource': np.random.choice(['Customer Data', 'Financial Records', 'System Config', 'Reports']),
                    'success': np.random.choice([True, False], p=[0.95, 0.05]),
                    'access_time': access_time,
                    'session_duration': np.random.exponential(30)  # minutes
                })
            
            return pd.DataFrame(access_logs)
        except Exception as e:
            logger.error(f"Error extracting access logs: {e}")
            return pd.DataFrame()
    
    def _extract_backup_status(self) -> Dict[str, Any]:
        """Extract system backup and recovery status"""
        try:
            return {
                'last_full_backup': datetime.now() - timedelta(hours=12),
                'last_incremental_backup': datetime.now() - timedelta(hours=2),
                'backup_success_rate': 0.98,
                'recovery_test_frequency': 'Monthly',
                'last_recovery_test': datetime.now() - timedelta(days=15),
                'recovery_test_success': True,
                'backup_encryption': True,
                'offsite_backup': True,
                'backup_retention_days': 90,
                'recovery_time_objective': 4,  # hours
                'recovery_point_objective': 1   # hour
            }
        except Exception as e:
            logger.error(f"Error extracting backup status: {e}")
            return {}
    
    def _initialize_threat_intelligence(self) -> Dict[str, Any]:
        """Initialize threat intelligence data"""
        return {
            'emerging_threats': [
                {'threat': 'Ransomware-as-a-Service', 'severity': 'High', 'sector': 'Financial'},
                {'threat': 'API Security Vulnerabilities', 'severity': 'Medium', 'sector': 'All'},
                {'threat': 'Supply Chain Attacks', 'severity': 'High', 'sector': 'Technology'}
            ],
            'threat_actors': [
                {'group': 'FIN7', 'targets': 'Financial Institutions', 'tactics': 'Phishing, Malware'},
                {'group': 'Lazarus', 'targets': 'Banks, Cryptocurrency', 'tactics': 'DDoS, Data Theft'}
            ],
            'vulnerability_trends': {
                'web_application': 0.35,
                'mobile_security': 0.25,
                'cloud_security': 0.20,
                'network_security': 0.15,
                'physical_security': 0.05
            }
        }
    
    def _analyze_threat_landscape(self, security_events: List[SecurityIncident]) -> Dict[str, Any]:
        """Analyze current threat landscape"""
        try:
            if not security_events:
                return {}
            
            # Threat category distribution
            threat_distribution = {}
            for incident in security_events:
                category = incident.threat_category.value
                threat_distribution[category] = threat_distribution.get(category, 0) + 1
            
            # Severity distribution
            severity_distribution = {}
            for incident in security_events:
                severity = incident.severity.value
                severity_distribution[severity] = severity_distribution.get(severity, 0) + 1
            
            # Response time analysis
            resolved_incidents = [inc for inc in security_events if inc.resolution_time]
            response_times = []
            for incident in resolved_incidents:
                response_time = (incident.resolution_time - incident.detection_time).total_seconds() / 3600  # hours
                response_times.append(response_time)
            
            avg_response_time = np.mean(response_times) if response_times else 0
            
            return {
                'threat_distribution': threat_distribution,
                'severity_distribution': severity_distribution,
                'total_incidents': len(security_events),
                'resolved_incidents': len(resolved_incidents),
                'average_response_time_hours': avg_response_time,
                'emerging_threats': self.threat_intelligence['emerging_threats'],
                'threat_actors': self.threat_intelligence['threat_actors']
            }
        except Exception as e:
            logger.error(f"Error analyzing threat landscape: {e}")
            return {}
    
    def _assess_cybersecurity_risk(self, vulnerabilities: pd.DataFrame, security_events: List[SecurityIncident]) -> Dict[str, Any]:
        """Assess overall cybersecurity risk"""
        try:
            # Vulnerability risk score
            vuln_risk_score = 0
            if not vulnerabilities.empty:
                severity_weights = {'Critical': 1.0, 'High': 0.7, 'Medium': 0.4, 'Low': 0.1}
                total_weight = 0
                for _, vuln in vulnerabilities.iterrows():
                    weight = severity_weights.get(vuln['severity'], 0.1)
                    vuln_risk_score += weight * (vuln['cvss_score'] / 10)
                    total_weight += weight
                
                vuln_risk_score = vuln_risk_score / total_weight if total_weight > 0 else 0
            
            # Incident risk score
            incident_risk_score = 0
            if security_events:
                severity_weights = {RiskLevel.CRITICAL: 1.0, RiskLevel.HIGH: 0.7, RiskLevel.MEDIUM: 0.4, 
                                  RiskLevel.LOW: 0.2, RiskLevel.MINIMAL: 0.1}
                total_weight = 0
                for incident in security_events:
                    weight = severity_weights.get(incident.severity, 0.1)
                    incident_risk_score += weight
                    total_weight += weight
                
                incident_risk_score = incident_risk_score / total_weight if total_weight > 0 else 0
            
            # Overall risk score (weighted average)
            overall_risk = (vuln_risk_score * 0.6 + incident_risk_score * 0.4) * 100
            
            # Determine risk level
            if overall_risk >= 80:
                risk_level = RiskLevel.CRITICAL
            elif overall_risk >= 60:
                risk_level = RiskLevel.HIGH
            elif overall_risk >= 40:
                risk_level = RiskLevel.MEDIUM
            elif overall_risk >= 20:
                risk_level = RiskLevel.LOW
            else:
                risk_level = RiskLevel.MINIMAL
            
            return {
                'overall_risk_score': overall_risk,
                'risk_level': risk_level,
                'vulnerability_risk_score': vuln_risk_score * 100,
                'incident_risk_score': incident_risk_score * 100,
                'critical_vulnerabilities': len(vulnerabilities[vulnerabilities['severity'] == 'Critical']) if not vulnerabilities.empty else 0,
                'unpatched_vulnerabilities': len(vulnerabilities[vulnerabilities['patch_status'] != 'Patched']) if not vulnerabilities.empty else 0,
                'trend_comparison': self._calculate_risk_trend(security_events)
            }
        except Exception as e:
            logger.error(f"Error assessing cybersecurity risk: {e}")
            return {
                'overall_risk_score': 0,
                'risk_level': RiskLevel.MINIMAL,
                'vulnerability_risk_score': 0,
                'incident_risk_score': 0,
                'critical_vulnerabilities': 0,
                'unpatched_vulnerabilities': 0,
                'trend_comparison': {}
            }
    
    def _analyze_business_continuity(self, backup_status: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze business continuity preparedness"""
        try:
            # Business Impact Analysis (simulated)
            business_processes = [
                BusinessImpact(
                    business_process="Core Banking Operations",
                    recovery_time_objective=4,
                    recovery_point_objective=1,
                    maximum_tolerable_downtime=8,
                    financial_impact_per_hour=50000,
                    operational_impact="Critical - No transactions possible",
                    criticality=RiskLevel.CRITICAL
                ),
                BusinessImpact(
                    business_process="Member Services",
                    recovery_time_objective=8,
                    recovery_point_objective=4,
                    maximum_tolerable_downtime=24,
                    financial_impact_per_hour=15000,
                    operational_impact="High - Limited member services",
                    criticality=RiskLevel.HIGH
                ),
                BusinessImpact(
                    business_process="Reporting & Analytics",
                    recovery_time_objective=24,
                    recovery_point_objective=12,
                    maximum_tolerable_downtime=48,
                    financial_impact_per_hour=5000,
                    operational_impact="Medium - Delayed reporting",
                    criticality=RiskLevel.MEDIUM
                )
            ]
            
            # Calculate BCP readiness score
            readiness_score = 0
            max_score = len(business_processes) * 100
            
            for process in business_processes:
                process_score = 100
                
                # Deduct points based on RTO/RPO compliance
                if backup_status.get('recovery_time_objective', 999) > process.recovery_time_objective:
                    process_score -= 30
                
                if backup_status.get('recovery_point_objective', 999) > process.recovery_point_objective:
                    process_score -= 20
                
                # Deduct points for backup issues
                if not backup_status.get('backup_encryption', False):
                    process_score -= 15
                
                if not backup_status.get('offsite_backup', False):
                    process_score -= 10
                
                readiness_score += max(0, process_score)
            
            overall_readiness = (readiness_score / max_score) * 100
            
            # Determine BCP status
            if overall_readiness >= 90:
                bcp_status = BCPStatus.FULLY_OPERATIONAL
            elif overall_readiness >= 75:
                bcp_status = BCPStatus.MINIMAL_IMPACT
            elif overall_readiness >= 60:
                bcp_status = BCPStatus.MODERATE_IMPACT
            elif overall_readiness >= 40:
                bcp_status = BCPStatus.SEVERE_IMPACT
            else:
                bcp_status = BCPStatus.CRITICAL_FAILURE
            
            return {
                'bcp_status': bcp_status,
                'readiness_score': overall_readiness,
                'business_impact_analysis': business_processes,
                'recovery_capabilities': backup_status,
                'last_recovery_test': backup_status.get('last_recovery_test', 'Unknown'),
                'recovery_test_success': backup_status.get('recovery_test_success', False)
            }
        except Exception as e:
            logger.error(f"Error analyzing business continuity: {e}")
            return {
                'bcp_status': BCPStatus.CRITICAL_FAILURE,
                'readiness_score': 0,
                'business_impact_analysis': [],
                'recovery_capabilities': {},
                'last_recovery_test': 'Unknown',
                'recovery_test_success': False
            }
    
    def _assess_security_controls(self) -> Dict[str, Any]:
        """Assess security controls effectiveness"""
        try:
            # Simulated security controls assessment
            controls = [
                SecurityControl(
                    control_id="CTL-001",
                    control_name="Multi-Factor Authentication",
                    category="Access Control",
                    implementation_status="Fully Implemented",
                    effectiveness_score=0.95,
                    last_test_date=datetime.now() - timedelta(days=30),
                    next_test_date=datetime.now() + timedelta(days=30)
                ),
                SecurityControl(
                    control_id="CTL-002",
                    control_name="Data Encryption at Rest",
                    category="Data Protection",
                    implementation_status="Fully Implemented",
                    effectiveness_score=0.90,
                    last_test_date=datetime.now() - timedelta(days=60),
                    next_test_date=datetime.now() + timedelta(days=30)
                ),
                SecurityControl(
                    control_id="CTL-003",
                    control_name="Network Segmentation",
                    category="Network Security",
                    implementation_status="Partially Implemented",
                    effectiveness_score=0.75,
                    last_test_date=datetime.now() - timedelta(days=90),
                    next_test_date=datetime.now() + timedelta(days=15)
                ),
                SecurityControl(
                    control_id="CTL-004",
                    control_name="Incident Response Plan",
                    category="Response & Recovery",
                    implementation_status="Fully Implemented",
                    effectiveness_score=0.85,
                    last_test_date=datetime.now() - timedelta(days=45),
                    next_test_date=datetime.now() + timedelta(days=45)
                )
            ]
            
            # Calculate overall effectiveness
            overall_effectiveness = np.mean([control.effectiveness_score for control in controls]) * 100
            
            return {
                'security_controls': controls,
                'overall_effectiveness': overall_effectiveness,
                'fully_implemented': len([c for c in controls if c.implementation_status == "Fully Implemented"]),
                'partially_implemented': len([c for c in controls if c.implementation_status == "Partially Implemented"]),
                'not_implemented': len([c for c in controls if c.implementation_status == "Not Implemented"])
            }
        except Exception as e:
            logger.error(f"Error assessing security controls: {e}")
            return {
                'security_controls': [],
                'overall_effectiveness': 0,
                'fully_implemented': 0,
                'partially_implemented': 0,
                'not_implemented': 0
            }
    
    def _monitor_compliance(self, access_logs: pd.DataFrame, security_events: List[SecurityIncident]) -> Dict[str, Any]:
        """Monitor regulatory and security compliance"""
        try:
            # Analyze access patterns for compliance
            failed_logins = len(access_logs[access_logs['action'] == 'Login'][access_logs['success'] == False]) if not access_logs.empty else 0
            total_logins = len(access_logs[access_logs['action'] == 'Login']) if not access_logs.empty else 0
            failed_login_rate = failed_logins / total_logins if total_logins > 0 else 0
            
            # Check for compliance violations
            compliance_violations = []
            
            if failed_login_rate > 0.1:  # More than 10% failed logins
                compliance_violations.append("High failed login rate detected")
            
            # Check session timeout compliance
            long_sessions = len(access_logs[access_logs['session_duration'] > 120]) if not access_logs.empty else 0  # > 2 hours
            if long_sessions > 10:
                compliance_violations.append("Excessive session durations detected")
            
            # Data access compliance
            unauthorized_access_attempts = len([e for e in security_events if e.threat_category == ThreatCategory.INSIDER_THREAT])
            if unauthorized_access_attempts > 0:
                compliance_violations.append("Unauthorized access attempts detected")
            
            return {
                'compliance_score': max(0, 100 - len(compliance_violations) * 10),
                'failed_login_rate': failed_login_rate * 100,
                'compliance_violations': compliance_violations,
                'gdpr_compliance': True,
                'data_protection_compliance': True,
                'access_control_compliance': failed_login_rate < 0.15,
                'audit_trail_compliance': True
            }
        except Exception as e:
            logger.error(f"Error monitoring compliance: {e}")
            return {
                'compliance_score': 0,
                'failed_login_rate': 0,
                'compliance_violations': ['Compliance monitoring unavailable'],
                'gdpr_compliance': False,
                'data_protection_compliance': False,
                'access_control_compliance': False,
                'audit_trail_compliance': False
            }
    
    def _analyze_incident_response(self, security_events: List[SecurityIncident]) -> Dict[str, Any]:
        """Analyze incident response effectiveness"""
        try:
            resolved_incidents = [inc for inc in security_events if inc.resolution_time]
            
            if not resolved_incidents:
                return {
                    'average_response_time': 0,
                    'incident_resolution_rate': 0,
                    'response_effectiveness': 'Unknown',
                    'improvement_areas': ['No incident data available']
                }
            
            response_times = []
            for incident in resolved_incidents:
                response_time = (incident.resolution_time - incident.detection_time).total_seconds() / 3600
                response_times.append(response_time)
            
            avg_response_time = np.mean(response_times)
            resolution_rate = len(resolved_incidents) / len(security_events) * 100
            
            # Determine effectiveness
            if avg_response_time <= 4 and resolution_rate >= 90:
                effectiveness = "Excellent"
            elif avg_response_time <= 8 and resolution_rate >= 80:
                effectiveness = "Good"
            elif avg_response_time <= 24 and resolution_rate >= 70:
                effectiveness = "Adequate"
            else:
                effectiveness = "Needs Improvement"
            
            improvement_areas = []
            if avg_response_time > 8:
                improvement_areas.append("Reduce incident response time")
            if resolution_rate < 80:
                improvement_areas.append("Improve incident resolution rate")
            
            return {
                'average_response_time': avg_response_time,
                'incident_resolution_rate': resolution_rate,
                'response_effectiveness': effectiveness,
                'improvement_areas': improvement_areas,
                'total_incidents_handled': len(resolved_incidents)
            }
        except Exception as e:
            logger.error(f"Error analyzing incident response: {e}")
            return {
                'average_response_time': 0,
                'incident_resolution_rate': 0,
                'response_effectiveness': 'Unknown',
                'improvement_areas': ['Incident response analysis unavailable'],
                'total_incidents_handled': 0
            }
    
    def _assess_recovery_capability(self, backup_status: Dict[str, Any]) -> Dict[str, Any]:
        """Assess disaster recovery capability"""
        try:
            recovery_score = 0
            max_score = 100
            
            # Backup frequency (25 points)
            backup_frequency = backup_status.get('backup_frequency_hours', 999)
            if backup_frequency <= 1:
                recovery_score += 25
            elif backup_frequency <= 4:
                recovery_score += 20
            elif backup_frequency <= 12:
                recovery_score += 15
            elif backup_frequency <= 24:
                recovery_score += 10
            else:
                recovery_score += 5
            
            # Backup success rate (25 points)
            success_rate = backup_status.get('backup_success_rate', 0)
            recovery_score += success_rate * 25
            
            # Recovery testing (25 points)
            last_test_days = (datetime.now() - backup_status.get('last_recovery_test', datetime.now())).days
            if last_test_days <= 7:
                recovery_score += 25
            elif last_test_days <= 30:
                recovery_score += 20
            elif last_test_days <= 90:
                recovery_score += 15
            elif last_test_days <= 180:
                recovery_score += 10
            else:
                recovery_score += 5
            
            # Security measures (25 points)
            security_points = 0
            if backup_status.get('backup_encryption', False):
                security_points += 10
            if backup_status.get('offsite_backup', False):
                security_points += 10
            if backup_status.get('recovery_test_success', False):
                security_points += 5
            
            recovery_score += security_points
            
            return {
                'recovery_capability_score': recovery_score,
                'recovery_readiness': 'High' if recovery_score >= 80 else 'Medium' if recovery_score >= 60 else 'Low',
                'backup_frequency_hours': backup_frequency,
                'backup_success_rate': success_rate * 100,
                'days_since_last_test': last_test_days,
                'security_measures': security_points
            }
        except Exception as e:
            logger.error(f"Error assessing recovery capability: {e}")
            return {
                'recovery_capability_score': 0,
                'recovery_readiness': 'Unknown',
                'backup_frequency_hours': 0,
                'backup_success_rate': 0,
                'days_since_last_test': 999,
                'security_measures': 0
            }
    
    def _generate_security_recommendations(self, risk_assessment: Dict[str, Any], controls_assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate security improvement recommendations"""
        recommendations = []
        
        # Risk-based recommendations
        risk_level = risk_assessment.get('risk_level', RiskLevel.MINIMAL)
        if risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
            recommendations.append({
                'priority': 'Critical',
                'category': 'Risk Mitigation',
                'recommendation': 'Implement immediate threat containment measures',
                'estimated_effort': '2-4 weeks',
                'impact': 'High'
            })
        
        # Vulnerability management
        unpatched_vulns = risk_assessment.get('unpatched_vulnerabilities', 0)
        if unpatched_vulns > 5:
            recommendations.append({
                'priority': 'High',
                'category': 'Vulnerability Management',
                'recommendation': f'Patch {unpatched_vulns} unpatched vulnerabilities',
                'estimated_effort': '1-2 weeks',
                'impact': 'High'
            })
        
        # Security controls
        controls_effectiveness = controls_assessment.get('overall_effectiveness', 0)
        if controls_effectiveness < 80:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Security Controls',
                'recommendation': 'Enhance security controls effectiveness',
                'estimated_effort': '4-8 weeks',
                'impact': 'Medium'
            })
        
        # Backup and recovery
        if controls_effectiveness < 70:
            recommendations.append({
                'priority': 'High',
                'category': 'Business Continuity',
                'recommendation': 'Improve backup and recovery procedures',
                'estimated_effort': '2-4 weeks',
                'impact': 'High'
            })
        
        return recommendations
    
    def _calculate_risk_trend(self, security_events: List[SecurityIncident]) -> Dict[str, float]:
        """Calculate cybersecurity risk trend"""
        # Simulated trend data
        return {
            '3_months_ago': 65.2,
            '2_months_ago': 58.7,
            '1_month_ago': 52.3,
            'current': 48.9
        }
    
    # Fallback methods
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Return fallback analysis when data is unavailable"""
        return {
            'threat_analysis': {},
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
            'incident_response': {
                'average_response_time': 0,
                'incident_resolution_rate': 0,
                'response_effectiveness': 'Unknown',
                'improvement_areas': ['Data unavailable'],
                'total_incidents_handled': 0
            },
            'recovery_capability': {
                'recovery_capability_score': 0,
                'recovery_readiness': 'Unknown',
                'backup_frequency_hours': 0,
                'backup_success_rate': 0,
                'days_since_last_test': 999,
                'security_measures': 0
            },
            'security_recommendations': [],
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }