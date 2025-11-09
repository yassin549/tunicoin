from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime, date
from uuid import UUID


# ==================== Investment Tier Schemas ====================

class InvestmentTierBase(BaseModel):
    name: str
    display_name: str
    minimum_deposit: float
    monthly_return_percentage: float
    annual_roi_percentage: float
    features: Dict = {}
    is_active: bool = True


class InvestmentTierResponse(InvestmentTierBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Investment Account Schemas ====================

class InvestmentAccountCreate(BaseModel):
    tier_id: UUID


class InvestmentAccountResponse(BaseModel):
    id: UUID
    user_id: UUID
    tier_id: UUID
    status: str
    initial_deposit: float
    current_balance: float
    total_returns: float
    total_withdrawn: float
    total_deposited: float
    last_payout_at: Optional[datetime]
    next_payout_at: Optional[datetime]
    opened_at: datetime
    activated_at: Optional[datetime]
    closed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Deposit Schemas ====================

class DepositCreate(BaseModel):
    investment_account_id: UUID
    amount: float = Field(gt=0, description="Deposit amount (must be positive)")
    currency: str = Field(default="USD", description="Currency code (USD, BTC, ETH, etc.)")
    payment_method: str = Field(description="Payment method (crypto, stripe, bank_transfer)")


class DepositResponse(BaseModel):
    id: UUID
    investment_account_id: UUID
    user_id: UUID
    amount: float
    currency: str
    payment_method: str
    transaction_hash: Optional[str]
    payment_provider: Optional[str]
    provider_transaction_id: Optional[str]
    status: str
    confirmed_at: Optional[datetime]
    failed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    admin_notes: Optional[str]

    class Config:
        from_attributes = True


# ==================== Investment Return Schemas ====================

class InvestmentReturnResponse(BaseModel):
    id: UUID
    investment_account_id: UUID
    period_start: date
    period_end: date
    period_type: str
    expected_return: float
    actual_return: float
    return_percentage: float
    balance_before: float
    balance_after: float
    status: str
    credited_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    notes: Optional[str]

    class Config:
        from_attributes = True


# ==================== Payout Schemas ====================

class PayoutRequest(BaseModel):
    investment_account_id: UUID
    amount: float = Field(gt=0, description="Payout amount (must be positive)")
    payout_method: str = Field(description="Payout method (crypto, bank_transfer, stripe)")
    destination: str = Field(description="Destination (wallet address or bank details)")
    currency: str = Field(default="USD", description="Currency code (USD, BTC, ETH, etc.)")


class PayoutResponse(BaseModel):
    id: UUID
    investment_account_id: UUID
    user_id: UUID
    amount: float
    payout_method: str
    destination: str
    currency: str
    status: str
    transaction_hash: Optional[str]
    provider_transaction_id: Optional[str]
    reviewed_by: Optional[UUID]
    admin_notes: Optional[str]
    rejection_reason: Optional[str]
    requested_at: datetime
    approved_at: Optional[datetime]
    processed_at: Optional[datetime]
    completed_at: Optional[datetime]
    rejected_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== KYC Schemas ====================

class KYCSubmissionCreate(BaseModel):
    full_name: str
    date_of_birth: date
    nationality: Optional[str] = None
    id_type: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: Optional[str] = None
    postal_code: str
    country: str
    phone: str
    is_accredited_investor: bool = False


class KYCSubmissionResponse(BaseModel):
    id: UUID
    user_id: UUID
    status: str
    kyc_provider: Optional[str]
    provider_reference_id: Optional[str]
    full_name: str
    date_of_birth: date
    nationality: Optional[str]
    id_type: str
    address_line1: str
    address_line2: Optional[str]
    city: str
    state: Optional[str]
    postal_code: str
    country: str
    phone: str
    is_accredited_investor: bool
    accreditation_proof: Optional[str]
    documents: Dict
    submitted_at: datetime
    reviewed_at: Optional[datetime]
    reviewed_by: Optional[UUID]
    rejection_reason: Optional[str]
    sanctions_check_passed: bool
    sanctions_check_date: Optional[datetime]
    aml_risk_score: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
