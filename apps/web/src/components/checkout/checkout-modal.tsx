'use client';

import { useState } from 'react';
import { Check, CreditCard, Coins, Loader2, AlertCircle } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { apiClient, getErrorMessage } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';

interface CheckoutModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  planName: string;
  planPrice: number;
  planInterval: string;
  planDescription: string;
}

export function CheckoutModal({
  open,
  onOpenChange,
  planName,
  planPrice,
  planInterval,
  planDescription,
}: CheckoutModalProps) {
  const { toast } = useToast();
  const [paymentMethod, setPaymentMethod] = useState<'stripe' | 'crypto' | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedCrypto, setSelectedCrypto] = useState('');

  const cryptoCurrencies = [
    { code: 'btc', name: 'Bitcoin', symbol: '₿' },
    { code: 'eth', name: 'Ethereum', symbol: 'Ξ' },
    { code: 'usdt', name: 'Tether', symbol: '₮' },
    { code: 'usdc', name: 'USD Coin', symbol: '$' },
    { code: 'ltc', name: 'Litecoin', symbol: 'Ł' },
    { code: 'trx', name: 'Tron', symbol: 'T' },
    { code: 'bnb', name: 'BNB', symbol: 'BNB' },
  ];

  const handleStripeCheckout = async () => {
    setIsProcessing(true);
    setError(null);

    try {
      // Call Stripe checkout endpoint
      const response = await apiClient.post('/api/billing/stripe/create-checkout', {
        plan: planName.toLowerCase(),
        success_url: `${window.location.origin}/dashboard?checkout=success`,
        cancel_url: `${window.location.origin}/pricing?checkout=cancelled`,
      });

      // Redirect to Stripe Checkout
      if (response.data.url) {
        window.location.href = response.data.url;
      }
    } catch (err) {
      setError(getErrorMessage(err));
      setIsProcessing(false);
    }
  };

  const handleCryptoCheckout = async () => {
    if (!selectedCrypto) {
      setError('Please select a cryptocurrency');
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      // Create crypto deposit for subscription payment
      const response = await apiClient.post('/api/crypto/deposit', {
        currency: selectedCrypto,
        amount: planPrice,
        purpose: 'subscription',
        metadata: {
          plan: planName.toLowerCase(),
          interval: planInterval,
        },
      });

      toast({
        title: 'Payment created!',
        description: 'Redirecting to payment page...',
        variant: 'default',
      });

      // Redirect to payment page or show payment details
      if (response.data.payment_url) {
        window.location.href = response.data.payment_url;
      } else {
        // Show payment details in modal
        alert(`Please send ${response.data.amount} ${response.data.currency.toUpperCase()} to: ${response.data.address}`);
      }
    } catch (err) {
      setError(getErrorMessage(err));
      setIsProcessing(false);
    }
  };

  const resetModal = () => {
    setPaymentMethod(null);
    setSelectedCrypto('');
    setError(null);
    setIsProcessing(false);
  };

  return (
    <Dialog open={open} onOpenChange={(open) => {
      onOpenChange(open);
      if (!open) resetModal();
    }}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="text-2xl">Complete Your Subscription</DialogTitle>
          <DialogDescription>
            Subscribe to the <strong>{planName}</strong> plan
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Plan Summary */}
          <div className="bg-muted p-4 rounded-lg space-y-2">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-semibold">{planName} Plan</h3>
                <p className="text-sm text-muted-foreground">{planDescription}</p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold">${planPrice}</p>
                <p className="text-xs text-muted-foreground">per {planInterval}</p>
              </div>
            </div>
          </div>

          {/* Error Alert */}
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Payment Method Selection */}
          {!paymentMethod && (
            <div className="space-y-3">
              <h3 className="font-semibold text-sm text-muted-foreground">Select Payment Method</h3>
              
              {/* Stripe Option */}
              <button
                onClick={() => setPaymentMethod('stripe')}
                className="w-full p-4 border-2 border-border rounded-lg hover:border-primary hover:bg-primary/5 transition-colors text-left group"
              >
                <div className="flex items-center gap-3">
                  <CreditCard className="h-6 w-6 text-primary" />
                  <div className="flex-1">
                    <h4 className="font-semibold group-hover:text-primary transition-colors">
                      Credit / Debit Card
                    </h4>
                    <p className="text-xs text-muted-foreground">Secure payment via Stripe</p>
                  </div>
                  <Check className="h-5 w-5 text-transparent group-hover:text-primary transition-colors" />
                </div>
              </button>

              {/* Crypto Option */}
              <button
                onClick={() => setPaymentMethod('crypto')}
                className="w-full p-4 border-2 border-border rounded-lg hover:border-primary hover:bg-primary/5 transition-colors text-left group"
              >
                <div className="flex items-center gap-3">
                  <Coins className="h-6 w-6 text-primary" />
                  <div className="flex-1">
                    <h4 className="font-semibold group-hover:text-primary transition-colors">
                      Cryptocurrency
                    </h4>
                    <p className="text-xs text-muted-foreground">Pay with BTC, ETH, USDT, and more</p>
                  </div>
                  <Check className="h-5 w-5 text-transparent group-hover:text-primary transition-colors" />
                </div>
              </button>
            </div>
          )}

          {/* Stripe Payment */}
          {paymentMethod === 'stripe' && (
            <div className="space-y-4">
              <Button
                onClick={handleStripeCheckout}
                disabled={isProcessing}
                className="w-full"
                size="lg"
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <CreditCard className="mr-2 h-5 w-5" />
                    Continue to Stripe
                  </>
                )}
              </Button>
              <Button
                onClick={() => setPaymentMethod(null)}
                variant="ghost"
                className="w-full"
                disabled={isProcessing}
              >
                Back
              </Button>
            </div>
          )}

          {/* Crypto Payment */}
          {paymentMethod === 'crypto' && (
            <div className="space-y-4">
              <div className="space-y-2">
                <h3 className="font-semibold text-sm">Select Cryptocurrency</h3>
                <div className="grid grid-cols-2 gap-2">
                  {cryptoCurrencies.map((crypto) => (
                    <button
                      key={crypto.code}
                      onClick={() => setSelectedCrypto(crypto.code)}
                      className={`p-3 border-2 rounded-lg text-left transition-all ${
                        selectedCrypto === crypto.code
                          ? 'border-primary bg-primary/5'
                          : 'border-border hover:border-primary/50'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <span className="text-xl">{crypto.symbol}</span>
                        <div>
                          <p className="text-sm font-semibold">{crypto.code.toUpperCase()}</p>
                          <p className="text-xs text-muted-foreground">{crypto.name}</p>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <Button
                onClick={handleCryptoCheckout}
                disabled={isProcessing || !selectedCrypto}
                className="w-full"
                size="lg"
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Creating payment...
                  </>
                ) : (
                  <>
                    <Coins className="mr-2 h-5 w-5" />
                    Continue to Payment
                  </>
                )}
              </Button>
              <Button
                onClick={() => setPaymentMethod(null)}
                variant="ghost"
                className="w-full"
                disabled={isProcessing}
              >
                Back
              </Button>
            </div>
          )}

          {/* Terms */}
          <div className="pt-4 border-t">
            <p className="text-xs text-center text-muted-foreground">
              By subscribing, you agree to our{' '}
              <a href="/terms" className="text-primary hover:underline">
                Terms of Service
              </a>{' '}
              and acknowledge that Tunicoin is a simulated trading platform for educational purposes.
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
