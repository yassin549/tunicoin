"""Account management API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List
from datetime import datetime
from uuid import uuid4
from decimal import Decimal

from app.core.database import get_session
from app.core.deps import get_current_user
from app.models.user import User
from app.models.account import Account
from app.models.ledger_entry import LedgerEntry
from app.schemas.account import CreateAccountRequest, AccountResponse, AccountSummary

router = APIRouter()


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    request: CreateAccountRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new simulated trading account.
    
    - User can have multiple accounts
    - Accounts start with specified initial balance
    - Demo accounts are pre-funded
    """
    # Create new account
    initial_balance = request.initial_balance or Decimal("10000.00")
    
    new_account = Account(
        id=uuid4(),
        user_id=current_user.id,
        name=request.name,
        base_currency=request.base_currency,
        balance=initial_balance,
        equity=initial_balance,
        margin_used=Decimal("0.00"),
        margin_available=initial_balance,
        is_demo=request.is_demo,
        is_active=True,
        max_leverage=request.max_leverage,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    session.add(new_account)
    await session.flush()
    
    # Create initial ledger entry for the deposit
    ledger_entry = LedgerEntry(
        id=uuid4(),
        account_id=new_account.id,
        entry_type="deposit",
        amount=initial_balance,
        balance_after=initial_balance,
        currency=request.base_currency,
        description=f"Initial deposit for account creation",
        meta={"source": "account_creation"},
        created_at=datetime.utcnow(),
    )
    
    session.add(ledger_entry)
    await session.commit()
    await session.refresh(new_account)
    
    return new_account


@router.get("", response_model=List[AccountSummary])
async def get_accounts(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get all accounts for the current user.
    
    - Returns list of user's accounts
    - Includes both demo and live accounts
    """
    result = await session.execute(
        select(Account)
        .where(Account.user_id == current_user.id)
        .where(Account.is_active == True)
        .order_by(Account.created_at.desc())
    )
    accounts = result.scalars().all()
    
    return accounts


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get detailed account information.
    
    - Returns full account details
    - Includes balance, equity, margin info
    """
    from uuid import UUID
    
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
    
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Delete (deactivate) an account.
    
    - Soft delete - sets is_active to False
    - Cannot delete account with open positions
    """
    from uuid import UUID
    from app.models.position import Position
    
    try:
        account_uuid = UUID(account_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid account ID format",
        )
    
    # Check account exists and belongs to user
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
    
    # Check for open positions
    positions_result = await session.execute(
        select(Position).where(
            Position.account_id == account_uuid,
            Position.is_open == True,
        )
    )
    open_positions = positions_result.scalars().all()
    
    if open_positions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete account with {len(open_positions)} open position(s). Please close all positions first.",
        )
    
    # Soft delete
    account.is_active = False
    account.updated_at = datetime.utcnow()
    session.add(account)
    await session.commit()
    
    return None
