# sacco_core/schemas/data_schemas.py
from pydantic import BaseModel, validator
from datetime import datetime, date
from typing import Optional, Literal
from decimal import Decimal

class LoanStateMonthly(BaseModel):
    loan_id: str
    member_id: str
    employer_id: str
    product: str
    origination_date: date
    month_end: date
    state: Literal['current', 'dpd1_30', 'dpd31_60', 'dpd61_90', 'dpd91_180', 'dpd180_plus', 'closed', 'written_off']
    os_principal: float
    days_past_due: int
    recoveries_cash: float
    interest_accrued: float
    charge_off_flag: int
    cure_flag: int
    
    @validator('os_principal', 'recoveries_cash', 'interest_accrued')
    def validate_non_negative(cls, v):
        if v < 0:
            raise ValueError('Value must be non-negative')
        return v
    
    @validator('charge_off_flag', 'cure_flag')
    def validate_binary(cls, v):
        if v not in [0, 1]:
            raise ValueError('Must be 0 or 1')
        return v

class Member(BaseModel):
    member_id: str
    join_date: date
    deposits_balance: float
    shares_balance: float
    channel: str
    employer_id: str
    phone: str
    email: str

class Employer(BaseModel):
    employer_id: str
    employer_name: str
    active_members: int