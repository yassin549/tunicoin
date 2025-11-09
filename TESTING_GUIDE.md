# 🧪 Complete Testing Guide — Phases 1-3

This guide will help you test everything we've built so far: infrastructure, database, and all API endpoints.

---

## 📋 Prerequisites

Before testing, ensure you have:
- ✅ Docker Desktop installed and running
- ✅ Windows PowerShell or Command Prompt
- ✅ curl or Postman for API testing
- ✅ A web browser

---

## 🚀 Step 1: Start All Services

### Option A: Using Makefile (Recommended)
```bash
cd "c:\Users\khoua\OneDrive\Desktop\crypto exchange"
make dev
```

### Option B: Using Docker Compose
```bash
cd "c:\Users\khoua\OneDrive\Desktop\crypto exchange"
docker-compose up -d
```

### Verify Services
```bash
docker-compose ps
```

**Expected Output:**
```
NAME                      STATUS
tunicoin-postgres         Up
tunicoin-redis            Up
tunicoin-pgadmin          Up
tunicoin-api              Up
tunicoin-worker           Up
tunicoin-web              Up
```

---

## 🗄️ Step 2: Initialize Database

### Run Migrations
```bash
# Create all database tables
docker exec tunicoin-api alembic upgrade head
```

**Expected Output:**
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial schema
```

### Seed Demo Data
```bash
# Generate demo user + 43,200 candles
docker exec tunicoin-api python -m app.scripts.seed
```

**Expected Output:**
```
🌱 Starting database seed...
👤 Creating demo user...
💰 Creating demo account with $10,000...
📊 Creating instruments...
📈 Generating 30 days of 1m candle data...
   Generated 1,000 candles...
   ...
✅ Created 43,200 total candles

📝 Demo Account Details:
   Email: demo@tunicoin.local
   Password: demo123
   Balance: $10,000.00
```

---

## 🌐 Step 3: Verify API is Running

### Check API Health
```bash
curl http://localhost:8000/health
```

**Expected:**
```json
{"status":"healthy","version":"1.0.0"}
```

### View API Documentation
Open in browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔐 Step 4: Test Authentication

### Test 1: Signup New User
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"password\":\"Test1234\"}"
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Save the access_token** — you'll need it for subsequent requests!

### Test 2: Login with Demo User
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"demo@tunicoin.local\",\"password\":\"demo123\"}"
```

**Save this access_token for testing!**

### Test 3: Refresh Token
```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\":\"YOUR_REFRESH_TOKEN\"}"
```

---

## 📊 Step 5: Test Market Data

### Test 1: Get All Instruments
```bash
curl http://localhost:8000/api/market/instruments
```

**Expected:** List of 5 instruments (BTC-USD, ETH-USD, BTC-FUT, SPX-FUT, EURUSD)

### Test 2: Get Specific Instrument
```bash
curl http://localhost:8000/api/market/instruments/BTC-USD
```

**Expected:** Detailed BTC-USD configuration

### Test 3: Get Candle Data
```bash
curl "http://localhost:8000/api/market/BTC-USD/candles?timeframe=1m&limit=10"
```

**Expected:** 10 most recent 1-minute candles for BTC-USD

---

## 💰 Step 6: Test Account Management

**Important:** Replace `YOUR_ACCESS_TOKEN` with the token from Step 4!

### Test 1: Create Account
```bash
curl -X POST http://localhost:8000/api/accounts \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"My Trading Account\",\"initial_balance\":5000,\"is_demo\":true,\"max_leverage\":10}"
```

**Save the account `id` from the response!**

### Test 2: List All Accounts
```bash
curl http://localhost:8000/api/accounts \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Test 3: Get Account Details
```bash
curl http://localhost:8000/api/accounts/YOUR_ACCOUNT_ID \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📈 Step 7: Test Order Placement

**You'll need:**
- `YOUR_ACCESS_TOKEN` from Step 4
- `YOUR_ACCOUNT_ID` from Step 6
- An `instrument_id` from Step 5 (use BTC-USD's ID)

### Test 1: Place Market Buy Order
```bash
curl -X POST "http://localhost:8000/api/accounts/YOUR_ACCOUNT_ID/orders" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"instrument_id\":\"INSTRUMENT_ID\",\"order_type\":\"market\",\"side\":\"buy\",\"size\":0.01,\"leverage\":1}"
```

**Expected:**
- Order is instantly filled
- `status`: "filled"
- `fill_price`: Current BTC price + spread
- Commission charged (~0.02%)
- Position created

### Test 2: List Orders
```bash
curl "http://localhost:8000/api/accounts/YOUR_ACCOUNT_ID/orders" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Test 3: Place Limit Order
```bash
curl -X POST "http://localhost:8000/api/accounts/YOUR_ACCOUNT_ID/orders" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"instrument_id\":\"INSTRUMENT_ID\",\"order_type\":\"limit\",\"side\":\"sell\",\"size\":0.01,\"price\":55000,\"leverage\":1}"
```

---

## 📊 Step 8: Test Position Management

### Test 1: Get Open Positions
```bash
curl "http://localhost:8000/api/accounts/YOUR_ACCOUNT_ID/positions?is_open=true" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected:** Position from your buy order with real-time P&L

### Test 2: Get Position Details
```bash
curl "http://localhost:8000/api/accounts/YOUR_ACCOUNT_ID/positions/POSITION_ID" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Test 3: Update Stop Loss / Take Profit
```bash
curl -X PATCH "http://localhost:8000/api/accounts/YOUR_ACCOUNT_ID/positions/POSITION_ID" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"stop_loss\":48000,\"take_profit\":52000}"
```

### Test 4: Close Position
```bash
curl -X POST "http://localhost:8000/api/accounts/YOUR_ACCOUNT_ID/positions/close" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"position_id\":\"POSITION_ID\"}"
```

**Expected:**
- Position closed at current market price
- Realized P&L calculated
- Account balance updated
- Ledger entry created

---

## 🧪 Step 9: Test Backtesting

### Test 1: Create Backtest Job
```bash
curl -X POST http://localhost:8000/api/backtests \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"strategy_id\":\"ema_crossover\",\"instrument_id\":\"INSTRUMENT_ID\",\"params\":{\"fast_period\":20,\"slow_period\":50},\"start_date\":\"2024-01-01T00:00:00Z\",\"end_date\":\"2024-01-31T23:59:59Z\",\"initial_capital\":10000}"
```

**Expected:** Backtest job created with `status`: "running"

### Test 2: List Backtests
```bash
curl http://localhost:8000/api/backtests \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Test 3: Get Backtest Results
```bash
curl http://localhost:8000/api/backtests/BACKTEST_ID \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🔌 Step 10: Test WebSocket

### Using JavaScript (Browser Console)
```javascript
// 1. Open http://localhost:3000 and open browser console (F12)

// 2. Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/accounts/YOUR_ACCOUNT_ID');

// 3. Handle connection
ws.onopen = () => {
    console.log('✅ WebSocket Connected');
    
    // Authenticate with JWT
    ws.send(JSON.stringify({
        token: 'YOUR_ACCESS_TOKEN'
    }));
};

// 4. Handle messages
ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    console.log('📨 Received:', message);
};

// 5. Handle errors
ws.onerror = (error) => {
    console.error('❌ WebSocket Error:', error);
};

// 6. Handle disconnection
ws.onclose = () => {
    console.log('🔌 WebSocket Disconnected');
};

// 7. Send keepalive ping every 30 seconds
setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({type: 'ping'}));
        console.log('💓 Ping sent');
    }
}, 30000);
```

**Expected Messages:**
```json
// 1. Connection confirmation
{
  "type": "connected",
  "account_id": "uuid",
  "message": "Connected to account stream"
}

// 2. When you place an order (order_update)
{
  "type": "order_update",
  "account_id": "uuid",
  "data": {
    "order_id": "uuid",
    "status": "filled",
    "fill_price": 50000.00
  }
}

// 3. When position P&L changes (position_update)
{
  "type": "position_update",
  "account_id": "uuid",
  "data": {
    "position_id": "uuid",
    "unrealized_pnl": 125.50
  }
}
```

---

## ✅ Full Integration Test

Let's do a complete trading flow:

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@tunicoin.local","password":"demo123"}' \
  | jq -r '.access_token')

echo "Token: $TOKEN"

# 2. Get BTC-USD instrument ID
INSTRUMENT_ID=$(curl -s http://localhost:8000/api/market/instruments/BTC-USD \
  | jq -r '.id')

echo "Instrument ID: $INSTRUMENT_ID"

# 3. Get account ID
ACCOUNT_ID=$(curl -s http://localhost:8000/api/accounts \
  -H "Authorization: Bearer $TOKEN" \
  | jq -r '.[0].id')

echo "Account ID: $ACCOUNT_ID"

# 4. Place buy order
ORDER_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/accounts/$ACCOUNT_ID/orders" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"instrument_id\":\"$INSTRUMENT_ID\",\"order_type\":\"market\",\"side\":\"buy\",\"size\":0.01,\"leverage\":1}")

echo "Order: $ORDER_RESPONSE"

# 5. Get positions
POSITIONS=$(curl -s "http://localhost:8000/api/accounts/$ACCOUNT_ID/positions?is_open=true" \
  -H "Authorization: Bearer $TOKEN")

echo "Positions: $POSITIONS"

# 6. Get account balance
BALANCE=$(curl -s "http://localhost:8000/api/accounts/$ACCOUNT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.balance')

echo "Current Balance: $BALANCE"
```

---

## 🎯 Success Criteria Checklist

Use this checklist to verify everything works:

### Infrastructure
- [ ] Docker containers are running
- [ ] PostgreSQL accessible on port 5432
- [ ] Redis accessible on port 6379
- [ ] API accessible on port 8000
- [ ] Frontend accessible on port 3000

### Database
- [ ] Migrations created 10 tables
- [ ] Demo user exists
- [ ] 5 instruments seeded
- [ ] 43,200 candles generated
- [ ] Can connect via PgAdmin

### Authentication
- [ ] Can signup new user
- [ ] Can login and receive tokens
- [ ] Can refresh access token
- [ ] Invalid credentials rejected
- [ ] JWT validation works

### Market Data
- [ ] Can list instruments
- [ ] Can get instrument details
- [ ] Can fetch candle data
- [ ] Pagination works
- [ ] Date filtering works

### Accounts
- [ ] Can create new account
- [ ] Can list user accounts
- [ ] Can get account details
- [ ] Initial balance set correctly
- [ ] Ledger entry created

### Orders
- [ ] Can place market order
- [ ] Order instantly filled
- [ ] Fill price includes spread
- [ ] Commission calculated
- [ ] Margin validated
- [ ] Insufficient margin rejected
- [ ] Can list orders
- [ ] Can get order details

### Positions
- [ ] Position created on order fill
- [ ] Unrealized P&L calculated
- [ ] Can list positions
- [ ] Can get position details
- [ ] Can update SL/TP
- [ ] Can close position
- [ ] Realized P&L calculated
- [ ] Account balance updated

### WebSocket
- [ ] Can connect to WS endpoint
- [ ] Authentication required
- [ ] Connection message received
- [ ] Can send/receive pings
- [ ] Updates received in real-time

### API Documentation
- [ ] Swagger UI loads at /docs
- [ ] All endpoints documented
- [ ] Can test endpoints in Swagger
- [ ] ReDoc loads at /redoc

---

## 🐛 Troubleshooting

### Issue: "Connection refused"
**Solution:**
```bash
# Check if services are running
docker-compose ps

# Restart services
docker-compose restart
```

### Issue: "401 Unauthorized"
**Solution:**
- Token expired (refresh it)
- Token invalid (login again)
- Check Authorization header format: `Bearer YOUR_TOKEN`

### Issue: "Instrument not found"
**Solution:**
- Run seed script: `make seed`
- Check instrument ID is correct UUID

### Issue: "Insufficient margin"
**Solution:**
- Reduce order size
- Reduce leverage
- Check account balance

### Issue: "WebSocket authentication timeout"
**Solution:**
- Send token within 10 seconds of connecting
- Format: `{"token": "YOUR_ACCESS_TOKEN"}`

---

## 📊 Performance Benchmarks

Expected response times (local):
- Authentication: < 100ms
- Market data: < 50ms
- Order placement: < 200ms
- Position updates: < 100ms
- WebSocket latency: < 10ms

---

## 🎉 What's Working

After completing all tests, you should have:
- ✅ Fully functional authentication system
- ✅ 22 working API endpoints
- ✅ Realistic order execution with slippage
- ✅ Real-time P&L calculations
- ✅ WebSocket streams
- ✅ Complete audit trail in ledger
- ✅ Interactive API documentation

---

## 📝 Next Steps

Once all tests pass, you're ready to:
1. Test via Swagger UI for interactive testing
2. Build frontend UI (Phase 4)
3. Integrate charts and real-time updates (Phase 5)
4. Implement AI bots (Phase 6-7)

---

**Need Help?**
- Check API docs: http://localhost:8000/docs
- View logs: `docker logs tunicoin-api -f`
- Check database: http://localhost:5050 (PgAdmin)

**Ready for Phase 4!** 🚀
