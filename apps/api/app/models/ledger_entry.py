from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from decimal import Decimal
from sqlalchemy import Column, JSON


class LedgerEntry(SQLModel, table=True):
    """Double-entry accounting ledger for all transactions."""

    __tablename__ = "ledger_entries"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    account_id: UUID = Field(foreign_key="accounts.id", index=True)
    
    # Entry type
    entry_type: str = Field(index=True, max_length=50)
    # Types: "deposit", "withdrawal", "trade_pnl", "commission", "funding", "adjustment"
    
    # Amount (positive = credit, negative = debit)
    amount: Decimal = Field(max_digits=20, decimal_places=2)
    balance_after: Decimal = Field(max_digits=20, decimal_places=2)
    
    # Currency
    currency: str = Field(default="USD", max_length=10)
    
    # References
    order_id: Optional[UUID] = Field(default=None, foreign_key="orders.id")
    position_id: Optional[UUID] = Field(default=None, foreign_key="positions.id")
    
    # Description
    description: Optional[str] = Field(default=None, max_length=500)
    
    # Metadata (JSON for additional context)
    meta: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    class Config:
        json_schema_extra = {
            "example": {
                "entry_type": "trade_pnl",
                "amount": 250.00,
                "balance_after": 10250.00,
                "description": "Profit from BTC-USD position",
            }
        }
