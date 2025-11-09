"""Account schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class CreateAccountRequest(BaseModel):
    """Request to create a new simulated account."""
    name: str = Field(..., min_length=1, max_length=255, description="Account name")
    base_currency: str = Field(default="USD", max_length=10, description="Base currency")
    initial_balance: Optional[Decimal] = Field(default=Decimal("10000.00"), description="Initial balance")
    is_demo: bool = Field(default=True, description="Is this a demo account")
    max_leverage: int = Field(default=10, ge=1, le=100, description="Maximum leverage")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "My Trading Account",
                "base_currency": "USD",
                "initial_balance": 10000.00,
                "is_demo": True,
                "max_leverage": 10
            }
        }


class AccountResponse(BaseModel):
    """Account response."""
    id: UUID
    user_id: UUID
    name: str
    base_currency: str
    balance: Decimal
    equity: Decimal
    margin_used: Decimal
    margin_available: Decimal
    is_demo: bool
    is_active: bool
    max_leverage: int
    max_daily_loss: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "456e4567-e89b-12d3-a456-426614174000",
                "name": "Demo Account",
                "base_currency": "USD",
                "balance": 10000.00,
                "equity": 10250.00,
                "margin_used": 2000.00,
                "margin_available": 8250.00,
                "is_demo": True,
                "is_active": True,
                "max_leverage": 10,
                "max_daily_loss": None,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T12:30:00Z"
            }
        }


class AccountSummary(BaseModel):
    """Brief account summary."""
    id: UUID
    name: str
    balance: Decimal
    equity: Decimal
    is_demo: bool
    
    class Config:
        from_attributes = True
