"""Crypto transaction model for deposits and withdrawals."""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class CryptoTransaction(SQLModel, table=True):
    """
    Tracks cryptocurrency deposits and withdrawals via NOWPayments.
    
    This model stores all crypto payment transactions including:
    - User deposits (crypto -> account balance)
    - User withdrawals (account balance -> crypto)
    - Transaction status tracking
    - NOWPayments payment IDs
    """
    
    __tablename__ = "crypto_transactions"
    
    # Primary Key
    id: UUID = Field(primary_key=True)
    
    # Foreign Keys
    user_id: UUID = Field(foreign_key="users.id", index=True)
    account_id: Optional[UUID] = Field(default=None, foreign_key="accounts.id", index=True)
    
    # Transaction Type
    transaction_type: str = Field(max_length=20, index=True)  # 'deposit' or 'withdrawal'
    
    # Crypto Details
    crypto_currency: str = Field(max_length=10)  # btc, eth, usdt, etc.
    crypto_amount: Decimal = Field(max_digits=18, decimal_places=8)  # Amount in crypto
    
    # Fiat Equivalent
    usd_amount: Decimal = Field(max_digits=12, decimal_places=2)  # Amount in USD
    exchange_rate: Optional[Decimal] = Field(default=None, max_digits=18, decimal_places=8)  # Crypto/USD rate
    
    # Status
    status: str = Field(max_length=50, default="pending", index=True)
    # Status values: pending, confirming, confirmed, completed, failed, expired, refunded
    
    # NOWPayments Data
    payment_id: Optional[str] = Field(default=None, max_length=255, index=True)  # NOWPayments payment ID
    invoice_id: Optional[str] = Field(default=None, max_length=255)  # NOWPayments invoice ID
    payment_url: Optional[str] = Field(default=None, max_length=512)  # Payment page URL
    
    # Blockchain Data
    txn_hash: Optional[str] = Field(default=None, max_length=255)  # Blockchain transaction hash
    blockchain_network: Optional[str] = Field(default=None, max_length=50)  # Network (e.g., Bitcoin, Ethereum)
    confirmations: int = Field(default=0)  # Number of blockchain confirmations
    
    # Withdrawal Specific
    recipient_address: Optional[str] = Field(default=None, max_length=255)  # Crypto address for withdrawals
    withdrawal_fee: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=2)  # Fee in USD
    
    # Metadata
    notes: Optional[str] = Field(default=None, max_length=500)
    error_message: Optional[str] = Field(default=None, max_length=500)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    confirmed_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "456e4567-e89b-12d3-a456-426614174000",
                "account_id": "789e4567-e89b-12d3-a456-426614174000",
                "transaction_type": "deposit",
                "crypto_currency": "btc",
                "crypto_amount": 0.001,
                "usd_amount": 50.00,
                "exchange_rate": 50000.00,
                "status": "completed",
                "payment_id": "12345678",
                "txn_hash": "abc123...",
                "blockchain_network": "Bitcoin",
                "confirmations": 3,
                "created_at": "2024-01-15T12:00:00Z",
                "completed_at": "2024-01-15T12:30:00Z"
            }
        }
