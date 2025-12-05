# sacco_core/analytics/vintages.py
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import warnings

class VintageAnalyzer:
    """Analyze loan vintages and roll rates from monthly state data"""
    
    def __init__(self):
        self.states_order = ['current', 'dpd1_30', 'dpd31_60', 'dpd61_90', 'dpd91_180', 'dpd180_plus']
    
    def build_cohorts(self, states_df: pd.DataFrame) -> pd.DataFrame:
        """
        Build loan cohorts by origination month
        
        Args:
            states_df: DataFrame with monthly loan states
            
        Returns:
            DataFrame with cohort analysis
        """
        try:
            # Ensure proper date formatting
            states_df['origination_date'] = pd.to_datetime(states_df['origination_date'])
            states_df['month_end'] = pd.to_datetime(states_df['month_end'])
            
            # Create cohort month
            states_df['cohort_month'] = states_df['origination_date'].dt.to_period('M')
            states_df['observation_month'] = states_df['month_end'].dt.to_period('M')
            
            # Calculate months on books
            states_df['months_on_books'] = (
                states_df['observation_month'] - states_df['cohort_month']
            ).apply(lambda x: x.n)
            
            return states_df
            
        except Exception as e:
            warnings.warn(f"Error building cohorts: {e}")
            return pd.DataFrame()
    
    def calculate_roll_rates(self, states_df: pd.DataFrame, segment_cols: List[str] = None) -> Dict:
        """
        Calculate roll rates between states
        
        Args:
            states_df: DataFrame with monthly loan states
            segment_cols: Columns to segment analysis by
            
        Returns:
            Dictionary with roll rate matrices
        """
        if segment_cols is None:
            segment_cols = ['product']
        
        try:
            # Sort by loan_id and month_end to ensure chronological order
            states_df = states_df.sort_values(['loan_id', 'month_end'])
            
            # Create next state by shifting
            states_df['next_state'] = states_df.groupby('loan_id')['state'].shift(-1)
            
            # Remove rows without next state (last observation for each loan)
            transition_df = states_df.dropna(subset=['next_state'])
            
            # Create transition matrix
            transition_matrix = pd.crosstab(
                transition_df['state'], 
                transition_df['next_state'], 
                normalize='index'
            ).round(4)
            
            return {
                'overall': transition_matrix,
                'segments': {}  # Would be populated with segment-specific matrices
            }
            
        except Exception as e:
            warnings.warn(f"Error calculating roll rates: {e}")
            return {}
    
    def calculate_cure_rates(self, states_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate cure rates from delinquent to current states
        
        Args:
            states_df: DataFrame with monthly loan states
            
        Returns:
            DataFrame with cure rate analysis
        """
        try:
            # Identify cured loans (moved from delinquent to current)
            states_df = states_df.sort_values(['loan_id', 'month_end'])
            states_df['prev_state'] = states_df.groupby('loan_id')['state'].shift(1)
            
            # Define delinquent states
            delinquent_states = ['dpd1_30', 'dpd31_60', 'dpd61_90', 'dpd91_180', 'dpd180_plus']
            
            # Identify cures
            cured_loans = states_df[
                (states_df['prev_state'].isin(delinquent_states)) & 
                (states_df['state'] == 'current')
            ].copy()
            
            cured_loans['cure_duration'] = (
                cured_loans['month_end'] - cured_loans.groupby('loan_id')['month_end'].shift(1)
            ).dt.days
            
            return cured_loans
            
        except Exception as e:
            warnings.warn(f"Error calculating cure rates: {e}")
            return pd.DataFrame()