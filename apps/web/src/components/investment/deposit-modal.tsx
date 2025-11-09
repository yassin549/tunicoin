'use client';

import { useState } from 'react';
import { X, Copy, Check, ExternalLink, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { apiClient } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';

interface DepositModalProps {
  open: boolean;
  onClose: () => void;
  investmentAccountId: string;
}

export function DepositModal({ open, onClose, investmentAccountId }: DepositModalProps) {
  const { toast } = useToast();
  const [step, setStep] = useState(1);
  const [amount, setAmount] = useState('');
  const [currency, setCurrency] = useState('btc');
  const [loading, setLoading] = useState(false);
  const [paymentData, setPaymentData] = useState<any>(null);
  const [copied, setCopied] = useState(false);

  const cryptoCurrencies = [
    { code: 'btc', name: 'Bitcoin', icon: '₿' },
    { code: 'eth', name: 'Ethereum', icon: 'Ξ' },
    { code: 'usdt', name: 'Tether (USDT)', icon: '₮' },
    { code: 'usdc', name: 'USD Coin', icon: '$' },
    { code: 'ltc', name: 'Litecoin', icon: 'Ł' },
    { code: 'trx', name: 'Tron', icon: 'T' },
    { code: 'bnb', name: 'Binance Coin', icon: 'B' },
  ];

  const handleCreateDeposit = async () => {
    if (!amount || parseFloat(amount) < 10) {
      toast({
        title: 'Invalid Amount',
        description: 'Minimum deposit is $10',
        variant: 'destructive',
      });
      return;
    }

    setLoading(true);

    try {
      const response = await apiClient.post('/api/investment/deposits', {
        investment_account_id: investmentAccountId,
        amount: parseFloat(amount),
        currency: currency,
        payment_method: 'crypto',
      });

      setPaymentData(response.data);
      setStep(2);
      
      toast({
        title: 'Payment Created',
        description: 'Send cryptocurrency to the address below',
      });
    } catch (error: any) {
      console.error('Deposit creation error:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to create deposit',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    toast({
      title: 'Copied!',
      description: 'Address copied to clipboard',
    });
    setTimeout(() => setCopied(false), 2000);
  };

  const handleClose = () => {
    setStep(1);
    setAmount('');
    setCurrency('btc');
    setPaymentData(null);
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>
            {step === 1 ? 'Deposit Funds' : 'Complete Payment'}
          </DialogTitle>
          <DialogDescription>
            {step === 1 ? 'Choose amount and cryptocurrency' : 'Send crypto to the address below'}
          </DialogDescription>
        </DialogHeader>

        {/* Step 1: Amount and Currency Selection */}
        {step === 1 && (
          <div className="space-y-4 py-4">
            <div>
              <Label htmlFor="amount">Amount (USD)</Label>
              <Input
                id="amount"
                type="number"
                min="10"
                step="1"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="100"
                className="mt-1"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Minimum: $10
              </p>
            </div>

            <div>
              <Label>Select Cryptocurrency</Label>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {cryptoCurrencies.map((crypto) => (
                  <button
                    key={crypto.code}
                    onClick={() => setCurrency(crypto.code)}
                    className={`p-3 border rounded-lg text-left transition-colors ${
                      currency === crypto.code
                        ? 'border-primary bg-primary/10'
                        : 'border-gray-300 hover:border-primary/50'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-2xl">{crypto.icon}</span>
                      <div className="flex-1 min-w-0">
                        <div className="font-semibold text-sm">{crypto.code.toUpperCase()}</div>
                        <div className="text-xs text-muted-foreground truncate">{crypto.name}</div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription className="text-xs">
                Funds will be credited to your account after blockchain confirmation (typically 10-30 minutes).
              </AlertDescription>
            </Alert>

            <div className="flex gap-2 pt-4">
              <Button variant="outline" onClick={handleClose} className="flex-1">
                Cancel
              </Button>
              <Button onClick={handleCreateDeposit} disabled={loading} className="flex-1">
                {loading ? 'Creating...' : 'Continue'}
              </Button>
            </div>
          </div>
        )}

        {/* Step 2: Payment Details */}
        {step === 2 && paymentData && (
          <div className="space-y-4 py-4">
            {/* Amount to Pay */}
            <div className="p-4 bg-primary/10 border border-primary/20 rounded-lg">
              <div className="text-sm text-muted-foreground mb-1">Amount to Pay</div>
              <div className="text-3xl font-bold text-primary">
                {paymentData.pay_amount} {paymentData.currency}
              </div>
              <div className="text-sm text-muted-foreground mt-1">
                ≈ ${paymentData.amount} USD
              </div>
            </div>

            {/* Payment Address */}
            <div>
              <Label>Send {paymentData.currency} to this address:</Label>
              <div className="mt-2 p-3 bg-gray-100 rounded-lg break-all font-mono text-sm relative">
                {paymentData.pay_address}
                <button
                  onClick={() => copyToClipboard(paymentData.pay_address)}
                  className="absolute top-2 right-2 p-2 hover:bg-gray-200 rounded transition-colors"
                  title="Copy address"
                >
                  {copied ? (
                    <Check className="h-4 w-4 text-green-600" />
                  ) : (
                    <Copy className="h-4 w-4 text-gray-600" />
                  )}
                </button>
              </div>
            </div>

            {/* Payment ID */}
            <div>
              <Label className="text-xs text-muted-foreground">Payment ID:</Label>
              <div className="text-xs font-mono mt-1 text-muted-foreground">
                {paymentData.payment_id}
              </div>
            </div>

            {/* Warnings */}
            <Alert variant="warning">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription className="text-xs space-y-2">
                <p><strong>Important:</strong></p>
                <ul className="list-disc ml-4 space-y-1">
                  <li>Only send {paymentData.currency.toUpperCase()} to this address</li>
                  <li>Sending other currencies will result in permanent loss</li>
                  <li>Payment expires in 1 hour</li>
                  <li>Minimum confirmations required: 1-3 blocks</li>
                </ul>
              </AlertDescription>
            </Alert>

            {/* Actions */}
            <div className="flex gap-2 pt-4">
              <Button variant="outline" onClick={handleClose} className="flex-1">
                Close
              </Button>
              <Button
                onClick={() => window.open(`https://nowpayments.io`, '_blank')}
                variant="secondary"
                className="flex-1"
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                View Status
              </Button>
            </div>

            <p className="text-xs text-center text-muted-foreground">
              Your deposit will appear in your account after blockchain confirmation
            </p>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
