"""Market data API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from app.core.database import get_session
from app.models.instrument import Instrument
from app.models.candle import Candle
from app.schemas.market import (
    InstrumentResponse,
    CandleResponse,
    CandlesResponse,
)

router = APIRouter()


@router.get("/instruments", response_model=List[InstrumentResponse])
async def get_instruments(
    symbol: Optional[str] = Query(default=None, description="Filter by symbol"),
    instrument_type: Optional[str] = Query(default=None, description="Filter by type (crypto, forex, futures)"),
    is_active: bool = Query(default=True, description="Filter by active status"),
    session: AsyncSession = Depends(get_session),
):
    """
    Get list of all trading instruments (symbols).
    
    - Returns all available instruments
    - Optional filtering by symbol, type, or status
    - Used to populate symbol dropdowns
    """
    query = select(Instrument).where(Instrument.is_active == is_active)
    
    if symbol:
        query = query.where(Instrument.symbol == symbol.upper())
    
    if instrument_type:
        query = query.where(Instrument.instrument_type == instrument_type.lower())
    
    result = await session.execute(query)
    instruments = result.scalars().all()
    
    return instruments


@router.get("/instruments/{symbol}", response_model=InstrumentResponse)
async def get_instrument_by_symbol(
    symbol: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Get instrument details by symbol.
    
    - Returns instrument configuration
    - Used to get tick size, spreads, min size, etc.
    """
    result = await session.execute(
        select(Instrument).where(Instrument.symbol == symbol.upper())
    )
    instrument = result.scalar_one_or_none()
    
    if not instrument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrument '{symbol}' not found",
        )
    
    return instrument


@router.get("/{symbol}/candles", response_model=CandlesResponse)
async def get_candles(
    symbol: str,
    timeframe: str = Query(default="1m", description="Timeframe (1m, 5m, 15m, 1h, 4h, 1d)"),
    from_time: Optional[datetime] = Query(default=None, description="Start time (UTC)"),
    to_time: Optional[datetime] = Query(default=None, description="End time (UTC)"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum candles to return"),
    session: AsyncSession = Depends(get_session),
):
    """
    Get candlestick (OHLCV) data for charting.
    
    - Returns historical price data
    - Supports multiple timeframes
    - Paginated results (max 1000 per request)
    """
    # Get instrument
    result = await session.execute(
        select(Instrument).where(Instrument.symbol == symbol.upper())
    )
    instrument = result.scalar_one_or_none()
    
    if not instrument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrument '{symbol}' not found",
        )
    
    # Build candles query
    query = select(Candle).where(
        Candle.instrument_id == instrument.id,
        Candle.timeframe == timeframe,
    )
    
    if from_time:
        query = query.where(Candle.timestamp >= from_time)
    
    if to_time:
        query = query.where(Candle.timestamp <= to_time)
    
    # Order by timestamp descending (newest first)
    query = query.order_by(Candle.timestamp.desc()).limit(limit)
    
    result = await session.execute(query)
    candles = result.scalars().all()
    
    # Count total available candles (for pagination info)
    count_query = select(Candle).where(
        Candle.instrument_id == instrument.id,
        Candle.timeframe == timeframe,
    )
    if from_time:
        count_query = count_query.where(Candle.timestamp >= from_time)
    if to_time:
        count_query = count_query.where(Candle.timestamp <= to_time)
    
    from sqlalchemy import func
    count_result = await session.execute(
        select(func.count()).select_from(count_query.subquery())
    )
    total = count_result.scalar() or 0
    
    # Reverse to get chronological order
    candles_list = list(reversed(candles))
    
    return CandlesResponse(
        candles=candles_list,
        total=total,
        symbol=symbol.upper(),
        timeframe=timeframe,
    )
