'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Check, X, ArrowLeft, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckoutModal } from '@/components/checkout/checkout-modal';

interface PricingTier {
  name: string;
  price: number;
  interval: string;
  description: string;
  popular?: boolean;
  features: {
    included: string[];
    excluded: string[];
  };
  cta: string;
}

const pricingTiers: PricingTier[] = [
  {
    name: 'Free',
    price: 0,
    interval: 'forever',
    description: 'Perfect for learning the basics',
    features: {
      included: [
        '1 simulated account',
        '$10,000 virtual balance',
        'Basic charting tools',
        '3 instrument types',
        'Manual trading only',
        'Basic order types (Market, Limit)',
        '30-day trade history',
        'Community support',
      ],
      excluded: [
        'AI trading bot',
        'Advanced indicators',
        'Backtesting',
        'Priority support',
      ],
    },
    cta: 'Start Free',
  },
  {
    name: 'Basic',
    price: 29,
    interval: 'month',
    description: 'For active traders',
    features: {
      included: [
        '3 simulated accounts',
        '$50,000 virtual balance per account',
        'Advanced charting (20+ indicators)',
        '5 instrument types',
        'AI bot (basic strategy)',
        'All order types',
        'Basic backtesting',
        'Unlimited trade history',
        'Email support',
      ],
      excluded: [
        'Custom bot parameters',
        'Walk-forward testing',
        'Strategy marketplace access',
      ],
    },
    cta: 'Start 7-Day Trial',
  },
  {
    name: 'Pro',
    price: 79,
    interval: 'month',
    description: 'For serious algorithmic traders',
    popular: true,
    features: {
      included: [
        '10 simulated accounts',
        '$250,000 virtual balance per account',
        'Professional charting suite',
        'All instruments',
        'AI bot (advanced strategies)',
        'Custom bot parameters',
        'Advanced backtesting',
        'Walk-forward testing',
        'Strategy marketplace access',
        'Export trade data (CSV/JSON)',
        'Priority support',
        '1:50 leverage',
      ],
      excluded: [],
    },
    cta: 'Start 14-Day Trial',
  },
  {
    name: 'Enterprise',
    price: 299,
    interval: 'month',
    description: 'For teams and institutions',
    features: {
      included: [
        'Unlimited simulated accounts',
        'Custom virtual balance',
        'White-label option',
        'Multiple AI bots running simultaneously',
        'Custom strategy development',
        'API access for integrations',
        'Advanced analytics dashboard',
        'Team collaboration features',
        'Dedicated account manager',
        '24/7 priority support',
        'Custom leverage limits',
        'SLA guarantee',
      ],
      excluded: [],
    },
    cta: 'Contact Sales',
  },
];

export default function PricingPage() {
  const [showCheckout, setShowCheckout] = useState(false);
  const [selectedTier, setSelectedTier] = useState<PricingTier | null>(null);

  const handleSelectPlan = (tier: PricingTier) => {
    if (tier.name === 'Free') {
      // Redirect to signup for free plan
      window.location.href = '/auth/signup';
    } else if (tier.name === 'Enterprise') {
      // Open contact form or email
      window.location.href = 'mailto:sales@tunicoin.com?subject=Enterprise Plan Inquiry';
    } else {
      setSelectedTier(tier);
      setShowCheckout(true);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <Link
            href="/"
            className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to home
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 text-center">
        <h1 className="text-5xl font-bold mb-4 gradient-text">
          Trading Plans
        </h1>
        <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
          Practice CFD trading risk-free with simulated accounts. Start free and upgrade for advanced features.
          All trading plans use virtual funds only.
        </p>

        {/* Disclaimer Alert */}
        <Alert variant="info" className="max-w-3xl mx-auto">
          <AlertDescription>
            <strong>⚠️ Simulated Trading:</strong> These plans are for practice trading with virtual funds only. No real money is traded. For real investment opportunities, see our <a href="/invest" className="text-primary font-semibold hover:underline">Investment Plans</a>.
          </AlertDescription>
        </Alert>
      </section>

      {/* Pricing Cards */}
      <section className="container mx-auto px-4 pb-20">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {pricingTiers.map((tier) => (
            <Card
              key={tier.name}
              className={`relative ${
                tier.popular
                  ? 'border-primary border-2 shadow-2xl scale-105'
                  : 'hover:shadow-lg transition-shadow'
              }`}
            >
              {tier.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <div className="bg-gradient-to-r from-[#2B6EEA] to-[#0B3D91] text-white px-4 py-1 rounded-full text-sm font-semibold flex items-center gap-1">
                    <Sparkles className="h-3 w-3" />
                    Most Popular
                  </div>
                </div>
              )}

              <CardHeader>
                <CardTitle className="text-2xl">{tier.name}</CardTitle>
                <CardDescription>{tier.description}</CardDescription>
                <div className="mt-4">
                  <span className="text-4xl font-bold">${tier.price}</span>
                  <span className="text-muted-foreground ml-2">/ {tier.interval}</span>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                {/* Included Features */}
                <div className="space-y-2">
                  {tier.features.included.map((feature, index) => (
                    <div key={index} className="flex items-start gap-2">
                      <Check className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                      <span className="text-sm">{feature}</span>
                    </div>
                  ))}
                </div>

                {/* Excluded Features */}
                {tier.features.excluded.length > 0 && (
                  <div className="space-y-2 pt-2 border-t">
                    {tier.features.excluded.map((feature, index) => (
                      <div key={index} className="flex items-start gap-2">
                        <X className="h-5 w-5 text-muted-foreground flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-muted-foreground">{feature}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* CTA Button */}
                <Button
                  onClick={() => handleSelectPlan(tier)}
                  variant={tier.popular ? 'default' : 'outline'}
                  className="w-full mt-6"
                  size="lg"
                >
                  {tier.cta}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* FAQ Section */}
      <section className="bg-white border-t py-16">
        <div className="container mx-auto px-4 max-w-3xl">
          <h2 className="text-3xl font-bold text-center mb-12">Frequently Asked Questions</h2>
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold mb-2">Is this real trading?</h3>
              <p className="text-muted-foreground">
                No. Tunicoin is a 100% simulated trading platform for educational purposes. No real
                money is ever at risk, and no real market orders are executed.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Can I upgrade or downgrade my plan?</h3>
              <p className="text-muted-foreground">
                Yes. You can change your plan at any time. Upgrades take effect immediately, and
                downgrades take effect at the end of your current billing period.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">What payment methods do you accept?</h3>
              <p className="text-muted-foreground">
                We accept major credit cards via Stripe, and cryptocurrency payments (BTC, ETH, USDT,
                USDC, LTC, TRX, BNB) via NOWPayments.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Is there a free trial?</h3>
              <p className="text-muted-foreground">
                Yes! The Free plan is available forever. Basic and Pro plans include 7-day and 14-day
                free trials respectively.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Can I cancel anytime?</h3>
              <p className="text-muted-foreground">
                Absolutely. Cancel anytime from your account settings. No questions asked.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Checkout Modal */}
      {selectedTier && (
        <CheckoutModal
          open={showCheckout}
          onOpenChange={setShowCheckout}
          planName={selectedTier.name}
          planPrice={selectedTier.price}
          planInterval={selectedTier.interval}
          planDescription={selectedTier.description}
        />
      )}
    </div>
  );
}
