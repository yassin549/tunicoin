# ExtraCoin Investment Platform - Implementation Prompts

⚠️ **LEGAL WARNING: This platform requires securities registration, MSB licensing, and KYC/AML compliance before launch.**

---

## Phase 0: Legal Foundation (REQUIRED FIRST)
1. Form business entity (LLC/C-Corp)
2. Hire securities attorney
3. File SEC Investment Advisor registration
4. Apply for MSB licenses
5. Set up KYC/AML systems
6. Purchase insurance
7. **DO NOT PROCEED WITHOUT LEGAL CLEARANCE**

---

## Phase 1: Rebrand Tunicoin → ExtraCoin
- Update all text references
- New branding/logo
- Update legal documents
- Change database names (optional)

---

## Phase 2: Investment Tiers System
**New Tables:** investment_tiers, investment_accounts, deposits, payouts, investment_returns, kyc_submissions

**Tiers:**
- Basic: $100 min, 25% monthly return
- Premium: $300 min, 50% monthly return
- Professional: $1K min, 60% monthly return
- Investor: $10K min, 75% monthly return

---

## Phase 3: Investment Dashboard
**Pages:** /dashboard/investment, /dashboard/investment/deposit, /dashboard/investment/withdraw, /dashboard/investment/history

**Components:** Portfolio value card, performance chart, transaction table, deposit/withdrawal modals

---

## Phase 4: KYC/AML Flow
**Pages:** /kyc/start → personal-info → address → identity → source-of-funds → review → pending/approved/rejected

**Integration:** Jumio or Onfido for identity verification

---

## Phase 5: Admin Investment Management
**Pages:** /admin/investments, /admin/accounts, /admin/deposits, /admin/payouts, /admin/kyc, /admin/compliance

---

## Phase 6: Automated Return Accrual
**Celery Tasks:** Daily return calculation, monthly settlements, notifications

---

## Phase 7: Payment Integration
- Stripe for fiat deposits
- NOWPayments for crypto deposits
- Withdrawal processing (manual approval)

---

## Phase 8: Updated Landing Page
**Sections:** Investment tiers, AI trading engine, how it works, social proof, FAQ, risk disclaimers

---

See BUSINESS_MODEL_UPDATE.md for complete details.
