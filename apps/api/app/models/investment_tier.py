from sqlmodel import SQLModel, Field, Column
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import JSON


class InvestmentTier(SQLModel, table=True):
    """Investment tier configuration model."""

    __tablename__ = "investment_tiers"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=50, unique=True, index=True)  # 'basic', 'premium', 'professional', 'investor'
    display_name: str = Field(max_length=100)  # 'Basic', 'Premium', etc.
    minimum_deposit: float = Field(ge=0)
    monthly_return_percentage: float = Field(ge=0, le=100)  # e.g., 25.0 for 25%
    annual_roi_percentage: float = Field(ge=0, le=1000)  # e.g., 300.0 for 300%
    features: dict = Field(default={}, sa_column=Column(JSON))  # JSON field for tier features
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "premium",
                "display_name": "Premium",
                "minimum_deposit": 300.0,
                "monthly_return_percentage": 50.0,
                "annual_roi_percentage": 600.0,
                "features": {
                    "priority_payouts": True,
                    "account_manager": True,
                    "support_level": "priority"
                },
                "is_active": True,
            }
        }
