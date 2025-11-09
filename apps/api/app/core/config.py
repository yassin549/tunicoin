from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # App
    APP_NAME: str = "ExtraCoin"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str
    DIRECT_URL: Optional[str] = None

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    # URLs
    API_URL: str = Field(default="http://localhost:8000", env="API_URL")
    FRONTEND_URL: str = Field(default="http://localhost:3000", env="FRONTEND_URL")

    # Stripe
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    # Binance Pay
    BINANCE_PAY_KEY: Optional[str] = None
    BINANCE_PAY_SECRET: Optional[str] = None

    # Coinbase Commerce
    COINBASE_COMMERCE_KEY: Optional[str] = None

    # NOWPayments.io - Crypto Payment Gateway
    NOWPAYMENTS_API_KEY: str = Field(default="A53GE0J-PPD4G6Z-NFVAC23-GNBEFAH", env="NOWPAYMENTS_API_KEY")
    NOWPAYMENTS_PUBLIC_KEY: str = Field(default="c83c4ff4-30e7-4bd8-8d91-4d4912ac5863", env="NOWPAYMENTS_PUBLIC_KEY")
    NOWPAYMENTS_IPN_SECRET: str = Field(default="OemSUwv9OSlRrCjhEV5lMTzfBGKanpen", env="NOWPAYMENTS_IPN_SECRET")
    NOWPAYMENTS_BASE_URL: str = Field(default="https://api.nowpayments.io/v1", env="NOWPAYMENTS_BASE_URL")

    # Supported cryptocurrencies for deposits/withdrawals
    SUPPORTED_CRYPTO: list = ["btc", "eth", "usdt", "usdc", "ltc", "trx", "bnb"]

    # Minimum deposit amounts (in USD equivalent)
    MIN_DEPOSIT_USD: float = Field(default=10.0, env="MIN_DEPOSIT_USD")
    MIN_WITHDRAWAL_USD: float = Field(default=20.0, env="MIN_WITHDRAWAL_USD")

    # Withdrawal fee percentage
    WITHDRAWAL_FEE_PERCENT: float = Field(default=1.0, env="WITHDRAWAL_FEE_PERCENT")

    # Sentry
    SENTRY_DSN: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
