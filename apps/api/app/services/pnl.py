"""P&L (Profit and Loss) calculation service."""

from decimal import Decimal
from typing import List, Dict, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.position import Position
from app.models.instrument import Instrument
from app.models.candle import Candle


class PnLCalculator:
    """
    Service for calculating profit and loss on positions.
    
    Calculates:
    - Unrealized P&L (open positions)
    - Realized P&L (closed positions)
    - P&L percentages
    - Total account P&L
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def update_position_pnl(self, position: Position) -> Position:
        """
        Update unrealized P&L for an open position.
        
        Args:
            position: Position to update
            
        Returns:
            Updated position
        """
        if not position.is_open:
            return position
        
        # Get current market price
        current_price = await self._get_current_price(position.instrument_id)
        
        if current_price is None:
            return position
        
        # Calculate unrealized P&L
        if position.side == "long":
            # Long: profit if current > entry
            pnl = (current_price - position.entry_price) * position.size
        else:
            # Short: profit if current < entry
            pnl = (position.entry_price - current_price) * position.size
        
        # Update position
        position.current_price = current_price
        position.unrealized_pnl = pnl
        position.updated_at = datetime.utcnow()
        
        self.session.add(position)
        
        return position
    
    async def update_all_positions_pnl(self, account_id) -> List[Position]:
        """
        Update P&L for all open positions in an account.
        
        Args:
            account_id: Account ID
            
        Returns:
            List of updated positions
        """
        # Get all open positions
        result = await self.session.execute(
            select(Position)
            .where(Position.account_id == account_id)
            .where(Position.is_open == True)
        )
        positions = result.scalars().all()
        
        # Update each position
        updated_positions = []
        for position in positions:
            updated = await self.update_position_pnl(position)
            updated_positions.append(updated)
        
        return updated_positions
    
    def calculate_pnl_percentage(self, position: Position) -> float:
        """
        Calculate P&L as a percentage of the position value.
        
        Args:
            position: Position
            
        Returns:
            P&L percentage
        """
        if position.entry_price == 0:
            return 0.0
        
        position_value = position.entry_price * position.size
        
        if position_value == 0:
            return 0.0
        
        pnl = position.unrealized_pnl if position.is_open else position.realized_pnl
        percentage = (float(pnl) / float(position_value)) * 100
        
        return round(percentage, 2)
    
    async def calculate_account_pnl(self, account_id) -> Dict[str, Any]:
        """
        Calculate total P&L for an account.
        
        Args:
            account_id: Account ID
            
        Returns:
            Dictionary with P&L metrics
        """
        # Get all positions (open and closed)
        result = await self.session.execute(
            select(Position).where(Position.account_id == account_id)
        )
        all_positions = result.scalars().all()
        
        # Separate open and closed positions
        open_positions = [p for p in all_positions if p.is_open]
        closed_positions = [p for p in all_positions if not p.is_open]
        
        # Update open positions P&L
        for position in open_positions:
            await self.update_position_pnl(position)
        
        # Calculate totals
        total_unrealized_pnl = sum(
            p.unrealized_pnl for p in open_positions
        )
        
        total_realized_pnl = sum(
            p.realized_pnl for p in closed_positions
        )
        
        total_pnl = total_unrealized_pnl + total_realized_pnl
        
        # Calculate win/loss stats for closed positions
        winning_positions = [p for p in closed_positions if p.realized_pnl > 0]
        losing_positions = [p for p in closed_positions if p.realized_pnl < 0]
        
        win_rate = 0.0
        if closed_positions:
            win_rate = (len(winning_positions) / len(closed_positions)) * 100
        
        avg_win = 0.0
        if winning_positions:
            avg_win = sum(p.realized_pnl for p in winning_positions) / len(winning_positions)
        
        avg_loss = 0.0
        if losing_positions:
            avg_loss = sum(p.realized_pnl for p in losing_positions) / len(losing_positions)
        
        return {
            "total_pnl": float(total_pnl),
            "unrealized_pnl": float(total_unrealized_pnl),
            "realized_pnl": float(total_realized_pnl),
            "open_positions_count": len(open_positions),
            "closed_positions_count": len(closed_positions),
            "winning_positions": len(winning_positions),
            "losing_positions": len(losing_positions),
            "win_rate": round(win_rate, 2),
            "avg_win": float(avg_win),
            "avg_loss": float(avg_loss),
        }
    
    async def _get_current_price(self, instrument_id) -> Decimal:
        """Get the latest price from candle data."""
        result = await self.session.execute(
            select(Candle)
            .where(Candle.instrument_id == instrument_id)
            .where(Candle.timeframe == "1m")
            .order_by(Candle.timestamp.desc())
            .limit(1)
        )
        candle = result.scalar_one_or_none()
        
        if candle:
            return candle.close
        
        return None
