"""Position management API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from app.core.database import get_session
from app.core.deps import get_current_user
from app.models.user import User
from app.models.account import Account
from app.models.position import Position
from app.schemas.position import (
    PositionResponse,
    ClosePositionRequest,
    UpdatePositionRequest,
)
from app.schemas.auth import MessageResponse
from app.services.pnl import PnLCalculator

router = APIRouter()


@router.get("/{account_id}/positions", response_model=List[PositionResponse])
async def get_positions(
    account_id: str,
    is_open: Optional[bool] = Query(default=True, description="Filter by open status"),
    limit: int = Query(default=50, ge=1, le=200, description="Maximum positions to return"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get positions for an account.
    
    - Returns list of positions
    - Default: only open positions
    - Set is_open=null to get all positions
    """
    # Validate account
    try:
        account_uuid = UUID(account_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid account ID format",
        )
    
    result = await session.execute(
        select(Account).where(
            Account.id == account_uuid,
            Account.user_id == current_user.id,
        )
    )
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )
    
    # Build query
    query = select(Position).where(Position.account_id == account.id)
    
    if is_open is not None:
        query = query.where(Position.is_open == is_open)
    
    query = query.order_by(Position.opened_at.desc()).limit(limit).offset(offset)
    
    positions_result = await session.execute(query)
    positions = positions_result.scalars().all()
    
    # Update P&L for open positions
    pnl_calculator = PnLCalculator(session)
    for position in positions:
        if position.is_open:
            await pnl_calculator.update_position_pnl(position)
            # Calculate P&L percentage
            position.pnl_percentage = pnl_calculator.calculate_pnl_percentage(position)
    
    await session.commit()
    
    return positions


@router.get("/{account_id}/positions/{position_id}", response_model=PositionResponse)
async def get_position(
    account_id: str,
    position_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get a specific position by ID.
    
    - Returns position details with current P&L
    """
    # Validate IDs
    try:
        account_uuid = UUID(account_id)
        position_uuid = UUID(position_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID format",
        )
    
    # Validate account
    account_result = await session.execute(
        select(Account).where(
            Account.id == account_uuid,
            Account.user_id == current_user.id,
        )
    )
    account = account_result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )
    
    # Get position
    position_result = await session.execute(
        select(Position).where(
            Position.id == position_uuid,
            Position.account_id == account.id,
        )
    )
    position = position_result.scalar_one_or_none()
    
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found",
        )
    
    # Update P&L if open
    if position.is_open:
        pnl_calculator = PnLCalculator(session)
        await pnl_calculator.update_position_pnl(position)
        position.pnl_percentage = pnl_calculator.calculate_pnl_percentage(position)
        await session.commit()
    
    return position


@router.post("/{account_id}/positions/close", response_model=MessageResponse)
async def close_position(
    account_id: str,
    request: ClosePositionRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Close a position (fully or partially).
    
    - Closes position at current market price
    - Updates account balance with realized P&L
    - Creates ledger entries
    """
    # Validate account
    try:
        account_uuid = UUID(account_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid account ID format",
        )
    
    account_result = await session.execute(
        select(Account).where(
            Account.id == account_uuid,
            Account.user_id == current_user.id,
        )
    )
    account = account_result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )
    
    # Get position
    position_result = await session.execute(
        select(Position).where(
            Position.id == request.position_id,
            Position.account_id == account.id,
        )
    )
    position = position_result.scalar_one_or_none()
    
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found",
        )
    
    if not position.is_open:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Position is already closed",
        )
    
    # Update P&L
    pnl_calculator = PnLCalculator(session)
    await pnl_calculator.update_position_pnl(position)
    
    # Determine close size
    close_size = request.size if request.size else position.size
    
    if close_size > position.size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Close size cannot exceed position size",
        )
    
    # Calculate partial P&L
    pnl_ratio = close_size / position.size
    realized_pnl = position.unrealized_pnl * pnl_ratio
    
    # Update account balance
    account.balance += realized_pnl
    account.margin_used -= (position.margin_used * pnl_ratio)
    account.margin_available += (position.margin_used * pnl_ratio)
    account.equity = account.balance + account.margin_used
    account.updated_at = datetime.utcnow()
    session.add(account)
    
    # Create ledger entry
    from app.models.ledger_entry import LedgerEntry
    from uuid import uuid4
    ledger_entry = LedgerEntry(
        id=uuid4(),
        account_id=account.id,
        entry_type="trade_pnl",
        amount=realized_pnl,
        balance_after=account.balance,
        currency=account.base_currency,
        position_id=position.id,
        description=f"P&L from closing position {position.id}",
        meta={
            "entry_price": float(position.entry_price),
            "exit_price": float(position.current_price),
            "size": float(close_size),
            "pnl": float(realized_pnl),
        },
        created_at=datetime.utcnow(),
    )
    session.add(ledger_entry)
    
    # Update or close position
    if close_size >= position.size:
        # Full close
        position.is_open = False
        position.closed_at = datetime.utcnow()
        position.realized_pnl = realized_pnl
        position.unrealized_pnl = 0
        message = f"Position {request.position_id} fully closed with P&L: {float(realized_pnl):.2f}"
    else:
        # Partial close
        position.size -= close_size
        position.margin_used -= (position.margin_used * pnl_ratio)
        position.realized_pnl += realized_pnl
        position.unrealized_pnl -= realized_pnl
        message = f"Position {request.position_id} partially closed ({float(close_size)} size) with P&L: {float(realized_pnl):.2f}"
    
    position.updated_at = datetime.utcnow()
    session.add(position)
    
    await session.commit()
    
    return MessageResponse(message=message)


@router.patch("/{account_id}/positions/{position_id}", response_model=PositionResponse)
async def update_position(
    account_id: str,
    position_id: str,
    request: UpdatePositionRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Update position stop loss / take profit.
    
    - Modifies position risk management settings
    - Does not execute trades
    """
    # Validate IDs
    try:
        account_uuid = UUID(account_id)
        position_uuid = UUID(position_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID format",
        )
    
    # Validate account
    account_result = await session.execute(
        select(Account).where(
            Account.id == account_uuid,
            Account.user_id == current_user.id,
        )
    )
    account = account_result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )
    
    # Get position
    position_result = await session.execute(
        select(Position).where(
            Position.id == position_uuid,
            Position.account_id == account.id,
        )
    )
    position = position_result.scalar_one_or_none()
    
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found",
        )
    
    if not position.is_open:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update closed position",
        )
    
    # Update stop loss / take profit
    if request.stop_loss is not None:
        position.stop_loss = request.stop_loss
    
    if request.take_profit is not None:
        position.take_profit = request.take_profit
    
    position.updated_at = datetime.utcnow()
    session.add(position)
    
    await session.commit()
    await session.refresh(position)
    
    return position
