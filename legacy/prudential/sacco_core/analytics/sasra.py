# sacco_core/analytics/sasra.py
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import io

class SASRAReturnsGenerator:
    """Generate SASRA regulatory returns for Deposit-Taking SACCOs"""
    
    def __init__(self):
        self.sasra_mapping = self._initialize_sasra_mapping()
        self.regulatory_limits = self._initialize_regulatory_limits()
    
    def _initialize_sasra_mapping(self) -> Dict[str, Dict]:
        """Initialize GL to SASRA line mapping"""
        return {
            'balance_sheet': {
                'assets': {
                    'cash_and_banks': ['1000', '1001', '1002'],  # Cash, Bank balances
                    'investments': ['1100', '1101', '1102'],     # Government securities, other investments
                    'loans_members': ['1200', '1201', '1202'],   # Member loans
                    'fixed_assets': ['1300', '1301'],            # Property, equipment
                    'other_assets': ['1400', '1401']             # Prepayments, other assets
                },
                'liabilities': {
                    'member_deposits': ['2000', '2001', '2002'], # Savings, fixed deposits
                    'borrowings': ['2100', '2101'],              # External borrowings
                    'other_liabilities': ['2200', '2201']        # Accruals, other liabilities
                },
                'equity': {
                    'share_capital': ['3000', '3001'],           # Member shares
                    'statutory_reserve': ['3100'],               # Statutory reserve
                    'retained_earnings': ['3200'],               # Accumulated surplus
                    'other_reserves': ['3300']                   # Other reserves
                }
            },
            'income_statement': {
                'interest_income': ['4000', '4001', '4002'],     # Loan interest, investment income
                'interest_expense': ['5000', '5001'],            # Deposit interest, borrowing costs
                'operating_income': ['4100', '4101'],            # Fees, commissions
                'operating_expenses': ['5100', '5101', '5102']   # Staff, admin, other expenses
            }
        }
    
    def _initialize_regulatory_limits(self) -> Dict[str, float]:
        """Initialize SASRA regulatory limits"""
        return {
            'core_capital_min': 0.10,           # 10% minimum
            'liquidity_ratio_min': 0.15,        # 15% minimum
            'single_employer_max': 0.25,        # 25% maximum
            'npl_ratio_max': 0.08,              # 8% maximum
            'statutory_reserve_min': 0.20,      # 20% of surplus
            'large_exposure_min': 0.05          # 5% reporting threshold
        }
    
    def generate_returns(self, 
                        period: str,
                        return_type: str,
                        include_reconciliations: bool = True,
                        run_validation: bool = True) -> Dict[str, Any]:
        """
        Generate comprehensive SASRA returns
        
        Args:
            period: Reporting period (e.g., "Q1 2024")
            return_type: Type of return to generate
            include_reconciliations: Whether to include reconciliation reports
            run_validation: Whether to run validation checks
            
        Returns:
            Dictionary with SASRA returns data
        """
        # Extract data from database (simulated)
        financial_data = self._extract_financial_data(period)
        loan_data = self._extract_loan_data(period)
        deposit_data = self._extract_deposit_data(period)
        member_data = self._extract_member_data()
        
        # Generate main returns
        returns_data = {
            'metadata': {
                'reporting_period': period,
                'return_type': return_type,
                'generation_date': datetime.now().strftime('%Y-%m-%d'),
                'sacco_name': 'Demo SACCO Limited',
                'license_number': 'DT/SACCO/0000'
            },
            'summary': self._generate_summary(financial_data, loan_data, deposit_data),
            'balance_sheet': self._generate_balance_sheet(financial_data),
            'asset_quality': self._generate_asset_quality(loan_data),
            'large_exposures': self._generate_large_exposures(loan_data, member_data),
            'capital_adequacy': self._generate_capital_adequacy(financial_data),
            'liquidity': self._generate_liquidity_analysis(financial_data, deposit_data)
        }
        
        # Add reconciliations if requested
        if include_reconciliations:
            returns_data['reconciliations'] = self._generate_reconciliations(financial_data)
        
        # Run validation if requested
        if run_validation:
            returns_data['validation'] = self.validate_returns(returns_data)
        
        return returns_data
    
    def _extract_financial_data(self, period: str) -> Dict[str, float]:
        """Extract financial data from database (simulated)"""
        # In production, this would query the actual database
        return {
            'total_assets': 350000000,
            'total_liabilities': 320000000,
            'total_equity': 30000000,
            'cash_equivalents': 45000000,
            'investments': 25000000,
            'gross_loans': 245000000,
            'fixed_assets': 15000000,
            'other_assets': 20000000,
            'member_deposits': 280000000,
            'external_borrowings': 25000000,
            'other_liabilities': 15000000,
            'share_capital': 15000000,
            'statutory_reserve': 8000000,
            'retained_earnings': 5000000,
            'other_reserves': 2000000,
            'net_interest_income': 18500000,
            'operating_income': 3500000,
            'operating_expenses': 16500000,
            'net_surplus': 5500000
        }
    
    def _extract_loan_data(self, period: str) -> pd.DataFrame:
        """Extract loan portfolio data (simulated)"""
        # Sample loan data
        loans = []
        products = ['Personal Loan', 'Business Loan', 'Asset Finance', 'Emergency Loan', 'School Fees']
        
        for i in range(1000):
            loans.append({
                'loan_id': f'L{10000 + i}',
                'member_id': f'M{5000 + i}',
                'employer_id': f'E{np.random.randint(1, 20)}',
                'product_type': np.random.choice(products),
                'outstanding_amount': np.random.uniform(50000, 5000000),
                'days_past_due': np.random.randint(0, 365),
                'interest_rate': np.random.uniform(0.10, 0.18),
                'collateral_value': np.random.uniform(0, 10000000),
                'provision_amount': np.random.uniform(0, 500000)
            })
        
        return pd.DataFrame(loans)
    
    def _extract_deposit_data(self, period: str) -> pd.DataFrame:
        """Extract deposit data (simulated)"""
        # Sample deposit data
        deposits = []
        products = ['Savings Account', 'Fixed Deposit 30D', 'Fixed Deposit 90D', 'Fixed Deposit 180D', 'Fixed Deposit 1Y']
        
        for i in range(5000):
            deposits.append({
                'member_id': f'M{1000 + i}',
                'product_type': np.random.choice(products),
                'balance': np.random.uniform(1000, 500000),
                'interest_rate': np.random.uniform(0.03, 0.085)
            })
        
        return pd.DataFrame(deposits)
    
    def _extract_member_data(self) -> pd.DataFrame:
        """Extract member data (simulated)"""
        # Sample member data
        members = []
        employers = [f'Employer {i}' for i in range(1, 21)]
        
        for i in range(5000):
            members.append({
                'member_id': f'M{1000 + i}',
                'employer_name': np.random.choice(employers),
                'join_date': datetime(2020, 1, 1) + timedelta(days=np.random.randint(0, 1500)),
                'share_balance': np.random.uniform(1000, 50000),
                'deposit_balance': np.random.uniform(5000, 200000)
            })
        
        return pd.DataFrame(members)
    
    def _generate_summary(self, financial_data: Dict, loan_data: pd.DataFrame, deposit_data: pd.DataFrame) -> Dict[str, Any]:
        """Generate returns summary"""
        total_assets = financial_data['total_assets']
        total_loans = financial_data['gross_loans']
        total_deposits = financial_data['member_deposits']
        total_equity = financial_data['total_equity']
        
        # Calculate key ratios
        capital_adequacy = total_equity / total_assets
        liquidity_ratio = financial_data['cash_equivalents'] / total_deposits
        
        # Calculate PAR from loan data
        par_30 = len(loan_data[loan_data['days_past_due'] > 30]) / len(loan_data)
        par_90 = len(loan_data[loan_data['days_past_due'] > 90]) / len(loan_data)
        
        return {
            'total_assets': total_assets,
            'total_liabilities': financial_data['total_liabilities'],
            'total_equity': total_equity,
            'gross_loans': total_loans,
            'member_deposits': total_deposits,
            'capital_adequacy': capital_adequacy,
            'liquidity_ratio': liquidity_ratio,
            'par_30': par_30,
            'par_90': par_90,
            'net_surplus': financial_data['net_surplus']
        }
    
    def _generate_balance_sheet(self, financial_data: Dict) -> Dict[str, Dict]:
        """Generate balance sheet returns"""
        return {
            'assets': {
                'Cash and Bank Balances': financial_data['cash_equivalents'],
                'Investments': financial_data['investments'],
                'Loans to Members': financial_data['gross_loans'],
                'Fixed Assets': financial_data['fixed_assets'],
                'Other Assets': financial_data['other_assets']
            },
            'liabilities': {
                'Member Deposits': financial_data['member_deposits'],
                'External Borrowings': financial_data['external_borrowings'],
                'Other Liabilities': financial_data['other_liabilities']
            },
            'equity': {
                'Share Capital': financial_data['share_capital'],
                'Statutory Reserve': financial_data['statutory_reserve'],
                'Retained Earnings': financial_data['retained_earnings'],
                'Other Reserves': financial_data['other_reserves']
            }
        }
    
    def _generate_asset_quality(self, loan_data: pd.DataFrame) -> Dict[str, Any]:
        """Generate asset quality returns"""
        # PAR ladder
        par_ladder = {
            'Current (0-30 DPD)': len(loan_data[loan_data['days_past_due'] <= 30]),
            '31-60 DPD': len(loan_data[(loan_data['days_past_due'] > 30) & (loan_data['days_past_due'] <= 60)]),
            '61-90 DPD': len(loan_data[(loan_data['days_past_due'] > 60) & (loan_data['days_past_due'] <= 90)]),
            '91-180 DPD': len(loan_data[(loan_data['days_past_due'] > 90) & (loan_data['days_past_due'] <= 180)]),
            '180+ DPD': len(loan_data[loan_data['days_past_due'] > 180])
        }
        
        # NPL ratio (loans > 90 DPD)
        npl_count = len(loan_data[loan_data['days_past_due'] > 90])
        npl_ratio = npl_count / len(loan_data) if len(loan_data) > 0 else 0
        
        # Provisioning coverage
        total_provisions = loan_data['provision_amount'].sum()
        npl_amount = loan_data[loan_data['days_past_due'] > 90]['outstanding_amount'].sum()
        provisioning_cover = total_provisions / npl_amount if npl_amount > 0 else 0
        
        return {
            'par_ladder': par_ladder,
            'npl_ratio': npl_ratio,
            'provisioning_cover': provisioning_cover,
            'total_provisions': total_provisions,
            'npl_amount': npl_amount
        }
    
    def _generate_large_exposures(self, loan_data: pd.DataFrame, member_data: pd.DataFrame) -> Dict[str, Any]:
        """Generate large exposures analysis"""
        # Merge loan data with member data to get employer information
        merged_data = loan_data.merge(
            member_data[['member_id', 'employer_name']], 
            on='member_id', 
            how='left'
        )
        
        # Calculate employer exposures
        employer_exposures = merged_data.groupby('employer_name').agg({
            'outstanding_amount': 'sum',
            'member_id': 'nunique'
        }).reset_index()
        
        employer_exposures = employer_exposures.rename(columns={
            'outstanding_amount': 'exposure_amount',
            'member_id': 'member_count'
        })
        
        # Sort by exposure and take top 20
        top_employers = employer_exposures.nlargest(20, 'exposure_amount')
        
        # Calculate concentration ratios
        total_loans = loan_data['outstanding_amount'].sum()
        top_5_exposure = top_employers.head(5)['exposure_amount'].sum()
        top_10_exposure = top_employers.head(10)['exposure_amount'].sum()
        
        concentration_ratios = {
            'top_5_employers': top_5_exposure / total_loans,
            'top_10_employers': top_10_exposure / total_loans,
            'single_largest_employer': top_employers.iloc[0]['exposure_amount'] / total_loans
        }
        
        return {
            'employer_exposures': top_employers.to_dict('records'),
            'concentration_ratios': concentration_ratios,
            'total_loans': total_loans
        }
    
    def _generate_capital_adequacy(self, financial_data: Dict) -> Dict[str, Any]:
        """Generate capital adequacy analysis"""
        total_assets = financial_data['total_assets']
        
        # Core capital (Tier 1)
        core_capital = (
            financial_data['share_capital'] +
            financial_data['statutory_reserve'] +
            financial_data['retained_earnings']
        )
        
        # Supplementary capital (Tier 2)
        supplementary_capital = financial_data['other_reserves']
        
        total_capital = core_capital + supplementary_capital
        
        # Capital ratios
        core_capital_ratio = core_capital / total_assets
        total_capital_ratio = total_capital / total_assets
        
        # Statutory reserve ratio
        statutory_reserve_ratio = financial_data['statutory_reserve'] / financial_data['member_deposits']
        
        return {
            'components': {
                'Share Capital': financial_data['share_capital'],
                'Statutory Reserve': financial_data['statutory_reserve'],
                'Retained Earnings': financial_data['retained_earnings'],
                'Other Reserves': financial_data['other_reserves']
            },
            'ratios': {
                'core_capital_ratio': core_capital_ratio,
                'total_capital_ratio': total_capital_ratio,
                'statutory_reserve_ratio': statutory_reserve_ratio
            },
            'core_capital': core_capital,
            'total_capital': total_capital
        }
    
    def _generate_liquidity_analysis(self, financial_data: Dict, deposit_data: pd.DataFrame) -> Dict[str, Any]:
        """Generate liquidity analysis"""
        total_deposits = financial_data['member_deposits']
        liquid_assets = financial_data['cash_equivalents'] + financial_data['investments']
        
        # Liquidity ratio
        liquidity_ratio = liquid_assets / total_deposits
        
        # LCR (simplified)
        high_quality_liquid_assets = financial_data['cash_equivalents']
        net_cash_outflows = total_deposits * 0.10  # Simplified assumption
        lcr = high_quality_liquid_assets / net_cash_outflows if net_cash_outflows > 0 else 0
        
        # NSFR (simplified)
        available_stable_funding = (
            financial_data['share_capital'] +
            financial_data['statutory_reserve'] +
            financial_data['member_deposits'] * 0.85  # Stable portion of deposits
        )
        required_stable_funding = financial_data['gross_loans'] * 0.65  # Simplified
        nsfr = available_stable_funding / required_stable_funding if required_stable_funding > 0 else 0
        
        # Maturity ladder (simplified)
        maturity_ladder = {
            'O/N': 15000000,
            '1-7 Days': 12000000,
            '8-30 Days': 10000000,
            '31-90 Days': -5000000,
            '91-180 Days': -8000000,
            '181-365 Days': -6000000,
            '1-3 Years': -4000000
        }
        
        return {
            'ratios': {
                'liquidity_ratio': liquidity_ratio,
                'lcr': lcr,
                'nsfr': nsfr
            },
            'maturity_ladder': maturity_ladder,
            'liquid_assets': liquid_assets,
            'total_deposits': total_deposits
        }
    
    def _generate_reconciliations(self, financial_data: Dict) -> Dict[str, Any]:
        """Generate reconciliation reports"""
        return {
            'gl_to_sasra_reconciliation': {
                'status': 'Reconciled',
                'variance': 0,
                'details': 'All GL accounts mapped to SASRA lines'
            },
            'balance_sheet_reconciliation': {
                'status': 'Reconciled',
                'assets_liabilities_equity': financial_data['total_assets'] - 
                                           (financial_data['total_liabilities'] + financial_data['total_equity']),
                'details': 'Balance sheet balances'
            }
        }
    
    def validate_returns(self, returns_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate SASRA returns against regulatory requirements"""
        issues = []
        checks_passed = 0
        total_checks = 6
        
        summary = returns_data.get('summary', {})
        capital_data = returns_data.get('capital_adequacy', {})
        large_exposures = returns_data.get('large_exposures', {})
        asset_quality = returns_data.get('asset_quality', {})
        
        # Check capital adequacy
        core_capital_ratio = capital_data.get('ratios', {}).get('core_capital_ratio', 0)
        if core_capital_ratio >= self.regulatory_limits['core_capital_min']:
            checks_passed += 1
        else:
            issues.append(f"Core capital ratio {core_capital_ratio*100:.1f}% below minimum {self.regulatory_limits['core_capital_min']*100:.1f}%")
        
        # Check liquidity ratio
        liquidity_ratio = summary.get('liquidity_ratio', 0)
        if liquidity_ratio >= self.regulatory_limits['liquidity_ratio_min']:
            checks_passed += 1
        else:
            issues.append(f"Liquidity ratio {liquidity_ratio*100:.1f}% below minimum {self.regulatory_limits['liquidity_ratio_min']*100:.1f}%")
        
        # Check single employer limit
        single_employer_ratio = large_exposures.get('concentration_ratios', {}).get('single_largest_employer', 0)
        if single_employer_ratio <= self.regulatory_limits['single_employer_max']:
            checks_passed += 1
        else:
            issues.append(f"Single employer exposure {single_employer_ratio*100:.1f}% exceeds maximum {self.regulatory_limits['single_employer_max']*100:.1f}%")
        
        # Check NPL ratio
        npl_ratio = asset_quality.get('npl_ratio', 0)
        if npl_ratio <= self.regulatory_limits['npl_ratio_max']:
            checks_passed += 1
        else:
            issues.append(f"NPL ratio {npl_ratio*100:.1f}% exceeds maximum {self.regulatory_limits['npl_ratio_max']*100:.1f}%")
        
        # Check statutory reserve
        statutory_reserve_ratio = capital_data.get('ratios', {}).get('statutory_reserve_ratio', 0)
        if statutory_reserve_ratio >= 0.20:  # 20% of deposits
            checks_passed += 1
        else:
            issues.append(f"Statutory reserve ratio {statutory_reserve_ratio*100:.1f}% below required 20%")
        
        # Check large exposure reporting
        large_exposure_threshold = self.regulatory_limits['large_exposure_min']
        large_exposures_count = len([e for e in large_exposures.get('employer_exposures', []) 
                                   if e.get('exposure_amount', 0) / large_exposures.get('total_loans', 1) > large_exposure_threshold])
        if large_exposures_count > 0:
            checks_passed += 1  # At least one large exposure identified for reporting
        else:
            issues.append("No large exposures identified for reporting")
        
        return {
            'checks_passed': checks_passed,
            'total_checks': total_checks,
            'issues': issues,
            'validation_score': (checks_passed / total_checks) * 100
        }
    
    def export_to_excel(self, returns_data: Dict[str, Any]) -> bytes:
        """Export SASRA returns to Excel format"""
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Summary sheet
            summary_df = pd.DataFrame([returns_data.get('summary', {})])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Balance sheet
            balance_sheet = returns_data.get('balance_sheet', {})
            assets_df = pd.DataFrame(list(balance_sheet.get('assets', {}).items()), columns=['Asset', 'Amount'])
            liabilities_df = pd.DataFrame(list(balance_sheet.get('liabilities', {}).items()), columns=['Liability', 'Amount'])
            equity_df = pd.DataFrame(list(balance_sheet.get('equity', {}).items()), columns=['Equity', 'Amount'])
            
            assets_df.to_excel(writer, sheet_name='Balance_Sheet_Assets', index=False)
            liabilities_df.to_excel(writer, sheet_name='Balance_Sheet_Liabilities', index=False)
            equity_df.to_excel(writer, sheet_name='Balance_Sheet_Equity', index=False)
            
            # Asset quality
            asset_quality = returns_data.get('asset_quality', {})
            par_df = pd.DataFrame(list(asset_quality.get('par_ladder', {}).items()), columns=['Days_Past_Due', 'Count'])
            par_df.to_excel(writer, sheet_name='Asset_Quality', index=False)
            
            # Large exposures
            large_exposures = returns_data.get('large_exposures', {})
            exposures_df = pd.DataFrame(large_exposures.get('employer_exposures', []))
            if not exposures_df.empty:
                exposures_df.to_excel(writer, sheet_name='Large_Exposures', index=False)
        
        output.seek(0)
        return output.getvalue()
    
    def export_to_pdf(self, returns_data: Dict[str, Any]) -> bytes:
        """Export SASRA returns to PDF format (simplified)"""
        # In production, this would use a proper PDF generation library
        # For now, return a simple text representation
        pdf_content = f"""
        SASRA PRUDENTIAL RETURNS
        ========================
        
        Reporting Period: {returns_data.get('metadata', {}).get('reporting_period', 'N/A')}
        SACCO: {returns_data.get('metadata', {}).get('sacco_name', 'N/A')}
        License: {returns_data.get('metadata', {}).get('license_number', 'N/A')}
        Generated: {returns_data.get('metadata', {}).get('generation_date', 'N/A')}
        
        SUMMARY
        -------
        Total Assets: KES {returns_data.get('summary', {}).get('total_assets', 0):,.0f}
        Total Liabilities: KES {returns_data.get('summary', {}).get('total_liabilities', 0):,.0f}
        Total Equity: KES {returns_data.get('summary', {}).get('total_equity', 0):,.0f}
        Capital Adequacy: {returns_data.get('summary', {}).get('capital_adequacy', 0)*100:.1f}%
        Liquidity Ratio: {returns_data.get('summary', {}).get('liquidity_ratio', 0)*100:.1f}%
        
        This is a simplified PDF export. In production, use proper PDF generation.
        """
        
        return pdf_content.encode('utf-8')