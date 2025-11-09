"""Ledger and accounting service."""

from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.account import Account
from app.models.ledger_entry import LedgerEntry


class LedgerService:
    """
    Service for managing ledger entries and account balances.
    
    Implements double-entry bookkeeping for all transactions.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_entry(
        self,
        account_id: UUID,
        entry_type: str,
        amount: Decimal,
        currency: str = "USD",
        order_id: UUID = None,
        position_id: UUID = None,
        description: str = None,
        meta: Dict[str, Any] = None,
    ) -> LedgerEntry:
        """
        Create a ledger entry.
        
        Args:
            account_id: Account ID
            entry_type: Type of entry (deposit, withdrawal, trade_pnl, commission, etc.)
            amount: Amount (positive = credit, negative = debit)
            currency: Currency code
            order_id: Related order ID (optional)
            position_id: Related position ID (optional)
            description: Human-readable description
            meta: Additional metadata
            
        Returns:
            Created ledger entry
        """
        # Get current account balance
        result = await self.session.execute(
            select(Account).where(Account.id == account_id)
        )
        account = result.scalar_one_or_none()
        
        if not account:
            raise ValueError(f"Account {account_id} not found")
        
        # Calculate new balance
        new_balance = account.balance + amount
        
        # Create entry
        entry = LedgerEntry(
            id=uuid4(),
            account_id=account_id,
            entry_type=entry_type,
            amount=amount,
            balance_after=new_balance,
            currency=currency,
            order_id=order_id,
            position_id=position_id,
            description=description or f"{entry_type.replace('_', ' ').title()}",
            meta=meta or {},
            created_at=datetime.utcnow(),
        )
        
        self.session.add(entry)
        
        # Update account balance
        account.balance = new_balance
        account.updated_at = datetime.utcnow()
        self.session.add(account)
        
        return entry
    
    async def get_entries(
        self,
        account_id: UUID,
        entry_type: str = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[LedgerEntry]:
        """
        Get ledger entries for an account.
        
        Args:
            account_id: Account ID
            entry_type: Filter by entry type (optional)
            limit: Maximum entries to return
            offset: Offset for pagination
            
        Returns:
            List of ledger entries
        """
        query = select(LedgerEntry).where(
            LedgerEntry.account_id == account_id
        )
        
        if entry_type:
            query = query.where(LedgerEntry.entry_type == entry_type)
        
        query = query.order_by(
            LedgerEntry.created_at.desc()
        ).limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def reconcile_account(self, account_id: UUID) -> Dict[str, Any]:
        """
        Reconcile an account by verifying ledger entries sum to current balance.
        
        Args:
            account_id: Account ID
            
        Returns:
            Reconciliation result with any discrepancies
        """
        # Get account
        result = await self.session.execute(
            select(Account).where(Account.id == account_id)
        )
        account = result.scalar_one_or_none()
        
        if not account:
            raise ValueError(f"Account {account_id} not found")
        
        # Get all ledger entries
        entries_result = await self.session.execute(
            select(LedgerEntry)
            .where(LedgerEntry.account_id == account_id)
            .order_by(LedgerEntry.created_at)
        )
        entries = entries_result.scalars().all()
        
        if not entries:
            return {
                "reconciled": True,
                "account_balance": float(account.balance),
                "ledger_balance": 0.0,
                "discrepancy": float(account.balance),
                "entries_count": 0,
            }
        
        # Calculate sum of all entries
        ledger_sum = sum(entry.amount for entry in entries)
        
        # The last entry's balance_after should equal current account balance
        last_entry_balance = entries[-1].balance_after if entries else Decimal("0")
        
        discrepancy = account.balance - last_entry_balance
        is_reconciled = abs(discrepancy) < Decimal("0.01")  # Allow 1 cent tolerance
        
        return {
            "reconciled": is_reconciled,
            "account_balance": float(account.balance),
            "ledger_balance": float(last_entry_balance),
            "ledger_sum": float(ledger_sum),
            "discrepancy": float(discrepancy),
            "entries_count": len(entries),
        }
