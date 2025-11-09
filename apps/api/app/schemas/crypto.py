"""Crypto payment schemas."""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class CreateDepositRequest(BaseModel):
    """Request to create a crypto deposit."""
    account_id: UUID = Field(..., description="Account to deposit into")
    usd_amount: float = Field(..., gt=0, description="Amount in USD to deposit")
    pay_currency: Optional[str] = Field(default=None, description="Crypto currency to pay with (e.g., 'btc', 'eth')")
    
    @validator('usd_amount')
    def validate_minimum(cls, v):
        from app.core.config import settings
        if v < settings.MIN_DEPOSIT_USD:
            raise ValueError(f'Minimum deposit is ${settings.MIN_DEPOSIT_USD}')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "account_id": "123e4567-e89b-12d3-a456-426614174000",
                "usd_amount": 100.00,
                "pay_currency": "btc"
            }
        }


class DepositResponse(BaseModel):
    """Deposit creation response."""
    transaction_id: UUID
    payment_id: Optional[str] = None
    invoice_id: Optional[str] = None
    payment_url: str
    crypto_currency: str
    crypto_amount: Optional[Decimal] = None
    usd_amount: Decimal
    pay_address: Optional[str] = None
    status: str
    expires_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
                "payment_id": "12345678",
                "invoice_id": "INV-123",
                "payment_url": "https://nowpayments.io/payment/?iid=...",
                "crypto_currency": "btc",
                "crypto_amount": 0.002,
                "usd_amount": 100.00,
                "pay_address": "bc1q...",
                "status": "pending",
                "expires_at": "2024-01-15T13:00:00Z"
            }
        }


class CreateWithdrawalRequest(BaseModel):
    """Request to create a crypto withdrawal."""
    account_id: UUID = Field(..., description="Account to withdraw from")
    usd_amount: float = Field(..., gt=0, description="Amount in USD to withdraw")
    crypto_currency: str = Field(..., description="Crypto currency to receive (e.g., 'btc', 'eth')")
    recipient_address: str = Field(..., min_length=10, description="Crypto address to send to")
    extra_id: Optional[str] = Field(default=None, description="Memo/tag for certain currencies (XRP, XLM, etc.)")
    
    @validator('usd_amount')
    def validate_minimum(cls, v):
        from app.core.config import settings
        if v < settings.MIN_WITHDRAWAL_USD:
            raise ValueError(f'Minimum withdrawal is ${settings.MIN_WITHDRAWAL_USD}')
        return v
    
    @validator('crypto_currency')
    def validate_currency(cls, v):
        from app.core.config import settings
        if v.lower() not in settings.SUPPORTED_CRYPTO:
            raise ValueError(f'Unsupported currency. Supported: {", ".join(settings.SUPPORTED_CRYPTO)}')
        return v.lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "account_id": "123e4567-e89b-12d3-a456-426614174000",
                "usd_amount": 50.00,
                "crypto_currency": "btc",
                "recipient_address": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
            }
        }


class WithdrawalResponse(BaseModel):
    """Withdrawal creation response."""
    transaction_id: UUID
    payment_id: Optional[str] = None
    crypto_currency: str
    crypto_amount: Decimal
    usd_amount: Decimal
    withdrawal_fee: Decimal
    net_amount: Decimal
    recipient_address: str
    status: str
    estimated_time: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
                "payment_id": "87654321",
                "crypto_currency": "btc",
                "crypto_amount": 0.001,
                "usd_amount": 50.00,
                "withdrawal_fee": 0.50,
                "net_amount": 49.50,
                "recipient_address": "bc1q...",
                "status": "pending",
                "estimated_time": "10-30 minutes"
            }
        }


class CryptoTransactionResponse(BaseModel):
    """Crypto transaction response."""
    id: UUID
    user_id: UUID
    account_id: Optional[UUID] = None
    transaction_type: str
    crypto_currency: str
    crypto_amount: Decimal
    usd_amount: Decimal
    status: str
    payment_id: Optional[str] = None
    txn_hash: Optional[str] = None
    confirmations: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "456e4567-e89b-12d3-a456-426614174000",
                "account_id": "789e4567-e89b-12d3-a456-426614174000",
                "transaction_type": "deposit",
                "crypto_currency": "btc",
                "crypto_amount": 0.002,
                "usd_amount": 100.00,
                "status": "completed",
                "payment_id": "12345678",
                "txn_hash": "abc123...",
                "confirmations": 3,
                "created_at": "2024-01-15T12:00:00Z",
                "completed_at": "2024-01-15T12:30:00Z"
            }
        }


class AvailableCurrenciesResponse(BaseModel):
    """Available cryptocurrencies response."""
    currencies: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "currencies": ["btc", "eth", "usdt", "usdc", "ltc", "trx", "bnb"]
            }
        }


class CryptoEstimateRequest(BaseModel):
    """Request for crypto amount estimate."""
    usd_amount: float = Field(..., gt=0, description="Amount in USD")
    crypto_currency: str = Field(..., description="Crypto currency to convert to")
    
    class Config:
        json_schema_extra = {
            "example": {
                "usd_amount": 100.00,
                "crypto_currency": "btc"
            }
        }


class CryptoEstimateResponse(BaseModel):
    """Crypto amount estimate response."""
    usd_amount: float
    crypto_currency: str
    crypto_amount: float
    exchange_rate: float
    minimum_amount: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "usd_amount": 100.00,
                "crypto_currency": "btc",
                "crypto_amount": 0.002,
                "exchange_rate": 50000.00,
                "minimum_amount": 10.00
            }
        }
