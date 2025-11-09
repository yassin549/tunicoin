from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
from datetime import datetime

from app.core.database import get_session as get_db
from app.core.deps import get_current_user, get_current_admin_user
from app.core.config import settings
from app.models import (
    User,
    InvestmentTier,
    InvestmentAccount,
    Deposit,
    InvestmentReturn,
    Payout,
)
from app.schemas.investment import (
    InvestmentTierResponse,
    InvestmentAccountCreate,
    InvestmentAccountResponse,
    DepositCreate,
    DepositResponse,
    PayoutRequest,
    PayoutResponse,
    InvestmentReturnResponse,
)
from app.services.nowpayments import nowpayments

router = APIRouter(prefix="/investment", tags=["investment"])


# ==================== Investment Tiers ====================

@router.get("/tiers", response_model=List[InvestmentTierResponse])
async def get_investment_tiers(
    db: AsyncSession = Depends(get_db),
    active_only: bool = True,
):
    """Get all available investment tiers."""
    query = select(InvestmentTier)
    if active_only:
        query = query.where(InvestmentTier.is_active == True)
    
    result = await db.execute(query.order_by(InvestmentTier.minimum_deposit))
    tiers = result.scalars().all()
    return tiers


@router.get("/tiers/{tier_id}", response_model=InvestmentTierResponse)
async def get_investment_tier(
    tier_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific investment tier."""
    result = await db.execute(
        select(InvestmentTier).where(InvestmentTier.id == tier_id)
    )
    tier = result.scalar_one_or_none()
    
    if not tier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment tier not found"
        )
    
    return tier


# ==================== Investment Accounts ====================

@router.post("/accounts", response_model=InvestmentAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_investment_account(
    account_data: InvestmentAccountCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new investment account."""
    
    # Check if user already has an active investment account
    existing = await db.execute(
        select(InvestmentAccount).where(
            InvestmentAccount.user_id == current_user.id,
            InvestmentAccount.status.in_(["pending_kyc", "active"])
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active investment account"
        )
    
    # Check if tier exists
    tier_result = await db.execute(
        select(InvestmentTier).where(InvestmentTier.id == account_data.tier_id)
    )
    tier = tier_result.scalar_one_or_none()
    if not tier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment tier not found"
        )
    
    # Check KYC status
    if current_user.kyc_status != "approved":
        status_to_set = "pending_kyc"
    else:
        status_to_set = "active"
    
    # Create investment account
    new_account = InvestmentAccount(
        user_id=current_user.id,
        tier_id=account_data.tier_id,
        status=status_to_set,
        opened_at=datetime.utcnow(),
        activated_at=datetime.utcnow() if status_to_set == "active" else None,
    )
    
    db.add(new_account)
    await db.commit()
    await db.refresh(new_account)
    
    return new_account


@router.get("/accounts", response_model=List[InvestmentAccountResponse])
async def get_my_investment_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all investment accounts for the current user."""
    result = await db.execute(
        select(InvestmentAccount)
        .where(InvestmentAccount.user_id == current_user.id)
        .order_by(InvestmentAccount.created_at.desc())
    )
    accounts = result.scalars().all()
    return accounts


@router.get("/accounts/{account_id}", response_model=InvestmentAccountResponse)
async def get_investment_account(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific investment account."""
    result = await db.execute(
        select(InvestmentAccount).where(InvestmentAccount.id == account_id)
    )
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment account not found"
        )
    
    # Check ownership
    if account.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this account"
        )
    
    return account


# ==================== Deposits ====================

