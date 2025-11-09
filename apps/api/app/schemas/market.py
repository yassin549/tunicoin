"""Market data schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class InstrumentResponse(BaseModel):
    """Instrument (symbol) response."""
    id: UUID
    symbol: str
    name: str
    instrument_type: str
    tick_size: Decimal
    contract_size: Decimal
    base_currency: str
    quote_currency: str
    base_spread: Decimal
    funding_rate: Optional[Decimal] = None
    slippage_factor: Decimal
    min_size: Decimal
    max_size: Optional[Decimal] = None
    is_active: bool
    is_tradeable: bool
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "symbol": "BTC-USD",
                "name": "Bitcoin / US Dollar",
                "instrument_type": "crypto",
                "tick_size": 0.01,
                "contract_size": 1.0,
                "base_currency": "BTC",
                "quote_currency": "USD",
                "base_spread": 0.001,
                "funding_rate": 0.0001,
                "slippage_factor": 0.0001,
                "min_size": 0.001,
                "max_size": None,
                "is_active": True,
                "is_tradeable": True
            }
        }


class CandleResponse(BaseModel):
    """Candlestick data response."""
    id: UUID
    instrument_id: UUID
    timeframe: str
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "instrument_id": "456e4567-e89b-12d3-a456-426614174000",
                "timeframe": "1m",
                "timestamp": "2024-01-15T12:30:00Z",
                "open": 50000.00,
                "high": 50100.00,
                "low": 49900.00,
                "close": 50050.00,
                "volume": 125.5
            }
        }


class CandlesRequest(BaseModel):
    """Request parameters for fetching candles."""
    symbol: str = Field(..., description="Instrument symbol (e.g., BTC-USD)")
    timeframe: str = Field(default="1m", description="Timeframe (1m, 5m, 15m, 1h, 4h, 1d)")
    from_time: Optional[datetime] = Field(default=None, description="Start time (UTC)")
    to_time: Optional[datetime] = Field(default=None, description="End time (UTC)")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of candles")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "BTC-USD",
                "timeframe": "1m",
                "from_time": "2024-01-01T00:00:00Z",
                "to_time": "2024-01-02T00:00:00Z",
                "limit": 100
            }
        }


class CandlesResponse(BaseModel):
    """Paginated candles response."""
    candles: List[CandleResponse]
    total: int
    symbol: str
    timeframe: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "candles": [],
                "total": 1440,
                "symbol": "BTC-USD",
                "timeframe": "1m"
            }
        }
