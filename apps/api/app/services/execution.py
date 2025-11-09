"""Order execution simulator service."""

from decimal import Decimal
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4
import random

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.instrument import Instrument
from app.models.account import Account
from app.models.order import Order
from app.models.position import Position
from app.models.candle import Candle
from app.models.ledger_entry import LedgerEntry


class ExecutionService:
    """
    Simulates order execution with realistic fills, slippage, and fees.
    
    This service models:
    - Bid/ask spreads
    - Market slippage
    - Commission fees
    - Margin calculations
    - Position opening/closing
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def execute_order(self, order: Order, account: Account, instrument: Instrument) -> Dict[str, Any]:
        """
        Execute a simulated order.
        
        Args:
            order: Order to execute
            account: Account placing the order
            instrument: Instrument being traded
            
        Returns:
            Execution result with fill details
        """
        # Get current market price from latest candle
        current_price = await self._get_current_price(instrument.id)
        
        if current_price is None:
            order.status = "rejected"
            order.canceled_at = datetime.utcnow()
            self.session.add(order)
            return {
                "success": False,
                "error": "No market data available",
            }
        
        # Calculate fill price based on order type
        fill_price = await self._calculate_fill_price(
            order, instrument, current_price
        )
        
        # Calculate slippage
        slippage = self._calculate_slippage(
            order.order_type, order.size, instrument
        )
        
        # Apply slippage to fill price
        if order.side == "buy":
            fill_price = fill_price * (1 + slippage)
        else:
            fill_price = fill_price * (1 - slippage)
        
        # Calculate commission
        commission = self._calculate_commission(order.size, fill_price, instrument)
        
        # Calculate margin required
        margin_required = (order.size * fill_price) / order.leverage
        
        # Check if account has sufficient margin
        if account.margin_available < margin_required + commission:
            order.status = "rejected"
            order.canceled_at = datetime.utcnow()
            self.session.add(order)
            return {
                "success": False,
                "error": "Insufficient margin",
                "required": float(margin_required + commission),
                "available": float(account.margin_available),
            }
        
        # Update order with execution details
        order.status = "filled"
        order.filled_size = order.size
        order.fill_price = fill_price
        order.slippage = slippage
        order.commission = commission
        order.margin_required = margin_required
        order.filled_at = datetime.utcnow()
        self.session.add(order)
        
        # Create or update position
        position = await self._handle_position(order, account, instrument, fill_price)
        
        # Update account balances
        account.margin_used += margin_required
        account.margin_available -= (margin_required + commission)
        account.balance -= commission  # Deduct commission
        account.equity = account.balance + account.margin_used
        account.updated_at = datetime.utcnow()
        self.session.add(account)
        
        # Create ledger entry for commission
        commission_entry = LedgerEntry(
            id=uuid4(),
            account_id=account.id,
            entry_type="commission",
            amount=-commission,
            balance_after=account.balance,
            currency=account.base_currency,
            order_id=order.id,
            description=f"Commission for order {order.id}",
            meta={
                "order_type": order.order_type,
                "side": order.side,
                "size": float(order.size),
                "fill_price": float(fill_price),
            },
            created_at=datetime.utcnow(),
        )
        self.session.add(commission_entry)
        
        return {
            "success": True,
            "order_id": str(order.id),
            "position_id": str(position.id) if position else None,
            "fill_price": float(fill_price),
            "slippage": float(slippage),
            "commission": float(commission),
            "margin_required": float(margin_required),
        }
    
    async def _get_current_price(self, instrument_id) -> Optional[Decimal]:
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
    
    async def _calculate_fill_price(
        self, order: Order, instrument: Instrument, current_price: Decimal
    ) -> Decimal:
        """Calculate the fill price based on order type."""
        if order.order_type == "market":
            # Market orders fill at current price + spread
            spread_amount = current_price * instrument.base_spread
            if order.side == "buy":
                return current_price + spread_amount
            else:
                return current_price - spread_amount
        
        elif order.order_type == "limit":
            # Limit orders fill at limit price if market reached it
            # For simulation, we assume it's reached
            return order.price
        
        elif order.order_type in ["stop", "stop_limit"]:
            # Stop orders fill at stop price (simplified)
            return order.stop_price or current_price
        
        else:
            # Default to current price
            return current_price
    
    def _calculate_slippage(
        self, order_type: str, size: Decimal, instrument: Instrument
    ) -> Decimal:
        """
        Calculate slippage based on order size and instrument.
        
        Slippage increases with order size.
        """
        if order_type == "limit":
            # Limit orders have no slippage (executed at limit price)
            return Decimal("0")
        
        # Base slippage from instrument
        base_slippage = instrument.slippage_factor
        
        # Size-based slippage (larger orders = more slippage)
        # Add random component for realism
        size_factor = float(size) * 0.001  # 0.1% per unit size
        random_factor = random.uniform(-0.0002, 0.0002)  # ±0.02%
        
        total_slippage = float(base_slippage) + size_factor + random_factor
        
        # Cap slippage at 1%
        return Decimal(str(min(max(total_slippage, 0), 0.01)))
    
    def _calculate_commission(
        self, size: Decimal, price: Decimal, instrument: Instrument
    ) -> Decimal:
        """
        Calculate trading commission.
        
        Default: 0.02% of notional value
        """
        notional_value = size * price
        commission_rate = Decimal("0.0002")  # 0.02%
        commission = notional_value * commission_rate
        
        # Minimum commission of 0.01
        return max(commission, Decimal("0.01"))
    
    async def _handle_position(
        self, order: Order, account: Account, instrument: Instrument, fill_price: Decimal
    ) -> Optional[Position]:
        """
        Create a new position or update existing one.
        
        For simplicity, we create a new position for each order.
        In a full implementation, this would aggregate positions.
        """
        # Check if there's an existing opposite position to close
        opposite_side = "short" if order.side == "buy" else "long"
        
        result = await self.session.execute(
            select(Position)
            .where(Position.account_id == account.id)
            .where(Position.instrument_id == order.instrument_id)
            .where(Position.side == opposite_side)
            .where(Position.is_open == True)
            .limit(1)
        )
        existing_position = result.scalar_one_or_none()
        
        if existing_position and existing_position.size <= order.size:
            # Close existing position
            pnl = self._calculate_position_pnl(
                existing_position, fill_price
            )
            
            existing_position.is_open = False
            existing_position.closed_at = datetime.utcnow()
            existing_position.realized_pnl = pnl
            existing_position.updated_at = datetime.utcnow()
            self.session.add(existing_position)
            
            # Update account balance with P&L
            account.balance += pnl
            account.margin_used -= existing_position.margin_used
            account.margin_available += existing_position.margin_used
            
            # Create ledger entry for P&L
            pnl_entry = LedgerEntry(
                id=uuid4(),
                account_id=account.id,
                entry_type="trade_pnl",
                amount=pnl,
                balance_after=account.balance,
                currency=account.base_currency,
                order_id=order.id,
                position_id=existing_position.id,
                description=f"P&L from closing position {existing_position.id}",
                meta={
                    "entry_price": float(existing_position.entry_price),
                    "exit_price": float(fill_price),
                    "size": float(existing_position.size),
                },
                created_at=datetime.utcnow(),
            )
            self.session.add(pnl_entry)
            
            # If order size is larger, create new position for remainder
            if order.size > existing_position.size:
                remaining_size = order.size - existing_position.size
                return await self._create_position(
                    order, account, instrument, fill_price, remaining_size
                )
            
            return existing_position
        
        # Create new position
        return await self._create_position(
            order, account, instrument, fill_price, order.size
        )
    
    async def _create_position(
        self, order: Order, account: Account, instrument: Instrument,
        fill_price: Decimal, size: Decimal
    ) -> Position:
        """Create a new position."""
        side = "long" if order.side == "buy" else "short"
        margin_used = (size * fill_price) / order.leverage
        
        position = Position(
            id=uuid4(),
            account_id=account.id,
            instrument_id=order.instrument_id,
            side=side,
            size=size,
            entry_price=fill_price,
            current_price=fill_price,
            unrealized_pnl=Decimal("0"),
            realized_pnl=Decimal("0"),
            leverage=order.leverage,
            margin_used=margin_used,
            is_open=True,
            bot_id=order.bot_id,
            opened_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        self.session.add(position)
        return position
    
    def _calculate_position_pnl(self, position: Position, exit_price: Decimal) -> Decimal:
        """Calculate P&L for closing a position."""
        if position.side == "long":
            # Long: profit if exit > entry
            pnl = (exit_price - position.entry_price) * position.size
        else:
            # Short: profit if exit < entry
            pnl = (position.entry_price - exit_price) * position.size
        
        return pnl
