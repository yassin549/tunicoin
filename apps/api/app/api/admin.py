"""Admin API endpoints for platform management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func
from typing import List
from datetime import datetime, timedelta

from app.core.database import get_session as get_db
from app.core.deps import get_current_admin_user
from app.models import (
    User,
    InvestmentAccount,
    Deposit,
    InvestmentReturn,
    Payout,
    KYCSubmission,
)

router = APIRouter(prefix="/admin", tags=["admin"])


# ==================== Dashboard Statistics ====================

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get admin dashboard statistics."""
    
    # Total users
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar_one()
    
    # Active investments
    active_investments_result = await db.execute(
        select(func.count(InvestmentAccount.id)).where(
            InvestmentAccount.status == "active"
        )
    )
    active_investments = active_investments_result.scalar_one()
    
    # Pending KYC
    pending_kyc_result = await db.execute(
        select(func.count(KYCSubmission.id)).where(
            KYCSubmission.status == "pending"
        )
    )
    pending_kyc = pending_kyc_result.scalar_one()
    
    # Total deposits
    total_deposits_result = await db.execute(
        select(func.count(Deposit.id), func.sum(Deposit.amount)).where(
            Deposit.status == "confirmed"
        )
    )
    total_deposits_row = total_deposits_result.one()
    total_deposits = total_deposits_row[0] or 0
    total_deposits_amount = float(total_deposits_row[1] or 0)
    
    # Total returns
    total_returns_result = await db.execute(
        select(func.count(InvestmentReturn.id), func.sum(InvestmentReturn.amount))
    )
    total_returns_row = total_returns_result.one()
    total_returns = total_returns_row[0] or 0
    total_returns_amount = float(total_returns_row[1] or 0)
    
    # Pending payouts
    pending_payouts_result = await db.execute(
        select(func.count(Payout.id), func.sum(Payout.amount)).where(
            Payout.status == "pending"
        )
    )
    pending_payouts_row = pending_payouts_result.one()
    pending_payouts = pending_payouts_row[0] or 0
    pending_payouts_amount = float(pending_payouts_row[1] or 0)
    
    return {
        "total_users": total_users,
        "active_investments": active_investments,
        "pending_kyc": pending_kyc,
        "total_deposits": total_deposits,
        "total_deposits_amount": total_deposits_amount,
        "total_returns": total_returns,
        "total_returns_amount": total_returns_amount,
        "pending_payouts": pending_payouts,
        "pending_payouts_amount": pending_payouts_amount,
    }


@router.get("/dashboard/activity")
async def get_recent_activity(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 10,
):
    """Get recent platform activity."""
    
    activity = []
    
    # Recent users (last 24 hours)
    day_ago = datetime.utcnow() - timedelta(days=1)
    recent_users_result = await db.execute(
        select(User)
        .where(User.created_at >= day_ago)
        .order_by(User.created_at.desc())
        .limit(3)
    )
    recent_users = recent_users_result.scalars().all()
    
    for user in recent_users:
        activity.append({
            "id": str(user.id),
            "type": "user",
            "description": f"New user registered: {user.email}",
            "timestamp": user.created_at.isoformat(),
            "status": "completed",
        })
    
    # Recent deposits
    recent_deposits_result = await db.execute(
        select(Deposit)
        .order_by(Deposit.created_at.desc())
        .limit(3)
    )
    recent_deposits = recent_deposits_result.scalars().all()
    
    for deposit in recent_deposits:
        activity.append({
            "id": str(deposit.id),
            "type": "deposit",
            "description": f"Deposit: ${deposit.amount} ({deposit.currency})",
            "timestamp": deposit.created_at.isoformat(),
            "status": deposit.status,
        })
    
    # Recent KYC submissions
    recent_kyc_result = await db.execute(
        select(KYCSubmission)
        .order_by(KYCSubmission.created_at.desc())
        .limit(2)
    )
    recent_kyc = recent_kyc_result.scalars().all()
    
    for kyc in recent_kyc:
        activity.append({
            "id": str(kyc.id),
            "type": "kyc",
            "description": f"KYC submission from user",
            "timestamp": kyc.created_at.isoformat(),
            "status": kyc.status,
        })
    
    # Recent payouts
    recent_payouts_result = await db.execute(
        select(Payout)
        .order_by(Payout.created_at.desc())
        .limit(2)
    )
    recent_payouts = recent_payouts_result.scalars().all()
    
    for payout in recent_payouts:
        activity.append({
            "id": str(payout.id),
            "type": "payout",
            "description": f"Payout request: ${payout.amount}",
            "timestamp": payout.created_at.isoformat(),
            "status": payout.status,
        })
    
    # Sort by timestamp and limit
    activity.sort(key=lambda x: x["timestamp"], reverse=True)
    return activity[:limit]


# ==================== User Management ====================

@router.get("/users")
async def get_all_users(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
):
    """Get all users with pagination."""
    
    result = await db.execute(
        select(User)
        .order_by(User.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    users = result.scalars().all()
    
    # Get total count
    count_result = await db.execute(select(func.count(User.id)))
    total = count_result.scalar_one()
    
    return {
        "users": users,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/users/{user_id}")
async def get_user_details(
    user_id: str,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed user information including investment accounts."""
    
    from uuid import UUID
    
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format",
        )
    
    # Get user
    user_result = await db.execute(
        select(User).where(User.id == user_uuid)
    )
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Get investment accounts
    accounts_result = await db.execute(
        select(InvestmentAccount).where(InvestmentAccount.user_id == user_uuid)
    )
    accounts = accounts_result.scalars().all()
    
    # Get KYC status
    kyc_result = await db.execute(
        select(KYCSubmission).where(KYCSubmission.user_id == user_uuid)
    )
    kyc = kyc_result.scalar_one_or_none()
    
    return {
        "user": user,
        "investment_accounts": accounts,
        "kyc_submission": kyc,
    }


@router.patch("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    is_active: bool,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user active status (suspend/activate)."""
    
    from uuid import UUID
    
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format",
        )
    
    # Get user
    user_result = await db.execute(
        select(User).where(User.id == user_uuid)
    )
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Prevent admins from suspending themselves
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify your own account status",
        )
    
    # Prevent suspending other admins
    if user.is_admin and not is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot suspend admin users",
        )
    
    # Update status
    user.is_active = is_active
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return {
        "message": f"User {'activated' if is_active else 'suspended'} successfully",
        "user": user,
    }


# ==================== KYC Management ====================

@router.get("/kyc/submissions")
async def get_kyc_submissions(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
    status: str = None,
    limit: int = 20,
    offset: int = 0,
):
    """Get all KYC submissions with optional status filter."""
    
    query = select(KYCSubmission).order_by(KYCSubmission.created_at.desc())
    
    if status and status != 'all':
        query = query.where(KYCSubmission.status == status)
    
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    submissions = result.scalars().all()
    
    # Get total count
    count_query = select(func.count(KYCSubmission.id))
    if status and status != 'all':
        count_query = count_query.where(KYCSubmission.status == status)
    
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()
    
    # Enrich with user email
    enriched_submissions = []
    for submission in submissions:
        submission_dict = submission.dict() if hasattr(submission, 'dict') else vars(submission)
        
        # Get user email
        user_result = await db.execute(
            select(User).where(User.id == submission.user_id)
        )
        user = user_result.scalar_one_or_none()
        if user:
            submission_dict['user_email'] = user.email
        
        enriched_submissions.append(submission_dict)
    
    return {
        "submissions": enriched_submissions,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("/kyc/submissions/{submission_id}/approve")
async def approve_kyc_submission(
    submission_id: str,
    admin_notes: str = "",
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve a KYC submission."""
    
    from uuid import UUID
    
    try:
        submission_uuid = UUID(submission_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid submission ID format",
        )
    
    # Get submission
    submission_result = await db.execute(
        select(KYCSubmission).where(KYCSubmission.id == submission_uuid)
    )
    submission = submission_result.scalar_one_or_none()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC submission not found",
        )
    
    if submission.status != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve submission with status: {submission.status}",
        )
    
    # Update submission status
    submission.status = 'approved'
    submission.admin_notes = admin_notes
    submission.updated_at = datetime.utcnow()
    db.add(submission)
    
    # Update user KYC status
    user_result = await db.execute(
        select(User).where(User.id == submission.user_id)
    )
    user = user_result.scalar_one_or_none()
    if user:
        user.kyc_status = 'approved'
        db.add(user)
    
    # Activate investment accounts if they exist
    accounts_result = await db.execute(
        select(InvestmentAccount).where(
            InvestmentAccount.user_id == submission.user_id,
            InvestmentAccount.status == 'pending'
        )
    )
    accounts = accounts_result.scalars().all()
    
    for account in accounts:
        account.status = 'active'
        db.add(account)
    
    await db.commit()
    await db.refresh(submission)
    
    return {
        "message": "KYC submission approved successfully",
        "submission": submission,
    }


@router.post("/kyc/submissions/{submission_id}/reject")
async def reject_kyc_submission(
    submission_id: str,
    admin_notes: str,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Reject a KYC submission with admin notes."""
    
    from uuid import UUID
    
    if not admin_notes or not admin_notes.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin notes are required for rejection",
        )
    
    try:
        submission_uuid = UUID(submission_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid submission ID format",
        )
    
    # Get submission
    submission_result = await db.execute(
        select(KYCSubmission).where(KYCSubmission.id == submission_uuid)
    )
    submission = submission_result.scalar_one_or_none()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC submission not found",
        )
    
    if submission.status != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject submission with status: {submission.status}",
        )
    
    # Update submission status
    submission.status = 'rejected'
    submission.admin_notes = admin_notes
    submission.updated_at = datetime.utcnow()
    db.add(submission)
    
    # Update user KYC status
    user_result = await db.execute(
        select(User).where(User.id == submission.user_id)
    )
    user = user_result.scalar_one_or_none()
    if user:
        user.kyc_status = 'rejected'
        db.add(user)
    
    await db.commit()
    await db.refresh(submission)
    
    return {
        "message": "KYC submission rejected",
        "submission": submission,
    }


# ==================== Deposit Management ====================

@router.get("/deposits")
async def get_all_deposits(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
    status: str = None,
    currency: str = None,
    limit: int = 20,
    offset: int = 0,
):
    """Get all deposits across all users with filters."""
    
    query = select(Deposit).order_by(Deposit.created_at.desc())
    
    if status and status != 'all':
        query = query.where(Deposit.status == status)
    
    if currency and currency != 'all':
        query = query.where(Deposit.currency == currency)
    
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    deposits = result.scalars().all()
    
    # Get total count
    count_query = select(func.count(Deposit.id))
    if status and status != 'all':
        count_query = count_query.where(Deposit.status == status)
    if currency and currency != 'all':
        count_query = count_query.where(Deposit.currency == currency)
    
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()
    
    # Enrich with user information
    enriched_deposits = []
    for deposit in deposits:
        deposit_dict = deposit.dict() if hasattr(deposit, 'dict') else vars(deposit)
        
        # Get investment account and user
        account_result = await db.execute(
            select(InvestmentAccount).where(InvestmentAccount.id == deposit.investment_account_id)
        )
        account = account_result.scalar_one_or_none()
        
        if account:
            user_result = await db.execute(
                select(User).where(User.id == account.user_id)
            )
            user = user_result.scalar_one_or_none()
            if user:
                deposit_dict['user_email'] = user.email
                deposit_dict['user_name'] = user.full_name
        
        enriched_deposits.append(deposit_dict)
    
    return {
        "deposits": enriched_deposits,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/deposits/stats")
async def get_deposit_stats(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get deposit statistics."""
    
    # Total deposits
    total_result = await db.execute(select(func.count(Deposit.id)))
    total_deposits = total_result.scalar_one()
    
    # Total amount (confirmed only)
    amount_result = await db.execute(
        select(func.sum(Deposit.amount)).where(Deposit.status == 'confirmed')
    )
    total_amount = float(amount_result.scalar_one() or 0)
    
    # Pending count
    pending_result = await db.execute(
        select(func.count(Deposit.id)).where(Deposit.status == 'pending')
    )
    pending_count = pending_result.scalar_one()
    
    # Confirmed count
    confirmed_result = await db.execute(
        select(func.count(Deposit.id)).where(Deposit.status == 'confirmed')
    )
    confirmed_count = confirmed_result.scalar_one()
    
    return {
        "total_deposits": total_deposits,
        "total_amount": total_amount,
        "pending_count": pending_count,
        "confirmed_count": confirmed_count,
    }


# ==================== Returns Management ====================

@router.get("/returns/eligible-accounts")
async def get_eligible_accounts(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all active investment accounts eligible for return generation."""
    
    # Get active accounts with positive balance
    accounts_result = await db.execute(
        select(InvestmentAccount)
        .where(
            InvestmentAccount.status == 'active',
            InvestmentAccount.balance > 0
        )
        .order_by(InvestmentAccount.balance.desc())
    )
    accounts = accounts_result.scalars().all()
    
    # Enrich with user information and last return date
    enriched_accounts = []
    for account in accounts:
        account_dict = account.dict() if hasattr(account, 'dict') else vars(account)
        
        # Get user info
        user_result = await db.execute(
            select(User).where(User.id == account.user_id)
        )
        user = user_result.scalar_one_or_none()
        if user:
            account_dict['user_email'] = user.email
            account_dict['user_name'] = user.full_name
        
        # Get last return date
        last_return_result = await db.execute(
            select(InvestmentReturn)
            .where(InvestmentReturn.investment_account_id == account.id)
            .order_by(InvestmentReturn.created_at.desc())
            .limit(1)
        )
        last_return = last_return_result.scalar_one_or_none()
        if last_return:
            account_dict['last_return_date'] = last_return.created_at.isoformat()
        
        enriched_accounts.append(account_dict)
    
    return {
        "accounts": enriched_accounts,
        "total": len(enriched_accounts),
    }


@router.get("/returns/stats")
async def get_returns_stats(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get returns generation statistics."""
    
    # Active accounts count
    active_result = await db.execute(
        select(func.count(InvestmentAccount.id)).where(
            InvestmentAccount.status == 'active',
            InvestmentAccount.balance > 0
        )
    )
    active_accounts = active_result.scalar_one()
    
    # Total balance
    balance_result = await db.execute(
        select(func.sum(InvestmentAccount.balance)).where(
            InvestmentAccount.status == 'active',
            InvestmentAccount.balance > 0
        )
    )
    total_balance = float(balance_result.scalar_one() or 0)
    
    # Estimated returns (using tier rates)
    accounts_result = await db.execute(
        select(InvestmentAccount).where(
            InvestmentAccount.status == 'active',
            InvestmentAccount.balance > 0
        )
    )
    accounts = accounts_result.scalars().all()
    
    estimated_returns = sum(
        (account.balance * account.return_rate / 100) for account in accounts
    )
    
    return {
        "active_accounts": active_accounts,
        "total_balance": total_balance,
        "estimated_returns": estimated_returns,
    }


@router.post("/returns/generate-bulk")
async def generate_bulk_returns(
    returns: list,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate returns for multiple accounts in bulk."""
    
    from uuid import UUID
    
    generated_count = 0
    total_amount = 0.0
    errors = []
    
    for return_data in returns:
        try:
            account_id = UUID(return_data['investment_account_id'])
            return_percentage = float(return_data['return_percentage'])
            
            # Get account
            account_result = await db.execute(
                select(InvestmentAccount).where(InvestmentAccount.id == account_id)
            )
            account = account_result.scalar_one_or_none()
            
            if not account:
                errors.append(f"Account {account_id} not found")
                continue
            
            if account.status != 'active':
                errors.append(f"Account {account_id} is not active")
                continue
            
            if account.balance <= 0:
                errors.append(f"Account {account_id} has zero balance")
                continue
            
            # Calculate return amount
            return_amount = (account.balance * return_percentage) / 100
            
            # Create investment return record
            investment_return = InvestmentReturn(
                investment_account_id=account.id,
                amount=return_amount,
                return_rate=return_percentage,
                period_start=datetime.utcnow(),
                period_end=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            db.add(investment_return)
            
            # Update account balance
            account.balance += return_amount
            account.total_returns = (account.total_returns or 0) + return_amount
            db.add(account)
            
            generated_count += 1
            total_amount += return_amount
            
        except Exception as e:
            errors.append(f"Error processing account: {str(e)}")
            continue
    
    await db.commit()
    
    return {
        "generated_count": generated_count,
        "total_amount": total_amount,
        "errors": errors if errors else None,
        "message": f"Successfully generated returns for {generated_count} accounts",
    }


# ==================== Payout Management ====================

@router.get("/payouts")
async def get_all_payouts(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
    status: str = None,
    limit: int = 20,
    offset: int = 0,
):
    """Get all payout requests with filters."""
    
    query = select(Payout).order_by(Payout.created_at.desc())
    
    if status and status != 'all':
        query = query.where(Payout.status == status)
    
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    payouts = result.scalars().all()
    
    # Get total count
    count_query = select(func.count(Payout.id))
    if status and status != 'all':
        count_query = count_query.where(Payout.status == status)
    
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()
    
    # Enrich with user information
    enriched_payouts = []
    for payout in payouts:
        payout_dict = payout.dict() if hasattr(payout, 'dict') else vars(payout)
        
        # Get investment account and user
        account_result = await db.execute(
            select(InvestmentAccount).where(InvestmentAccount.id == payout.investment_account_id)
        )
        account = account_result.scalar_one_or_none()
        
        if account:
            user_result = await db.execute(
                select(User).where(User.id == account.user_id)
            )
            user = user_result.scalar_one_or_none()
            if user:
                payout_dict['user_email'] = user.email
                payout_dict['user_name'] = user.full_name
        
        enriched_payouts.append(payout_dict)
    
    return {
        "payouts": enriched_payouts,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/payouts/stats")
async def get_payout_stats(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get payout statistics."""
    
    # Pending count and amount
    pending_count_result = await db.execute(
        select(func.count(Payout.id)).where(Payout.status == 'pending')
    )
    pending_count = pending_count_result.scalar_one()
    
    pending_amount_result = await db.execute(
        select(func.sum(Payout.amount)).where(Payout.status == 'pending')
    )
    pending_amount = float(pending_amount_result.scalar_one() or 0)
    
    # Approved count and amount
    approved_count_result = await db.execute(
        select(func.count(Payout.id)).where(Payout.status == 'approved')
    )
    approved_count = approved_count_result.scalar_one()
    
    approved_amount_result = await db.execute(
        select(func.sum(Payout.amount)).where(Payout.status == 'approved')
    )
    approved_amount = float(approved_amount_result.scalar_one() or 0)
    
    return {
        "pending_count": pending_count,
        "pending_amount": pending_amount,
        "approved_count": approved_count,
        "approved_amount": approved_amount,
    }


@router.post("/payouts/{payout_id}/approve")
async def approve_payout(
    payout_id: str,
    admin_notes: str = None,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve a payout request."""
    
    from uuid import UUID
    
    try:
        payout_uuid = UUID(payout_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payout ID format")
    
    # Get payout
    payout_result = await db.execute(
        select(Payout).where(Payout.id == payout_uuid)
    )
    payout = payout_result.scalar_one_or_none()
    
    if not payout:
        raise HTTPException(status_code=404, detail="Payout not found")
    
    if payout.status != 'pending':
        raise HTTPException(
            status_code=400,
            detail=f"Cannot approve payout with status: {payout.status}"
        )
    
    # Update payout status
    payout.status = 'approved'
    payout.processed_at = datetime.utcnow()
    if admin_notes:
        payout.admin_notes = admin_notes
    
    db.add(payout)
    await db.commit()
    await db.refresh(payout)
    
    return {
        "message": "Payout approved successfully",
        "payout": payout,
    }


@router.post("/payouts/{payout_id}/reject")
async def reject_payout(
    payout_id: str,
    admin_notes: str,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Reject a payout request."""
    
    from uuid import UUID
    
    if not admin_notes or not admin_notes.strip():
        raise HTTPException(
            status_code=400,
            detail="Admin notes are required for rejection"
        )
    
    try:
        payout_uuid = UUID(payout_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payout ID format")
    
    # Get payout
    payout_result = await db.execute(
        select(Payout).where(Payout.id == payout_uuid)
    )
    payout = payout_result.scalar_one_or_none()
    
    if not payout:
        raise HTTPException(status_code=404, detail="Payout not found")
    
    if payout.status != 'pending':
        raise HTTPException(
            status_code=400,
            detail=f"Cannot reject payout with status: {payout.status}"
        )
    
    # Get investment account to refund
    account_result = await db.execute(
        select(InvestmentAccount).where(InvestmentAccount.id == payout.investment_account_id)
    )
    account = account_result.scalar_one_or_none()
    
    if account:
        # Refund the amount back to account balance
        account.balance += payout.amount
        db.add(account)
    
    # Update payout status
    payout.status = 'rejected'
    payout.processed_at = datetime.utcnow()
    payout.admin_notes = admin_notes
    
    db.add(payout)
    await db.commit()
    await db.refresh(payout)
    
    return {
        "message": "Payout rejected and amount refunded",
        "payout": payout,
    }
