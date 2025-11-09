from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column, JSON


class BotDecision(SQLModel, table=True):
    """Bot decision log for explainability."""

    __tablename__ = "bot_decisions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    bot_id: UUID = Field(foreign_key="bots.id", index=True)
    account_id: UUID = Field(foreign_key="accounts.id", index=True)
    
    # Decision context
    candle_timestamp: datetime = Field(index=True)
    instrument_id: UUID = Field(foreign_key="instruments.id")
    
    # Input indicators (JSON containing all indicator values)
    indicators: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    # Example: {"ema_20": 50000, "ema_50": 49800, "rsi": 65}
    
    # Decision
    decision: str = Field(max_length=50)  # "buy", "sell", "hold", "close"
    reason: str = Field(max_length=1000)  # Human-readable explanation
    
    # Proposed order
    proposed_order: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    
    # Actual order placed (may differ due to risk manager)
    order_id: Optional[UUID] = Field(default=None, foreign_key="orders.id")
    final_order: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    
    # Risk manager adjustments
    risk_adjusted: bool = Field(default=False)
    risk_adjustment_reason: Optional[str] = Field(default=None, max_length=500)
    
    # Execution result
    executed: bool = Field(default=False)
    execution_result: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    class Config:
        json_schema_extra = {
            "example": {
                "decision": "buy",
                "reason": "EMA20 crossed above EMA50",
                "indicators": {"ema_20": 50000, "ema_50": 49800},
                "executed": True,
            }
        }
