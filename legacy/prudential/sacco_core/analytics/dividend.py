# sacco_core/analytics/dividend.py
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from datetime import datetime

class DividendCalculator:
    """Calculate dividend capacity based on financial metrics and policy gates"""
    
    def __init__(self):
        self.policy_gates = []
    
    def calculate_dividend_capacity(self, 
                                  total_shares: float,
                                  net_surplus: float,
                                  statutory_reserve_pct: float,
                                  current_liquidity: float,
                                  current_par30: float,
                                  ecl_provision: float,
                                  config: Any,
                                  other_reserves: float = None,
                                  previous_dividend_pct: float = None,
                                  growth_factor: float = None,
                                  current_capital_adequacy: float = None) -> Dict[str, Any]:
        """
        Calculate dividend capacity considering all policy gates
        
        Args:
            total_shares: Total share capital
            net_surplus: Net surplus for the year
            statutory_reserve_pct: Percentage to statutory reserve
            current_liquidity: Current liquidity ratio
            current_par30: Current PAR30 ratio
            ecl_provision: Required ECL provision
            config: Application configuration
            other_reserves: Additional reserves allocation (optional)
            previous_dividend_pct: Previous year dividend rate (optional)
            growth_factor: Growth expectation factor (optional)
            current_capital_adequacy: Current capital adequacy ratio (optional)
            
        Returns:
            Dictionary with dividend calculation results
        """
        
        # Calculate statutory reserve
        statutory_reserve_amount = net_surplus * (statutory_reserve_pct / 100)
        
        # Use provided other_reserves or default to 10% of net surplus
        if other_reserves is None:
            other_reserves = net_surplus * 0.10  # 10% for other reserves
        
        # Calculate available for distribution
        available_for_distribution = (
            net_surplus - 
            statutory_reserve_amount - 
            ecl_provision - 
            other_reserves
        )
        
        # Check policy gates - pass capital adequacy if provided
        policy_gates = self._check_policy_gates(
            current_liquidity, 
            current_par30, 
            current_capital_adequacy,  # Pass the new parameter
            config
        )
        
        all_gates_passed = all(gate['passed'] for gate in policy_gates)
        
        # Calculate maximum possible dividend
        max_dividend_amount = available_for_distribution
        max_dividend_pct = (max_dividend_amount / total_shares) * 100
        
        # Apply policy maximum (safely handle missing config)
        try:
            max_recommendation = config.dividend.max_recommendation * 100
        except AttributeError:
            max_recommendation = 7.0  # Default 7%
        
        recommended_dividend_pct = min(max_dividend_pct, max_recommendation)
        
        # If policy gates failed, recommend 0 dividend
        if not all_gates_passed:
            recommended_dividend_pct = 0.0
        
        recommended_dividend_amount = total_shares * (recommended_dividend_pct / 100)
        
        # Use provided previous dividend or default
        if previous_dividend_pct is None:
            previous_dividend_pct = 6.5  # Sample previous year
        
        # Use provided capital adequacy or default
        if current_capital_adequacy is None:
            current_capital_adequacy = 0.22  # Sample value
        
        return {
            'total_shares': total_shares,
            'net_surplus': net_surplus,
            'statutory_reserve_amount': statutory_reserve_amount,
            'ecl_provision': ecl_provision,
            'other_reserves': other_reserves,
            'available_for_distribution': available_for_distribution,
            'max_dividend_pct': max_dividend_pct,
            'recommended_dividend_pct': recommended_dividend_pct,
            'dividend_amount': recommended_dividend_amount,
            'policy_gates_passed': all_gates_passed,
            'policy_gates': policy_gates,
            'previous_dividend_pct': previous_dividend_pct,
            'current_liquidity': current_liquidity,
            'current_par30': current_par30,
            'current_capital_adequacy': current_capital_adequacy,
            'calculation_date': datetime.now().strftime('%Y-%m-%d')
        }
    
    def _check_policy_gates(self, 
                           current_liquidity: float, 
                           current_par30: float, 
                           current_capital_adequacy: float = None,
                           config: Any = None) -> List[Dict[str, Any]]:
        """
        Check all policy gates for dividend declaration
        
        Args:
            current_liquidity: Current liquidity ratio
            current_par30: Current PAR30 ratio
            current_capital_adequacy: Current capital adequacy ratio (optional)
            config: Application configuration (optional)
            
        Returns:
            List of policy gate check results
        """
        gates = []
        
        # Safely get config values with defaults
        if config is not None and hasattr(config, 'dividend'):
            liquidity_gate = getattr(config.dividend, 'liquidity_gate', 0.10)
            par30_gate = getattr(config.dividend, 'par30_gate', 0.15)
        else:
            liquidity_gate = 0.10  # Default 10%
            par30_gate = 0.15      # Default 15%
        
        # Liquidity gate
        liquidity_passed = current_liquidity >= liquidity_gate
        gates.append({
            'name': 'Liquidity Ratio',
            'current_value': current_liquidity * 100,
            'threshold': liquidity_gate * 100,
            'passed': liquidity_passed,
            'description': 'Minimum liquidity ratio required',
            'margin': f"{(current_liquidity - liquidity_gate) * 100:.1f}%"
        })
        
        # PAR30 gate
        par30_passed = current_par30 <= par30_gate
        gates.append({
            'name': 'PAR30 Ratio',
            'current_value': current_par30 * 100,
            'threshold': par30_gate * 100,
            'passed': par30_passed,
            'description': 'Maximum PAR30 allowed',
            'margin': f"{(par30_gate - current_par30) * 100:.1f}%"
        })
        
        # Capital adequacy gate
        if current_capital_adequacy is not None:
            capital_threshold = 0.18  # 18% minimum SASRA requirement
            capital_passed = current_capital_adequacy >= capital_threshold
            gates.append({
                'name': 'Capital Adequacy',
                'current_value': current_capital_adequacy * 100,
                'threshold': capital_threshold * 100,
                'passed': capital_passed,
                'description': 'Minimum capital adequacy ratio',
                'margin': f"{(current_capital_adequacy - capital_threshold) * 100:.1f}%"
            })
        
        # Regulatory compliance gate (sample)
        regulatory_passed = True  # Assume compliant
        gates.append({
            'name': 'Regulatory Compliance',
            'current_value': "Compliant",
            'threshold': "Full Compliance",
            'passed': regulatory_passed,
            'description': 'All regulatory requirements met',
            'margin': "N/A"
        })
        
        return gates
    
    def generate_dividend_scenarios(self, 
                                  base_parameters: Dict[str, float],
                                  config: Any) -> pd.DataFrame:
        """
        Generate multiple dividend scenarios for sensitivity analysis
        
        Args:
            base_parameters: Base financial parameters
            config: Application configuration
            
        Returns:
            DataFrame with scenario analysis
        """
        scenarios = []
        
        # Base scenario
        base_result = self.calculate_dividend_capacity(**base_parameters, config=config)
        scenarios.append({
            'Scenario': 'Base Case',
            'Net_Surplus': base_parameters['net_surplus'],
            'Liquidity_Ratio': base_parameters['current_liquidity'] * 100,
            'PAR30': base_parameters['current_par30'] * 100,
            'Dividend_Rate': base_result['recommended_dividend_pct'],
            'Dividend_Amount': base_result['dividend_amount'],
            'Policy_Gates_Passed': base_result['policy_gates_passed']
        })
        
        # Optimistic scenario (20% better surplus)
        optimistic_params = base_parameters.copy()
        optimistic_params['net_surplus'] *= 1.2
        optimistic_params['current_liquidity'] = min(optimistic_params['current_liquidity'] * 1.1, 0.25)
        optimistic_params['current_par30'] = max(optimistic_params['current_par30'] * 0.8, 0.02)
        
        opt_result = self.calculate_dividend_capacity(**optimistic_params, config=config)
        scenarios.append({
            'Scenario': 'Optimistic',
            'Net_Surplus': optimistic_params['net_surplus'],
            'Liquidity_Ratio': optimistic_params['current_liquidity'] * 100,
            'PAR30': optimistic_params['current_par30'] * 100,
            'Dividend_Rate': opt_result['recommended_dividend_pct'],
            'Dividend_Amount': opt_result['dividend_amount'],
            'Policy_Gates_Passed': opt_result['policy_gates_passed']
        })
        
        # Pessimistic scenario (20% worse surplus)
        pessimistic_params = base_parameters.copy()
        pessimistic_params['net_surplus'] *= 0.8
        pessimistic_params['current_liquidity'] = pessimistic_params['current_liquidity'] * 0.9
        pessimistic_params['current_par30'] = pessimistic_params['current_par30'] * 1.2
        
        pess_result = self.calculate_dividend_capacity(**pessimistic_params, config=config)
        scenarios.append({
            'Scenario': 'Pessimistic',
            'Net_Surplus': pessimistic_params['net_surplus'],
            'Liquidity_Ratio': pessimistic_params['current_liquidity'] * 100,
            'PAR30': pessimistic_params['current_par30'] * 100,
            'Dividend_Rate': pess_result['recommended_dividend_pct'],
            'Dividend_Amount': pess_result['dividend_amount'],
            'Policy_Gates_Passed': pess_result['policy_gates_passed']
        })
        
        return pd.DataFrame(scenarios)
    
    def calculate_member_dividend(self, 
                                 member_shares: float, 
                                 dividend_rate: float) -> Dict[str, float]:
        """
        Calculate dividend for individual member
        
        Args:
            member_shares: Member's share balance
            dividend_rate: Declared dividend rate
            
        Returns:
            Member dividend calculation
        """
        gross_dividend = member_shares * (dividend_rate / 100)
        
        # Assume withholding tax (sample)
        withholding_tax = gross_dividend * 0.05  # 5% withholding tax
        
        net_dividend = gross_dividend - withholding_tax
        
        return {
            'member_shares': member_shares,
            'dividend_rate': dividend_rate,
            'gross_dividend': gross_dividend,
            'withholding_tax': withholding_tax,
            'net_dividend': net_dividend
        }