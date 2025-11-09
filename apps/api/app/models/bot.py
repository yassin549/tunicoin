from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column, JSON


class Bot(SQLModel, table=True):
    """AI trading bot instance."""

    __tablename__ = "bots"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    account_id: UUID = Field(foreign_key="accounts.id", index=True)
    
    # Bot configuration
    name: str = Field(max_length=255)
    strategy_id: str = Field(max_length=100)  # e.g., "ema_crossover", "rsi_divergence"
    
    # Parameters (JSON for strategy-specific params)
    params: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Status
    status: str = Field(default="idle", max_length=50)
    # Status: "idle", "running", "paused", "error", "stopped"
    
    # Risk settings
    max_position_size: float = Field(default=0.1)  # 10% of account
    max_daily_loss: Optional[float] = Field(default=None)
    max_drawdown: Optional[float] = Field(default=None)
    
    # Performance tracking
    total_trades: int = Field(default=0)
    winning_trades: int = Field(default=0)
    losing_trades: int = Field(default=0)
    total_pnl: float = Field(default=0.0)
    
    # Circuit breaker
    is_circuit_broken: bool = Field(default=False)
    circuit_breaker_reason: Optional[str] = Field(default=None, max_length=500)
    
    # Last execution
    last_execution_at: Optional[datetime] = Field(default=None)
    last_error: Optional[str] = Field(default=None, max_length=1000)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "My EMA Bot",
                "strategy_id": "ema_crossover",
                "status": "running",
                "max_position_size": 0.1,
                "total_trades": 25,
            }
        }
