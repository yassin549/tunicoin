# 💰 Crypto Payments Integration Guide

## Overview

Tunicoin now uses **NOWPayments.io** as the exclusive payment solution. Users can deposit and withdraw funds using cryptocurrency only.

---

## 🔑 NOWPayments Credentials

### API Keys (Already Configured)
```
API Key: A53GE0J-PPD4G6Z-NFVAC23-GNBEFAH
Public Key: c83c4ff4-30e7-4bd8-8d91-4d4912ac5863
IPN Secret: OemSUwv9OSlRrCjhEV5lMTzfBGKanpen
```

### 🌐 Webhook URL

**Your IPN Callback URL:**
```
https://your-domain.com/api/crypto/webhook
```

**For local development:**
```
http://your-public-ip-or-ngrok-url/api/crypto/webhook
```

⚠️ **Important:** You must configure this webhook URL in your NOWPayments dashboard:
1. Go to https://nowpayments.io/dashboard
2. Navigate to Settings → IPN/Callbacks
3. Add your webhook URL
4. Save changes

---

## 🪙 Supported Cryptocurrencies

- ✅ Bitcoin (BTC)
- ✅ Ethereum (ETH)
- ✅ Tether (USDT)
- ✅ USD Coin (USDC)
- ✅ Litecoin (LTC)
- ✅ Tron (TRX)
- ✅ Binance Coin (BNB)

---

## 📊 Payment Limits & Fees

### Deposits
- **Minimum:** $10 USD
- **Maximum:** No limit
- **Fees:** Network fees only (paid by user)
- **Confirmations Required:** Varies by currency (1-3 blocks)

### Withdrawals
- **Minimum:** $20 USD
- **Maximum:** Account balance
- **Platform Fee:** 1% of withdrawal amount
- **Network Fees:** Deducted from withdrawal amount
- **Processing Time:** 10-30 minutes

---

## 🔄 Payment Flow

### Deposit Flow

```
1. User requests deposit
   ↓
2. API creates NOWPayments invoice/payment
   ↓
3. User receives payment URL & crypto address
   ↓
4. User sends crypto to provided address
   ↓
5. NOWPayments detects payment → sends IPN
   ↓
6. Webhook verifies signature & updates status
   ↓
7. Account balance credited after confirmations
```

### Withdrawal Flow

```
1. User requests withdrawal (provides crypto address)
   ↓
2. API validates address & balance
   ↓
3. Amount + fee deducted from account
   ↓
4. API creates NOWPayments payout
   ↓
5. NOWPayments processes withdrawal
   ↓
6. User receives crypto in their wallet
   ↓
7. Webhook confirms completion
```

---

## 🛠️ API Endpoints

### 1. Get Available Currencies
```http
GET /api/crypto/currencies
```

**Response:**
```json
{
  "currencies": ["btc", "eth", "usdt", "usdc", "ltc", "trx", "bnb"]
}
```

---

### 2. Estimate Crypto Amount
```http
POST /api/crypto/estimate
```

**Request:**
```json
{
  "usd_amount": 100.00,
  "crypto_currency": "btc"
}
```

**Response:**
```json
{
  "usd_amount": 100.00,
  "crypto_currency": "btc",
  "crypto_amount": 0.002,
  "exchange_rate": 50000.00,
  "minimum_amount": 10.00
}
```

---

### 3. Create Deposit
```http
POST /api/crypto/deposit
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "account_id": "uuid",
  "usd_amount": 100.00,
  "pay_currency": "btc"
}
```

**Response:**
```json
{
  "transaction_id": "uuid",
  "payment_id": "12345678",
  "payment_url": "https://nowpayments.io/payment/?iid=...",
  "crypto_currency": "btc",
  "crypto_amount": 0.002,
  "usd_amount": 100.00,
  "pay_address": "bc1q...",
  "status": "pending",
  "expires_at": "2024-01-15T13:00:00Z"
}
```

**User Flow:**
- Redirect user to `payment_url` or show `pay_address`
- User sends exact `crypto_amount` to `pay_address`
- Wait for webhook confirmation
- Account balance auto-credited

---

### 4. Create Withdrawal
```http
POST /api/crypto/withdraw
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "account_id": "uuid",
  "usd_amount": 50.00,
  "crypto_currency": "btc",
  "recipient_address": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
}
```

