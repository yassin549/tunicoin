"""Order schemas."""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from enum import Enum


class OrderType(str, Enum):
    """Order type enumeration."""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TAKE_PROFIT = "take_profit"
    TRAILING_STOP = "trailing_stop"


class OrderSide(str, Enum):
    """Order side enumeration."""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "pending"
    FILLED = "filled"
    PARTIAL = "partial"
    CANCELED = "canceled"
    REJECTED = "rejected"


class CreateOrderRequest(BaseModel):
    """Request to create a new order."""
    instrument_id: UUID = Field(..., description="Instrument ID to trade")
    order_type: OrderType = Field(..., description="Order type")
    side: OrderSide = Field(..., description="Buy or sell")
    size: Decimal = Field(..., gt=0, description="Order size")
    price: Optional[Decimal] = Field(default=None, description="Limit price (required for limit orders)")
    stop_price: Optional[Decimal] = Field(default=None, description="Stop price (for stop orders)")
    leverage: int = Field(default=1, ge=1, le=100, description="Leverage multiplier")
    
    @validator('price')
    def validate_price(cls, v, values):
        """Validate price is provided for limit orders."""
        order_type = values.get('order_type')
        if order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT] and v is None:
            raise ValueError(f'Price is required for {order_type} orders')
        return v
    
    @validator('stop_price')
    def validate_stop_price(cls, v, values):
        """Validate stop_price is provided for stop orders."""
        order_type = values.get('order_type')
        if order_type in [OrderType.STOP, OrderType.STOP_LIMIT] and v is None:
            raise ValueError(f'Stop price is required for {order_type} orders')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "instrument_id": "123e4567-e89b-12d3-a456-426614174000",
                "order_type": "market",
                "side": "buy",
                "size": 0.5,
                "price": None,
                "stop_price": None,
                "leverage": 1
            }
        }


class OrderResponse(BaseModel):
    """Order response."""
    id: UUID
    account_id: UUID
    instrument_id: UUID
    order_type: str
    side: str
    size: Decimal
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    status: str
    filled_size: Decimal
    fill_price: Optional[Decimal] = None
    slippage: Optional[Decimal] = None
    commission: Decimal
    leverage: int
    margin_required: Decimal
    bot_id: Optional[UUID] = None
    created_at: datetime
    filled_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "account_id": "456e4567-e89b-12d3-a456-426614174000",
                "instrument_id": "789e4567-e89b-12d3-a456-426614174000",
                "order_type": "market",
                "side": "buy",
                "size": 0.5,
                "price": None,
                "stop_price": None,
                "status": "filled",
                "filled_size": 0.5,
                "fill_price": 50000.00,
                "slippage": 0.0002,
                "commission": 5.00,
                "leverage": 1,
                "margin_required": 25000.00,
                "bot_id": None,
                "created_at": "2024-01-15T12:30:00Z",
                "filled_at": "2024-01-15T12:30:01Z",
                "canceled_at": None
            }
        }


class CancelOrderRequest(BaseModel):
    """Request to cancel an order."""
    order_id: UUID = Field(..., description="Order ID to cancel")
    
    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
