import { apiClient } from './api-client';

// Types
export interface InvestmentTier {
  id: string;
  name: string;
  minimum_deposit: number;
  maximum_deposit: number;
  min_annual_return_rate: number;
  max_annual_return_rate: number;
  min_monthly_return_rate: number;
  max_monthly_return_rate: number;
  lock_period_days: number;
  features: string[];
  is_active: boolean;
}

export interface InvestmentAccount {
  id: string;
  user_id: string;
  tier_id: string;
  tier_name: string;
  status: string;
  balance: number;
  total_invested: number;
  total_returns: number;
  created_at: string;
  updated_at: string;
}

export interface Deposit {
  id: string;
  investment_account_id: string;
  user_id: string;
  amount: number;
  currency: string;
  status: string;
  payment_id: string | null;
  payment_address: string | null;
  payment_url: string | null;
  created_at: string;
  updated_at: string;
  confirmed_at: string | null;
}

export interface InvestmentReturn {
  id: string;
  investment_account_id: string;
  amount: number;
  return_rate: number;
  period_start: string;
  period_end: string;
  created_at: string;
}

export interface Payout {
  id: string;
  investment_account_id: string;
  user_id: string;
  amount: number;
  currency: string;
  crypto_address: string;
  status: string;
  created_at: string;
  updated_at: string;
  processed_at: string | null;
}

// API Functions

export const investmentApi = {
  // Get all investment tiers
  getTiers: async (): Promise<InvestmentTier[]> => {
    const response = await apiClient.get('/api/investment/tiers');
    return response.data;
  },

  // Get all investment accounts for current user
  getMyAccounts: async (): Promise<InvestmentAccount[]> => {
    const response = await apiClient.get('/api/investment/accounts');
    return response.data;
  },

  // Get specific investment account
  getAccount: async (accountId: string): Promise<InvestmentAccount> => {
    const response = await apiClient.get(`/api/investment/accounts/${accountId}`);
    return response.data;
  },

  // Create new investment account
  createAccount: async (tierId: string): Promise<InvestmentAccount> => {
    const response = await apiClient.post('/api/investment/accounts', {
      tier_id: tierId,
    });
    return response.data;
  },

  // Get deposits for an account
  getDeposits: async (accountId: string): Promise<Deposit[]> => {
    const response = await apiClient.get(`/api/investment/deposits?account_id=${accountId}`);
    return response.data;
  },

  // Create new deposit
  createDeposit: async (data: {
    investment_account_id: string;
    amount: number;
    currency: string;
  }): Promise<Deposit> => {
    const response = await apiClient.post('/api/investment/deposits', data);
    return response.data;
  },

  // Get investment returns for an account
  getReturns: async (accountId: string): Promise<InvestmentReturn[]> => {
    const response = await apiClient.get(`/api/investment/accounts/${accountId}/returns`);
    return response.data;
  },

  // Get payouts for an account
  getPayouts: async (accountId: string): Promise<Payout[]> => {
    const response = await apiClient.get(`/api/investment/payouts?account_id=${accountId}`);
    return response.data;
  },

  // Request payout
  requestPayout: async (data: {
    investment_account_id: string;
    amount: number;
    currency: string;
    crypto_address: string;
  }): Promise<Payout> => {
    const response = await apiClient.post('/api/investment/payouts', data);
    return response.data;
  },
};
