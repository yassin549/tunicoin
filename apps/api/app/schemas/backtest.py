"""Backtest schemas."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class CreateBacktestRequest(BaseModel):
    """Request to create a backtest job."""
    strategy_id: str = Field(..., max_length=100, description="Strategy identifier (e.g., 'ema_crossover')")
    instrument_id: UUID = Field(..., description="Instrument to backtest")
    params: Dict[str, Any] = Field(default_factory=dict, description="Strategy parameters")
    start_date: datetime = Field(..., description="Backtest start date (UTC)")
    end_date: datetime = Field(..., description="Backtest end date (UTC)")
    initial_capital: float = Field(default=10000.0, gt=0, description="Initial capital")
    
    class Config:
        json_schema_extra = {
            "example": {
                "strategy_id": "ema_crossover",
                "instrument_id": "123e4567-e89b-12d3-a456-426614174000",
                "params": {
                    "fast_period": 20,
                    "slow_period": 50
                },
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-12-31T23:59:59Z",
                "initial_capital": 10000.0
            }
        }


class BacktestResponse(BaseModel):
    """Backtest response."""
    id: UUID
    user_id: UUID
    strategy_id: str
    instrument_id: UUID
    params: Dict[str, Any]
    start_date: datetime
    end_date: datetime
    initial_capital: float
    status: str
    progress: float
    metrics: Optional[Dict[str, Any]] = None
    trade_log_url: Optional[str] = None
    error_message: Optional[str] = None
    task_id: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "456e4567-e89b-12d3-a456-426614174000",
                "strategy_id": "ema_crossover",
                "instrument_id": "789e4567-e89b-12d3-a456-426614174000",
                "params": {"fast_period": 20, "slow_period": 50},
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-12-31T23:59:59Z",
                "initial_capital": 10000.0,
                "status": "completed",
                "progress": 1.0,
                "metrics": {
                    "cagr": 15.5,
                    "sharpe": 1.8,
                    "max_drawdown": -12.3,
                    "win_rate": 62.5,
                    "total_trades": 150
                },
                "trade_log_url": None,
                "error_message": None,
                "task_id": "abc123",
                "created_at": "2024-01-15T12:00:00Z",
                "started_at": "2024-01-15T12:00:01Z",
                "completed_at": "2024-01-15T12:05:30Z"
            }
        }


class BacktestMetrics(BaseModel):
    """Backtest metrics."""
    cagr: float = Field(..., description="Compound Annual Growth Rate (%)")
    sharpe: float = Field(..., description="Sharpe Ratio")
    max_drawdown: float = Field(..., description="Maximum Drawdown (%)")
    win_rate: float = Field(..., description="Win Rate (%)")
    total_trades: int = Field(..., description="Total number of trades")
    winning_trades: int = Field(..., description="Number of winning trades")
    losing_trades: int = Field(..., description="Number of losing trades")
    avg_win: float = Field(..., description="Average winning trade amount")
    avg_loss: float = Field(..., description="Average losing trade amount")
    profit_factor: float = Field(..., description="Profit Factor (gross profit / gross loss)")
    expectancy: float = Field(..., description="Expected value per trade")
    
    class Config:
        json_schema_extra = {
            "example": {
                "cagr": 15.5,
                "sharpe": 1.8,
                "max_drawdown": -12.3,
                "win_rate": 62.5,
                "total_trades": 150,
                "winning_trades": 94,
                "losing_trades": 56,
                "avg_win": 125.50,
                "avg_loss": -87.30,
                "profit_factor": 1.75,
                "expectancy": 52.15
            }
        }
