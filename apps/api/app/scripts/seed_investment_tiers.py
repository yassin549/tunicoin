"""
Seed investment tiers into the database.
Run this after running migrations to populate the investment_tiers table.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.investment_tier import InvestmentTier


async def seed_investment_tiers():
    """Seed the investment tiers into the database."""
    
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        echo=True,
    )
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Define the 4 investment tiers
        tiers = [
            InvestmentTier(
                name="basic",
                display_name="Basic",
                minimum_deposit=100.0,
                monthly_return_percentage=25.0,
                annual_roi_percentage=300.0,
                features={
                    "monthly_returns": "25%",
                    "minimum_deposit": "$100",
                    "payout_frequency": "monthly",
                    "support_level": "email",
                    "account_manager": False,
                    "priority_payouts": False,
                    "withdraw_anytime": True,
                },
                is_active=True,
            ),
            InvestmentTier(
                name="premium",
                display_name="Premium",
                minimum_deposit=300.0,
                monthly_return_percentage=50.0,
                annual_roi_percentage=600.0,
                features={
                    "monthly_returns": "50%",
                    "minimum_deposit": "$300",
                    "payout_frequency": "monthly",
                    "support_level": "priority_email",
                    "account_manager": True,
                    "priority_payouts": True,
                    "advanced_analytics": True,
                    "withdraw_anytime": True,
                },
                is_active=True,
            ),
            InvestmentTier(
                name="professional",
                display_name="Professional",
                minimum_deposit=1000.0,
                monthly_return_percentage=60.0,
                annual_roi_percentage=720.0,
                features={
                    "monthly_returns": "60%",
                    "minimum_deposit": "$1,000",
                    "payout_frequency": "monthly",
                    "support_level": "24_7_priority",
                    "account_manager": True,
                    "priority_payouts": True,
                    "advanced_analytics": True,
                    "tax_documentation": True,
                    "early_payout_requests": True,
                    "withdraw_anytime": True,
                },
                is_active=True,
            ),
            InvestmentTier(
                name="investor",
                display_name="Investor",
                minimum_deposit=10000.0,
                monthly_return_percentage=75.0,
                annual_roi_percentage=900.0,
                features={
                    "monthly_returns": "75%",
                    "minimum_deposit": "$10,000",
                    "payout_frequency": "instant",
                    "support_level": "24_7_vip",
                    "personal_account_manager": True,
                    "instant_payout_processing": True,
                    "vip_dashboard": True,
                    "tax_legal_documentation": True,
                    "custom_payout_schedules": True,
                    "dedicated_portfolio_review": True,
                    "withdraw_anytime": True,
                },
                is_active=True,
            ),
        ]
        
        # Add all tiers to session
        for tier in tiers:
            session.add(tier)
        
        # Commit to database
        await session.commit()
        
        print("✅ Successfully seeded 4 investment tiers:")
        for tier in tiers:
            print(f"   - {tier.display_name}: ${tier.minimum_deposit} min, {tier.monthly_return_percentage}% monthly")
    
    await engine.dispose()


if __name__ == "__main__":
    print("🌱 Seeding investment tiers...")
    asyncio.run(seed_investment_tiers())
    print("✅ Done!")
