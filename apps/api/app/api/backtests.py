"""Backtest API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List
from datetime import datetime
from uuid import uuid4, UUID

from app.core.database import get_session
from app.core.deps import get_current_user
from app.models.user import User
from app.models.backtest import Backtest
from app.models.instrument import Instrument
from app.schemas.backtest import CreateBacktestRequest, BacktestResponse

router = APIRouter()


@router.post("", response_model=BacktestResponse, status_code=status.HTTP_201_CREATED)
async def create_backtest(
    request: CreateBacktestRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new backtest job.
    
    - Validates date range and instrument
    - Queues backtest job to Celery worker
    - Returns job ID for status tracking
    """
    # Validate instrument
    instrument_result = await session.execute(
        select(Instrument).where(Instrument.id == request.instrument_id)
    )
    instrument = instrument_result.scalar_one_or_none()
    
    if not instrument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instrument not found",
        )
    
    # Validate date range
    if request.end_date <= request.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date",
        )
    
    # Create backtest record
    backtest = Backtest(
        id=uuid4(),
        user_id=current_user.id,
        strategy_id=request.strategy_id,
        instrument_id=request.instrument_id,
        params=request.params,
        start_date=request.start_date,
        end_date=request.end_date,
        initial_capital=request.initial_capital,
        status="pending",
        progress=0.0,
        created_at=datetime.utcnow(),
    )
    
    session.add(backtest)
    await session.commit()
    await session.refresh(backtest)
    
    # Queue backtest job to Celery (Phase 6 will implement full logic)
    # For now, we'll mark it as pending and return the ID
    try:
        from tasks.backtest import run_backtest
        
        # Queue the task
        task = run_backtest.delay(
            str(backtest.id),
            {
                "strategy_id": request.strategy_id,
                "instrument_id": str(request.instrument_id),
                "params": request.params,
                "start_date": request.start_date.isoformat(),
                "end_date": request.end_date.isoformat(),
                "initial_capital": request.initial_capital,
            }
        )
        
        # Store task ID
        backtest.task_id = task.id
        backtest.status = "running"
        backtest.started_at = datetime.utcnow()
        session.add(backtest)
        await session.commit()
        await session.refresh(backtest)
        
    except Exception as e:
        # If Celery is not available, just mark as pending
        print(f"Warning: Could not queue backtest task: {e}")
        backtest.status = "pending"
        session.add(backtest)
        await session.commit()
    
    return backtest


@router.get("", response_model=List[BacktestResponse])
async def get_backtests(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get all backtests for the current user.
    
    - Returns list of backtest jobs
    - Includes status and results
    """
    result = await session.execute(
        select(Backtest)
        .where(Backtest.user_id == current_user.id)
        .order_by(Backtest.created_at.desc())
    )
    backtests = result.scalars().all()
    
    return backtests


@router.get("/{backtest_id}", response_model=BacktestResponse)
async def get_backtest(
    backtest_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get a specific backtest by ID.
    
    - Returns backtest details and results
    - Includes progress and metrics if completed
    """
    try:
        backtest_uuid = UUID(backtest_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid backtest ID format",
        )
    
    result = await session.execute(
        select(Backtest).where(
            Backtest.id == backtest_uuid,
            Backtest.user_id == current_user.id,
        )
    )
    backtest = result.scalar_one_or_none()
    
    if not backtest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backtest not found",
        )
    
    # If backtest has a task_id, check Celery task status
    if backtest.task_id and backtest.status == "running":
        try:
            from celery.result import AsyncResult
            from celery_app import app
            
            task = AsyncResult(backtest.task_id, app=app)
            
            if task.ready():
                if task.successful():
                    result = task.result
                    backtest.status = "completed"
                    backtest.progress = 1.0
                    backtest.metrics = result.get("metrics", {})
                    backtest.completed_at = datetime.utcnow()
                else:
                    backtest.status = "failed"
                    backtest.error_message = str(task.info)
                
                session.add(backtest)
                await session.commit()
                await session.refresh(backtest)
            
        except Exception as e:
            print(f"Warning: Could not check task status: {e}")
    
    return backtest


@router.delete("/{backtest_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_backtest(
    backtest_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a backtest.
    
    - Removes backtest record
    - Does not cancel running jobs (Phase 6 will implement)
    """
    try:
        backtest_uuid = UUID(backtest_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid backtest ID format",
        )
    
    result = await session.execute(
        select(Backtest).where(
            Backtest.id == backtest_uuid,
            Backtest.user_id == current_user.id,
        )
    )
    backtest = result.scalar_one_or_none()
    
    if not backtest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backtest not found",
        )
    
    await session.delete(backtest)
    await session.commit()
    
    return None
