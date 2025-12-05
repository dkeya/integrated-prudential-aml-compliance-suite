# sacco_core/analytics/policy_engine.py

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
import logging
from dataclass import dataclass
from enum import Enum
import yaml
import json
from sqlalchemy import text

logger = logging.getLogger(__name__)

class PolicyRuleType(Enum):
    """Policy Rule Types"""
    RISK_MONITORING = "Risk Monitoring"
    COMPLIANCE = "Compliance"
    OPERATIONAL = "Operational"
    FINANCIAL = "Financial"
    SECURITY = "Security"

class RuleStatus(Enum):
    """Rule Execution Status"""
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    TRIGGERED = "Triggered"
    OVERRIDDEN = "Overridden"
    DISABLED = "Disabled"

class AlertSeverity(Enum):
    """Alert Severity Levels"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Information"

@dataclass
class PolicyRule:
    """Policy Rule Definition"""
    rule_id: str
    rule_name: str
    rule_type: PolicyRuleType
    description: str
    condition: str
    action: str
    severity: AlertSeverity
    status: RuleStatus
    created_date: datetime
    last_triggered: Optional[datetime]
    trigger_count: int
    parameters: Dict[str, Any]

@dataclass
class RuleExecution:
    """Rule Execution Record"""
    execution_id: str
    rule_id: str
    timestamp: datetime
    status: str
    triggered: bool
    conditions_met: Dict[str, Any]
    actions_taken: List[str]
    alert_generated: bool
    override_reason: Optional[str]

@dataclass
class PolicyAlert:
    """Policy Alert Record"""
    alert_id: str
    rule_id: str
    timestamp: datetime
    severity: AlertSeverity
    title: str
    description: str
    affected_entities: List[str]
    status: str
    assigned_to: Optional[str]
    resolution_notes: Optional[str]
    resolved_at: Optional[datetime]

class PolicyEngineAnalyzer:
    """Policy Rule Monitoring and Execution Engine"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.policy_rules = self._load_policy_rules()
        self.rule_executions = []
        self.active_alerts = []
    
    def _load_policy_rules(self) -> List[PolicyRule]:
        """Load policy rules from configuration"""
        try:
            # Load from YAML configuration
            rules_config = self._load_rules_config()
            rules = []
            
            for rule_config in rules_config:
                rules.append(PolicyRule(
                    rule_id=rule_config['rule_id'],
                    rule_name=rule_config['rule_name'],
                    rule_type=PolicyRuleType(rule_config['rule_type']),
                    description=rule_config['description'],
                    condition=rule_config['condition'],
                    action=rule_config['action'],
                    severity=AlertSeverity(rule_config['severity']),
                    status=RuleStatus(rule_config['status']),
                    created_date=datetime.strptime(rule_config['created_date'], '%Y-%m-%d'),
                    last_triggered=datetime.strptime(rule_config['last_triggered'], '%Y-%m-%d') if rule_config['last_triggered'] else None,
                    trigger_count=rule_config['trigger_count'],
                    parameters=rule_config.get('parameters', {})
                ))
            
            return rules
            
        except Exception as e:
            logger.error(f"Error loading policy rules: {e}")
            return self._get_default_rules()
    
    def _load_rules_config(self) -> List[Dict[str, Any]]:
        """Load rules configuration from YAML"""
        default_rules = [
            {
                'rule_id': 'RULE-001',
                'rule_name': 'PAR 30 Days Threshold',
                'rule_type': 'Risk Monitoring',
                'description': 'Alert when PAR 30 days exceeds 5% threshold',
                'condition': 'par_30_days > 5.0',
                'action': 'generate_alert, notify_risk_team, escalate_management',
                'severity': 'High',
                'status': 'Active',
                'created_date': '2024-01-01',
                'last_triggered': '2024-01-15',
                'trigger_count': 3,
                'parameters': {'threshold': 5.0, 'escalation_level': 'Management'}
            },
            {
                'rule_id': 'RULE-002',
                'rule_name': 'Single Employer Concentration',
                'rule_type': 'Risk Monitoring',
                'description': 'Alert when single employer exposure exceeds 25%',
                'condition': 'employer_concentration > 25.0',
                'action': 'generate_alert, notify_credit_committee, require_approval',
                'severity': 'Critical',
                'status': 'Active',
                'created_date': '2024-01-01',
                'last_triggered': '2024-01-10',
                'trigger_count': 2,
                'parameters': {'threshold': 25.0, 'approval_required': True}
            },
            {
                'rule_id': 'RULE-003',
                'rule_name': 'Liquidity Coverage Ratio',
                'rule_type': 'Financial',
                'description': 'Monitor LCR compliance below 100%',
                'condition': 'liquidity_coverage_ratio < 100.0',
                'action': 'generate_alert, notify_treasury, restrict_lending',
                'severity': 'Critical',
                'status': 'Active',
                'created_date': '2024-01-01',
                'last_triggered': None,
                'trigger_count': 0,
                'parameters': {'minimum_ratio': 100.0, 'restriction_level': 'High'}
            },
            {
                'rule_id': 'RULE-004',
                'rule_name': 'Capital Adequacy Ratio',
                'rule_type': 'Compliance',
                'description': 'Ensure CAR remains above regulatory minimum',
                'condition': 'capital_adequacy_ratio < 10.0',
                'action': 'generate_alert, notify_board, require_capital_plan',
                'severity': 'High',
                'status': 'Active',
                'created_date': '2024-01-01',
                'last_triggered': None,
                'trigger_count': 0,
                'parameters': {'regulatory_minimum': 10.0, 'plan_required': True}
            },
            {
                'rule_id': 'RULE-005',
                'rule_name': 'Loan Turnaround Time',
                'rule_type': 'Operational',
                'description': 'Monitor loan application processing delays',
                'condition': 'avg_processing_time > 48',
                'action': 'generate_alert, notify_operations, optimize_process',
                'severity': 'Medium',
                'status': 'Active',
                'created_date': '2024-01-01',
                'last_triggered': '2024-01-20',
                'trigger_count': 5,
                'parameters': {'max_hours': 48, 'review_process': True}
            },
            {
                'rule_id': 'RULE-006',
                'rule_name': 'Data Quality Threshold',
                'rule_type': 'Operational',
                'description': 'Alert on data quality issues',
                'condition': 'data_quality_score < 90.0',
                'action': 'generate_alert, notify_data_team, suspend_reporting',
                'severity': 'High',
                'status': 'Active',
                'created_date': '2024-01-01',
                'last_triggered': '2024-01-08',
                'trigger_count': 1,
                'parameters': {'min_score': 90.0, 'suspension_threshold': 80.0}
            },
            {
                'rule_id': 'RULE-007',
                'rule_name': 'Dividend Capacity',
                'rule_type': 'Financial',
                'description': 'Monitor dividend distribution capacity',
                'condition': 'dividend_capacity_ratio < 1.2',
                'action': 'generate_alert, notify_finance, adjust_dividend',
                'severity': 'Medium',
                'status': 'Active',
                'created_date': '2024-01-01',
                'last_triggered': None,
                'trigger_count': 0,
                'parameters': {'min_ratio': 1.2, 'adjustment_required': True}
            },
            {
                'rule_id': 'RULE-008',
                'rule_name': 'Cybersecurity Incident',
                'rule_type': 'Security',
                'description': 'Monitor cybersecurity threat levels',
                'condition': 'cyber_risk_score > 70.0',
                'action': 'generate_alert, notify_security_team, enhance_monitoring',
                'severity': 'Critical',
                'status': 'Active',
                'created_date': '2024-01-01',
                'last_triggered': None,
                'trigger_count': 0,
                'parameters': {'risk_threshold': 70.0, 'response_level': 'Enhanced'}
            }
        ]
        return default_rules
    
    def _get_default_rules(self) -> List[PolicyRule]:
        """Get default policy rules as fallback"""
        return [
            PolicyRule(
                rule_id='RULE-DEFAULT-001',
                rule_name='Default Risk Monitor',
                rule_type=PolicyRuleType.RISK_MONITORING,
                description='Default risk monitoring rule',
                condition='true',
                action='generate_alert',
                severity=AlertSeverity.MEDIUM,
                status=RuleStatus.ACTIVE,
                created_date=datetime.now(),
                last_triggered=None,
                trigger_count=0,
                parameters={}
            )
        ]
    
    def execute_policy_engine(self) -> Dict[str, Any]:
        """
        Execute all policy rules and return comprehensive analysis
        
        Returns:
            Dictionary with policy engine execution results
        """
        try:
            # Execute all active rules
            execution_results = []
            triggered_rules = []
            generated_alerts = []
            
            for rule in self.policy_rules:
                if rule.status == RuleStatus.ACTIVE:
                    execution = self._execute_rule(rule)
                    execution_results.append(execution)
                    
                    if execution.triggered:
                        triggered_rules.append(rule)
                        alert = self._generate_alert(rule, execution)
                        if alert:
                            generated_alerts.append(alert)
            
            # Update rule statistics
            self._update_rule_statistics(triggered_rules)
            
            # Comprehensive analysis
            analysis = {
                'execution_summary': self._generate_execution_summary(execution_results),
                'triggered_rules': triggered_rules,
                'active_alerts': generated_alerts,
                'rule_effectiveness': self._analyze_rule_effectiveness(execution_results),
                'risk_exposure': self._calculate_risk_exposure(triggered_rules),
                'compliance_status': self._assess_compliance_status(execution_results),
                'recommendations': self._generate_policy_recommendations(execution_results),
                'execution_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error executing policy engine: {e}")
            return self._get_fallback_analysis()
    
    def _execute_rule(self, rule: PolicyRule) -> RuleExecution:
        """Execute a single policy rule"""
        try:
            # Evaluate rule condition
            conditions_met = self._evaluate_condition(rule.condition, rule.parameters)
            triggered = bool(conditions_met)
            
            # Execute actions if triggered
            actions_taken = []
            alert_generated = False
            
            if triggered:
                actions_taken = self._execute_actions(rule.action, rule.parameters)
                alert_generated = 'generate_alert' in rule.action
            
            return RuleExecution(
                execution_id=f"EXEC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{rule.rule_id}",
                rule_id=rule.rule_id,
                timestamp=datetime.now(),
                status="Completed",
                triggered=triggered,
                conditions_met=conditions_met,
                actions_taken=actions_taken,
                alert_generated=alert_generated,
                override_reason=None
            )
            
        except Exception as e:
            logger.error(f"Error executing rule {rule.rule_id}: {e}")
            return RuleExecution(
                execution_id=f"EXEC-ERROR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                rule_id=rule.rule_id,
                timestamp=datetime.now(),
                status="Error",
                triggered=False,
                conditions_met={},
                actions_taken=[],
                alert_generated=False,
                override_reason=f"Execution error: {str(e)}"
            )
    
    def _evaluate_condition(self, condition: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate rule condition against current data"""
        try:
            # Simulate condition evaluation with real data
            current_metrics = self._get_current_metrics()
            
            # Map condition to actual metric evaluation
            condition_evaluation = {}
            
            if 'par_30_days' in condition:
                par_30 = current_metrics.get('par_30_days', 3.2)
                threshold = parameters.get('threshold', 5.0)
                condition_evaluation['par_30_days'] = {
                    'current_value': par_30,
                    'threshold': threshold,
                    'triggered': par_30 > threshold
                }
            
            elif 'employer_concentration' in condition:
                concentration = current_metrics.get('max_employer_concentration', 18.5)
                threshold = parameters.get('threshold', 25.0)
                condition_evaluation['employer_concentration'] = {
                    'current_value': concentration,
                    'threshold': threshold,
                    'triggered': concentration > threshold
                }
            
            elif 'liquidity_coverage_ratio' in condition:
                lcr = current_metrics.get('liquidity_coverage_ratio', 125.0)
                threshold = parameters.get('minimum_ratio', 100.0)
                condition_evaluation['liquidity_coverage_ratio'] = {
                    'current_value': lcr,
                    'threshold': threshold,
                    'triggered': lcr < threshold
                }
            
            elif 'capital_adequacy_ratio' in condition:
                car = current_metrics.get('capital_adequacy_ratio', 15.2)
                threshold = parameters.get('regulatory_minimum', 10.0)
                condition_evaluation['capital_adequacy_ratio'] = {
                    'current_value': car,
                    'threshold': threshold,
                    'triggered': car < threshold
                }
            
            elif 'avg_processing_time' in condition:
                processing_time = current_metrics.get('avg_loan_processing_hours', 36.0)
                threshold = parameters.get('max_hours', 48.0)
                condition_evaluation['avg_processing_time'] = {
                    'current_value': processing_time,
                    'threshold': threshold,
                    'triggered': processing_time > threshold
                }
            
            elif 'data_quality_score' in condition:
                dq_score = current_metrics.get('data_quality_score', 95.0)
                threshold = parameters.get('min_score', 90.0)
                condition_evaluation['data_quality_score'] = {
                    'current_value': dq_score,
                    'threshold': threshold,
                    'triggered': dq_score < threshold
                }
            
            elif 'dividend_capacity_ratio' in condition:
                dividend_ratio = current_metrics.get('dividend_capacity_ratio', 1.8)
                threshold = parameters.get('min_ratio', 1.2)
                condition_evaluation['dividend_capacity_ratio'] = {
                    'current_value': dividend_ratio,
                    'threshold': threshold,
                    'triggered': dividend_ratio < threshold
                }
            
            elif 'cyber_risk_score' in condition:
                cyber_score = current_metrics.get('cyber_risk_score', 45.0)
                threshold = parameters.get('risk_threshold', 70.0)
                condition_evaluation['cyber_risk_score'] = {
                    'current_value': cyber_score,
                    'threshold': threshold,
                    'triggered': cyber_score > threshold
                }
            
            return condition_evaluation
            
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return {'error': str(e)}
    
    def _get_current_metrics(self) -> Dict[str, float]:
        """Get current SACCO metrics for rule evaluation"""
        try:
            # Simulate current metrics - in production this would query actual data
            return {
                'par_30_days': 3.2,
                'max_employer_concentration': 18.5,
                'liquidity_coverage_ratio': 125.0,
                'capital_adequacy_ratio': 15.2,
                'avg_loan_processing_hours': 36.0,
                'data_quality_score': 95.0,
                'dividend_capacity_ratio': 1.8,
                'cyber_risk_score': 45.0,
                'total_assets': 2500000000,
                'total_loans': 1800000000,
                'total_deposits': 2200000000
            }
        except Exception as e:
            logger.error(f"Error getting current metrics: {e}")
            return {}
    
    def _execute_actions(self, actions: str, parameters: Dict[str, Any]) -> List[str]:
        """Execute rule actions"""
        action_list = [action.strip() for action in actions.split(',')]
        executed_actions = []
        
        for action in action_list:
            try:
                if action == 'generate_alert':
                    executed_actions.append('Alert generated')
                elif action == 'notify_risk_team':
                    executed_actions.append('Risk team notified')
                elif action == 'escalate_management':
                    executed_actions.append('Management escalation initiated')
                elif action == 'notify_credit_committee':
                    executed_actions.append('Credit committee notified')
                elif action == 'require_approval':
                    executed_actions.append('Additional approval required')
                elif action == 'notify_treasury':
                    executed_actions.append('Treasury team notified')
                elif action == 'restrict_lending':
                    executed_actions.append('Lending restrictions applied')
                elif action == 'notify_board':
                    executed_actions.append('Board of directors notified')
                elif action == 'require_capital_plan':
                    executed_actions.append('Capital plan requirement triggered')
                elif action == 'notify_operations':
                    executed_actions.append('Operations team notified')
                elif action == 'optimize_process':
                    executed_actions.append('Process optimization initiated')
                elif action == 'notify_data_team':
                    executed_actions.append('Data team notified')
                elif action == 'suspend_reporting':
                    executed_actions.append('Reporting suspension initiated')
                elif action == 'notify_finance':
                    executed_actions.append('Finance team notified')
                elif action == 'adjust_dividend':
                    executed_actions.append('Dividend adjustment initiated')
                elif action == 'notify_security_team':
                    executed_actions.append('Security team notified')
                elif action == 'enhance_monitoring':
                    executed_actions.append('Enhanced monitoring activated')
                
            except Exception as e:
                logger.error(f"Error executing action {action}: {e}")
                executed_actions.append(f"Action failed: {action}")
        
        return executed_actions
    
    def _generate_alert(self, rule: PolicyRule, execution: RuleExecution) -> Optional[PolicyAlert]:
        """Generate policy alert for triggered rule"""
        try:
            return PolicyAlert(
                alert_id=f"ALERT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                rule_id=rule.rule_id,
                timestamp=datetime.now(),
                severity=rule.severity,
                title=f"{rule.rule_name} - Rule Triggered",
                description=f"Policy rule {rule.rule_name} has been triggered. {rule.description}",
                affected_entities=self._get_affected_entities(rule, execution),
                status='Open',
                assigned_to=self._assign_alert(rule),
                resolution_notes=None,
                resolved_at=None
            )
        except Exception as e:
            logger.error(f"Error generating alert: {e}")
            return None
    
    def _get_affected_entities(self, rule: PolicyRule, execution: RuleExecution) -> List[str]:
        """Get entities affected by rule trigger"""
        entities = []
        
        if 'employer' in rule.rule_name.lower():
            entities.append('Top Employers Portfolio')
        if 'liquidity' in rule.rule_name.lower():
            entities.append('Treasury Operations')
        if 'capital' in rule.rule_name.lower():
            entities.append('Capital Management')
        if 'loan' in rule.rule_name.lower():
            entities.append('Loan Portfolio')
        if 'data' in rule.rule_name.lower():
            entities.append('Data Management')
        if 'dividend' in rule.rule_name.lower():
            entities.append('Dividend Distribution')
        if 'cyber' in rule.rule_name.lower():
            entities.append('IT Infrastructure')
        
        return entities if entities else ['General Operations']
    
    def _assign_alert(self, rule: PolicyRule) -> str:
        """Assign alert to appropriate team"""
        assignment_map = {
            PolicyRuleType.RISK_MONITORING: 'Risk Management Team',
            PolicyRuleType.COMPLIANCE: 'Compliance Office',
            PolicyRuleType.OPERATIONAL: 'Operations Department',
            PolicyRuleType.FINANCIAL: 'Finance Department',
            PolicyRuleType.SECURITY: 'Cybersecurity Team'
        }
        return assignment_map.get(rule.rule_type, 'General Administration')
    
    def _update_rule_statistics(self, triggered_rules: List[PolicyRule]):
        """Update rule trigger statistics"""
        for rule in triggered_rules:
            rule.trigger_count += 1
            rule.last_triggered = datetime.now()
    
    def _generate_execution_summary(self, executions: List[RuleExecution]) -> Dict[str, Any]:
        """Generate execution summary statistics"""
        total_rules = len(executions)
        triggered_rules = len([e for e in executions if e.triggered])
        successful_executions = len([e for e in executions if e.status == 'Completed'])
        
        return {
            'total_rules_executed': total_rules,
            'rules_triggered': triggered_rules,
            'successful_executions': successful_executions,
            'execution_success_rate': (successful_executions / total_rules * 100) if total_rules > 0 else 0,
            'trigger_rate': (triggered_rules / total_rules * 100) if total_rules > 0 else 0,
            'last_execution_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _analyze_rule_effectiveness(self, executions: List[RuleExecution]) -> Dict[str, Any]:
        """Analyze rule effectiveness and performance"""
        try:
            rule_performance = {}
            
            for execution in executions:
                rule_id = execution.rule_id
                if rule_id not in rule_performance:
                    rule_performance[rule_id] = {
                        'total_executions': 0,
                        'triggered_count': 0,
                        'success_count': 0,
                        'average_response_time': 0
                    }
                
                rule_performance[rule_id]['total_executions'] += 1
                if execution.triggered:
                    rule_performance[rule_id]['triggered_count'] += 1
                if execution.status == 'Completed':
                    rule_performance[rule_id]['success_count'] += 1
            
            # Calculate effectiveness metrics
            effectiveness_scores = {}
            for rule_id, perf in rule_performance.items():
                if perf['total_executions'] > 0:
                    trigger_rate = (perf['triggered_count'] / perf['total_executions']) * 100
                    success_rate = (perf['success_count'] / perf['total_executions']) * 100
                    effectiveness_scores[rule_id] = (trigger_rate + success_rate) / 2
            
            return {
                'rule_performance': rule_performance,
                'effectiveness_scores': effectiveness_scores,
                'overall_effectiveness': np.mean(list(effectiveness_scores.values())) if effectiveness_scores else 0,
                'most_effective_rule': max(effectiveness_scores, key=effectiveness_scores.get) if effectiveness_scores else None
            }
            
        except Exception as e:
            logger.error(f"Error analyzing rule effectiveness: {e}")
            return {'overall_effectiveness': 0, 'rule_performance': {}}
    
    def _calculate_risk_exposure(self, triggered_rules: List[PolicyRule]) -> Dict[str, Any]:
        """Calculate overall risk exposure based on triggered rules"""
        try:
            risk_weights = {
                AlertSeverity.CRITICAL: 1.0,
                AlertSeverity.HIGH: 0.7,
                AlertSeverity.MEDIUM: 0.4,
                AlertSeverity.LOW: 0.2,
                AlertSeverity.INFO: 0.1
            }
            
            total_risk_score = 0
            max_possible_score = len(triggered_rules) * 1.0  # Assuming all critical
            
            for rule in triggered_rules:
                total_risk_score += risk_weights.get(rule.severity, 0.1)
            
            risk_exposure = (total_risk_score / max_possible_score * 100) if max_possible_score > 0 else 0
            
            return {
                'total_risk_score': total_risk_score,
                'risk_exposure_percentage': risk_exposure,
                'critical_alerts': len([r for r in triggered_rules if r.severity == AlertSeverity.CRITICAL]),
                'high_alerts': len([r for r in triggered_rules if r.severity == AlertSeverity.HIGH]),
                'risk_level': 'Critical' if risk_exposure >= 80 else 'High' if risk_exposure >= 60 else 'Medium' if risk_exposure >= 40 else 'Low'
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk exposure: {e}")
            return {'total_risk_score': 0, 'risk_exposure_percentage': 0, 'risk_level': 'Low'}
    
    def _assess_compliance_status(self, executions: List[RuleExecution]) -> Dict[str, Any]:
        """Assess overall compliance status"""
        try:
            compliance_rules = [e for e in executions if any(word in e.rule_id for word in ['COMPLIANCE', 'REGULATORY'])]
            triggered_compliance = len([e for e in compliance_rules if e.triggered])
            
            total_compliance = len(compliance_rules)
            compliance_rate = ((total_compliance - triggered_compliance) / total_compliance * 100) if total_compliance > 0 else 100
            
            return {
                'compliance_rate': compliance_rate,
                'total_compliance_rules': total_compliance,
                'compliance_violations': triggered_compliance,
                'compliance_status': 'Compliant' if compliance_rate >= 95 else 'Minor Issues' if compliance_rate >= 85 else 'Non-Compliant'
            }
            
        except Exception as e:
            logger.error(f"Error assessing compliance status: {e}")
            return {'compliance_rate': 0, 'compliance_status': 'Unknown'}
    
    def _generate_policy_recommendations(self, executions: List[RuleExecution]) -> List[Dict[str, Any]]:
        """Generate policy improvement recommendations"""
        recommendations = []
        
        # Analyze frequently triggered rules
        frequent_triggers = []
        for execution in executions:
            if execution.triggered:
                # This would normally analyze historical data
                frequent_triggers.append(execution.rule_id)
        
        if len(frequent_triggers) > 3:
            recommendations.append({
                'type': 'Rule Optimization',
                'priority': 'High',
                'recommendation': 'Review frequently triggered rules for threshold adjustments',
                'rationale': f'{len(frequent_triggers)} rules triggered frequently, indicating potential threshold issues'
            })
        
        # Check rule coverage
        rule_types = set()
        for execution in executions:
            rule = next((r for r in self.policy_rules if r.rule_id == execution.rule_id), None)
            if rule:
                rule_types.add(rule.rule_type)
        
        if len(rule_types) < len(PolicyRuleType):
            recommendations.append({
                'type': 'Rule Coverage',
                'priority': 'Medium',
                'recommendation': 'Expand policy rules to cover all risk categories',
                'rationale': f'Currently covering {len(rule_types)} out of {len(PolicyRuleType)} rule types'
            })
        
        return recommendations
    
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Return fallback analysis when execution fails"""
        return {
            'execution_summary': {
                'total_rules_executed': 0,
                'rules_triggered': 0,
                'successful_executions': 0,
                'execution_success_rate': 0,
                'trigger_rate': 0,
                'last_execution_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'triggered_rules': [],
            'active_alerts': [],
            'rule_effectiveness': {'overall_effectiveness': 0},
            'risk_exposure': {'risk_exposure_percentage': 0, 'risk_level': 'Low'},
            'compliance_status': {'compliance_rate': 0, 'compliance_status': 'Unknown'},
            'recommendations': [],
            'execution_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }