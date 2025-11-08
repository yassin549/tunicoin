# Tunicoin — Virtual CFD Futures Trading Platform

> A complete, immersive simulated trading platform with AI-powered trading agents

## 🎯 Overview

Tunicoin is a **virtual CFD futures trading platform** that provides a realistic simulated trading environment where users can:

- 📊 Trade virtual CFD futures with realistic market simulation
- 🤖 Subscribe to AI trading agents that execute strategies automatically
- 📈 Backtest strategies and analyze performance metrics
- 💰 Learn trading without risking real capital
- 🎓 Access educational tools and compete safely

**Important**: Tunicoin simulates CFD & futures trading for educational purposes. No real funds are traded. Past simulated performance is not indicative of future results.

---

## 🏗️ Architecture

This is a monorepo containing 4 main applications:

```
tunicoin/
├── apps/
│   ├── web/          # Next.js 14 Frontend (TypeScript + Tailwind)
│   ├── api/          # FastAPI Backend (Python + SQLModel)
│   ├── worker/       # Celery Workers (Python)
│   └── agent/        # AI Strategy Engine (Python)
├── packages/         # Shared utilities (future)
├── infrastructure/   # Docker, K8s configs
└── docs/            # Documentation
```

---

## 🚀 Quick Start

### Prerequisites

- **Node.js**: v18+ (LTS recommended)
- **Python**: 3.11+
- **Docker**: Latest version
- **Docker Compose**: v2+
- **Git**: Latest version

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd tunicoin

# Start all services
make dev

# Or manually:
docker-compose up -d
```

### Access Points

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **PgAdmin**: http://localhost:5050 (admin@tunicoin.local / admin)
- **Redis**: localhost:6379

---

## 🛠️ Development Commands

```bash
# Start all services
make dev

# Run database migrations
make migrate

# Seed demo data
make seed

# Run tests
make test

# Build production images
make build

# Stop all services
make down

# View logs
make logs

# Clean everything
make clean
```

---

## 📦 Tech Stack

### Frontend (`/apps/web`)
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Charts**: TradingView Lightweight Charts
- **State**: Zustand + React Query
- **Icons**: Lucide React
- **Animations**: Framer Motion

### Backend (`/apps/api`)
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Database**: PostgreSQL 15
- **ORM**: SQLModel + Alembic
- **Cache**: Redis
- **Auth**: JWT + 2FA (TOTP)
- **WebSocket**: FastAPI WebSocket
- **Validation**: Pydantic v2

### Workers (`/apps/worker`)
- **Queue**: Celery
- **Broker**: Redis
- **Tasks**: Bot execution, backtesting, notifications

### AI Agent (`/apps/agent`)
- **Strategies**: Python classes (BaseStrategy)
- **Backtesting**: Pandas + NumPy (vectorized)
- **ML**: Scikit-learn (future)

### Infrastructure
- **Containers**: Docker + Docker Compose
- **Orchestration**: Kubernetes (optional)
- **CI/CD**: GitHub Actions
- **Monitoring**: Sentry, Prometheus, Grafana

---

## 📚 Project Structure

```
tunicoin/
├── apps/
│   ├── web/
│   │   ├── src/
│   │   │   ├── app/              # Next.js App Router pages
│   │   │   ├── components/       # React components
│   │   │   ├── lib/              # Utilities, stores, hooks
│   │   │   └── styles/           # Global styles
│   │   ├── public/               # Static assets
│   │   ├── next.config.js
│   │   ├── tailwind.config.ts
│   │   └── package.json
│   │
│   ├── api/
│   │   ├── app/
│   │   │   ├── api/              # API endpoints
│   │   │   ├── core/             # Core utilities
│   │   │   ├── models/           # Database models
│   │   │   ├── schemas/          # Pydantic schemas
│   │   │   └── services/         # Business logic
│   │   ├── migrations/           # Alembic migrations
│   │   ├── tests/                # Unit & integration tests
│   │   ├── main.py               # FastAPI app entry
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── worker/
│   │   ├── tasks/                # Celery tasks
│   │   ├── celery_app.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── agent/
│       ├── strategies/           # Trading strategies
│       ├── backtesting/          # Backtest engine
│       ├── risk/                 # Risk management
│       ├── explainability/       # Decision logging
│       ├── requirements.txt
│       └── setup.py
│
├── infrastructure/
│   ├── docker-compose.yml
│   ├── docker-compose.dev.yml
│   ├── nginx/                    # Nginx configs
│   └── k8s/                      # Kubernetes manifests (future)
│
├── .github/
│   └── workflows/
│       └── ci.yml                # GitHub Actions
│
├── .gitignore
├── Makefile
├── README.md
├── PROJECT_VISION.md
└── PROGRESS_TRACKER.md
```

---

## 🔐 Environment Variables

### Frontend (`.env.local` in `/apps/web`)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Backend (`.env` in `/apps/api`)
```env
DATABASE_URL=postgresql://tunicoin:tunicoin@localhost:5432/tunicoin
DIRECT_URL=postgresql://tunicoin:tunicoin@localhost:5432/tunicoin
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-change-in-production
STRIPE_SECRET_KEY=sk_test_...
BINANCE_PAY_KEY=...
```

### Worker (`.env` in `/apps/worker`)
```env
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
DATABASE_URL=postgresql://tunicoin:tunicoin@localhost:5432/tunicoin
```

---

## 🧪 Testing

```bash
# Frontend tests
cd apps/web
npm test

