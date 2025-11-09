from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4


class Deposit(SQLModel, table=True):
    """Deposit transaction model."""

    __tablename__ = "deposits"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    investment_account_id: UUID = Field(foreign_key="investment_accounts.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    
    # Transaction details
    amount: float = Field(ge=0)
    currency: str = Field(max_length=10, default="USD")  # USD, BTC, ETH, USDT, etc.
    payment_method: str = Field(max_length=50)  # 'crypto', 'stripe', 'bank_transfer'
    
    # Payment provider details
    transaction_hash: Optional[str] = Field(default=None, max_length=255)  # Blockchain tx hash or payment ID
    payment_provider: Optional[str] = Field(default=None, max_length=50)  # 'stripe', 'nowpayments', 'bank'
    provider_transaction_id: Optional[str] = Field(default=None, max_length=255)
    
    # Status tracking
    status: str = Field(max_length=20, default="pending")  # pending, confirmed, failed, cancelled
    
    # Timestamps
    confirmed_at: Optional[datetime] = Field(default=None)
    failed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Admin notes
    admin_notes: Optional[str] = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "investment_account_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "amount": 500.0,
                "currency": "USD",
                "payment_method": "stripe",
                "status": "confirmed",
            }
        }
