from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4


class Payout(SQLModel, table=True):
    """Payout/withdrawal request model."""

    __tablename__ = "payouts"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    investment_account_id: UUID = Field(foreign_key="investment_accounts.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    
    # Payout details
    amount: float = Field(ge=0)
    payout_method: str = Field(max_length=50)  # 'crypto', 'bank_transfer', 'stripe'
    destination: str = Field(max_length=500)  # Wallet address, bank account, etc.
    currency: str = Field(max_length=10, default="USD")  # USD, BTC, ETH, etc.
    
    # Processing details
    status: str = Field(max_length=20, default="pending")  # pending, approved, processing, completed, rejected, failed
    transaction_hash: Optional[str] = Field(default=None, max_length=255)  # For crypto payouts
    provider_transaction_id: Optional[str] = Field(default=None, max_length=255)
    
    # Admin management
    reviewed_by: Optional[UUID] = Field(default=None, foreign_key="users.id")
    admin_notes: Optional[str] = Field(default=None)
    rejection_reason: Optional[str] = Field(default=None)
    
    # Timestamps
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = Field(default=None)
    processed_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    rejected_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "investment_account_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "amount": 250.0,
                "payout_method": "crypto",
                "destination": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "currency": "USDT",
                "status": "pending",
            }
        }