# Backend tests
cd apps/api
pytest

# Integration tests
make test
```

---

## 📈 Key Features

### Trading Features
- 6 order types (Market, Limit, Stop, Stop-Limit, Take-Profit, Trailing Stop)
- Real-time WebSocket updates
- Professional TradingView charts
- Position management with P&L tracking
- Simulated spread, slippage, and funding costs

### AI Trading Bot
- Multiple strategy support
- Risk management (position sizing, circuit breakers)
- Explainable decisions
- Backtesting with comprehensive metrics

### Payment Options
- **Fiat**: Stripe subscriptions
- **Crypto**: Binance Pay, Coinbase Commerce
- **On-chain**: WalletConnect + MetaMask (USDC)

### Security & Compliance
- JWT auth with 2FA
- Rate limiting
- Prominent disclaimers
- KYC for withdrawals
- Complete audit logging

---

## 🚦 Development Workflow

1. **Branch**: Create feature branch from `develop`
2. **Develop**: Make changes and commit
3. **Test**: Run tests locally (`make test`)
4. **PR**: Create pull request to `develop`
5. **Review**: Code review and CI checks
6. **Merge**: Merge to `develop` after approval
7. **Deploy**: Deploy to staging, then production

---

## 📖 Documentation

- [Product Specification](./description.txt) — Complete feature specification
- [Build Prompts](./prompts.txt) — 10-phase build plan
- [Project Vision](./PROJECT_VISION.md) — Strategic roadmap
- [Progress Tracker](./PROGRESS_TRACKER.md) — Build checklist

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is proprietary and confidential.

---

## ⚠️ Legal Disclaimer

**Tunicoin simulates CFD & futures trading for educational purposes only. No real funds are traded. Past simulated performance is not indicative of future results.**

Tunicoin is not a broker or custodian and does not execute real market orders. Subscribing to Tunicoin's AI strategies does not constitute investment advice. Users acknowledge they are using a simulated trading environment.

---

## 📧 Contact

- **Website**: [Coming Soon]
- **Email**: support@tunicoin.local
- **GitHub**: [Repository]

---

**Status**: 🚧 Phase 1 Complete — Monorepo Scaffold Ready
**Next**: Phase 2 — Database Schema & Migrations

---

Built with ❤️ for traders who want to learn without risk.
#   t u n i c o i n  
 