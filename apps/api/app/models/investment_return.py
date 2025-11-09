from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, date
from uuid import UUID, uuid4


class InvestmentReturn(SQLModel, table=True):
    """Investment return tracking model."""

    __tablename__ = "investment_returns"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    investment_account_id: UUID = Field(foreign_key="investment_accounts.id", index=True)
    
    # Period tracking
    period_start: date = Field(index=True)
    period_end: date = Field(index=True)
    period_type: str = Field(max_length=20, default="daily")  # daily, monthly, annual
    
    # Return calculations
    expected_return: float = Field(default=0.0)
    actual_return: float = Field(default=0.0, ge=0)
    return_percentage: float = Field(default=0.0)
    
    # Balance tracking
    balance_before: float = Field(default=0.0, ge=0)
    balance_after: float = Field(default=0.0, ge=0)
    
    # Status
    status: str = Field(max_length=20, default="projected")  # projected, accrued, paid
    
    # Timestamps
    credited_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Notes
    notes: Optional[str] = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "investment_account_id": "123e4567-e89b-12d3-a456-426614174000",
                "period_start": "2025-11-01",
                "period_end": "2025-11-30",
                "period_type": "monthly",
                "actual_return": 500.0,
                "return_percentage": 50.0,
                "balance_before": 1000.0,
                "balance_after": 1500.0,
                "status": "accrued",
            }
        }
