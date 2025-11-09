"""API routes package."""

from .auth import router as auth_router
from .market import router as market_router
from .accounts import router as accounts_router
from .orders import router as orders_router
from .positions import router as positions_router
from .backtests import router as backtests_router
from .investment import router as investment_router

__all__ = [
    "auth_router",
    "market_router",
    "accounts_router",
    "orders_router",
    "positions_router",
    "backtests_router",
    "investment_router",
]