**Response:**
```json
{
  "transaction_id": "uuid",
  "payment_id": "87654321",
  "crypto_currency": "btc",
  "crypto_amount": 0.001,
  "usd_amount": 50.00,
  "withdrawal_fee": 0.50,
  "net_amount": 49.50,
  "recipient_address": "bc1q...",
  "status": "pending",
  "estimated_time": "10-30 minutes"
}
```

---

### 5. Get Transactions
```http
GET /api/crypto/transactions?transaction_type=deposit&status=completed
Authorization: Bearer <access_token>
```

**Response:**
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "account_id": "uuid",
    "transaction_type": "deposit",
    "crypto_currency": "btc",
    "crypto_amount": 0.002,
    "usd_amount": 100.00,
    "status": "completed",
    "payment_id": "12345678",
    "txn_hash": "abc123...",
    "confirmations": 3,
    "created_at": "2024-01-15T12:00:00Z",
    "completed_at": "2024-01-15T12:30:00Z"
  }
]
```

---

### 6. Get Single Transaction
```http
GET /api/crypto/transactions/{transaction_id}
Authorization: Bearer <access_token>
```

---

## 🔐 Webhook Verification

The webhook endpoint (`/api/crypto/webhook`) automatically:

1. **Verifies HMAC-SHA512 signature** using IPN secret
2. **Validates payload** format
3. **Updates transaction status** in database
4. **Credits/refunds account balance** as needed
5. **Creates ledger entries** for audit trail

### Webhook Payload Example

```json
{
  "payment_id": "12345678",
  "payment_status": "finished",
  "pay_address": "bc1q...",
  "price_amount": 100.00,
  "price_currency": "usd",
  "pay_amount": 0.002,
  "pay_currency": "btc",
  "order_id": "transaction-uuid",
  "order_description": "Deposit to account...",
  "outcome_amount": 0.002,
  "outcome_currency": "btc",
  "outcome_transaction_hash": "abc123...",
  "confirmations": 3
}
```

### Payment Statuses

- `pending` - Waiting for payment
- `confirming` - Payment detected, awaiting confirmations
- `confirmed` - Confirmations received
- `finished` - Payment complete (balance credited)
- `failed` - Payment failed
- `expired` - Payment expired (15 min timeout)
- `refunded` - Payment refunded

---

## 🧪 Testing

### Local Testing with ngrok

Since NOWPayments needs a public URL for webhooks:

1. **Install ngrok:**
   ```bash
   choco install ngrok  # Windows
   ```

2. **Start your API:**
   ```bash
   docker-compose up -d
   ```

3. **Create ngrok tunnel:**
   ```bash
   ngrok http 8000
   ```

4. **Copy forwarding URL:**
   ```
   Forwarding: https://abc123.ngrok.io -> http://localhost:8000
   ```

5. **Update webhook URL in NOWPayments dashboard:**
   ```
   https://abc123.ngrok.io/api/crypto/webhook
   ```

### Test Deposit

```bash
# 1. Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@tunicoin.local","password":"demo123"}'

# Save access_token

# 2. Create deposit
curl -X POST http://localhost:8000/api/crypto/deposit \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id":"YOUR_ACCOUNT_ID",
    "usd_amount":10.00,
    "pay_currency":"btc"
  }'

# 3. Use payment_url or pay_address to make test payment
# 4. Check transaction status
curl http://localhost:8000/api/crypto/transactions/TRANSACTION_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Withdrawal

```bash
curl -X POST http://localhost:8000/api/crypto/withdraw \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id":"YOUR_ACCOUNT_ID",
    "usd_amount":20.00,
    "crypto_currency":"btc",
    "recipient_address":"bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
  }'
```

---

## 🗄️ Database Schema

### crypto_transactions Table

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to users |
| account_id | UUID | Foreign key to accounts |
| transaction_type | String | 'deposit' or 'withdrawal' |
| crypto_currency | String | Crypto used (btc, eth, etc.) |
| crypto_amount | Decimal(18,8) | Amount in crypto |
| usd_amount | Decimal(12,2) | Amount in USD |
| exchange_rate | Decimal(18,8) | Exchange rate at time |
| status | String | Transaction status |
| payment_id | String | NOWPayments payment ID |
| invoice_id | String | NOWPayments invoice ID |
| payment_url | String | Payment page URL |
| txn_hash | String | Blockchain transaction hash |
| blockchain_network | String | Network (Bitcoin, Ethereum) |
| confirmations | Integer | Block confirmations |
| recipient_address | String | Withdrawal address |
| withdrawal_fee | Decimal(12,2) | Fee charged (withdrawals) |
| notes | String | Additional notes |
| error_message | String | Error details if failed |
| created_at | DateTime | Creation timestamp |
| confirmed_at | DateTime | Confirmation timestamp |
| completed_at | DateTime | Completion timestamp |
| updated_at | DateTime | Last update timestamp |

---

## 📊 Admin Panel Integration

### View Pending Withdrawals

```sql
SELECT 
  ct.id,
  u.email,
  ct.usd_amount,
  ct.crypto_currency,
  ct.crypto_amount,
  ct.recipient_address,
  ct.status,
  ct.created_at
FROM crypto_transactions ct
JOIN users u ON u.id = ct.user_id
WHERE ct.transaction_type = 'withdrawal'
  AND ct.status IN ('pending', 'confirming')
ORDER BY ct.created_at DESC;
```

### Monitor Deposit Success Rate

```sql
SELECT 
  DATE(created_at) as date,
  COUNT(*) as total_deposits,
  SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful,
  SUM(usd_amount) as total_usd,
  AVG(EXTRACT(EPOCH FROM (completed_at - created_at))/60) as avg_minutes
FROM crypto_transactions
WHERE transaction_type = 'deposit'
  AND created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

---

## ⚠️ Important Notes

### Security

1. **Never expose API keys** in frontend code
2. **Always verify webhook signatures** (already implemented)
3. **Validate crypto addresses** before withdrawals (already implemented)
4. **Use HTTPS** in production for webhook URL

### Production Checklist

- [ ] Configure production webhook URL in NOWPayments
- [ ] Set up monitoring for failed transactions
- [ ] Create admin dashboard for transaction monitoring
- [ ] Set up email notifications for large transactions
- [ ] Test all supported cryptocurrencies
- [ ] Configure firewall to allow NOWPayments IPs
- [ ] Set up Sentry for error tracking
- [ ] Create backup/recovery procedures

### Rate Limits

NOWPayments has rate limits:
- **Payments API:** 100 requests/minute
- **Status API:** 300 requests/minute
- **Webhook:** No limit (but verify signature!)

---

## 🔧 Troubleshooting

### Issue: Webhook not receiving callbacks

**Solution:**
1. Check webhook URL is public and accessible
2. Verify webhook URL in NOWPayments dashboard
3. Check firewall settings
4. View ngrok inspector: http://localhost:4040

### Issue: Invalid signature error

**Solution:**
1. Verify IPN secret matches NOWPayments dashboard
2. Check signature calculation in `nowpayments.py`
3. Ensure raw request body is used (not parsed JSON)

### Issue: Payment stuck in "pending"

**Solution:**
1. Check NOWPayments payment status manually
2. User may not have sent funds yet
3. Payment may have expired (15 min default)
4. Check blockchain confirmations

### Issue: Address validation fails

**Solution:**
1. Ensure currency code is lowercase
2. Check address format is correct for currency
3. Some currencies require extra_id (XRP, XLM)

---

## 📚 NOWPayments Resources

- **Dashboard:** https://nowpayments.io/dashboard
- **API Docs:** https://documenter.getpostman.com/view/7907941/S1a32n38
- **Support:** support@nowpayments.io
- **Status Page:** https://status.nowpayments.io

---

## 🚀 Next Steps

1. **Run migration:**
   ```bash
   docker exec tunicoin-api alembic upgrade head
   ```

2. **Test locally with ngrok**

3. **Configure webhook URL in NOWPayments dashboard**

4. **Test deposits and withdrawals**

5. **Monitor transactions in database**

6. **Build frontend UI for crypto payments**

---

**Your Webhook URL for NOWPayments Dashboard:**
```
https://YOUR-DOMAIN.com/api/crypto/webhook
```

**For local testing:**
```
https://YOUR-NGROK-URL.ngrok.io/api/crypto/webhook
```

---

*Last Updated: November 8, 2024*
