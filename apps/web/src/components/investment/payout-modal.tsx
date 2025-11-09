'use client';

import { useState } from 'react';
import { X, AlertCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { investmentApi } from '@/lib/investment-api';

interface PayoutModalProps {
  isOpen: boolean;
  onClose: () => void;
  accountId: string;
  availableBalance: number;
  onSuccess?: () => void;
}

export function PayoutModal({
  isOpen,
  onClose,
  accountId,
  availableBalance,
  onSuccess,
}: PayoutModalProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    amount: '',
    currency: 'BTC',
    destination: '',
  });

  const MIN_PAYOUT = 50;

  const supportedCurrencies = [
    { value: 'BTC', label: 'Bitcoin (BTC)', icon: '₿' },
    { value: 'ETH', label: 'Ethereum (ETH)', icon: 'Ξ' },
    { value: 'USDT', label: 'Tether (USDT)', icon: '₮' },
    { value: 'USDC', label: 'USD Coin (USDC)', icon: '$' },
    { value: 'LTC', label: 'Litecoin (LTC)', icon: 'Ł' },
    { value: 'TRX', label: 'Tron (TRX)', icon: 'T' },
    { value: 'BNB', label: 'Binance Coin (BNB)', icon: 'B' },
  ];

  const validateForm = (): string | null => {
    const amount = parseFloat(formData.amount);

    if (!formData.amount || isNaN(amount)) {
      return 'Please enter a valid amount';
    }

    if (amount < MIN_PAYOUT) {
      return `Minimum payout amount is $${MIN_PAYOUT}`;
    }

    if (amount > availableBalance) {
      return 'Amount exceeds available balance';
    }

    if (!formData.destination.trim()) {
      return 'Please enter a wallet address';
    }

    // Basic address validation (length check)
    if (formData.destination.length < 20) {
      return 'Please enter a valid wallet address';
    }

    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    try {
      setIsSubmitting(true);

      await investmentApi.requestPayout({
        investment_account_id: accountId,
        amount: parseFloat(formData.amount),
        payout_method: 'crypto',
        destination: formData.destination.trim(),
        currency: formData.currency,
      });

      // Reset form
      setFormData({
        amount: '',
        currency: 'BTC',
        destination: '',
      });

      if (onSuccess) {
        onSuccess();
      }

      onClose();
    } catch (err: any) {
      console.error('Failed to request payout:', err);
      setError(
        err.response?.data?.detail || 'Failed to submit payout request. Please try again.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      setFormData({
        amount: '',
        currency: 'BTC',
        destination: '',
      });
      setError(null);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-2xl font-bold gradient-text">Request Payout</h2>
            <p className="text-sm text-muted-foreground mt-1">
              Withdraw funds to your crypto wallet
            </p>
          </div>
          <button
            onClick={handleClose}
            disabled={isSubmitting}
            className="p-2 hover:bg-muted rounded-lg transition-colors disabled:opacity-50"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Available Balance */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-700">Available Balance</p>
            <p className="text-2xl font-bold text-blue-900">${availableBalance.toFixed(2)}</p>
            <p className="text-xs text-blue-600 mt-1">
              Minimum withdrawal: ${MIN_PAYOUT.toFixed(2)}
            </p>
          </div>

          {/* Error Alert */}
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Amount Field */}
          <div className="space-y-2">
            <Label htmlFor="amount">
              Amount (USD) <span className="text-red-500">*</span>
            </Label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                $
              </span>
              <Input
                id="amount"
                type="number"
                step="0.01"
                min={MIN_PAYOUT}
                max={availableBalance}
                value={formData.amount}
                onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                placeholder={`Min $${MIN_PAYOUT}`}
                className="pl-7"
                disabled={isSubmitting}
                required
              />
            </div>
            <p className="text-xs text-muted-foreground">
              Enter the amount you wish to withdraw
            </p>
          </div>

          {/* Currency Selection */}
          <div className="space-y-2">
            <Label htmlFor="currency">
              Cryptocurrency <span className="text-red-500">*</span>
            </Label>
            <select
              id="currency"
              value={formData.currency}
              onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
              className="w-full px-3 py-2 border border-input bg-background rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
              disabled={isSubmitting}
              required
            >
              {supportedCurrencies.map((curr) => (
                <option key={curr.value} value={curr.value}>
                  {curr.icon} {curr.label}
                </option>
              ))}
            </select>
            <p className="text-xs text-muted-foreground">
              Select the cryptocurrency for withdrawal
            </p>
          </div>

          {/* Wallet Address */}
          <div className="space-y-2">
            <Label htmlFor="destination">
              Wallet Address <span className="text-red-500">*</span>
            </Label>
            <Input
              id="destination"
              type="text"
              value={formData.destination}
              onChange={(e) => setFormData({ ...formData, destination: e.target.value })}
              placeholder={`Enter your ${formData.currency} wallet address`}
              disabled={isSubmitting}
              required
            />
            <p className="text-xs text-muted-foreground">
              Double-check your address. Funds sent to wrong addresses cannot be recovered.
            </p>
          </div>

          {/* Important Notice */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex gap-3">
              <AlertCircle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-yellow-800 space-y-1">
                <p className="font-semibold">Important Notice</p>
                <ul className="list-disc list-inside space-y-1 text-xs">
                  <li>Payout requests are processed within 1-3 business days</li>
                  <li>Verify your wallet address carefully</li>
                  <li>Network fees may apply</li>
                  <li>Minimum withdrawal: ${MIN_PAYOUT}</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isSubmitting}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting} className="flex-1">
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing...
                </>
              ) : (
                'Request Payout'
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
