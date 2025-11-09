"""Crypto payment API endpoints (deposits and withdrawals)."""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List, Optional
from datetime import datetime
from uuid import uuid4, UUID
from decimal import Decimal
import json

from app.core.database import get_session
from app.core.deps import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.account import Account
from app.models.crypto_transaction import CryptoTransaction
from app.models.ledger_entry import LedgerEntry
from app.schemas.crypto import (
    CreateDepositRequest,
    DepositResponse,
    CreateWithdrawalRequest,
    WithdrawalResponse,
    CryptoTransactionResponse,
    AvailableCurrenciesResponse,
    CryptoEstimateRequest,
    CryptoEstimateResponse,
)
from app.schemas.auth import MessageResponse
from app.services.nowpayments import nowpayments

router = APIRouter()


@router.get("/currencies", response_model=AvailableCurrenciesResponse)
async def get_available_currencies():
    """
    Get list of available cryptocurrencies for deposits/withdrawals.
    
    Returns list of supported crypto currencies.
    """
    try:
        currencies = await nowpayments.get_available_currencies()
        # Filter to only our supported currencies
        supported = [c for c in currencies if c in settings.SUPPORTED_CRYPTO]
        return AvailableCurrenciesResponse(currencies=supported)
    except Exception as e:
        # Fallback to configured list if API fails
        return AvailableCurrenciesResponse(currencies=settings.SUPPORTED_CRYPTO)


@router.post("/estimate", response_model=CryptoEstimateResponse)
async def estimate_crypto_amount(request: CryptoEstimateRequest):
    """
    Estimate cryptocurrency amount for a given USD amount.
    
    Provides exchange rate and minimum deposit information.
    """
    try:
        # Get estimate from NOWPayments
        estimate = await nowpayments.get_estimate(
            amount=request.usd_amount,
            currency_from="usd",
            currency_to=request.crypto_currency.lower()
        )
        
        # Get minimum amount
        try:
            min_data = await nowpayments.get_minimum_payment_amount(
                currency_from="usd",
                currency_to=request.crypto_currency.lower()
            )
            minimum_amount = float(min_data.get("min_amount", settings.MIN_DEPOSIT_USD))
        except:
            minimum_amount = settings.MIN_DEPOSIT_USD
        
        crypto_amount = float(estimate.get("estimated_amount", 0))
        exchange_rate = request.usd_amount / crypto_amount if crypto_amount > 0 else 0
        
        return CryptoEstimateResponse(
            usd_amount=request.usd_amount,
            crypto_currency=request.crypto_currency.lower(),
            crypto_amount=crypto_amount,
            exchange_rate=exchange_rate,
            minimum_amount=minimum_amount,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get estimate: {str(e)}"
        )


