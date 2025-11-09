"""Position schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class PositionResponse(BaseModel):
    """Position response."""
    id: UUID
    account_id: UUID
    instrument_id: UUID
    side: str
    size: Decimal
    entry_price: Decimal
    current_price: Optional[Decimal] = None
    unrealized_pnl: Decimal
    realized_pnl: Decimal
    leverage: int
    margin_used: Decimal
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    funding_paid: Decimal
    last_funding_at: Optional[datetime] = None
    is_open: bool
    bot_id: Optional[UUID] = None
    opened_at: datetime
    closed_at: Optional[datetime] = None
    updated_at: datetime
    
    # Computed fields
    pnl_percentage: Optional[float] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "account_id": "456e4567-e89b-12d3-a456-426614174000",
                "instrument_id": "789e4567-e89b-12d3-a456-426614174000",
                "side": "long",
                "size": 0.5,
                "entry_price": 50000.00,
                "current_price": 50500.00,
                "unrealized_pnl": 250.00,
                "realized_pnl": 0.00,
                "leverage": 10,
                "margin_used": 2500.00,
                "stop_loss": 49000.00,
                "take_profit": 52000.00,
                "funding_paid": 0.50,
                "last_funding_at": "2024-01-15T00:00:00Z",
                "is_open": True,
                "bot_id": None,
                "opened_at": "2024-01-15T12:30:00Z",
                "closed_at": None,
                "updated_at": "2024-01-15T13:00:00Z",
                "pnl_percentage": 1.0
            }
        }


class ClosePositionRequest(BaseModel):
    """Request to close a position."""
    position_id: UUID = Field(..., description="Position ID to close")
    size: Optional[Decimal] = Field(default=None, description="Partial close size (None = close all)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "position_id": "123e4567-e89b-12d3-a456-426614174000",
                "size": None
            }
        }


class UpdatePositionRequest(BaseModel):
    """Request to update position stop loss / take profit."""
    position_id: UUID = Field(..., description="Position ID")
    stop_loss: Optional[Decimal] = Field(default=None, description="Stop loss price")
    take_profit: Optional[Decimal] = Field(default=None, description="Take profit price")
    
    class Config:
        json_schema_extra = {
            "example": {
                "position_id": "123e4567-e89b-12d3-a456-426614174000",
                "stop_loss": 49000.00,
                "take_profit": 52000.00
            }
        }
