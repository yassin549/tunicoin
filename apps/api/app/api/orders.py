"""Order management API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List, Optional
from datetime import datetime
from uuid import uuid4, UUID

from app.core.database import get_session
from app.core.deps import get_current_user
from app.models.user import User
from app.models.account import Account
from app.models.order import Order
from app.models.instrument import Instrument
from app.schemas.order import (
    CreateOrderRequest,
    OrderResponse,
    CancelOrderRequest,
)
from app.schemas.auth import MessageResponse
from app.services.execution import ExecutionService

router = APIRouter()


@router.post("/{account_id}/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def place_order(
    account_id: str,
    request: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Place a new order.
    
    - Creates and executes a simulated order
    - Updates account balances
    - Creates or updates positions
    - Generates ledger entries
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
    
    if not account.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is not active",
        )
    
    # Validate instrument
    instrument_result = await session.execute(
        select(Instrument).where(Instrument.id == request.instrument_id)
    )
    instrument = instrument_result.scalar_one_or_none()
    
    if not instrument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instrument not found",
        )
    
    if not instrument.is_tradeable:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Instrument is not tradeable",
        )
    
    # Validate size
    if request.size < instrument.min_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order size must be at least {instrument.min_size}",
        )
    
    if instrument.max_size and request.size > instrument.max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order size cannot exceed {instrument.max_size}",
        )
    
    # Validate leverage
    if request.leverage > account.max_leverage:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Leverage cannot exceed account maximum of {account.max_leverage}x",
        )
    
    # Create order
    new_order = Order(
        id=uuid4(),
        account_id=account.id,
        instrument_id=instrument.id,
        order_type=request.order_type.value,
        side=request.side.value,
        size=request.size,
        price=request.price,
        stop_price=request.stop_price,
        status="pending",
        filled_size=0,
        commission=0,
        leverage=request.leverage,
        margin_required=0,
        created_at=datetime.utcnow(),
    )
    
    session.add(new_order)
    await session.flush()
    
    # Execute order
    execution_service = ExecutionService(session)
    execution_result = await execution_service.execute_order(
        new_order, account, instrument
    )
    
    await session.commit()
    await session.refresh(new_order)
    
    if not execution_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=execution_result.get("error", "Order execution failed"),
        )
    
    return new_order


@router.get("/{account_id}/orders", response_model=List[OrderResponse])
async def get_orders(
    account_id: str,
    status_filter: Optional[str] = Query(default=None, description="Filter by status"),
    limit: int = Query(default=50, ge=1, le=200, description="Maximum orders to return"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get orders for an account.
    
    - Returns list of orders
    - Optional filtering by status
    - Paginated results
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
    query = select(Order).where(Order.account_id == account.id)
    
    if status_filter:
        query = query.where(Order.status == status_filter)
    
    query = query.order_by(Order.created_at.desc()).limit(limit).offset(offset)
    
    orders_result = await session.execute(query)
    orders = orders_result.scalars().all()
    
    return orders


@router.get("/{account_id}/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    account_id: str,
    order_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get a specific order by ID.
    
    - Returns order details including execution info
    """
    # Validate IDs
    try:
        account_uuid = UUID(account_id)
        order_uuid = UUID(order_id)
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
    
    # Get order
    order_result = await session.execute(
        select(Order).where(
            Order.id == order_uuid,
            Order.account_id == account.id,
        )
    )
    order = order_result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    
    return order


@router.delete("/{account_id}/orders/{order_id}", response_model=MessageResponse)
async def cancel_order(
    account_id: str,
    order_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Cancel a pending order.
    
    - Only pending orders can be canceled
    - Filled orders cannot be canceled
    """
    # Validate IDs
    try:
        account_uuid = UUID(account_id)
        order_uuid = UUID(order_id)
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
    
    # Get order
    order_result = await session.execute(
        select(Order).where(
            Order.id == order_uuid,
            Order.account_id == account.id,
        )
    )
    order = order_result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    
    # Check if order can be canceled
    if order.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel order with status '{order.status}'",
        )
    
    # Cancel order
    order.status = "canceled"
    order.canceled_at = datetime.utcnow()
    session.add(order)
    await session.commit()
    
    return MessageResponse(message=f"Order {order_id} canceled successfully")
