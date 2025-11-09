from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4


class InvestmentAccount(SQLModel, table=True):
    """User investment account model."""

    __tablename__ = "investment_accounts"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    tier_id: UUID = Field(foreign_key="investment_tiers.id", index=True)
    
    # Account status
    status: str = Field(max_length=20, default="pending_kyc")  # pending_kyc, active, suspended, closed
    
    # Financial tracking
    initial_deposit: float = Field(default=0.0, ge=0)
    current_balance: float = Field(default=0.0, ge=0)
    total_returns: float = Field(default=0.0, ge=0)
    total_withdrawn: float = Field(default=0.0, ge=0)
    total_deposited: float = Field(default=0.0, ge=0)
    
    # Payout tracking
    last_payout_at: Optional[datetime] = Field(default=None)
    next_payout_at: Optional[datetime] = Field(default=None)
    
    # Timestamps
    opened_at: datetime = Field(default_factory=datetime.utcnow)
    activated_at: Optional[datetime] = Field(default=None)
    closed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "tier_id": "123e4567-e89b-12d3-a456-426614174001",
                "status": "active",
                "initial_deposit": 1000.0,
                "current_balance": 1250.0,
                "total_returns": 250.0,
            }
        }