@router.post("/deposit", response_model=DepositResponse, status_code=status.HTTP_201_CREATED)
async def create_deposit(
    request: CreateDepositRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Create a crypto deposit request.
    
    - Creates a NOWPayments invoice or payment
    - Returns payment URL for the user
    - User pays cryptocurrency to the address
    - IPN webhook confirms payment
    - Account balance is credited
    """
    # Validate account ownership
    account_result = await session.execute(
        select(Account).where(
            Account.id == request.account_id,
            Account.user_id == current_user.id,
        )
    )
    account = account_result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    if not account.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is not active"
        )
    
    # Create transaction record
    transaction_id = uuid4()
    transaction = CryptoTransaction(
        id=transaction_id,
        user_id=current_user.id,
        account_id=account.id,
        transaction_type="deposit",
        crypto_currency=request.pay_currency.lower() if request.pay_currency else "btc",
        crypto_amount=Decimal("0"),  # Will be updated when payment is made
        usd_amount=Decimal(str(request.usd_amount)),
        status="pending",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    session.add(transaction)
    await session.flush()
    
    # Create payment/invoice with NOWPayments
    try:
        # IPN callback URL (webhook endpoint)
        ipn_url = f"{settings.API_URL}/api/crypto/webhook"
        success_url = f"{settings.FRONTEND_URL}/deposits/success"
        cancel_url = f"{settings.FRONTEND_URL}/deposits/cancel"
        
        if request.pay_currency:
            # Create payment with specific currency
            payment_data = await nowpayments.create_payment(
                price_amount=request.usd_amount,
                price_currency="usd",
                pay_currency=request.pay_currency.lower(),
                order_id=str(transaction_id),
                order_description=f"Deposit to account {account.name}",
                ipn_callback_url=ipn_url,
                success_url=success_url,
                cancel_url=cancel_url,
            )
            
            # Update transaction
            transaction.payment_id = str(payment_data.get("payment_id"))
            transaction.crypto_amount = Decimal(str(payment_data.get("pay_amount", 0)))
            transaction.payment_url = payment_data.get("pay_address", "")
            transaction.exchange_rate = Decimal(str(payment_data.get("price_amount", 0))) / Decimal(str(payment_data.get("pay_amount", 1)))
            
            response = DepositResponse(
                transaction_id=transaction_id,
                payment_id=payment_data.get("payment_id"),
                invoice_id=None,
                payment_url=payment_data.get("pay_address", ""),
                crypto_currency=request.pay_currency.lower(),
                crypto_amount=Decimal(str(payment_data.get("pay_amount", 0))),
                usd_amount=Decimal(str(request.usd_amount)),
                pay_address=payment_data.get("pay_address"),
                status="pending",
                expires_at=None,
            )
        else:
            # Create invoice (let user choose currency)
            invoice_data = await nowpayments.create_invoice(
                price_amount=request.usd_amount,
                price_currency="usd",
                order_id=str(transaction_id),
                order_description=f"Deposit to account {account.name}",
                ipn_callback_url=ipn_url,
                success_url=success_url,
                cancel_url=cancel_url,
            )
            
            # Update transaction
            transaction.invoice_id = str(invoice_data.get("id"))
            transaction.payment_url = invoice_data.get("invoice_url", "")
            
            response = DepositResponse(
                transaction_id=transaction_id,
                payment_id=None,
                invoice_id=invoice_data.get("id"),
                payment_url=invoice_data.get("invoice_url", ""),
                crypto_currency="multiple",
                crypto_amount=None,
                usd_amount=Decimal(str(request.usd_amount)),
                pay_address=None,
                status="pending",
                expires_at=None,
            )
        
        session.add(transaction)
        await session.commit()
        
        return response
        
    except Exception as e:
        # Delete transaction if payment creation failed
        await session.delete(transaction)
        await session.commit()
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create payment: {str(e)}"
        )


@router.post("/withdraw", response_model=WithdrawalResponse, status_code=status.HTTP_201_CREATED)
async def create_withdrawal(
    request: CreateWithdrawalRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Create a crypto withdrawal request.
    
    - Validates recipient address
    - Checks account balance
    - Deducts amount + fee from account
    - Creates payout via NOWPayments
    - Sends crypto to recipient address
    """
    # Validate account ownership
    account_result = await session.execute(
        select(Account).where(
            Account.id == request.account_id,
            Account.user_id == current_user.id,
        )
    )
    account = account_result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    if not account.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is not active"
        )
    
    # Calculate withdrawal fee
    withdrawal_fee = Decimal(str(request.usd_amount)) * Decimal(str(settings.WITHDRAWAL_FEE_PERCENT / 100))
    total_deduction = Decimal(str(request.usd_amount)) + withdrawal_fee
    
    # Check balance
    if account.balance < total_deduction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance. Required: ${float(total_deduction):.2f}, Available: ${float(account.balance):.2f}"
        )
    
    # Validate crypto address
    try:
        validation = await nowpayments.validate_address(
            currency=request.crypto_currency,
            address=request.recipient_address
        )
        
        if not validation.get("valid", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid cryptocurrency address"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Address validation failed: {str(e)}"
        )
    
    # Get crypto amount estimate
    try:
        estimate = await nowpayments.get_estimate(
            amount=request.usd_amount,
            currency_from="usd",
            currency_to=request.crypto_currency
        )
        crypto_amount = Decimal(str(estimate.get("estimated_amount", 0)))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get exchange rate: {str(e)}"
        )
    
    # Create transaction record
    transaction_id = uuid4()
    transaction = CryptoTransaction(
        id=transaction_id,
        user_id=current_user.id,
        account_id=account.id,
        transaction_type="withdrawal",
        crypto_currency=request.crypto_currency,
        crypto_amount=crypto_amount,
        usd_amount=Decimal(str(request.usd_amount)),
        status="pending",
        recipient_address=request.recipient_address,
        withdrawal_fee=withdrawal_fee,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    session.add(transaction)
    await session.flush()
    
    # Deduct from account balance
    account.balance -= total_deduction
    account.updated_at = datetime.utcnow()
    session.add(account)
    
    # Create ledger entries
    withdrawal_entry = LedgerEntry(
        id=uuid4(),
        account_id=account.id,
        entry_type="withdrawal",
        amount=-Decimal(str(request.usd_amount)),
        balance_after=account.balance + withdrawal_fee,  # Before fee deduction
        currency=account.base_currency,
        description=f"Crypto withdrawal: {crypto_amount} {request.crypto_currency}",
        meta={"transaction_id": str(transaction_id)},
        created_at=datetime.utcnow(),
    )
    session.add(withdrawal_entry)
    
    fee_entry = LedgerEntry(
        id=uuid4(),
        account_id=account.id,
        entry_type="fee",
        amount=-withdrawal_fee,
        balance_after=account.balance,
        currency=account.base_currency,
        description=f"Withdrawal fee ({settings.WITHDRAWAL_FEE_PERCENT}%)",
        meta={"transaction_id": str(transaction_id)},
        created_at=datetime.utcnow(),
    )
    session.add(fee_entry)
    
    # Create payout via NOWPayments
    try:
        ipn_url = f"{settings.API_URL}/api/crypto/webhook"
        
        payout_data = await nowpayments.create_payout(
            withdrawals=[{
                "address": request.recipient_address,
                "currency": request.crypto_currency,
                "amount": float(crypto_amount),
                "ipn_callback_url": ipn_url,
                "extra_id": request.extra_id,
            }]
        )
        
        # Update transaction with payout ID
        if payout_data.get("id"):
            transaction.payment_id = str(payout_data["id"])
            transaction.status = "confirming"
        
        session.add(transaction)
        await session.commit()
        
        return WithdrawalResponse(
            transaction_id=transaction_id,
            payment_id=transaction.payment_id,
            crypto_currency=request.crypto_currency,
            crypto_amount=crypto_amount,
            usd_amount=Decimal(str(request.usd_amount)),
            withdrawal_fee=withdrawal_fee,
            net_amount=Decimal(str(request.usd_amount)) - withdrawal_fee,
            recipient_address=request.recipient_address,
            status=transaction.status,
            estimated_time="10-30 minutes",
        )
        
    except Exception as e:
        # Rollback balance deduction
        account.balance += total_deduction
        session.add(account)
        await session.delete(withdrawal_entry)
        await session.delete(fee_entry)
        await session.delete(transaction)
        await session.commit()
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create withdrawal: {str(e)}"
        )


