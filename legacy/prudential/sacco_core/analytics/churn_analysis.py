# sacco_core/analytics/churn_analysis.py
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum
import warnings

# Import scikit-learn with fallback
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("scikit-learn not available. Using fallback implementations.")

logger = logging.getLogger(__name__)

class ChurnRiskLevel(Enum):
    """Churn Risk Levels"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    MINIMAL = "Minimal"

class InterventionType(Enum):
    """Retention Intervention Types"""
    PERSONAL_CALL = "Personal Call"
    OFFER_UPGRADE = "Offer Upgrade"
    LOYALTY_BONUS = "Loyalty Bonus"
    FEE_WAIVER = "Fee Waiver"
    PRODUCT_RECOMMENDATION = "Product Recommendation"
    SERVICE_REVIEW = "Service Review"

@dataclass
class ChurnPrediction:
    """Churn Prediction Result"""
    member_id: str
    churn_probability: float
    risk_level: ChurnRiskLevel
    predicted_churn_date: datetime
    key_drivers: List[str]
    confidence_score: float

@dataclass
class RetentionIntervention:
    """Retention Intervention Plan"""
    member_id: str
    intervention_type: InterventionType
    priority: str
    expected_success_rate: float
    estimated_roi: float
    recommended_message: str
    optimal_timing: datetime

class ChurnAnalyzer:
    """Advanced Churn Prediction and Retention Analytics"""
    
    def __init__(self):
        self.model_parameters = {
            'churn_threshold': 0.65,
            'critical_threshold': 0.85,
            'high_threshold': 0.75,
            'medium_threshold': 0.60,
            'minimal_threshold': 0.30,
            'prediction_horizon_days': 90
        }
        
        # Initialize ML model (in production, this would be pre-trained)
        self.model = None
        self.feature_importance = {}
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        
    def analyze_churn_risk(self) -> Dict[str, Any]:
        """
        Perform comprehensive churn risk analysis
        
        Returns:
            Dictionary with churn analysis results
        """
        try:
            # Extract member data for churn analysis
            member_data = self._extract_member_churn_data()
            behavioral_data = self._extract_behavioral_data()
            transaction_data = self._extract_transaction_patterns()
            service_data = self._extract_service_interactions()
            
            # Prepare features for ML model
            features, labels = self._prepare_training_data(member_data, behavioral_data, transaction_data, service_data)
            
            # Train/load churn prediction model
            predictions = self._predict_churn_risk(features, member_data)
            
            # Generate intervention strategies
            interventions = self._generate_intervention_strategies(predictions, member_data)
            
            # Campaign performance analysis
            campaign_analysis = self._analyze_campaign_performance()
            
            analysis = {
                'churn_predictions': predictions,
                'intervention_strategies': interventions,
                'campaign_analysis': campaign_analysis,
                'risk_distribution': self._calculate_risk_distribution(predictions),
                'early_warning_indicators': self._identify_early_warnings(member_data, behavioral_data),
                'churn_drivers': self._analyze_churn_drivers(features, predictions),
                'retention_roi': self._calculate_retention_roi(interventions),
                'model_performance': self._evaluate_model_performance(features, labels),
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in churn risk analysis: {e}")
            return self._get_fallback_analysis()
    
    def _extract_member_churn_data(self) -> pd.DataFrame:
        """Extract member data for churn prediction"""
        try:
            np.random.seed(42)
            n_members = 5000
            
            members = []
            for i in range(n_members):
                join_date = datetime(2018, 1, 1) + timedelta(days=np.random.randint(0, 2190))
                is_churned = np.random.choice([0, 1], p=[0.85, 0.15])  # 15% churn rate
                
                members.append({
                    'member_id': f'M{10000 + i}',
                    'join_date': join_date,
                    'age': np.random.randint(25, 65),
                    'gender': np.random.choice(['Male', 'Female'], p=[0.6, 0.4]),
                    'employment_status': np.random.choice(['Employed', 'Self-Employed', 'Business Owner'], p=[0.7, 0.2, 0.1]),
                    'monthly_income': np.random.lognormal(11, 0.3),
                    'education_level': np.random.choice(['Primary', 'Secondary', 'College', 'University'], p=[0.2, 0.4, 0.3, 0.1]),
                    'branch': np.random.choice(['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret']),
                    'years_membership': (datetime.now() - join_date).days / 365.25,
                    'product_count': np.random.poisson(2.5),
                    'total_balance': np.random.lognormal(10, 1.0),
                    'loan_balance': np.random.lognormal(9, 1.2),
                    'savings_balance': np.random.lognormal(9.5, 0.8),
                    'is_churned': is_churned,
                    'churn_date': datetime.now() - timedelta(days=np.random.randint(1, 180)) if is_churned else None
                })
            
            return pd.DataFrame(members)
        except Exception as e:
            logger.error(f"Error extracting member churn data: {e}")
            return pd.DataFrame()
    
    def _extract_behavioral_data(self) -> pd.DataFrame:
        """Extract member behavioral data"""
        try:
            np.random.seed(42)
            n_behaviors = 75000
            
            behaviors = []
            for i in range(n_behaviors):
                behavior_date = datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 365))
                
                behaviors.append({
                    'member_id': f'M{10000 + np.random.randint(0, 5000)}',
                    'behavior_date': behavior_date,
                    'activity_type': np.random.choice([
                        'Login', 'Transaction', 'Inquiry', 'Service Request', 
                        'Complaint', 'App Usage', 'Branch Visit'
                    ]),
                    'channel': np.random.choice(['Mobile', 'Online', 'Branch', 'ATM', 'Phone']),
                    'session_duration': np.random.exponential(300),  # seconds
                    'satisfaction_score': np.random.randint(1, 6),
                    'response_time': np.random.exponential(120)  # seconds
                })
            
            return pd.DataFrame(behaviors)
        except Exception as e:
            logger.error(f"Error extracting behavioral data: {e}")
            return pd.DataFrame()
    
    def _extract_transaction_patterns(self) -> pd.DataFrame:
        """Extract transaction patterns for churn prediction"""
        try:
            np.random.seed(42)
            n_transactions = 100000
            
            transactions = []
            for i in range(n_transactions):
                transaction_date = datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 365))
                
                transactions.append({
                    'member_id': f'M{10000 + np.random.randint(0, 5000)}',
                    'transaction_date': transaction_date,
                    'transaction_type': np.random.choice(['Deposit', 'Withdrawal', 'Transfer', 'Payment']),
                    'amount': np.random.lognormal(7, 1.2),
                    'channel': np.random.choice(['Branch', 'Mobile', 'ATM', 'Online']),
                    'is_foreign': np.random.choice([0, 1], p=[0.95, 0.05]),
                    'balance_after': np.random.lognormal(10, 1.0)
                })
            
            return pd.DataFrame(transactions)
        except Exception as e:
            logger.error(f"Error extracting transaction patterns: {e}")
            return pd.DataFrame()
    
    def _extract_service_interactions(self) -> pd.DataFrame:
        """Extract service interaction data"""
        try:
            np.random.seed(42)
            n_interactions = 30000
            
            interactions = []
            for i in range(n_interactions):
                interaction_date = datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 365))
                
                interactions.append({
                    'member_id': f'M{10000 + np.random.randint(0, 5000)}',
                    'interaction_date': interaction_date,
                    'interaction_type': np.random.choice([
                        'Complaint', 'Inquiry', 'Service Request', 'Feedback',
                        'Technical Support', 'Account Management'
                    ]),
                    'channel': np.random.choice(['Phone', 'Email', 'Chat', 'Branch']),
                    'resolution_time': np.random.exponential(240),  # minutes
                    'satisfaction_rating': np.random.randint(1, 6),
                    'escalation_level': np.random.randint(1, 4),
                    'first_contact_resolution': np.random.choice([0, 1], p=[0.3, 0.7])
                })
            
            return pd.DataFrame(interactions)
        except Exception as e:
            logger.error(f"Error extracting service interactions: {e}")
            return pd.DataFrame()
    
    def _prepare_training_data(self, member_data: pd.DataFrame, behavioral_data: pd.DataFrame, 
                             transaction_data: pd.DataFrame, service_data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features and labels for ML model"""
        try:
            if member_data.empty:
                return pd.DataFrame(), pd.Series()
            
            # Calculate behavioral features
            behavioral_features = self._calculate_behavioral_features(behavioral_data, member_data)
            transaction_features = self._calculate_transaction_features(transaction_data, member_data)
            service_features = self._calculate_service_features(service_data, member_data)
            
            # Merge all features
            features = member_data[['member_id']].copy()
            features = features.merge(behavioral_features, on='member_id', how='left')
            features = features.merge(transaction_features, on='member_id', how='left')
            features = features.merge(service_features, on='member_id', how='left')
            
            # Select features for model
            feature_columns = [
                'recency_days', 'frequency_score', 'engagement_score',
                'transaction_velocity', 'balance_trend', 'complaint_ratio',
                'satisfaction_trend', 'product_diversity', 'channel_diversity',
                'service_response_time', 'age', 'years_membership', 'monthly_income'
            ]
            
            # Fill missing values
            features[feature_columns] = features[feature_columns].fillna(features[feature_columns].mean())
            
            # Get labels
            labels = member_data.set_index('member_id')['is_churned']
            
            return features.set_index('member_id')[feature_columns], labels
            
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            return pd.DataFrame(), pd.Series()
    
    def _calculate_behavioral_features(self, behavioral_data: pd.DataFrame, member_data: pd.DataFrame) -> pd.DataFrame:
        """Calculate behavioral features from activity data"""
        try:
            if behavioral_data.empty:
                return pd.DataFrame()
            
            # Recency: Days since last activity
            last_activity = behavioral_data.groupby('member_id')['behavior_date'].max()
            recency_days = (datetime.now() - last_activity).dt.days
            
            # Frequency: Activity count in last 90 days
            recent_cutoff = datetime.now() - timedelta(days=90)
            recent_activities = behavioral_data[behavioral_data['behavior_date'] >= recent_cutoff]
            frequency = recent_activities.groupby('member_id').size()
            
            # Engagement score based on activity diversity and frequency
            activity_diversity = behavioral_data.groupby('member_id')['activity_type'].nunique()
            channel_diversity = behavioral_data.groupby('member_id')['channel'].nunique()
            
            engagement_score = (
                frequency / frequency.max() * 0.4 +
                activity_diversity / activity_diversity.max() * 0.3 +
                channel_diversity / channel_diversity.max() * 0.3
            )
            
            behavioral_features = pd.DataFrame({
                'recency_days': recency_days,
                'frequency_score': frequency / frequency.max() if frequency.max() > 0 else 0,
                'engagement_score': engagement_score,
                'channel_diversity': channel_diversity
            }).fillna(0)
            
            return behavioral_features.reset_index()
        except Exception as e:
            logger.error(f"Error calculating behavioral features: {e}")
            return pd.DataFrame()
    
    def _calculate_transaction_features(self, transaction_data: pd.DataFrame, member_data: pd.DataFrame) -> pd.DataFrame:
        """Calculate transaction-based features"""
        try:
            if transaction_data.empty:
                return pd.DataFrame()
            
            # Transaction velocity (transactions per month)
            transaction_counts = transaction_data.groupby('member_id').size()
            membership_days = member_data.set_index('member_id')['years_membership'] * 365.25
            transaction_velocity = transaction_counts / (membership_days / 30)  # per month
            
            # Balance trend (recent vs historical)
            recent_cutoff = datetime.now() - timedelta(days=60)
            recent_transactions = transaction_data[transaction_data['transaction_date'] >= recent_cutoff]
            historical_avg = transaction_data.groupby('member_id')['amount'].mean()
            recent_avg = recent_transactions.groupby('member_id')['amount'].mean()
            
            balance_trend = (recent_avg / historical_avg).fillna(1)
            
            # Transaction type diversity
            transaction_diversity = transaction_data.groupby('member_id')['transaction_type'].nunique()
            
            transaction_features = pd.DataFrame({
                'transaction_velocity': transaction_velocity,
                'balance_trend': balance_trend,
                'transaction_diversity': transaction_diversity
            }).fillna(0)
            
            return transaction_features.reset_index()
        except Exception as e:
            logger.error(f"Error calculating transaction features: {e}")
            return pd.DataFrame()
    
    def _calculate_service_features(self, service_data: pd.DataFrame, member_data: pd.DataFrame) -> pd.DataFrame:
        """Calculate service interaction features"""
        try:
            if service_data.empty:
                return pd.DataFrame()
            
            # Complaint ratio
            total_interactions = service_data.groupby('member_id').size()
            complaint_interactions = service_data[service_data['interaction_type'] == 'Complaint'].groupby('member_id').size()
            complaint_ratio = (complaint_interactions / total_interactions).fillna(0)
            
            # Satisfaction trend
            satisfaction_trend = service_data.groupby('member_id')['satisfaction_rating'].mean()
            
            # Service response time
            avg_response_time = service_data.groupby('member_id')['resolution_time'].mean()
            
            # First contact resolution rate
            fcr_data = service_data.groupby('member_id')['first_contact_resolution'].mean()
            
            service_features = pd.DataFrame({
                'complaint_ratio': complaint_ratio,
                'satisfaction_trend': satisfaction_trend,
                'service_response_time': avg_response_time,
                'first_contact_resolution': fcr_data
            }).fillna(0)
            
            return service_features.reset_index()
        except Exception as e:
            logger.error(f"Error calculating service features: {e}")
            return pd.DataFrame()
    
    def _predict_churn_risk(self, features: pd.DataFrame, member_data: pd.DataFrame) -> List[ChurnPrediction]:
        """Predict churn risk using ML model"""
        try:
            if features.empty:
                return []
            
            # For demonstration, using simulated predictions
            # In production, this would use the trained ML model
            predictions = []
            
            for member_id, row in features.iterrows():
                # Simulated churn probability based on features
                base_risk = 0.1
                
                # Risk factors
                if row.get('recency_days', 0) > 60:
                    base_risk += 0.3
                if row.get('engagement_score', 0) < 0.3:
                    base_risk += 0.2
                if row.get('complaint_ratio', 0) > 0.5:
                    base_risk += 0.15
                if row.get('satisfaction_trend', 3) < 3:
                    base_risk += 0.1
                if row.get('transaction_velocity', 0) < 0.5:
                    base_risk += 0.1
                
                churn_probability = min(0.95, base_risk)
                
                # Determine risk level
                if churn_probability >= self.model_parameters['critical_threshold']:
                    risk_level = ChurnRiskLevel.CRITICAL
                elif churn_probability >= self.model_parameters['high_threshold']:
                    risk_level = ChurnRiskLevel.HIGH
                elif churn_probability >= self.model_parameters['medium_threshold']:
                    risk_level = ChurnRiskLevel.MEDIUM
                elif churn_probability >= self.model_parameters['minimal_threshold']:
                    risk_level = ChurnRiskLevel.LOW
                else:
                    risk_level = ChurnRiskLevel.MINIMAL
                
                # Predict churn date
                days_to_churn = int((1 - churn_probability) * 180)  # Simplified calculation
                predicted_churn_date = datetime.now() + timedelta(days=days_to_churn)
                
                # Identify key drivers
                key_drivers = self._identify_key_drivers(row, churn_probability)
                
                predictions.append(ChurnPrediction(
                    member_id=member_id,
                    churn_probability=churn_probability,
                    risk_level=risk_level,
                    predicted_churn_date=predicted_churn_date,
                    key_drivers=key_drivers,
                    confidence_score=0.85  # Simulated confidence
                ))
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting churn risk: {e}")
            return []
    
    def _identify_key_drivers(self, features: pd.Series, churn_probability: float) -> List[str]:
        """Identify key drivers for churn prediction"""
        drivers = []
        
        if features.get('recency_days', 0) > 60:
            drivers.append("Low recent activity")
        if features.get('engagement_score', 0) < 0.3:
            drivers.append("Poor engagement")
        if features.get('complaint_ratio', 0) > 0.5:
            drivers.append("High complaint frequency")
        if features.get('satisfaction_trend', 3) < 3:
            drivers.append("Low satisfaction")
        if features.get('transaction_velocity', 0) < 0.5:
            drivers.append("Declining transaction volume")
        if features.get('service_response_time', 0) > 300:
            drivers.append("Slow service response")
        
        return drivers[:3]  # Return top 3 drivers
    
    def _generate_intervention_strategies(self, predictions: List[ChurnPrediction], member_data: pd.DataFrame) -> List[RetentionIntervention]:
        """Generate personalized intervention strategies"""
        try:
            interventions = []
            
            for prediction in predictions:
                if prediction.risk_level in [ChurnRiskLevel.CRITICAL, ChurnRiskLevel.HIGH]:
                    # High-risk interventions
                    intervention_type = self._select_intervention_type(prediction, member_data)
                    success_rate = self._calculate_success_rate(prediction, intervention_type)
                    estimated_roi = self._calculate_intervention_roi(prediction, intervention_type, success_rate)
                    
                    interventions.append(RetentionIntervention(
                        member_id=prediction.member_id,
                        intervention_type=intervention_type,
                        priority="High" if prediction.risk_level == ChurnRiskLevel.CRITICAL else "Medium",
                        expected_success_rate=success_rate,
                        estimated_roi=estimated_roi,
                        recommended_message=self._generate_intervention_message(prediction, intervention_type),
                        optimal_timing=datetime.now() + timedelta(days=1)  # Immediate action for high risk
                    ))
            
            return interventions
            
        except Exception as e:
            logger.error(f"Error generating intervention strategies: {e}")
            return []
    
    def _select_intervention_type(self, prediction: ChurnPrediction, member_data: pd.DataFrame) -> InterventionType:
        """Select optimal intervention type based on member profile"""
        # Simplified logic - in production, this would use more sophisticated rules
        drivers = prediction.key_drivers
        
        if "Low satisfaction" in drivers or "High complaint frequency" in drivers:
            return InterventionType.SERVICE_REVIEW
        elif "Poor engagement" in drivers or "Low recent activity" in drivers:
            return InterventionType.PERSONAL_CALL
        elif "Declining transaction volume" in drivers:
            return InterventionType.OFFER_UPGRADE
        else:
            return InterventionType.LOYALTY_BONUS
    
    def _calculate_success_rate(self, prediction: ChurnPrediction, intervention_type: InterventionType) -> float:
        """Calculate expected success rate for intervention"""
        base_success = {
            InterventionType.PERSONAL_CALL: 0.6,
            InterventionType.OFFER_UPGRADE: 0.5,
            InterventionType.LOYALTY_BONUS: 0.4,
            InterventionType.FEE_WAIVER: 0.3,
            InterventionType.PRODUCT_RECOMMENDATION: 0.35,
            InterventionType.SERVICE_REVIEW: 0.55
        }
        
        # Adjust based on risk level
        risk_adjustment = {
            ChurnRiskLevel.CRITICAL: 0.8,
            ChurnRiskLevel.HIGH: 0.9,
            ChurnRiskLevel.MEDIUM: 1.0,
            ChurnRiskLevel.LOW: 1.1,
            ChurnRiskLevel.MINIMAL: 1.2
        }
        
        return base_success[intervention_type] * risk_adjustment[prediction.risk_level]
    
    def _calculate_intervention_roi(self, prediction: ChurnPrediction, intervention_type: InterventionType, success_rate: float) -> float:
        """Calculate estimated ROI for intervention"""
        intervention_costs = {
            InterventionType.PERSONAL_CALL: 50,
            InterventionType.OFFER_UPGRADE: 100,
            InterventionType.LOYALTY_BONUS: 75,
            InterventionType.FEE_WAIVER: 25,
            InterventionType.PRODUCT_RECOMMENDATION: 10,
            InterventionType.SERVICE_REVIEW: 30
        }
        
        # Simplified value calculation
        member_value = 1000  # Base member value - in production, this would come from LTV model
        cost = intervention_costs[intervention_type]
        expected_value = member_value * success_rate
        
        return (expected_value - cost) / cost if cost > 0 else float('inf')
    
    def _generate_intervention_message(self, prediction: ChurnPrediction, intervention_type: InterventionType) -> str:
        """Generate personalized intervention message"""
        messages = {
            InterventionType.PERSONAL_CALL: f"Personal call to discuss {prediction.member_id}'s needs and address concerns",
            InterventionType.OFFER_UPGRADE: f"Special offer upgrade for {prediction.member_id} to enhance value",
            InterventionType.LOYALTY_BONUS: f"Loyalty bonus award for {prediction.member_id}'s continued membership",
            InterventionType.FEE_WAIVER: f"Fee waiver offer for {prediction.member_id} to improve satisfaction",
            InterventionType.PRODUCT_RECOMMENDATION: f"Personalized product recommendation for {prediction.member_id}",
            InterventionType.SERVICE_REVIEW: f"Service review call to address {prediction.member_id}'s experience"
        }
        
        return messages[intervention_type]
    
    def _analyze_campaign_performance(self) -> Dict[str, Any]:
        """Analyze retention campaign performance"""
        # Simulated campaign performance data
        return {
            'active_campaigns': [
                {
                    'campaign_id': 'RET-2024-Q1',
                    'name': 'Q1 High-Risk Retention',
                    'start_date': '2024-01-01',
                    'target_members': 250,
                    'engaged_members': 189,
                    'successful_retentions': 142,
                    'success_rate': 0.75,
                    'total_cost': 12500,
                    'estimated_value_saved': 425000,
                    'roi': 33.0
                }
            ],
            'historical_performance': {
                'Q4-2023': {'success_rate': 0.72, 'roi': 28.5},
                'Q3-2023': {'success_rate': 0.68, 'roi': 25.2},
                'Q2-2023': {'success_rate': 0.65, 'roi': 22.8},
                'Q1-2023': {'success_rate': 0.61, 'roi': 20.1}
            },
            'best_performing_interventions': [
                {'type': 'Personal Call', 'success_rate': 0.78, 'cost_per_member': 45},
                {'type': 'Service Review', 'success_rate': 0.72, 'cost_per_member': 30},
                {'type': 'Loyalty Bonus', 'success_rate': 0.65, 'cost_per_member': 75}
            ]
        }
    
    def _calculate_risk_distribution(self, predictions: List[ChurnPrediction]) -> Dict[str, int]:
        """Calculate churn risk distribution"""
        distribution = {level.value: 0 for level in ChurnRiskLevel}
        
        for prediction in predictions:
            distribution[prediction.risk_level.value] += 1
        
        return distribution
    
    def _identify_early_warnings(self, member_data: pd.DataFrame, behavioral_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify early warning indicators"""
        warnings = []
        
        # Simulated early warnings
        warnings.append({
            'indicator': 'Activity Drop',
            'description': '20% drop in monthly activity among medium-risk members',
            'severity': 'Medium',
            'affected_members': 45,
            'trend': 'Worsening'
        })
        
        warnings.append({
            'indicator': 'Complaint Spike',
            'description': '35% increase in service complaints in last 30 days',
            'severity': 'High',
            'affected_members': 28,
            'trend': 'Emerging'
        })
        
        warnings.append({
            'indicator': 'Balance Decline',
            'description': '15% of high-value members showing balance declines',
            'severity': 'Medium',
            'affected_members': 32,
            'trend': 'Stable'
        })
        
        return warnings
    
    def _analyze_churn_drivers(self, features: pd.DataFrame, predictions: List[ChurnPrediction]) -> Dict[str, float]:
        """Analyze primary churn drivers"""
        # Simplified driver analysis
        return {
            'Low Engagement': 0.35,
            'Poor Service Experience': 0.25,
            'Competitive Offers': 0.15,
            'Financial Stress': 0.12,
            'Life Events': 0.08,
            'Other': 0.05
        }
    
    def _calculate_retention_roi(self, interventions: List[RetentionIntervention]) -> Dict[str, float]:
        """Calculate overall retention ROI"""
        total_cost = sum(50 for _ in interventions)  # Simplified cost calculation
        total_value = sum(intervention.estimated_roi * 50 for intervention in interventions)  # Simplified value
        
        return {
            'total_estimated_savings': total_value,
            'total_intervention_cost': total_cost,
            'overall_roi': (total_value - total_cost) / total_cost if total_cost > 0 else 0,
            'members_at_risk': len(interventions),
            'potential_savings_per_member': total_value / len(interventions) if interventions else 0
        }
    
    def _evaluate_model_performance(self, features: pd.DataFrame, labels: pd.Series) -> Dict[str, Any]:
        """Evaluate ML model performance"""
        # Simulated model performance
        return {
            'accuracy': 0.87,
            'precision': 0.82,
            'recall': 0.79,
            'f1_score': 0.80,
            'auc_roc': 0.89,
            'feature_importance': {
                'recency_days': 0.25,
                'engagement_score': 0.20,
                'complaint_ratio': 0.15,
                'satisfaction_trend': 0.12,
                'transaction_velocity': 0.10,
                'service_response_time': 0.08,
                'other': 0.10
            },
            'model_type': 'Gradient Boosting',
            'training_date': '2024-01-15',
            'data_freshness': '7 days'
        }
    
    # Fallback methods
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Return fallback analysis when data is unavailable"""
        return {
            'churn_predictions': [],
            'intervention_strategies': [],
            'campaign_analysis': {
                'active_campaigns': [],
                'historical_performance': {},
                'best_performing_interventions': []
            },
            'risk_distribution': {},
            'early_warning_indicators': [],
            'churn_drivers': {},
            'retention_roi': {
                'total_estimated_savings': 0,
                'total_intervention_cost': 0,
                'overall_roi': 0,
                'members_at_risk': 0,
                'potential_savings_per_member': 0
            },
            'model_performance': {
                'accuracy': 0,
                'precision': 0,
                'recall': 0,
                'f1_score': 0,
                'auc_roc': 0,
                'feature_importance': {},
                'model_type': 'Unknown',
                'training_date': 'Unknown',
                'data_freshness': 'Unknown'
            },
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }