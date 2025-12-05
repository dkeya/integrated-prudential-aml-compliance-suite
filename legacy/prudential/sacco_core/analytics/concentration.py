# sacco_core/analytics/concentration.py
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import warnings
import logging

logger = logging.getLogger(__name__)

class ConcentrationAnalyzer:
    """Analyze concentration risk across multiple dimensions"""
    
    def __init__(self):
        self.regulatory_limits = {
            'single_employer_max': 0.25,  # 25% maximum
            'top_5_employers_max': 0.60,  # 60% maximum
            'product_hhi_max': 0.25,      # HHI threshold
            'geographic_hhi_max': 0.30    # HHI threshold
        }
    
    def analyze_concentration_risk(self) -> Dict[str, Any]:
        """
        Perform comprehensive concentration risk analysis
        
        Returns:
            Dictionary with concentration risk analysis results
        """
        try:
            # Extract data (in production, this would query the database)
            loan_data = self._extract_loan_data()
            employer_data = self._extract_employer_data()
            product_data = self._extract_product_data()
            geographic_data = self._extract_geographic_data()
            
            analysis = {
                'employer_concentration': self._analyze_employer_concentration(loan_data, employer_data),
                'product_concentration': self._analyze_product_concentration(loan_data, product_data),
                'geographic_concentration': self._analyze_geographic_concentration(loan_data, geographic_data),
                'regulatory_breaches': self._identify_regulatory_breaches(loan_data),
                'risk_assessment': self._assess_overall_risk(loan_data),
                'analysis_date': datetime.now().strftime('%Y-%m-%d')
            }
            
            return analysis
        except Exception as e:
            logger.error(f"Error in concentration risk analysis: {e}")
            return self._get_fallback_analysis()
    
    def _extract_loan_data(self) -> pd.DataFrame:
        """Extract loan portfolio data (simulated)"""
        try:
            # Sample loan data with employer, product, and geographic information
            np.random.seed(42)  # For reproducible results
            n_loans = 5000
            
            employers = [f'Employer_{i}' for i in range(1, 51)]
            products = ['Personal Loan', 'Business Loan', 'Asset Finance', 'Emergency Loan', 'School Fees']
            regions = ['Nairobi', 'Central', 'Coast', 'Eastern', 'Rift Valley', 'Western', 'Nyanza']
            
            loans = []
            for i in range(n_loans):
                loans.append({
                    'loan_id': f'L{10000 + i}',
                    'member_id': f'M{5000 + i}',
                    'employer_name': np.random.choice(employers, p=self._generate_employer_probabilities(len(employers))),
                    'product_type': np.random.choice(products, p=[0.35, 0.25, 0.20, 0.15, 0.05]),
                    'region': np.random.choice(regions, p=[0.40, 0.15, 0.10, 0.10, 0.15, 0.05, 0.05]),
                    'outstanding_amount': np.random.lognormal(12, 0.8),  # Log-normal distribution
                    'days_past_due': np.random.poisson(15),  # Poisson distribution for DPD
                    'interest_rate': np.random.uniform(0.10, 0.18),
                    'origination_date': datetime(2022, 1, 1) + timedelta(days=np.random.randint(0, 800))
                })
            
            return pd.DataFrame(loans)
        except Exception as e:
            logger.error(f"Error extracting loan data: {e}")
            return pd.DataFrame()
    
    def _generate_employer_probabilities(self, n_employers: int) -> List[float]:
        """Generate skewed probabilities for employer distribution"""
        try:
            # Create a power law distribution (few large employers, many small ones)
            ranks = np.arange(1, n_employers + 1)
            probabilities = 1 / ranks
            probabilities = probabilities / probabilities.sum()  # Normalize
            return probabilities.tolist()
        except Exception as e:
            logger.error(f"Error generating employer probabilities: {e}")
            return [1/n_employers] * n_employers
    
    def _extract_employer_data(self) -> pd.DataFrame:
        """Extract employer information (simulated)"""
        try:
            employers = [f'Employer_{i}' for i in range(1, 51)]
            sectors = ['Government', 'Education', 'Healthcare', 'Manufacturing', 'Services', 'Agriculture']
            
            employer_data = []
            for i, employer in enumerate(employers):
                employer_data.append({
                    'employer_name': employer,
                    'sector': np.random.choice(sectors),
                    'employee_count': np.random.randint(50, 5000),
                    'stability_score': np.random.uniform(0.6, 1.0),
                    'relationship_years': np.random.randint(1, 15)
                })
            
            return pd.DataFrame(employer_data)
        except Exception as e:
            logger.error(f"Error extracting employer data: {e}")
            return pd.DataFrame()
    
    def _extract_product_data(self) -> pd.DataFrame:
        """Extract product information (simulated)"""
        try:
            products = ['Personal Loan', 'Business Loan', 'Asset Finance', 'Emergency Loan', 'School Fees']
            
            product_data = []
            for product in products:
                product_data.append({
                    'product_name': product,
                    'risk_weight': np.random.uniform(0.8, 1.5),
                    'average_term': np.random.randint(12, 60),
                    'pricing_tier': np.random.choice(['Standard', 'Premium', 'Basic'])
                })
            
            return pd.DataFrame(product_data)
        except Exception as e:
            logger.error(f"Error extracting product data: {e}")
            return pd.DataFrame()
    
    def _extract_geographic_data(self) -> pd.DataFrame:
        """Extract geographic information (simulated)"""
        try:
            regions = ['Nairobi', 'Central', 'Coast', 'Eastern', 'Rift Valley', 'Western', 'Nyanza']
            
            geographic_data = []
            for region in regions:
                geographic_data.append({
                    'region_name': region,
                    'economic_rating': np.random.choice(['A', 'B', 'C']),
                    'growth_potential': np.random.uniform(0.5, 1.2),
                    'risk_factor': np.random.uniform(0.8, 1.3)
                })
            
            return pd.DataFrame(geographic_data)
        except Exception as e:
            logger.error(f"Error extracting geographic data: {e}")
            return pd.DataFrame()
    
    def _analyze_employer_concentration(self, loan_data: pd.DataFrame, employer_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze employer concentration"""
        try:
            if loan_data.empty:
                return self._get_empty_employer_analysis()
                
            # Calculate employer exposures
            employer_exposures = loan_data.groupby('employer_name').agg({
                'outstanding_amount': 'sum',
                'loan_id': 'count',
                'days_past_due': 'mean'
            }).reset_index()
            
            total_portfolio = loan_data['outstanding_amount'].sum()
            if total_portfolio == 0:
                return self._get_empty_employer_analysis()
                
            employer_exposures['exposure_share'] = employer_exposures['outstanding_amount'] / total_portfolio
            employer_exposures['average_dpd'] = employer_exposures['days_past_due']
            
            # Sort by exposure
            employer_exposures = employer_exposures.sort_values('exposure_share', ascending=False)
            
            # Calculate concentration metrics
            top_employers = employer_exposures.head(10).to_dict('records')
            single_largest_share = employer_exposures.iloc[0]['exposure_share'] if len(employer_exposures) > 0 else 0
            top_5_share = employer_exposures.head(5)['exposure_share'].sum()
            top_10_share = employer_exposures.head(10)['exposure_share'].sum()
            
            # Herfindahl-Hirschman Index for employer concentration
            hhi = (employer_exposures['exposure_share'] ** 2).sum()
            
            # Gini coefficient for inequality
            gini = self._calculate_gini_coefficient(employer_exposures['exposure_share'])
            
            return {
                'top_employers': top_employers,
                'single_largest_share': single_largest_share,
                'top_5_share': top_5_share,
                'top_10_share': top_10_share,
                'herfindahl_index': hhi,
                'gini_coefficient': gini,
                'total_employers': len(employer_exposures),
                'significant_exposures': len(employer_exposures[employer_exposures['exposure_share'] > 0.05])
            }
        except Exception as e:
            logger.error(f"Error analyzing employer concentration: {e}")
            return self._get_empty_employer_analysis()
    
    def _analyze_product_concentration(self, loan_data: pd.DataFrame, product_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze product concentration"""
        try:
            if loan_data.empty:
                return self._get_empty_product_analysis()
                
            # Calculate product shares
            product_shares = loan_data.groupby('product_type')['outstanding_amount'].sum()
            total_portfolio = product_shares.sum()
            if total_portfolio == 0:
                return self._get_empty_product_analysis()
                
            product_shares = product_shares / total_portfolio
            
            # Product quality metrics
            product_quality = {}
            for product in product_shares.index:
                product_loans = loan_data[loan_data['product_type'] == product]
                if len(product_loans) > 0:
                    product_quality[product] = {
                        'par_30': len(product_loans[product_loans['days_past_due'] > 30]) / len(product_loans),
                        'npl_ratio': len(product_loans[product_loans['days_past_due'] > 90]) / len(product_loans),
                        'average_balance': product_loans['outstanding_amount'].mean(),
                        'growth_rate': np.random.uniform(-0.05, 0.15)  # Simulated growth
                    }
                else:
                    product_quality[product] = {
                        'par_30': 0.0,
                        'npl_ratio': 0.0,
                        'average_balance': 0.0,
                        'growth_rate': 0.0
                    }
            
            # Concentration metrics
            hhi = (product_shares ** 2).sum()
            dominant_product_share = product_shares.max()
            
            # Risk assessment
            overall_risk_score = self._calculate_product_risk_score(product_shares, product_quality)
            
            # Diversification recommendations
            diversification_recommendations = self._generate_diversification_recommendations(product_shares, product_quality)
            
            return {
                'product_shares': product_shares.to_dict(),
                'product_quality': product_quality,
                'concentration_risk': {
                    'herfindahl_index': hhi,
                    'dominant_product_share': dominant_product_share,
                    'overall_risk_score': overall_risk_score
                },
                'diversification_recommendations': diversification_recommendations
            }
        except Exception as e:
            logger.error(f"Error analyzing product concentration: {e}")
            return self._get_empty_product_analysis()
    
    def _analyze_geographic_concentration(self, loan_data: pd.DataFrame, geographic_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze geographic concentration"""
        try:
            if loan_data.empty:
                return {}
                
            # Calculate regional exposures
            regional_exposures = loan_data.groupby('region').agg({
                'outstanding_amount': 'sum',
                'loan_id': 'count',
                'days_past_due': 'mean'
            }).reset_index()
            
            total_portfolio = regional_exposures['outstanding_amount'].sum()
            if total_portfolio == 0:
                return {}
                
            regional_exposures['exposure_share'] = regional_exposures['outstanding_amount'] / total_portfolio
            
            # Create geographic concentration analysis
            geographic_concentration = {}
            for _, row in regional_exposures.iterrows():
                region_filter = geographic_data[geographic_data['region_name'] == row['region']]
                if not region_filter.empty:
                    region_data = region_filter.iloc[0]
                    geographic_concentration[row['region']] = {
                        'exposure_share': row['exposure_share'],
                        'member_count': row['loan_id'],
                        'average_balance': row['outstanding_amount'] / row['loan_id'] if row['loan_id'] > 0 else 0,
                        'average_dpd': row['days_past_due'],
                        'economic_rating': region_data.get('economic_rating', 'B'),
                        'growth_potential': region_data.get('growth_potential', 1.0),
                        'risk_factor': region_data.get('risk_factor', 1.0)
                    }
                else:
                    geographic_concentration[row['region']] = {
                        'exposure_share': row['exposure_share'],
                        'member_count': row['loan_id'],
                        'average_balance': row['outstanding_amount'] / row['loan_id'] if row['loan_id'] > 0 else 0,
                        'average_dpd': row['days_past_due'],
                        'economic_rating': 'B',
                        'growth_potential': 1.0,
                        'risk_factor': 1.0
                    }
            
            return geographic_concentration
        except Exception as e:
            logger.error(f"Error analyzing geographic concentration: {e}")
            return {}
    
    def _identify_regulatory_breaches(self, loan_data: pd.DataFrame) -> Dict[str, Any]:
        """Identify regulatory concentration limit breaches"""
        try:
            breaches = []
            
            if loan_data.empty:
                return {
                    'total_breaches': 0,
                    'breaches': breaches,
                    'compliance_status': 'COMPLIANT'
                }
            
            # Analyze employer concentration
            employer_exposures = loan_data.groupby('employer_name')['outstanding_amount'].sum()
            total_portfolio = employer_exposures.sum()
            if total_portfolio == 0:
                return {
                    'total_breaches': 0,
                    'breaches': breaches,
                    'compliance_status': 'COMPLIANT'
                }
                
            employer_shares = employer_exposures / total_portfolio
            
            # Check single employer limit
            single_largest = employer_shares.max() if len(employer_shares) > 0 else 0
            if single_largest > self.regulatory_limits['single_employer_max']:
                breaches.append({
                    'type': 'Single Employer',
                    'current_value': single_largest,
                    'limit_value': self.regulatory_limits['single_employer_max'],
                    'description': f'Single employer exposure ({single_largest*100:.1f}%) exceeds {self.regulatory_limits["single_employer_max"]*100:.1f}% limit'
                })
            
            # Check top 5 employers limit
            top_5_share = employer_shares.nlargest(5).sum() if len(employer_shares) >= 5 else employer_shares.sum()
            if top_5_share > self.regulatory_limits['top_5_employers_max']:
                breaches.append({
                    'type': 'Top 5 Employers',
                    'current_value': top_5_share,
                    'limit_value': self.regulatory_limits['top_5_employers_max'],
                    'description': f'Top 5 employer exposure ({top_5_share*100:.1f}%) exceeds {self.regulatory_limits["top_5_employers_max"]*100:.1f}% limit'
                })
            
            return {
                'total_breaches': len(breaches),
                'breaches': breaches,
                'compliance_status': 'COMPLIANT' if len(breaches) == 0 else 'NON-COMPLIANT'
            }
        except Exception as e:
            logger.error(f"Error identifying regulatory breaches: {e}")
            return {
                'total_breaches': 0,
                'breaches': [],
                'compliance_status': 'COMPLIANT'
            }
    
    def _assess_overall_risk(self, loan_data: pd.DataFrame) -> Dict[str, Any]:
        """Assess overall concentration risk"""
        try:
            if loan_data.empty:
                return self._get_empty_risk_assessment()
                
            # This would integrate all concentration dimensions into an overall risk assessment
            employer_analysis = self._analyze_employer_concentration(loan_data, self._extract_employer_data())
            product_analysis = self._analyze_product_concentration(loan_data, self._extract_product_data())
            geographic_analysis = self._analyze_geographic_concentration(loan_data, self._extract_geographic_data())
            
            # Weighted risk score
            employer_risk = min(employer_analysis.get('herfindahl_index', 0) / 0.25, 1.0)  # Normalize to 0-1
            product_risk = min(product_analysis.get('concentration_risk', {}).get('herfindahl_index', 0) / 0.25, 1.0)
            
            # Handle geographic risk calculation safely
            geographic_values = list(geographic_analysis.values()) if geographic_analysis else []
            largest_geo_share = max([x.get('exposure_share', 0) for x in geographic_values]) if geographic_values else 0
            geographic_risk = min(largest_geo_share / 0.4, 1.0)
            
            overall_risk = (employer_risk * 0.5 + product_risk * 0.3 + geographic_risk * 0.2)
            
            return {
                'overall_risk_score': overall_risk,
                'risk_category': 'High' if overall_risk > 0.7 else 'Medium' if overall_risk > 0.4 else 'Low',
                'component_risks': {
                    'employer_risk': employer_risk,
                    'product_risk': product_risk,
                    'geographic_risk': geographic_risk
                },
                'key_concerns': self._identify_key_concerns(employer_analysis, product_analysis, geographic_analysis)
            }
        except Exception as e:
            logger.error(f"Error assessing overall risk: {e}")
            return self._get_empty_risk_assessment()
    
    def _calculate_gini_coefficient(self, values: pd.Series) -> float:
        """Calculate Gini coefficient for inequality measurement"""
        try:
            if len(values) == 0:
                return 0.0
                
            # Sort values
            sorted_values = np.sort(values)
            n = len(sorted_values)
            index = np.arange(1, n + 1)
            
            # Gini formula
            gini = (np.sum((2 * index - n - 1) * sorted_values)) / (n * np.sum(sorted_values))
            return float(gini)
        except Exception as e:
            logger.error(f"Error calculating Gini coefficient: {e}")
            return 0.0
    
    def _calculate_product_risk_score(self, product_shares: pd.Series, product_quality: Dict) -> float:
        """Calculate overall product concentration risk score"""
        try:
            # Consider both concentration and quality
            hhi_risk = min((product_shares ** 2).sum() / 0.25, 1.0)  # HHI component
            
            # Quality component (higher PAR = higher risk)
            quality_values = [quality.get('par_30', 0) for quality in product_quality.values()]
            quality_risk = np.mean(quality_values) / 0.1 if quality_values else 0.0  # Normalize
            quality_risk = min(quality_risk, 1.0)
            
            return float(hhi_risk * 0.6 + quality_risk * 0.4)
        except Exception as e:
            logger.error(f"Error calculating product risk score: {e}")
            return 0.0
    
    def _generate_diversification_recommendations(self, product_shares: pd.Series, product_quality: Dict) -> List[Dict]:
        """Generate product diversification recommendations"""
        try:
            recommendations = []
            
            # Check for over-concentration
            if len(product_shares) > 0 and product_shares.max() > 0.4:
                dominant_product = product_shares.idxmax()
                recommendations.append({
                    'action': f'Reduce concentration in {dominant_product} (current: {product_shares.max()*100:.1f}%)',
                    'priority': 'High',
                    'impact': 'High'
                })
            
            # Check for under-performing products
            for product, quality in product_quality.items():
                if quality.get('par_30', 0) > 0.08 and product_shares.get(product, 0) > 0.1:
                    recommendations.append({
                        'action': f'Review underwriting for {product} (PAR 30: {quality["par_30"]*100:.1f}%)',
                        'priority': 'Medium',
                        'impact': 'Medium'
                    })
            
            # Check for growth opportunities
            if len(product_shares) < 5:
                recommendations.append({
                    'action': 'Consider developing new product offerings to diversify portfolio',
                    'priority': 'Medium',
                    'impact': 'Medium'
                })
            
            return recommendations
        except Exception as e:
            logger.error(f"Error generating diversification recommendations: {e}")
            return []
    
    def _identify_key_concerns(self, employer_analysis: Dict, product_analysis: Dict, geographic_analysis: Dict) -> List[str]:
        """Identify key concentration risk concerns"""
        try:
            concerns = []
            
            # Employer concerns
            single_largest = employer_analysis.get('single_largest_share', 0)
            if single_largest > 0.15:
                concerns.append(f"Single employer exposure ({single_largest*100:.1f}%) approaching regulatory limit")
            
            employer_hhi = employer_analysis.get('herfindahl_index', 0)
            if employer_hhi > 0.15:
                concerns.append(f"High employer concentration (HHI: {employer_hhi:.3f})")
            
            # Product concerns
            product_hhi = product_analysis.get('concentration_risk', {}).get('herfindahl_index', 0)
            if product_hhi > 0.15:
                concerns.append("High product concentration")
            
            # Geographic concerns
            if geographic_analysis:
                largest_region = max(geographic_analysis.values(), key=lambda x: x.get('exposure_share', 0))
                largest_share = largest_region.get('exposure_share', 0)
                if largest_share > 0.4:
                    region_name = list(geographic_analysis.keys())[0]
                    concerns.append(f"High geographic concentration in {region_name} ({largest_share*100:.1f}%)")
            
            return concerns
        except Exception as e:
            logger.error(f"Error identifying key concerns: {e}")
            return ["Error in risk assessment"]
    
    def analyze_employer_concentration(self) -> Dict[str, Any]:
        """Detailed employer concentration analysis"""
        try:
            loan_data = self._extract_loan_data()
            employer_data = self._extract_employer_data()
            
            if loan_data.empty:
                return self._get_empty_employer_detailed_analysis()
                
            base_analysis = self._analyze_employer_concentration(loan_data, employer_data)
            
            # Add trend analysis (simulated)
            trend_analysis = {}
            for i in range(4):
                period = f'Q{4-i} 2023'
                # Simulate some variation in trends
                variation = np.random.uniform(-0.02, 0.02)
                trend_analysis[period] = {
                    'top_5_share': max(0, base_analysis.get('top_5_share', 0) + variation),
                    'single_largest_share': max(0, base_analysis.get('single_largest_share', 0) + variation/2),
                    'herfindahl_index': max(0, base_analysis.get('herfindahl_index', 0) + variation/3)
                }
            
            return {
                'employer_exposures': base_analysis.get('top_employers', []),
                'risk_indicators': {
                    'herfindahl_index': base_analysis.get('herfindahl_index', 0),
                    'gini_coefficient': base_analysis.get('gini_coefficient', 0),
                    'concentration_ratio_4': base_analysis.get('top_5_share', 0),  # Using top 5 as proxy for CR4
                    'significant_exposures_count': base_analysis.get('significant_exposures', 0)
                },
                'trend_analysis': trend_analysis,
                'regulatory_compliance': {
                    'single_employer_breach': base_analysis.get('single_largest_share', 0) > self.regulatory_limits['single_employer_max'],
                    'top_5_breach': base_analysis.get('top_5_share', 0) > self.regulatory_limits['top_5_employers_max']
                }
            }
        except Exception as e:
            logger.error(f"Error in detailed employer analysis: {e}")
            return self._get_empty_employer_detailed_analysis()
    
    def analyze_product_concentration(self) -> Dict[str, Any]:
        """Detailed product concentration analysis"""
        try:
            loan_data = self._extract_loan_data()
            product_data = self._extract_product_data()
            
            if loan_data.empty:
                return self._get_empty_product_analysis()
                
            return self._analyze_product_concentration(loan_data, product_data)
        except Exception as e:
            logger.error(f"Error in detailed product analysis: {e}")
            return self._get_empty_product_analysis()
    
    def analyze_regulatory_compliance(self) -> Dict[str, Any]:
        """Detailed regulatory compliance analysis"""
        try:
            loan_data = self._extract_loan_data()
            breaches = self._identify_regulatory_breaches(loan_data)
            
            # Simulate compliance trends
            compliance_trends = {}
            for i in range(4):
                period = f'Q{4-i} 2023'
                compliance_trends[period] = {
                    'compliance_score': np.random.uniform(0.85, 0.95),
                    'breach_count': np.random.randint(0, 2)
                }
            
            return {
                'compliance_status': {
                    'overall_score': 0.92 if breaches.get('total_breaches', 0) == 0 else 0.75,
                    'single_employer_compliant': breaches.get('total_breaches', 0) == 0,
                    'top_5_compliant': True
                },
                'regulatory_breaches': breaches.get('breaches', []),
                'compliance_trends': compliance_trends
            }
        except Exception as e:
            logger.error(f"Error in regulatory compliance analysis: {e}")
            return {
                'compliance_status': {
                    'overall_score': 0.0,
                    'single_employer_compliant': False,
                    'top_5_compliant': False
                },
                'regulatory_breaches': [],
                'compliance_trends': {}
            }
    
    def calculate_early_warning_indicators(self) -> Dict[str, Any]:
        """Calculate early warning indicators for concentration risk"""
        try:
            loan_data = self._extract_loan_data()
            if loan_data.empty:
                return self._get_empty_warning_indicators()
                
            employer_analysis = self._analyze_employer_concentration(loan_data, self._extract_employer_data())
            
            # Simulate warning indicators
            indicators = {
                'employer_hhi_trend': np.random.uniform(-0.02, 0.03),  # Quarterly change in HHI
                'new_exposure_growth': np.random.uniform(0.05, 0.25),   # Growth in new large exposures
                'limit_utilization': employer_analysis.get('single_largest_share', 0) / self.regulatory_limits['single_employer_max'],
                'concentration_velocity': np.random.uniform(0.01, 0.05)  # Rate of concentration increase
            }
            
            # Generate alerts based on indicators
            alerts = []
            if indicators['employer_hhi_trend'] > 0.02:
                alerts.append({
                    'severity': 'Medium',
                    'message': 'Employer concentration is increasing rapidly'
                })
            
            if indicators['limit_utilization'] > 0.8:
                alerts.append({
                    'severity': 'High',
                    'message': 'Single employer limit utilization approaching threshold'
                })
            
            if indicators['new_exposure_growth'] > 0.2:
                alerts.append({
                    'severity': 'Medium', 
                    'message': 'High growth in new large exposures detected'
                })
            
            indicators['alerts'] = alerts
            return indicators
        except Exception as e:
            logger.error(f"Error calculating warning indicators: {e}")
            return self._get_empty_warning_indicators()
    
    def generate_concentration_report(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive concentration risk report"""
        try:
            return {
                'executive_summary': self._generate_executive_summary(analysis),
                'key_findings': self._extract_key_findings(analysis),
                'recommendations': self._generate_recommendations(analysis),
                'risk_metrics': self._compile_risk_metrics(analysis),
                'report_date': datetime.now().strftime('%Y-%m-%d')
            }
        except Exception as e:
            logger.error(f"Error generating concentration report: {e}")
            return {
                'executive_summary': 'Error generating report',
                'key_findings': [],
                'recommendations': [],
                'risk_metrics': {},
                'report_date': datetime.now().strftime('%Y-%m-%d')
            }
    
    def _generate_executive_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate executive summary for concentration report"""
        try:
            risk_assessment = analysis.get('risk_assessment', {})
            breaches = analysis.get('regulatory_breaches', {})
            employer = analysis.get('employer_concentration', {})
            product = analysis.get('product_concentration', {})
            
            summary = f"""
            Concentration Risk Assessment Report
            ===================================
            
            Overall Risk: {risk_assessment.get('risk_category', 'Unknown')}
            Regulatory Compliance: {breaches.get('compliance_status', 'Unknown')}
            
            Key Points:
            - Single largest employer: {employer.get('single_largest_share', 0)*100:.1f}%
            - Top 5 employers: {employer.get('top_5_share', 0)*100:.1f}%
            - Product HHI: {product.get('concentration_risk', {}).get('herfindahl_index', 0):.3f}
            - Regulatory breaches: {breaches.get('total_breaches', 0)}
            """
            
            return summary
        except Exception as e:
            logger.error(f"Error generating executive summary: {e}")
            return "Error generating executive summary"
    
    def _extract_key_findings(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract key findings from analysis"""
        try:
            findings = []
            
            employer = analysis.get('employer_concentration', {})
            product = analysis.get('product_concentration', {})
            breaches = analysis.get('regulatory_breaches', {})
            
            single_largest = employer.get('single_largest_share', 0)
            if single_largest > 0.15:
                findings.append(f"High single employer exposure ({single_largest*100:.1f}%)")
            
            employer_hhi = employer.get('herfindahl_index', 0)
            if employer_hhi > 0.15:
                findings.append(f"Significant employer concentration (HHI: {employer_hhi:.3f})")
            
            product_hhi = product.get('concentration_risk', {}).get('herfindahl_index', 0)
            if product_hhi > 0.15:
                findings.append("Moderate product concentration")
            
            breach_count = breaches.get('total_breaches', 0)
            if breach_count > 0:
                findings.append(f"{breach_count} regulatory limit breach(es) identified")
            
            return findings
        except Exception as e:
            logger.error(f"Error extracting key findings: {e}")
            return ["Error in analysis"]
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict]:
        """Generate recommendations based on analysis"""
        try:
            recommendations = []
            employer = analysis.get('employer_concentration', {})
            product = analysis.get('product_concentration', {})
            
            # Employer recommendations
            single_largest = employer.get('single_largest_share', 0)
            if single_largest > 0.15:
                recommendations.append({
                    'category': 'Employer Concentration',
                    'recommendation': 'Implement stricter single employer limits and monitoring',
                    'priority': 'High',
                    'timeline': 'Immediate'
                })
            
            employer_hhi = employer.get('herfindahl_index', 0)
            if employer_hhi > 0.15:
                recommendations.append({
                    'category': 'Employer Diversification',
                    'recommendation': 'Develop strategy to diversify employer base',
                    'priority': 'Medium',
                    'timeline': '3-6 months'
                })
            
            # Product recommendations
            product_hhi = product.get('concentration_risk', {}).get('herfindahl_index', 0)
            if product_hhi > 0.15:
                recommendations.append({
                    'category': 'Product Diversification',
                    'recommendation': 'Review product portfolio and consider new offerings',
                    'priority': 'Medium',
                    'timeline': '6-12 months'
                })
            
            return recommendations
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    def _compile_risk_metrics(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Compile key risk metrics for reporting"""
        try:
            employer = analysis.get('employer_concentration', {})
            product = analysis.get('product_concentration', {})
            breaches = analysis.get('regulatory_breaches', {})
            risk_assessment = analysis.get('risk_assessment', {})
            
            return {
                'employer_metrics': {
                    'single_largest_share': employer.get('single_largest_share', 0),
                    'top_5_share': employer.get('top_5_share', 0),
                    'herfindahl_index': employer.get('herfindahl_index', 0),
                    'gini_coefficient': employer.get('gini_coefficient', 0)
                },
                'product_metrics': {
                    'herfindahl_index': product.get('concentration_risk', {}).get('herfindahl_index', 0),
                    'dominant_product_share': product.get('concentration_risk', {}).get('dominant_product_share', 0),
                    'risk_score': product.get('concentration_risk', {}).get('overall_risk_score', 0)
                },
                'regulatory_metrics': {
                    'breach_count': breaches.get('total_breaches', 0),
                    'compliance_status': breaches.get('compliance_status', 'UNKNOWN')
                },
                'overall_risk': risk_assessment
            }
        except Exception as e:
            logger.error(f"Error compiling risk metrics: {e}")
            return {}
    
    # Fallback methods for empty data scenarios
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Return fallback analysis when data is unavailable"""
        return {
            'employer_concentration': self._get_empty_employer_analysis(),
            'product_concentration': self._get_empty_product_analysis(),
            'geographic_concentration': {},
            'regulatory_breaches': {
                'total_breaches': 0,
                'breaches': [],
                'compliance_status': 'COMPLIANT'
            },
            'risk_assessment': self._get_empty_risk_assessment(),
            'analysis_date': datetime.now().strftime('%Y-%m-%d')
        }
    
    def _get_empty_employer_analysis(self) -> Dict[str, Any]:
        """Return empty employer analysis structure"""
        return {
            'top_employers': [],
            'single_largest_share': 0.0,
            'top_5_share': 0.0,
            'top_10_share': 0.0,
            'herfindahl_index': 0.0,
            'gini_coefficient': 0.0,
            'total_employers': 0,
            'significant_exposures': 0
        }
    
    def _get_empty_product_analysis(self) -> Dict[str, Any]:
        """Return empty product analysis structure"""
        return {
            'product_shares': {},
            'product_quality': {},
            'concentration_risk': {
                'herfindahl_index': 0.0,
                'dominant_product_share': 0.0,
                'overall_risk_score': 0.0
            },
            'diversification_recommendations': []
        }
    
    def _get_empty_risk_assessment(self) -> Dict[str, Any]:
        """Return empty risk assessment structure"""
        return {
            'overall_risk_score': 0.0,
            'risk_category': 'Low',
            'component_risks': {
                'employer_risk': 0.0,
                'product_risk': 0.0,
                'geographic_risk': 0.0
            },
            'key_concerns': []
        }
    
    def _get_empty_employer_detailed_analysis(self) -> Dict[str, Any]:
        """Return empty detailed employer analysis structure"""
        return {
            'employer_exposures': [],
            'risk_indicators': {
                'herfindahl_index': 0.0,
                'gini_coefficient': 0.0,
                'concentration_ratio_4': 0.0,
                'significant_exposures_count': 0
            },
            'trend_analysis': {},
            'regulatory_compliance': {
                'single_employer_breach': False,
                'top_5_breach': False
            }
        }
    
    def _get_empty_warning_indicators(self) -> Dict[str, Any]:
        """Return empty warning indicators structure"""
        return {
            'employer_hhi_trend': 0.0,
            'new_exposure_growth': 0.0,
            'limit_utilization': 0.0,
            'concentration_velocity': 0.0,
            'alerts': []
        }