@router.get("/transactions", response_model=List[CryptoTransactionResponse])
async def get_transactions(
    transaction_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get crypto transactions for the current user.
    
    - Returns deposits and withdrawals
    - Optional filtering by type and status
    - Paginated results
    """
    query = select(CryptoTransaction).where(
        CryptoTransaction.user_id == current_user.id
    )
    
    if transaction_type:
        query = query.where(CryptoTransaction.transaction_type == transaction_type)
    
    if status:
        query = query.where(CryptoTransaction.status == status)
    
    query = query.order_by(
        CryptoTransaction.created_at.desc()
    ).limit(limit).offset(offset)
    
    result = await session.execute(query)
    transactions = result.scalars().all()
    
    return transactions


@router.get("/transactions/{transaction_id}", response_model=CryptoTransactionResponse)
async def get_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get a specific crypto transaction by ID.
    """
    try:
        trans_uuid = UUID(transaction_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid transaction ID format"
        )
    
    result = await session.execute(
        select(CryptoTransaction).where(
            CryptoTransaction.id == trans_uuid,
            CryptoTransaction.user_id == current_user.id,
        )
    )
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Update status from NOWPayments if pending
    if transaction.status in ["pending", "confirming"] and transaction.payment_id:
        try:
            if transaction.transaction_type == "deposit":
                payment_status = await nowpayments.get_payment_status(transaction.payment_id)
            else:
                payment_status = await nowpayments.get_payout_status(transaction.payment_id)
            
            # Update status based on NOWPayments response
            now_status = payment_status.get("payment_status", "")
            if now_status in ["finished", "confirmed"]:
                transaction.status = "completed"
                transaction.completed_at = datetime.utcnow()
            elif now_status in ["failed", "expired", "refunded"]:
                transaction.status = now_status
            
            session.add(transaction)
            await session.commit()
            await session.refresh(transaction)
        except:
            pass  # Ignore errors when checking status
    
    return transaction


@router.post("/webhook")
async def nowpayments_webhook(
    request: Request,
    x_nowpayments_sig: str = Header(None),
    session: AsyncSession = Depends(get_session),
):
    """
    IPN webhook endpoint for NOWPayments callbacks.
    
    **Webhook URL:** https://your-domain.com/api/crypto/webhook
    
    This endpoint receives payment notifications from NOWPayments
    and updates transaction status accordingly.
    
    Security: Verifies HMAC-SHA512 signature using IPN secret.
    """
    # Get raw request body
    body = await request.body()
    
    # Verify signature
    if not x_nowpayments_sig:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing signature header"
        )
    
    if not nowpayments.verify_ipn_signature(body, x_nowpayments_sig):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )
    
    # Parse webhook data
    try:
        data = json.loads(body)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON"
        )
    
    # Get transaction by order_id (our transaction UUID)
    order_id = data.get("order_id")
    if not order_id:
        return {"status": "ignored", "reason": "no order_id"}
    
    try:
        trans_uuid = UUID(order_id)
    except ValueError:
        return {"status": "ignored", "reason": "invalid order_id"}
    
    result = await session.execute(
        select(CryptoTransaction).where(CryptoTransaction.id == trans_uuid)
    )
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        return {"status": "ignored", "reason": "transaction not found"}
    
    # Update transaction based on payment status
    payment_status = data.get("payment_status", "")
    payment_id = data.get("payment_id")
    
    transaction.payment_id = payment_id or transaction.payment_id
    transaction.txn_hash = data.get("outcome_transaction_hash") or data.get("txn_id")
    transaction.confirmations = data.get("confirmations", 0)
    transaction.updated_at = datetime.utcnow()
    
    # Update status
    if payment_status == "finished":
        if transaction.status != "completed":
            transaction.status = "completed"
            transaction.completed_at = datetime.utcnow()
            
            # Credit account balance for deposits
            if transaction.transaction_type == "deposit":
                account_result = await session.execute(
                    select(Account).where(Account.id == transaction.account_id)
                )
                account = account_result.scalar_one_or_none()
                
                if account:
                    # Credit balance
                    account.balance += transaction.usd_amount
                    account.updated_at = datetime.utcnow()
                    session.add(account)
                    
                    # Create ledger entry
                    ledger_entry = LedgerEntry(
                        id=uuid4(),
                        account_id=account.id,
                        entry_type="deposit",
                        amount=transaction.usd_amount,
                        balance_after=account.balance,
                        currency=account.base_currency,
                        description=f"Crypto deposit: {transaction.crypto_amount} {transaction.crypto_currency}",
                        meta={"transaction_id": str(transaction.id)},
                        created_at=datetime.utcnow(),
                    )
                    session.add(ledger_entry)
    
    elif payment_status in ["confirming", "sending"]:
        transaction.status = "confirming"
    
    elif payment_status in ["failed", "expired"]:
        transaction.status = payment_status
        transaction.error_message = data.get("error_message")
        
        # Refund withdrawal if it failed
        if transaction.transaction_type == "withdrawal" and transaction.status == "failed":
            account_result = await session.execute(
                select(Account).where(Account.id == transaction.account_id)
            )
            account = account_result.scalar_one_or_none()
            
            if account:
                # Refund amount (without fee)
                refund_amount = transaction.usd_amount
                account.balance += refund_amount
                account.updated_at = datetime.utcnow()
                session.add(account)
                
                # Create ledger entry
                ledger_entry = LedgerEntry(
                    id=uuid4(),
                    account_id=account.id,
                    entry_type="refund",
                    amount=refund_amount,
                    balance_after=account.balance,
                    currency=account.base_currency,
                    description=f"Withdrawal refund (failed transaction)",
                    meta={"transaction_id": str(transaction.id)},
                    created_at=datetime.utcnow(),
                )
                session.add(ledger_entry)
    
    session.add(transaction)
    await session.commit()
    
    return {"status": "ok", "transaction_id": str(transaction.id)}
