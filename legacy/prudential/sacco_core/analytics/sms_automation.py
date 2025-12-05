# sacco_core/analytics/sms_automation.py
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum
import json
import re

logger = logging.getLogger(__name__)

class SMSStage(Enum):
    """SMS Funnel Stages"""
    REMINDER = "Reminder"
    FOLLOW_UP = "Follow-up"
    URGENT = "Urgent"
    FINAL_NOTICE = "Final Notice"
    LEGAL_WARNING = "Legal Warning"

class MessageTemplate(Enum):
    """SMS Message Templates"""
    SOFT_REMINDER = "Soft Reminder"
    PAYMENT_REMINDER = "Payment Reminder"
    OVERDUE_NOTICE = "Overdue Notice"
    SETTLEMENT_OFFER = "Settlement Offer"
    LEGAL_NOTICE = "Legal Notice"

class DeliveryStatus(Enum):
    """SMS Delivery Status"""
    SENT = "Sent"
    DELIVERED = "Delivered"
    FAILED = "Failed"
    READ = "Read"
    RESPONDED = "Responded"

@dataclass
class SMSCampaign:
    """SMS Campaign Configuration"""
    campaign_id: str
    name: str
    target_segment: str
    message_template: MessageTemplate
    scheduled_time: datetime
    status: str
    target_count: int
    sent_count: int
    response_rate: float

@dataclass
class SMSMessage:
    """Individual SMS Message"""
    message_id: str
    member_id: str
    phone_number: str
    message_content: str
    template_type: MessageTemplate
    stage: SMSStage
    sent_time: datetime
    delivery_status: DeliveryStatus
    response_received: bool
    response_content: Optional[str]
    response_time: Optional[datetime]
    cost: float

@dataclass
class ConversationFunnel:
    """SMS Conversation Funnel Analysis"""
    stage: SMSStage
    messages_sent: int
    messages_delivered: int
    responses_received: int
    response_rate: float
    conversion_rate: float
    average_response_time: float

class SMSAutomationAnalyzer:
    """Collections SMS Automation and Funnel Management"""
    
    def __init__(self):
        self.sms_parameters = {
            'max_messages_per_day': 3,
            'optimal_send_times': ['09:00', '14:00', '18:00'],
            'message_cost': 1.0,  # KES per SMS
            'compliance_check': True,
            'opt_out_keywords': ['STOP', 'UNSUBSCRIBE', 'CANCEL']
        }
        
        self.template_library = self._initialize_templates()
        self.stage_triggers = self._initialize_stage_triggers()
    
    def analyze_sms_automation(self) -> Dict[str, Any]:
        """
        Perform comprehensive SMS automation analysis
        
        Returns:
            Dictionary with SMS automation analysis results
        """
        try:
            # Extract SMS campaign data
            sms_campaigns = self._extract_sms_campaigns()
            sms_messages = self._extract_sms_messages()
            member_responses = self._extract_member_responses()
            delivery_metrics = self._extract_delivery_metrics()
            
            # Analyze conversation funnel
            funnel_analysis = self._analyze_conversation_funnel(sms_messages)
            
            # Campaign performance
            campaign_performance = self._analyze_campaign_performance(sms_campaigns, sms_messages)
            
            # Response optimization
            response_optimization = self._optimize_response_rates(sms_messages, member_responses)
            
            # Compliance monitoring
            compliance_analysis = self._monitor_compliance(sms_messages, member_responses)
            
            # Cost analysis
            cost_analysis = self._analyze_campaign_costs(sms_campaigns, sms_messages)
            
            analysis = {
                'funnel_analysis': funnel_analysis,
                'campaign_performance': campaign_performance,
                'response_optimization': response_optimization,
                'compliance_analysis': compliance_analysis,
                'cost_analysis': cost_analysis,
                'template_effectiveness': self._analyze_template_effectiveness(sms_messages),
                'send_time_optimization': self._optimize_send_times(sms_messages, member_responses),
                'recommendations': self._generate_recommendations(funnel_analysis, campaign_performance),
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in SMS automation analysis: {e}")
            return self._get_fallback_analysis()
    
    def _extract_sms_campaigns(self) -> List[SMSCampaign]:
        """Extract SMS campaign data"""
        try:
            np.random.seed(42)
            n_campaigns = 12
            
            campaigns = []
            for i in range(n_campaigns):
                campaign_date = datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 300))
                
                campaigns.append(SMSCampaign(
                    campaign_id=f'SMS-CAMP-{2023}{i+1:02d}',
                    name=f"Q{(i % 4) + 1} {2023} Collections Campaign",
                    target_segment=np.random.choice(['Delinquent 1-30', 'Delinquent 31-60', 'Delinquent 61-90', 'Legal']),
                    message_template=np.random.choice(list(MessageTemplate)),
                    scheduled_time=campaign_date,
                    status=np.random.choice(['Completed', 'Active', 'Scheduled']),
                    target_count=np.random.randint(100, 500),
                    sent_count=np.random.randint(80, 450),
                    response_rate=np.random.uniform(0.15, 0.45)
                ))
            
            return campaigns
        except Exception as e:
            logger.error(f"Error extracting SMS campaigns: {e}")
            return []
    
    def _extract_sms_messages(self) -> List[SMSMessage]:
        """Extract individual SMS message data"""
        try:
            np.random.seed(42)
            n_messages = 5000
            
            messages = []
            for i in range(n_messages):
                sent_time = datetime(2023, 1, 1) + timedelta(
                    days=np.random.randint(0, 300),
                    hours=np.random.randint(8, 20)
                )
                
                # Simulate delivery timeline
                delivery_delay = timedelta(minutes=np.random.exponential(30))
                response_delay = timedelta(hours=np.random.exponential(24)) if np.random.random() > 0.7 else None
                
                messages.append(SMSMessage(
                    message_id=f'SMS-MSG-{50000 + i}',
                    member_id=f'M{10000 + np.random.randint(1, 5000)}',
                    phone_number=f"07{np.random.randint(10, 99)}{np.random.randint(100000, 999999)}",
                    message_content=self._generate_message_content(),
                    template_type=np.random.choice(list(MessageTemplate)),
                    stage=np.random.choice(list(SMSStage)),
                    sent_time=sent_time,
                    delivery_status=np.random.choice(list(DeliveryStatus), p=[0.02, 0.85, 0.03, 0.05, 0.05]),
                    response_received=np.random.random() > 0.7,
                    response_content="Will pay tomorrow" if np.random.random() > 0.7 else None,
                    response_time=sent_time + response_delay if response_delay else None,
                    cost=1.0  # Base cost per SMS
                ))
            
            return messages
        except Exception as e:
            logger.error(f"Error extracting SMS messages: {e}")
            return []
    
    def _extract_member_responses(self) -> pd.DataFrame:
        """Extract member response patterns"""
        try:
            np.random.seed(42)
            n_responses = 1500
            
            responses = []
            for i in range(n_responses):
                response_time = datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 300))
                
                responses.append({
                    'response_id': f'RES-{60000 + i}',
                    'member_id': f'M{10000 + np.random.randint(1, 5000)}',
                    'message_id': f'SMS-MSG-{50000 + np.random.randint(0, 5000)}',
                    'response_content': np.random.choice([
                        "I will pay tomorrow",
                        "Please call me",
                        "I have paid already",
                        "STOP",
                        "I need more time",
                        "What is my balance?",
                        "I want to restructure"
                    ]),
                    'response_time': response_time,
                    'response_type': np.random.choice(['Promise', 'Inquiry', 'Complaint', 'Opt-out', 'Payment']),
                    'converted_to_payment': np.random.random() > 0.6
                })
            
            return pd.DataFrame(responses)
        except Exception as e:
            logger.error(f"Error extracting member responses: {e}")
            return pd.DataFrame()
    
    def _extract_delivery_metrics(self) -> pd.DataFrame:
        """Extract SMS delivery metrics"""
        try:
            np.random.seed(42)
            n_deliveries = 5000
            
            deliveries = []
            for i in range(n_deliveries):
                deliveries.append({
                    'message_id': f'SMS-MSG-{50000 + i}',
                    'carrier': np.random.choice(['Safaricom', 'Airtel', 'Telkom']),
                    'delivery_time': np.random.exponential(5),  # minutes
                    'delivery_status': np.random.choice(['Delivered', 'Failed', 'Pending']),
                    'cost': 1.0,
                    'api_response': 'Success' if np.random.random() > 0.05 else 'Failed'
                })
            
            return pd.DataFrame(deliveries)
        except Exception as e:
            logger.error(f"Error extracting delivery metrics: {e}")
            return pd.DataFrame()
    
    def _initialize_templates(self) -> Dict[MessageTemplate, str]:
        """Initialize SMS message template library"""
        return {
            MessageTemplate.SOFT_REMINDER: 
                "Hello {member_name}, this is a friendly reminder that your loan payment of KES {amount_due} is due. Thank you for your prompt attention.",
            
            MessageTemplate.PAYMENT_REMINDER:
                "Dear {member_name}, your loan payment of KES {amount_due} is now due. Please make payment to avoid late fees. Need help? Reply HELP.",
            
            MessageTemplate.OVERDUE_NOTICE:
                "URGENT: {member_name}, your loan payment of KES {amount_due} is {days_overdue} days overdue. Immediate payment required to maintain your credit standing.",
            
            MessageTemplate.SETTLEMENT_OFFER:
                "OFFER: {member_name}, we can help! Settle your KES {amount_due} balance with a payment plan. Reply PLAN to discuss options. Limited time offer.",
            
            MessageTemplate.LEGAL_NOTICE:
                "FINAL NOTICE: {member_name}, legal action may be initiated for your KES {amount_due} overdue loan. Contact us immediately at {contact_number} to avoid proceedings."
        }
    
    def _initialize_stage_triggers(self) -> Dict[SMSStage, Dict[str, Any]]:
        """Initialize SMS stage triggers and conditions"""
        return {
            SMSStage.REMINDER: {
                'days_delinquent': (1, 7),
                'max_messages': 2,
                'time_between_messages': timedelta(days=2)
            },
            SMSStage.FOLLOW_UP: {
                'days_delinquent': (8, 30),
                'max_messages': 3,
                'time_between_messages': timedelta(days=3)
            },
            SMSStage.URGENT: {
                'days_delinquent': (31, 60),
                'max_messages': 4,
                'time_between_messages': timedelta(days=4)
            },
            SMSStage.FINAL_NOTICE: {
                'days_delinquent': (61, 90),
                'max_messages': 3,
                'time_between_messages': timedelta(days=5)
            },
            SMSStage.LEGAL_WARNING: {
                'days_delinquent': (91, 999),
                'max_messages': 2,
                'time_between_messages': timedelta(days=7)
            }
        }
    
    def _generate_message_content(self) -> str:
        """Generate sample message content"""
        templates = [
            "Reminder: Your payment of {amount} is due. Please pay to avoid charges.",
            "Urgent: Your account is {days} days overdue. Contact us immediately.",
            "Offer: We can help with your {amount} balance. Reply for options.",
            "Final Notice: Legal action may be taken. Call {phone} now.",
            "Friendly reminder: Your payment is due. Thank you for your cooperation."
        ]
        return np.random.choice(templates)
    
    def _analyze_conversation_funnel(self, sms_messages: List[SMSMessage]) -> Dict[SMSStage, ConversationFunnel]:
        """Analyze SMS conversation funnel by stage"""
        try:
            if not sms_messages:
                return {}
            
            funnel_analysis = {}
            
            for stage in SMSStage:
                stage_messages = [msg for msg in sms_messages if msg.stage == stage]
                
                if not stage_messages:
                    continue
                
                messages_sent = len(stage_messages)
                messages_delivered = len([msg for msg in stage_messages if msg.delivery_status in [DeliveryStatus.DELIVERED, DeliveryStatus.READ, DeliveryStatus.RESPONDED]])
                responses_received = len([msg for msg in stage_messages if msg.response_received])
                
                response_rate = responses_received / messages_delivered if messages_delivered > 0 else 0
                
                # Calculate conversion rate (responses that led to payments)
                converted_responses = len([msg for msg in stage_messages if msg.response_received and np.random.random() > 0.6])  # Simulated
                conversion_rate = converted_responses / responses_received if responses_received > 0 else 0
                
                # Calculate average response time
                response_times = []
                for msg in stage_messages:
                    if msg.response_received and msg.response_time:
                        response_time = (msg.response_time - msg.sent_time).total_seconds() / 3600  # hours
                        response_times.append(response_time)
                
                average_response_time = np.mean(response_times) if response_times else 0
                
                funnel_analysis[stage] = ConversationFunnel(
                    stage=stage,
                    messages_sent=messages_sent,
                    messages_delivered=messages_delivered,
                    responses_received=responses_received,
                    response_rate=response_rate,
                    conversion_rate=conversion_rate,
                    average_response_time=average_response_time
                )
            
            return funnel_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing conversation funnel: {e}")
            return {}
    
    def _analyze_campaign_performance(self, sms_campaigns: List[SMSCampaign], sms_messages: List[SMSMessage]) -> Dict[str, Any]:
        """Analyze SMS campaign performance"""
        try:
            if not sms_campaigns:
                return {}
            
            campaign_performance = {}
            
            for campaign in sms_campaigns:
                campaign_messages = [msg for msg in sms_messages if campaign.campaign_id in msg.message_id]
                
                if not campaign_messages:
                    continue
                
                delivered_count = len([msg for msg in campaign_messages if msg.delivery_status in [DeliveryStatus.DELIVERED, DeliveryStatus.READ, DeliveryStatus.RESPONDED]])
                response_count = len([msg for msg in campaign_messages if msg.response_received])
                conversion_count = len([msg for msg in campaign_messages if msg.response_received and np.random.random() > 0.6])  # Simulated
                
                delivery_rate = delivered_count / len(campaign_messages) if campaign_messages else 0
                response_rate = response_count / delivered_count if delivered_count > 0 else 0
                conversion_rate = conversion_count / response_count if response_count > 0 else 0
                
                total_cost = len(campaign_messages) * self.sms_parameters['message_cost']
                estimated_revenue = conversion_count * 5000  # Simulated average payment
                roi = (estimated_revenue - total_cost) / total_cost if total_cost > 0 else 0
                
                campaign_performance[campaign.campaign_id] = {
                    'campaign_name': campaign.name,
                    'messages_sent': len(campaign_messages),
                    'delivery_rate': delivery_rate,
                    'response_rate': response_rate,
                    'conversion_rate': conversion_rate,
                    'total_cost': total_cost,
                    'estimated_revenue': estimated_revenue,
                    'roi': roi,
                    'status': campaign.status
                }
            
            return campaign_performance
            
        except Exception as e:
            logger.error(f"Error analyzing campaign performance: {e}")
            return {}
    
    def _optimize_response_rates(self, sms_messages: List[SMSMessage], member_responses: pd.DataFrame) -> Dict[str, Any]:
        """Optimize SMS response rates through analysis"""
        try:
            if not sms_messages:
                return {}
            
            # Analyze by template type
            template_performance = {}
            for template in MessageTemplate:
                template_messages = [msg for msg in sms_messages if msg.template_type == template]
                if template_messages:
                    responses = len([msg for msg in template_messages if msg.response_received])
                    response_rate = responses / len(template_messages)
                    template_performance[template.value] = response_rate
            
            # Analyze by send time
            time_performance = {}
            for hour in range(8, 21):  # 8 AM to 8 PM
                hour_messages = [msg for msg in sms_messages if msg.sent_time.hour == hour]
                if hour_messages:
                    responses = len([msg for msg in hour_messages if msg.response_received])
                    response_rate = responses / len(hour_messages)
                    time_performance[f"{hour:02d}:00"] = response_rate
            
            # Analyze by message length
            length_performance = {}
            for msg in sms_messages:
                length = len(msg.message_content)
                length_group = f"{((length-1)//50)*50}+"  # Group by 50-character increments
                if length_group not in length_performance:
                    length_performance[length_group] = {'total': 0, 'responses': 0}
                length_performance[length_group]['total'] += 1
                if msg.response_received:
                    length_performance[length_group]['responses'] += 1
            
            # Calculate response rates by length
            length_rates = {}
            for length_group, data in length_performance.items():
                length_rates[length_group] = data['responses'] / data['total'] if data['total'] > 0 else 0
            
            return {
                'template_performance': template_performance,
                'time_performance': time_performance,
                'length_performance': length_rates,
                'optimal_send_times': sorted(time_performance.items(), key=lambda x: x[1], reverse=True)[:3],
                'best_performing_templates': sorted(template_performance.items(), key=lambda x: x[1], reverse=True)[:3]
            }
            
        except Exception as e:
            logger.error(f"Error optimizing response rates: {e}")
            return {}
    
    def _monitor_compliance(self, sms_messages: List[SMSMessage], member_responses: pd.DataFrame) -> Dict[str, Any]:
        """Monitor SMS compliance and opt-out management"""
        try:
            if not sms_messages:
                return {}
            
            # Count opt-out requests
            opt_out_responses = member_responses[
                member_responses['response_content'].str.contains('STOP|UNSUBSCRIBE|CANCEL', na=False, case=False)
            ] if not member_responses.empty else []
            
            opt_out_count = len(opt_out_responses)
            
            # Check message compliance
            compliant_messages = 0
            for msg in sms_messages:
                if self._check_message_compliance(msg.message_content):
                    compliant_messages += 1
            
            compliance_rate = compliant_messages / len(sms_messages) if sms_messages else 1.0
            
            # Delivery failure analysis
            failed_messages = len([msg for msg in sms_messages if msg.delivery_status == DeliveryStatus.FAILED])
            failure_rate = failed_messages / len(sms_messages) if sms_messages else 0
            
            return {
                'opt_out_count': opt_out_count,
                'opt_out_rate': opt_out_count / len(member_responses) if len(member_responses) > 0 else 0,
                'compliance_rate': compliance_rate,
                'failed_messages': failed_messages,
                'failure_rate': failure_rate,
                'compliance_issues': self._identify_compliance_issues(sms_messages),
                'opt_out_trend': self._calculate_opt_out_trend(member_responses)
            }
            
        except Exception as e:
            logger.error(f"Error monitoring compliance: {e}")
            return {
                'opt_out_count': 0,
                'opt_out_rate': 0,
                'compliance_rate': 1.0,
                'failed_messages': 0,
                'failure_rate': 0,
                'compliance_issues': [],
                'opt_out_trend': {}
            }
    
    def _analyze_campaign_costs(self, sms_campaigns: List[SMSCampaign], sms_messages: List[SMSMessage]) -> Dict[str, Any]:
        """Analyze SMS campaign costs and ROI"""
        try:
            total_messages = len(sms_messages)
            total_cost = total_messages * self.sms_parameters['message_cost']
            
            # Calculate responses and conversions
            total_responses = len([msg for msg in sms_messages if msg.response_received])
            total_conversions = len([msg for msg in sms_messages if msg.response_received and np.random.random() > 0.6])  # Simulated
            
            # Calculate cost metrics
            cost_per_message = self.sms_parameters['message_cost']
            cost_per_response = total_cost / total_responses if total_responses > 0 else 0
            cost_per_conversion = total_cost / total_conversions if total_conversions > 0 else 0
            
            # Estimated revenue (simulated)
            estimated_revenue = total_conversions * 5000  # Average payment amount
            total_roi = (estimated_revenue - total_cost) / total_cost if total_cost > 0 else 0
            
            return {
                'total_messages': total_messages,
                'total_cost': total_cost,
                'cost_per_message': cost_per_message,
                'cost_per_response': cost_per_response,
                'cost_per_conversion': cost_per_conversion,
                'estimated_revenue': estimated_revenue,
                'total_roi': total_roi,
                'break_even_point': total_cost / 5000 if 5000 > 0 else 0,  # Messages needed to break even
                'cost_trend': self._calculate_cost_trend(sms_messages)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing campaign costs: {e}")
            return {
                'total_messages': 0,
                'total_cost': 0,
                'cost_per_message': 0,
                'cost_per_response': 0,
                'cost_per_conversion': 0,
                'estimated_revenue': 0,
                'total_roi': 0,
                'break_even_point': 0,
                'cost_trend': {}
            }
    
    def _analyze_template_effectiveness(self, sms_messages: List[SMSMessage]) -> Dict[str, Any]:
        """Analyze template effectiveness across different segments"""
        # Simulated template effectiveness analysis
        return {
            'Soft Reminder': {'response_rate': 0.25, 'conversion_rate': 0.15, 'avg_response_time': 4.5},
            'Payment Reminder': {'response_rate': 0.35, 'conversion_rate': 0.22, 'avg_response_time': 3.2},
            'Overdue Notice': {'response_rate': 0.45, 'conversion_rate': 0.28, 'avg_response_time': 2.1},
            'Settlement Offer': {'response_rate': 0.52, 'conversion_rate': 0.35, 'avg_response_time': 1.8},
            'Legal Notice': {'response_rate': 0.38, 'conversion_rate': 0.18, 'avg_response_time': 6.2}
        }
    
    def _optimize_send_times(self, sms_messages: List[SMSMessage], member_responses: pd.DataFrame) -> Dict[str, Any]:
        """Optimize SMS send times based on historical performance"""
        # Simulated send time optimization
        return {
            'best_times': ['09:00', '14:00', '18:00'],
            'worst_times': ['08:00', '13:00', '20:00'],
            'time_performance': {
                '08:00': 0.18, '09:00': 0.32, '10:00': 0.28, '11:00': 0.25,
                '12:00': 0.22, '13:00': 0.19, '14:00': 0.35, '15:00': 0.30,
                '16:00': 0.27, '17:00': 0.24, '18:00': 0.33, '19:00': 0.21, '20:00': 0.16
            }
        }
    
    def _generate_recommendations(self, funnel_analysis: Dict[SMSStage, ConversationFunnel], 
                                campaign_performance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Funnel optimization recommendations
        for stage, funnel in funnel_analysis.items():
            if funnel.response_rate < 0.2:
                recommendations.append({
                    'type': 'Funnel Optimization',
                    'priority': 'High',
                    'description': f'Low response rate ({funnel.response_rate:.1%}) in {stage.value} stage',
                    'action': 'Test new message templates and send times',
                    'expected_impact': '20-30% increase in response rate'
                })
        
        # Cost optimization recommendations
        high_cost_campaigns = [camp for camp, perf in campaign_performance.items() if perf.get('cost_per_response', 0) > 50]
        if high_cost_campaigns:
            recommendations.append({
                'type': 'Cost Optimization',
                'priority': 'Medium',
                'description': f'High cost per response in {len(high_cost_campaigns)} campaigns',
                'action': 'Optimize targeting and message frequency',
                'expected_impact': '15-25% reduction in cost per response'
            })
        
        return recommendations
    
    # Helper methods
    def _check_message_compliance(self, message_content: str) -> bool:
        """Check if message complies with regulations"""
        # Basic compliance checks
        required_elements = ['STOP', 'HELP']  # Opt-out and help instructions
        has_opt_out = any(keyword in message_content.upper() for keyword in ['STOP', 'UNSUBSCRIBE'])
        has_help = 'HELP' in message_content.upper() or 'CALL' in message_content
        
        return has_opt_out and has_help
    
    def _identify_compliance_issues(self, sms_messages: List[SMSMessage]) -> List[str]:
        """Identify compliance issues in SMS messages"""
        issues = []
        
        for msg in sms_messages[:10]:  # Check sample of messages
            if not self._check_message_compliance(msg.message_content):
                issues.append(f"Message {msg.message_id} missing compliance elements")
        
        return issues[:5]  # Return top 5 issues
    
    def _calculate_opt_out_trend(self, member_responses: pd.DataFrame) -> Dict[str, int]:
        """Calculate opt-out trend over time"""
        # Simulated trend data
        return {
            'Jan': 5, 'Feb': 3, 'Mar': 7, 'Apr': 4,
            'May': 6, 'Jun': 8, 'Jul': 5, 'Aug': 4
        }
    
    def _calculate_cost_trend(self, sms_messages: List[SMSMessage]) -> Dict[str, float]:
        """Calculate cost trend over time"""
        # Simulated trend data
        return {
            'Jan': 1250, 'Feb': 1380, 'Mar': 1520, 'Apr': 1450,
            'May': 1680, 'Jun': 1570, 'Jul': 1720, 'Aug': 1650
        }
    
    # Fallback methods
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Return fallback analysis when data is unavailable"""
        return {
            'funnel_analysis': {},
            'campaign_performance': {},
            'response_optimization': {},
            'compliance_analysis': {
                'opt_out_count': 0,
                'opt_out_rate': 0,
                'compliance_rate': 1.0,
                'failed_messages': 0,
                'failure_rate': 0,
                'compliance_issues': [],
                'opt_out_trend': {}
            },
            'cost_analysis': {
                'total_messages': 0,
                'total_cost': 0,
                'cost_per_message': 0,
                'cost_per_response': 0,
                'cost_per_conversion': 0,
                'estimated_revenue': 0,
                'total_roi': 0,
                'break_even_point': 0,
                'cost_trend': {}
            },
            'template_effectiveness': {},
            'send_time_optimization': {},
            'recommendations': [],
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }