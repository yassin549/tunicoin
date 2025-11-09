# Tunicoin API

FastAPI backend for the Tunicoin virtual CFD futures trading platform.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
DATABASE_URL=postgresql://tunicoin:tunicoin@localhost:5432/tunicoin
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
```

### Database Setup

```bash
# Run migrations
alembic upgrade head

# Seed demo data
python -m app.scripts.seed
```

### Running the Server

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📚 API Documentation

Once the server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🗄️ Database Models

### Core Tables

1. **users** — User authentication and profiles
2. **accounts** — Simulated trading accounts
3. **instruments** — Trading symbols (BTC-USD, ETH-USD, etc.)
4. **candles** — OHLCV candlestick data
5. **orders** — Trading orders (simulated)
6. **positions** — Open positions
7. **ledger_entries** — Double-entry accounting ledger
8. **bots** — AI trading bot instances
9. **backtests** — Backtest jobs and results
10. **bot_decisions** — Bot decision logs for explainability

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# View current version
alembic current
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v
```

## 📦 Project Structure

```
apps/api/
├── app/
│   ├── api/              # API endpoints (Phase 3+)
│   ├── core/             # Core configuration
│   │   ├── config.py     # Settings
│   │   └── database.py   # DB connection
│   ├── models/           # SQLModel database models
│   ├── schemas/          # Pydantic schemas (Phase 3+)
│   ├── services/         # Business logic (Phase 3+)
│   ├── scripts/          # Utility scripts
│   │   └── seed.py       # Database seeding
│   └── main.py           # FastAPI application
├── migrations/           # Alembic migrations
│   ├── versions/         # Migration files
│   └── env.py            # Alembic environment
├── tests/                # Test suite (Phase 3+)
├── requirements.txt      # Python dependencies
├── alembic.ini           # Alembic configuration
├── Dockerfile            # Production Docker image
└── README.md             # This file
```

## 🔧 Configuration

### Settings (app/core/config.py)

All configuration is managed through environment variables using `pydantic-settings`:

- `DATABASE_URL` — PostgreSQL connection string
- `REDIS_URL` — Redis connection string
- `SECRET_KEY` — JWT secret key
- `STRIPE_SECRET_KEY` — Stripe API key
- `BINANCE_PAY_KEY` — Binance Pay API key
- `COINBASE_COMMERCE_KEY` — Coinbase Commerce API key

## 📝 Demo Data

After running the seed script, you can use:

**Demo Account:**
- Email: `demo@tunicoin.local`
- Password: `demo123`
- Initial Balance: $10,000

**Instruments:**
- BTC-USD (Bitcoin / US Dollar)
- ETH-USD (Ethereum / US Dollar)
- BTC-FUT (Bitcoin Futures)
- SPX-FUT (S&P 500 Futures)
- EURUSD (Euro / US Dollar)

**Candle Data:**
- 30 days of 1-minute candles per instrument
- ~8,640 candles per symbol
- Realistic OHLCV data with volatility

## 🚦 API Endpoints (Coming in Phase 3)

### Authentication
- `POST /api/auth/signup` — Register new user
- `POST /api/auth/login` — Login and get JWT token
- `POST /api/auth/refresh` — Refresh JWT token

### Market Data
- `GET /api/market/instruments` — List all instruments
- `GET /api/market/{symbol}/candles` — Get candle data

### Trading
- `POST /api/accounts/:id/orders` — Place order
- `GET /api/accounts/:id/orders` — List orders
- `GET /api/accounts/:id/positions` — List positions

### Bots
- `POST /api/bots/:id/attach` — Subscribe to bot
- `GET /api/bots/:id/status` — Get bot status

### Backtesting
- `POST /api/backtests` — Start backtest
- `GET /api/backtests/:id/results` — Get results

## 🔐 Security

- Passwords hashed with bcrypt
- JWT authentication with refresh tokens
- Rate limiting on auth endpoints
- CORS middleware configured
- SQL injection protection (SQLModel ORM)
- Input validation (Pydantic)

## 📈 Performance

- Connection pooling (10 connections, 20 max overflow)
- Async database operations (asyncpg)
- Redis caching
- GZip compression
- Optimized queries with indexes

## 🐛 Debugging

```bash
# View logs in Docker
docker logs tunicoin-api -f

# Access Python shell in container
docker exec -it tunicoin-api python

# Database shell
docker exec -it tunicoin-postgres psql -U tunicoin -d tunicoin
```

## 📖 Additional Documentation

- [Product Specification](../../description.txt)
- [Build Prompts](../../prompts.txt)
- [Project Vision](../../PROJECT_VISION.md)

---

**Phase 2 Complete** — Database schema, migrations, and seed data ready!
