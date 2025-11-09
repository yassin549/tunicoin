from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column, JSON


class Backtest(SQLModel, table=True):
    """Backtest job and results."""

    __tablename__ = "backtests"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    
    # Backtest configuration
    strategy_id: str = Field(max_length=100)
    instrument_id: UUID = Field(foreign_key="instruments.id")
    
    # Parameters
    params: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Date range
    start_date: datetime
    end_date: datetime
    initial_capital: float = Field(default=10000.0)
    
    # Status
    status: str = Field(default="pending", max_length=50)
    # Status: "pending", "running", "completed", "failed", "canceled"
    
    # Progress
    progress: float = Field(default=0.0)  # 0.0 to 1.0
    
    # Results (JSON containing metrics)
    metrics: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    # Metrics: cagr, sharpe, max_drawdown, win_rate, total_trades, etc.
    
    # Trade log reference (could be stored in S3/file system)
    trade_log_url: Optional[str] = Field(default=None, max_length=500)
    
    # Error handling
    error_message: Optional[str] = Field(default=None, max_length=1000)
    
    # Task ID (Celery)
    task_id: Optional[str] = Field(default=None, max_length=255)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "strategy_id": "ema_crossover",
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-12-31T23:59:59Z",
                "initial_capital": 10000.0,
                "status": "completed",
                "metrics": {
                    "cagr": 15.5,
                    "sharpe": 1.8,
                    "max_drawdown": -12.3,
                },
            }
        }