@router.post("/deposits", status_code=status.HTTP_201_CREATED)
async def create_deposit(
    deposit_data: DepositCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Initiate a new crypto deposit via NOWPayments.
    Returns payment details including payment address and URL.
    """
    
    # Verify account exists and belongs to user
    account_result = await db.execute(
        select(InvestmentAccount).where(InvestmentAccount.id == deposit_data.investment_account_id)
    )
    account = account_result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment account not found"
        )
    
    if account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to deposit to this account"
        )
    
    if account.status not in ["active", "pending_kyc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot deposit to account with status: {account.status}"
        )
    
    # Validate currency
    supported_crypto = settings.SUPPORTED_CRYPTO
    if deposit_data.currency.lower() not in supported_crypto:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Currency {deposit_data.currency} not supported. Supported: {', '.join(supported_crypto)}"
        )
    
    # Create deposit record
    new_deposit = Deposit(
        investment_account_id=deposit_data.investment_account_id,
        user_id=current_user.id,
        amount=deposit_data.amount,
        currency=deposit_data.currency.upper(),
        payment_method="crypto",
        payment_provider="nowpayments",
        status="pending",
    )
    
    db.add(new_deposit)
    await db.flush()
    
    # Create NOWPayments invoice
    try:
        ipn_url = f"{settings.API_URL}/api/investment/deposits/webhook"
        success_url = f"{settings.FRONTEND_URL}/dashboard/investment?deposit=success"
        cancel_url = f"{settings.FRONTEND_URL}/dashboard/investment?deposit=cancelled"
        
        # Create payment with NOWPayments
        payment_data = await nowpayments.create_payment(
            price_amount=deposit_data.amount,
            price_currency="usd",
            pay_currency=deposit_data.currency.lower(),
            order_id=str(new_deposit.id),
            order_description=f"Investment deposit - {current_user.email}",
            ipn_callback_url=ipn_url,
            success_url=success_url,
            cancel_url=cancel_url,
        )
        
        # Update deposit with payment details
        new_deposit.transaction_hash = payment_data.get("payment_id")
        new_deposit.provider_transaction_id = payment_data.get("payment_id")
        
        await db.commit()
        await db.refresh(new_deposit)
        
        # Return payment information
        return {
            "deposit_id": str(new_deposit.id),
            "amount": new_deposit.amount,
            "currency": new_deposit.currency,
            "status": new_deposit.status,
            "payment_id": payment_data.get("payment_id"),
            "pay_address": payment_data.get("pay_address"),
            "pay_amount": payment_data.get("pay_amount"),
            "created_at": new_deposit.created_at,
            "expires_at": payment_data.get("expiration_estimate_date"),
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment: {str(e)}"
        )


@router.get("/deposits", response_model=List[DepositResponse])
async def get_my_deposits(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
):
    """Get all deposits for the current user."""
    result = await db.execute(
        select(Deposit)
        .where(Deposit.user_id == current_user.id)
        .order_by(Deposit.created_at.desc())
        .limit(limit)
    )
    deposits = result.scalars().all()
    return deposits


# ==================== Returns ====================

@router.get("/accounts/{account_id}/returns", response_model=List[InvestmentReturnResponse])
async def get_investment_returns(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 100,
):
    """Get return history for an investment account."""
    
    # Verify account ownership
    account_result = await db.execute(
        select(InvestmentAccount).where(InvestmentAccount.id == account_id)
    )
    account = account_result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment account not found"
        )
    
    if account.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view returns for this account"
        )
    
    # Get returns
    result = await db.execute(
        select(InvestmentReturn)
        .where(InvestmentReturn.investment_account_id == account_id)
        .order_by(InvestmentReturn.period_start.desc())
        .limit(limit)
    )
    returns = result.scalars().all()
    return returns


# ==================== Payouts ====================

@router.post("/payouts", response_model=PayoutResponse, status_code=status.HTTP_201_CREATED)
async def request_payout(
    payout_data: PayoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Request a payout/withdrawal."""
    
    # Verify account
    account_result = await db.execute(
        select(InvestmentAccount).where(InvestmentAccount.id == payout_data.investment_account_id)
    )
    account = account_result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment account not found"
        )
    
    if account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to request payout from this account"
        )
    
    if account.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot request payout from account with status: {account.status}"
        )
    
    # Check balance
    if payout_data.amount > account.current_balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance for payout"
        )
    
    # Minimum payout check
    if payout_data.amount < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minimum payout amount is $50"
        )
    
    # Create payout request
    new_payout = Payout(
        investment_account_id=payout_data.investment_account_id,
        user_id=current_user.id,
        amount=payout_data.amount,
        payout_method=payout_data.payout_method,
        destination=payout_data.destination,
        currency=payout_data.currency,
        status="pending",
        requested_at=datetime.utcnow(),
    )
    
    db.add(new_payout)
    await db.commit()
    await db.refresh(new_payout)
    
    return new_payout


