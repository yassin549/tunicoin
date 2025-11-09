"""
Seed script to populate database with demo data.

Creates:
- 1 demo user
- 1 demo account with $10,000
- 5 instruments (BTC-USD, ETH-USD, BTC-FUT, S&P-FUT, EURUSD)
- 30 days of 1m candle data per instrument
"""

import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4
import random
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import select

from app.core.config import settings
from app.models import User, Account, Instrument, Candle

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Create async engine
engine = create_async_engine(
    str(settings.DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://"),
    echo=False,
)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def generate_candle_data(base_price: float, volatility: float = 0.02) -> dict:
    """
    Generate realistic OHLCV candle data.
    
    Args:
        base_price: Starting price
        volatility: Price volatility (default 2%)
    
    Returns:
        Dict with open, high, low, close, volume
    """
    open_price = base_price * (1 + random.uniform(-volatility, volatility))
    close_price = open_price * (1 + random.uniform(-volatility, volatility))
    high_price = max(open_price, close_price) * (1 + random.uniform(0, volatility / 2))
    low_price = min(open_price, close_price) * (1 - random.uniform(0, volatility / 2))
    volume = random.uniform(10, 1000)
    
    return {
        "open": Decimal(str(round(open_price, 2))),
        "high": Decimal(str(round(high_price, 2))),
        "low": Decimal(str(round(low_price, 2))),
        "close": Decimal(str(round(close_price, 2))),
        "volume": Decimal(str(round(volume, 4))),
    }


async def seed_database():
    """Seed the database with initial data."""
    
    async with async_session() as session:
        print("🌱 Starting database seed...")
        
        # Check if data already exists
        result = await session.execute(select(User))
        existing_users = result.scalars().all()
        if existing_users:
            print("⚠️  Database already seeded. Skipping...")
            return
        
        # 1. Create demo user
        print("👤 Creating demo user...")
        demo_user = User(
            id=uuid4(),
            email="demo@tunicoin.local",
            hashed_password=pwd_context.hash("demo123"),
            is_verified=True,
            is_active=True,
            is_admin=False,
            plan_id="free",
            kyc_status="approved",
        )
        session.add(demo_user)
        await session.flush()
        
        # 2. Create demo account
        print("💰 Creating demo account with $10,000...")
        demo_account = Account(
            id=uuid4(),
            user_id=demo_user.id,
            name="Demo Account",
            base_currency="USD",
            balance=Decimal("10000.00"),
            equity=Decimal("10000.00"),
            margin_used=Decimal("0.00"),
            margin_available=Decimal("10000.00"),
            is_demo=True,
            is_active=True,
            max_leverage=10,
        )
        session.add(demo_account)
        
        # 3. Create instruments
        print("📊 Creating instruments...")
        instruments_data = [
            {
                "symbol": "BTC-USD",
                "name": "Bitcoin / US Dollar",
                "instrument_type": "crypto",
                "base_price": 50000.00,
                "tick_size": Decimal("0.01"),
                "contract_size": Decimal("1"),
                "base_currency": "BTC",
                "quote_currency": "USD",
                "base_spread": Decimal("0.001"),
                "funding_rate": Decimal("0.0001"),
                "slippage_factor": Decimal("0.0001"),
                "min_size": Decimal("0.001"),
            },
            {
                "symbol": "ETH-USD",
                "name": "Ethereum / US Dollar",
                "instrument_type": "crypto",
                "base_price": 3000.00,
                "tick_size": Decimal("0.01"),
                "contract_size": Decimal("1"),
                "base_currency": "ETH",
                "quote_currency": "USD",
                "base_spread": Decimal("0.001"),
                "funding_rate": Decimal("0.0001"),
                "slippage_factor": Decimal("0.0001"),
                "min_size": Decimal("0.01"),
            },
            {
                "symbol": "BTC-FUT",
                "name": "Bitcoin Futures",
                "instrument_type": "futures",
                "base_price": 50500.00,
                "tick_size": Decimal("0.5"),
                "contract_size": Decimal("1"),
                "base_currency": "BTC",
                "quote_currency": "USD",
                "base_spread": Decimal("0.0015"),
                "funding_rate": Decimal("0.0002"),
                "slippage_factor": Decimal("0.0002"),
                "min_size": Decimal("0.01"),
            },
            {
                "symbol": "SPX-FUT",
                "name": "S&P 500 Futures",
                "instrument_type": "futures",
                "base_price": 4500.00,
                "tick_size": Decimal("0.25"),
                "contract_size": Decimal("50"),
                "base_currency": "USD",
                "quote_currency": "USD",
                "base_spread": Decimal("0.0005"),
                "funding_rate": Decimal("0.00005"),
                "slippage_factor": Decimal("0.00005"),
                "min_size": Decimal("1"),
            },
            {
                "symbol": "EURUSD",
                "name": "Euro / US Dollar",
                "instrument_type": "forex",
                "base_price": 1.10,
                "tick_size": Decimal("0.00001"),
                "contract_size": Decimal("100000"),
                "base_currency": "EUR",
                "quote_currency": "USD",
                "base_spread": Decimal("0.00002"),
                "funding_rate": Decimal("0.00001"),
                "slippage_factor": Decimal("0.00001"),
                "min_size": Decimal("0.01"),
            },
        ]
        
        instruments = []
        for instr_data in instruments_data:
            base_price = instr_data.pop("base_price")
            instrument = Instrument(
                id=uuid4(),
                **instr_data,
            )
            instruments.append((instrument, base_price))
            session.add(instrument)
        
        await session.flush()
        
        # 4. Generate candle data for each instrument
        print("📈 Generating 30 days of 1m candle data...")
        timeframes = ["1m"]
        start_date = datetime.utcnow() - timedelta(days=30)
        
        candles_created = 0
        for instrument, base_price in instruments:
            current_price = base_price
            
            for timeframe in timeframes:
                # Generate candles for 30 days (1 per minute = 43,200 candles)
                # We'll generate 1 candle per 5 minutes to reduce data (8,640 candles per instrument)
                current_time = start_date
                end_date = datetime.utcnow()
                
                while current_time < end_date:
                    candle_data = generate_candle_data(current_price, volatility=0.015)
                    current_price = float(candle_data["close"])
                    
                    candle = Candle(
                        id=uuid4(),
                        instrument_id=instrument.id,
                        timeframe=timeframe,
                        timestamp=current_time,
                        **candle_data,
                    )
                    session.add(candle)
                    candles_created += 1
                    
                    # Move to next candle (5 minutes)
                    current_time += timedelta(minutes=5)
                    
                    # Batch commit every 1000 candles for performance
                    if candles_created % 1000 == 0:
                        await session.flush()
                        print(f"   Generated {candles_created:,} candles...")
        
        print(f"✅ Created {candles_created:,} total candles")
        
        # Commit all changes
        await session.commit()
        
        print("\n✅ Database seeded successfully!")
        print("\n📝 Demo Account Details:")
        print(f"   Email: demo@tunicoin.local")
        print(f"   Password: demo123")
        print(f"   Balance: $10,000.00")
        print(f"   Instruments: {len(instruments)} symbols")
        print(f"   Candles: {candles_created:,} data points")


async def main():
    """Main entry point."""
    try:
        await seed_database()
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
