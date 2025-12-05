# scripts/load_seed_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sacco_core.db import DatabaseManager

def generate_sample_data():
    """Generate comprehensive sample data for demonstration"""
    
    # Members data
    members_data = []
    for i in range(1, 101):
        members_data.append({
            'member_id': f'M{str(i).zfill(5)}',
            'join_date': datetime(2022, 1, 1) + timedelta(days=np.random.randint(0, 730)),
            'deposits_balance': np.random.uniform(5000, 50000),
            'shares_balance': np.random.uniform(1000, 20000),
            'channel': np.random.choice(['Branch', 'Mobile', 'Agent']),
            'employer_id': np.random.choice(['EMP001', 'EMP002', 'EMP003', 'EMP004']),
            'phone': f'2547{np.random.randint(10000000, 99999999)}',
            'email': f'member{i}@example.com'
        })
    
    members_df = pd.DataFrame(members_data)
    
    # Loan states monthly data
    loan_states = []
    states = ['current', 'dpd1_30', 'dpd31_60', 'dpd61_90', 'dpd91_180', 'dpd180_plus', 'closed']
    
    for i in range(1, 51):  # 50 loans
        loan_id = f'L{str(i).zfill(5)}'
        member_id = f'M{str(np.random.randint(1, 101)).zfill(5)}'
        origination_date = datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 180))
        
        current_date = origination_date
        while current_date <= datetime(2024, 1, 1):
            month_end = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            if month_end > datetime(2024, 1, 1):
                break
                
            loan_states.append({
                'loan_id': loan_id,
                'member_id': member_id,
                'employer_id': members_df[members_df['member_id'] == member_id]['employer_id'].iloc[0],
                'product': np.random.choice(['Personal', 'Business', 'Asset', 'Emergency']),
                'origination_date': origination_date,
                'month_end': month_end,
                'state': np.random.choice(states, p=[0.85, 0.06, 0.03, 0.02, 0.02, 0.01, 0.01]),
                'os_principal': np.random.uniform(50000, 500000),
                'days_past_due': np.random.randint(0, 200),
                'recoveries_cash': np.random.uniform(0, 5000),
                'interest_accrued': np.random.uniform(1000, 20000),
                'charge_off_flag': np.random.choice([0, 1], p=[0.95, 0.05]),
                'cure_flag': np.random.choice([0, 1], p=[0.90, 0.10])
            })
            
            current_date = month_end + timedelta(days=1)
    
    loan_states_df = pd.DataFrame(loan_states)
    
    # Employers data
    employers_df = pd.DataFrame({
        'employer_id': ['EMP001', 'EMP002', 'EMP003', 'EMP004'],
        'employer_name': ['Kenya Government', 'Private School A', 'Manufacturing Co', 'Hospital B'],
        'active_members': [45, 25, 20, 10]
    })
    
    return {
        'members': members_df,
        'loan_states_monthly': loan_states_df,
        'employers': employers_df
    }

def load_data_to_db():
    """Load sample data to database"""
    db_manager = DatabaseManager()
    connection = db_manager.connect()
    
    try:
        data = generate_sample_data()
        
        for table_name, df in data.items():
            print(f"Loading {len(df)} records into {table_name}...")
            # Convert DataFrame to table
            connection.execute(f"DROP TABLE IF EXISTS {table_name}")
            connection.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
        
        print("Sample data loaded successfully!")
        
    except Exception as e:
        print(f"Error loading data: {e}")
    finally:
        db_manager.close()

if __name__ == "__main__":
    load_data_to_db()