@router.get("/payouts", response_model=List[PayoutResponse])
async def get_my_payouts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
):
    """Get all payout requests for the current user."""
    result = await db.execute(
        select(Payout)
        .where(Payout.user_id == current_user.id)
        .order_by(Payout.requested_at.desc())
        .limit(limit)
    )
    payouts = result.scalars().all()
    return payouts


@router.get("/payouts/{payout_id}", response_model=PayoutResponse)
async def get_payout(
    payout_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific payout request."""
    result = await db.execute(
        select(Payout).where(Payout.id == payout_id)
    )
    payout = result.scalar_one_or_none()
    
    if not payout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payout not found"
        )
    
    if payout.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this payout"
        )
    
    return payout


# ==================== NOWPayments Webhook ====================

@router.post("/deposits/webhook")
async def nowpayments_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    NOWPayments IPN webhook for investment deposits.
    
    This endpoint receives payment status updates from NOWPayments
    and processes confirmed deposits by crediting the investment account.
    """
    from fastapi import Request, Header
    
    # Get signature from header
    signature = request.headers.get("x-nowpayments-sig")
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing signature header"
        )
    
    # Get raw body
    body = await request.body()
    
    # Verify signature
    if not nowpayments.verify_ipn_signature(body, signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )
    
    # Parse webhook data
    import json
    try:
        webhook_data = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    
    # Extract payment information
    payment_id = webhook_data.get("payment_id")
    payment_status = webhook_data.get("payment_status")
    order_id = webhook_data.get("order_id")
    
    if not all([payment_id, payment_status, order_id]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required fields in webhook"
        )
    
    # Find deposit record
    try:
        deposit_id = UUID(order_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order ID format"
        )
    
    result = await db.execute(
        select(Deposit).where(Deposit.id == deposit_id)
    )
    deposit = result.scalar_one_or_none()
    
    if not deposit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit not found"
        )
    
    # Update deposit status based on payment status
    if payment_status == "finished":
        # Payment confirmed - credit the account
        deposit.status = "confirmed"
        deposit.confirmed_at = datetime.utcnow()
        
        # Get investment account
        account_result = await db.execute(
            select(InvestmentAccount).where(InvestmentAccount.id == deposit.investment_account_id)
        )
        account = account_result.scalar_one()
        
        # Credit the account
        if not account.initial_deposit:
            account.initial_deposit = deposit.amount
        
        account.current_balance += deposit.amount
        account.total_deposited += deposit.amount
        account.updated_at = datetime.utcnow()
        
        # If this is the first deposit and account is pending KYC, keep it pending
        # If KYC is approved, ensure account is active
        if account.status == "pending_kyc":
            # Check user's KYC status
            user_result = await db.execute(
                select(User).where(User.id == deposit.user_id)
            )
            user = user_result.scalar_one()
            if user.kyc_status == "approved" and account.status == "pending_kyc":
                account.status = "active"
                account.activated_at = datetime.utcnow()
        
        await db.commit()
        
        return {"status": "success", "message": "Deposit confirmed and account credited"}
    
    elif payment_status in ["confirming", "sending"]:
        # Payment in progress
        deposit.status = "confirming"
        deposit.updated_at = datetime.utcnow()
        await db.commit()
        return {"status": "success", "message": "Payment confirming"}
    
    elif payment_status in ["failed", "expired"]:
        # Payment failed
        deposit.status = "failed"
        deposit.failed_at = datetime.utcnow()
        deposit.admin_notes = f"Payment {payment_status}: {webhook_data.get('outcome', {}).get('message', 'Unknown error')}"
        await db.commit()
        return {"status": "success", "message": f"Payment {payment_status}"}
    
    # For other statuses, just log
    return {"status": "success", "message": f"Webhook received with status: {payment_status}"}
