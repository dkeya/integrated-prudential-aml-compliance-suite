# sacco_core/analytics/alm_stress.py
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from datetime import datetime

class ALMStressTester:
    """Perform ALM stress testing for various scenarios"""
    
    def __init__(self):
        self.scenarios = {}
        self.baseline_data = self._get_baseline_data()
    
    def _get_baseline_data(self) -> Dict[str, Any]:
        """Get baseline financial data"""
        return {
            'total_assets': 350000000,  # 350M
            'total_liabilities': 320000000,  # 320M
            'total_deposits': 280000000,  # 280M
            'total_loans': 245000000,  # 245M
            'cash_equivalents': 45000000,  # 45M
            'investments': 25000000,  # 25M
            'net_interest_income': 18500000,  # 18.5M
            'capital_adequacy': 0.221,  # 22.1%
            'liquidity_ratio': 0.185,  # 18.5%
            'cumulative_gap': -15000000,  # -15M
            'ecl_provision': 8500000  # 8.5M
        }
    
    def run_all_stress_tests(self, scenario_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run comprehensive stress tests for all scenarios
        
        Args:
            scenario_params: Dictionary of stress scenario parameters
            
        Returns:
            Dictionary with all stress test results
        """
        results = {}
        
        # Baseline scenario
        results['baseline'] = self._calculate_baseline_metrics()
        
        # Deposit run-off scenarios
        results['mild_deposit_runoff'] = self._deposit_runoff_stress(
            self.baseline_data, scenario_params['mild_deposit_runoff']
        )
        
        results['severe_deposit_runoff'] = self._deposit_runoff_stress(
            self.baseline_data, scenario_params['severe_deposit_runoff']
        )
        
        # Interest rate shock scenarios
        results['mild_rate_shock'] = self._interest_rate_stress(
            self.baseline_data, scenario_params['mild_rate_shock_bps']
        )
        
        results['severe_rate_shock'] = self._interest_rate_stress(
            self.baseline_data, scenario_params['severe_rate_shock_bps']
        )
        
        # Credit risk scenarios
        results['mild_credit_stress'] = self._credit_risk_stress(
            self.baseline_data, scenario_params['mild_pd_increase']
        )
        
        results['severe_credit_stress'] = self._credit_risk_stress(
            self.baseline_data, scenario_params['severe_pd_increase']
        )
        
        # Combined severe scenario
        results['combined_severe'] = self._combined_stress_scenario(
            self.baseline_data, scenario_params
        )
        
        return results
    
    # ADD THIS METHOD TO FIX THE ERROR
    def run_comprehensive_stress_tests(self, scenarios: Dict, scenario_groups: List[str]) -> Dict:
        """
        Alias for run_all_stress_tests - added for compatibility with the page code
        """
        # Map the parameter names from the page to what run_all_stress_tests expects
        scenario_params = {
            'mild_deposit_runoff': scenarios.get('mild_deposit_runoff', 0.10),
            'severe_deposit_runoff': scenarios.get('severe_deposit_runoff', 0.25),
            'mild_rate_shock_bps': scenarios.get('mild_rate_shock_bps', 50),
            'severe_rate_shock_bps': scenarios.get('severe_rate_shock_bps', 200),
            'mild_pd_increase': scenarios.get('mild_pd_increase', 0.05),
            'severe_pd_increase': scenarios.get('severe_pd_increase', 0.15)
        }
        
        # Run the stress tests
        results = self.run_all_stress_tests(scenario_params)
        
        # Add additional scenarios that might be in the page but not in the original method
        if 'extreme_deposit_runoff' in scenarios:
            results['extreme_deposit_runoff'] = self._deposit_runoff_stress(
                self.baseline_data, scenarios['extreme_deposit_runoff']
            )
        
        if 'extreme_rate_shock_bps' in scenarios:
            results['extreme_rate_shock'] = self._interest_rate_stress(
                self.baseline_data, scenarios['extreme_rate_shock_bps']
            )
        
        if 'extreme_pd_increase' in scenarios:
            results['extreme_credit_stress'] = self._credit_risk_stress(
                self.baseline_data, scenarios['extreme_pd_increase']
            )
        
        # Add reverse stress test if requested
        if 'Reverse Stress Tests' in scenario_groups:
            results['reverse_stress'] = self._reverse_stress_test(scenarios)
        
        # Add yield curve stress if requested
        if scenarios.get('yield_curve_shift'):
            results['yield_curve_stress'] = self._yield_curve_stress(
                self.baseline_data, 
                scenarios.get('yield_curve_shift'),
                scenarios.get('yield_curve_magnitude', 100)
            )
        
        return results
    
    # ADD THESE ADDITIONAL METHODS FOR COMPREHENSIVE TESTING
    def _reverse_stress_test(self, scenarios: Dict) -> Dict[str, Any]:
        """Perform reverse stress test to find breaking point"""
        result = self.baseline_data.copy()
        
        # Find the point where capital adequacy falls below regulatory minimum
        # Simplified calculation
        extreme_deposit_runoff = scenarios.get('extreme_deposit_runoff', 0.40)
        extreme_pd_increase = scenarios.get('extreme_pd_increase', 0.30)
        
        # Calculate combined extreme impact
        capital_impact = (extreme_deposit_runoff * 0.15) + (extreme_pd_increase * 0.25)
        result['capital_adequacy'] = max(self.baseline_data['capital_adequacy'] - capital_impact, 0.05)
        
        # Liquidity impact
        liquidity_impact = extreme_deposit_runoff * 0.3
        result['liquidity_ratio'] = max(self.baseline_data['liquidity_ratio'] - liquidity_impact, 0.03)
        
        result['status'] = 'Fail' if result['capital_adequacy'] < 0.10 or result['liquidity_ratio'] < 0.05 else 'Watch'
        result['scenario'] = 'Reverse Stress Test (Breaking Point)'
        result['ecl_increase'] = self.baseline_data['ecl_provision'] * 0.5
        
        return result
    
    def _yield_curve_stress(self, baseline: Dict, shift_type: str, magnitude_bps: int) -> Dict[str, Any]:
        """Calculate yield curve shift impact"""
        result = baseline.copy()
        magnitude = magnitude_bps / 10000  # Convert bps to percentage
        
        # Simplified NII impact based on yield curve shift
        if shift_type == "Parallel Up":
            nii_impact = -baseline['net_interest_income'] * magnitude * 0.8
        elif shift_type == "Parallel Down":
            nii_impact = baseline['net_interest_income'] * magnitude * 0.6
        elif shift_type == "Steepening":
            nii_impact = -baseline['net_interest_income'] * magnitude * 0.4
        elif shift_type == "Flattening":
            nii_impact = baseline['net_interest_income'] * magnitude * 0.3
        else:  # Inversion
            nii_impact = -baseline['net_interest_income'] * magnitude * 0.7
        
        result['net_interest_income'] = max(baseline['net_interest_income'] + nii_impact, 0)
        
        # Capital impact
        capital_impact = abs(nii_impact) / baseline['total_assets'] * 0.3
        result['capital_adequacy'] = max(baseline['capital_adequacy'] - capital_impact, 0.10)
        
        # Determine status
        nii_change_pct = abs(nii_impact) / baseline['net_interest_income']
        if nii_change_pct > 0.20:
            result['status'] = 'Watch'
        else:
            result['status'] = 'Pass'
        
        result['scenario'] = f'Yield Curve {shift_type} ({magnitude_bps} bps)'
        result['ecl_increase'] = abs(nii_impact) * 0.08
        
        return result
    
    # KEEP ALL THE EXISTING METHODS BELOW EXACTLY AS THEY ARE
    def _calculate_baseline_metrics(self) -> Dict[str, Any]:
        """Calculate baseline financial metrics"""
        baseline = self.baseline_data.copy()
        baseline['status'] = 'Pass'
        baseline['ecl_increase'] = 0
        baseline['scenario'] = 'Baseline'
        return baseline
    
    def _deposit_runoff_stress(self, baseline: Dict, runoff_rate: float) -> Dict[str, Any]:
        """Calculate deposit run-off stress impact"""
        result = baseline.copy()
        
        # Reduce deposits
        deposit_reduction = baseline['total_deposits'] * runoff_rate
        result['total_deposits'] = baseline['total_deposits'] - deposit_reduction
        result['total_liabilities'] = baseline['total_liabilities'] - deposit_reduction
        
        # Use cash to cover run-off
        cash_used = min(deposit_reduction, baseline['cash_equivalents'])
        result['cash_equivalents'] = baseline['cash_equivalents'] - cash_used
        
        # Calculate new liquidity ratio
        result['liquidity_ratio'] = (
            result['cash_equivalents'] / result['total_deposits']
        )
        
        # Impact on capital adequacy
        result['capital_adequacy'] = max(
            baseline['capital_adequacy'] - (runoff_rate * 0.1),  # Simplified impact
            0.10  # Minimum
        )
        
        # Determine status
        if result['liquidity_ratio'] < 0.10:
            result['status'] = 'Fail'
        elif result['liquidity_ratio'] < 0.15:
            result['status'] = 'Watch'
        else:
            result['status'] = 'Pass'
        
        result['scenario'] = f'Deposit Run-off ({runoff_rate*100:.1f}%)'
        result['ecl_increase'] = deposit_reduction * 0.02  # Simplified ECL impact
        
        return result
    
    def _interest_rate_stress(self, baseline: Dict, rate_shock_bps: int) -> Dict[str, Any]:
        """Calculate interest rate shock impact"""
        result = baseline.copy()
        
        # Convert bps to percentage
        rate_shock = rate_shock_bps / 10000
        
        # Simplified NII impact calculation
        # Assume 40% of assets and 60% of liabilities are rate sensitive
        rate_sensitive_assets = baseline['total_assets'] * 0.4
        rate_sensitive_liabilities = baseline['total_liabilities'] * 0.6
        
        # NII impact (simplified)
        nii_impact = (rate_sensitive_assets - rate_sensitive_liabilities) * rate_shock
        result['net_interest_income'] = max(baseline['net_interest_income'] + nii_impact, 0)
        
        # Impact on cumulative gap (simplified)
        result['cumulative_gap'] = baseline['cumulative_gap'] - (nii_impact * 10)
        
        # Impact on capital (through NII)
        capital_impact = abs(nii_impact) / baseline['total_assets'] * 0.5
        if nii_impact < 0:  # Negative impact
            result['capital_adequacy'] = max(baseline['capital_adequacy'] - capital_impact, 0.10)
        else:  # Positive impact
            result['capital_adequacy'] = baseline['capital_adequacy'] + capital_impact
        
        # Determine status based on NII impact
        nii_change_pct = abs(nii_impact) / baseline['net_interest_income']
        
        if nii_change_pct > 0.25:
            result['status'] = 'Fail'
        elif nii_change_pct > 0.15:
            result['status'] = 'Watch'
        else:
            result['status'] = 'Pass'
        
        result['scenario'] = f'Rate Shock ({rate_shock_bps} bps)'
        result['ecl_increase'] = abs(nii_impact) * 0.1  # Simplified ECL impact
        
        return result
    
    def _credit_risk_stress(self, baseline: Dict, pd_increase: float) -> Dict[str, Any]:
        """Calculate credit risk stress impact"""
        result = baseline.copy()
        
        # Increase in ECL provision
        ecl_increase = baseline['ecl_provision'] * pd_increase
        result['ecl_provision'] = baseline['ecl_provision'] + ecl_increase
        
        # Impact on capital through provisions
        capital_reduction = ecl_increase / baseline['total_assets']
        result['capital_adequacy'] = max(baseline['capital_adequacy'] - capital_reduction, 0.10)
        
        # Impact on liquidity (increased provisions reduce available funds)
        result['cash_equivalents'] = max(baseline['cash_equivalents'] - (ecl_increase * 0.3), 0)
        result['liquidity_ratio'] = result['cash_equivalents'] / result['total_deposits']
        
        # Determine status
        if result['capital_adequacy'] < 0.15:
            result['status'] = 'Fail'
        elif result['capital_adequacy'] < 0.18:
            result['status'] = 'Watch'
        else:
            result['status'] = 'Pass'
        
        result['scenario'] = f'Credit Stress (PD +{pd_increase*100:.1f}%)'
        result['ecl_increase'] = ecl_increase
        
        return result
    
    def _combined_stress_scenario(self, baseline: Dict, scenario_params: Dict) -> Dict[str, Any]:
        """Calculate combined severe stress scenario"""
        # Start with severe deposit run-off
        result = self._deposit_runoff_stress(baseline, scenario_params['severe_deposit_runoff'])
        
        # Add severe rate shock
        rate_stress = self._interest_rate_stress(baseline, scenario_params['severe_rate_shock_bps'])
        result['net_interest_income'] = rate_stress['net_interest_income']
        result['cumulative_gap'] = rate_stress['cumulative_gap']
        
        # Add severe credit stress
        credit_stress = self._credit_risk_stress(baseline, scenario_params['severe_pd_increase'])
        result['ecl_provision'] = credit_stress['ecl_provision']
        result['capital_adequacy'] = min(result['capital_adequacy'], credit_stress['capital_adequacy'])
        
        # Recalculate overall status (most conservative)
        if result['liquidity_ratio'] < 0.08 or result['capital_adequacy'] < 0.12:
            result['status'] = 'Fail'
        elif result['liquidity_ratio'] < 0.12 or result['capital_adequacy'] < 0.15:
            result['status'] = 'Watch'
        else:
            result['status'] = 'Pass'
        
        result['scenario'] = 'Combined Severe Stress'
        result['ecl_increase'] = (
            self._deposit_runoff_stress(baseline, scenario_params['severe_deposit_runoff'])['ecl_increase'] +
            self._interest_rate_stress(baseline, scenario_params['severe_rate_shock_bps'])['ecl_increase'] +
            self._credit_risk_stress(baseline, scenario_params['severe_pd_increase'])['ecl_increase']
        )
        
        return result
    
    def calculate_liquidity_at_risk(self, confidence_level: float = 0.95) -> Dict[str, float]:
        """
        Calculate Liquidity at Risk (LaR)
        
        Args:
            confidence_level: Confidence level for LaR calculation
            
        Returns:
            Dictionary with LaR metrics
        """
        # Simplified LaR calculation
        daily_volatility = 0.02  # 2% daily volatility
        var_factor = {0.95: 1.645, 0.99: 2.326}[confidence_level]
        
        lar = self.baseline_data['cash_equivalents'] * daily_volatility * var_factor
        
        return {
            'liquidity_at_risk': lar,
            'confidence_level': confidence_level,
            'time_horizon': '1-day',
            'lar_as_percent': (lar / self.baseline_data['cash_equivalents']) * 100
        }
    
    def generate_stress_test_report(self, results: Dict[str, Any]) -> pd.DataFrame:
        """
        Generate comprehensive stress test report
        
        Args:
            results: Stress test results dictionary
            
        Returns:
            DataFrame with formatted report
        """
        report_data = []
        
        for scenario_name, scenario_data in results.items():
            report_data.append({
                'Scenario': scenario_name.replace('_', ' ').title(),
                'Liquidity_Ratio': f"{scenario_data['liquidity_ratio'] * 100:.1f}%",
                'Capital_Adequacy': f"{scenario_data['capital_adequacy'] * 100:.1f}%",
                'NII_Change': f"{(scenario_data['net_interest_income'] - self.baseline_data['net_interest_income']):,.0f}",
                'ECL_Increase': f"{scenario_data['ecl_increase']:,.0f}",
                'Status': scenario_data['status'],
                'Severity': self._classify_severity(scenario_data)
            })
        
        return pd.DataFrame(report_data)
    
    def _classify_severity(self, scenario_data: Dict) -> str:
        """Classify scenario severity"""
        if scenario_data['status'] == 'Fail':
            return 'High'
        elif scenario_data['status'] == 'Watch':
            return 'Medium'
        else:
            return 'Low'