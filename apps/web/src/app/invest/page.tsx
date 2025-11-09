'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Check, TrendingUp, Shield, BarChart3, Sparkles, Award, Lock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

interface InvestmentTier {
  name: string;
  minimumDeposit: number;
  monthlyReturn: number;
  annualROI: number;
  popular?: boolean;
  features: string[];
  cta: string;
}

const investmentTiers: InvestmentTier[] = [
  {
    name: 'Basic',
    minimumDeposit: 100,
    monthlyReturn: 25,
    annualROI: 300,
    features: [
      '$100 minimum deposit',
      '25% monthly returns',
      'AI-powered trading engine',
      'Monthly payout options',
      'Dashboard performance tracking',
      'Email support',
      'Withdraw anytime',
    ],
    cta: 'Start with Basic',
  },
  {
    name: 'Premium',
    minimumDeposit: 300,
    monthlyReturn: 50,
    annualROI: 600,
    popular: true,
    features: [
      '$300 minimum deposit',
      '50% monthly returns',
      'AI-powered trading engine',
      'Priority monthly payouts',
      'Advanced performance analytics',
      'Priority email support',
      'Dedicated account manager',
      'Withdraw anytime',
    ],
    cta: 'Go Premium',
  },
  {
    name: 'Professional',
    minimumDeposit: 1000,
    monthlyReturn: 60,
    annualROI: 720,
    features: [
      '$1,000 minimum deposit',
      '60% monthly returns',
      'AI-powered trading engine',
      'Priority monthly payouts',
      'Real-time performance dashboard',
      '24/7 priority support',
      'Dedicated account manager',
      'Tax documentation included',
      'Early payout requests',
      'Withdraw anytime',
    ],
    cta: 'Choose Professional',
  },
  {
    name: 'Investor',
    minimumDeposit: 10000,
    monthlyReturn: 75,
    annualROI: 900,
    features: [
      '$10,000 minimum deposit',
      '75% monthly returns',
      'AI-powered trading engine',
      'Instant payout processing',
      'VIP performance dashboard',
      '24/7 VIP support',
      'Personal account manager',
      'Tax & legal documentation',
      'Custom payout schedules',
      'Dedicated portfolio review',
      'Withdraw anytime',
    ],
    cta: 'Become an Investor',
  },
];

export default function InvestPage() {
  const [selectedTier, setSelectedTier] = useState<InvestmentTier | null>(null);

  const handleSelectTier = (tier: InvestmentTier) => {
    // Check if user is logged in, then redirect to KYC or signup
    const token = localStorage.getItem('token');
    if (token) {
      // User is logged in, redirect to KYC
      window.location.href = '/kyc';
    } else {
      // User not logged in, redirect to signup
      window.location.href = `/auth/signup?plan=${tier.name.toLowerCase()}`;
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
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-50 border border-green-200 text-green-700 text-sm font-semibold mb-6">
          <Shield className="h-4 w-4" />
          Regulated by CMF (Conseil du Marché Financier)
        </div>
        
        <h1 className="text-5xl font-bold mb-4 gradient-text">
          Investment Plans
        </h1>
        <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
          Let your money work for you with our AI-powered trading engine. Choose your investment tier and start earning monthly returns.
        </p>

        {/* CMF Certificate Badge */}
        <div className="flex justify-center items-center gap-8 mb-8">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Award className="h-5 w-5 text-primary" />
            <span className="font-semibold">CMF Licensed</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Lock className="h-5 w-5 text-primary" />
            <span className="font-semibold">Secure & Insured</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <BarChart3 className="h-5 w-5 text-primary" />
            <span className="font-semibold">50 Years of Data</span>
          </div>
        </div>
      </section>

      {/* Investment Tiers */}
      <section className="container mx-auto px-4 pb-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {investmentTiers.map((tier) => (
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
                <CardDescription>Investment Tier</CardDescription>
                <div className="mt-4">
                  <div className="text-sm text-muted-foreground">Minimum Deposit</div>
                  <div className="text-4xl font-bold">${tier.minimumDeposit.toLocaleString()}</div>
                </div>
                <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                  <div className="text-sm text-green-700 font-semibold">Monthly Returns</div>
                  <div className="text-3xl font-bold text-green-600">{tier.monthlyReturn}%</div>
                  <div className="text-xs text-green-600 mt-1">{tier.annualROI}% Annual ROI</div>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                {/* Features */}
                <div className="space-y-2">
                  {tier.features.map((feature, index) => (
                    <div key={index} className="flex items-start gap-2">
                      <Check className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                      <span className="text-sm">{feature}</span>
                    </div>
                  ))}
                </div>

                {/* CTA Button */}
                <Button
                  onClick={() => handleSelectTier(tier)}
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

      {/* How It Works */}
      <section className="bg-white border-t py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 max-w-5xl mx-auto">
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-primary text-2xl font-bold mb-4">
                1
              </div>
              <h3 className="font-semibold mb-2">Choose Your Tier</h3>
              <p className="text-sm text-muted-foreground">
                Select the investment plan that matches your goals and budget.
              </p>
            </div>
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-primary text-2xl font-bold mb-4">
                2
              </div>
              <h3 className="font-semibold mb-2">Complete KYC</h3>
              <p className="text-sm text-muted-foreground">
                Verify your identity to comply with CMF regulations (required).
              </p>
            </div>
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-primary text-2xl font-bold mb-4">
                3
              </div>
              <h3 className="font-semibold mb-2">Make Deposit</h3>
              <p className="text-sm text-muted-foreground">
                Fund your account via crypto or bank transfer securely.
              </p>
            </div>
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-primary text-2xl font-bold mb-4">
                4
              </div>
              <h3 className="font-semibold mb-2">Earn & Withdraw</h3>
              <p className="text-sm text-muted-foreground">
                Watch your balance grow monthly and request payouts anytime.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* AI Trading Engine Section */}
      <section className="py-16 bg-gradient-to-br from-blue-900 to-blue-700 text-white">
        <div className="container mx-auto px-4 text-center">
          <TrendingUp className="h-16 w-16 mx-auto mb-6 text-blue-200" />
          <h2 className="text-4xl font-bold mb-4">Powered by Advanced AI Trading</h2>
          <p className="text-xl text-blue-100 mb-8 max-w-3xl mx-auto">
            Our proprietary AI trading engine analyzes 50 years of market data using reinforcement learning
            and advanced quantitative techniques. The AI executes trades on your behalf, optimized for consistent
            monthly returns.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div>
              <div className="text-5xl font-bold text-blue-200 mb-2">50+</div>
              <div className="text-blue-100">Years of Data</div>
            </div>
            <div>
              <div className="text-5xl font-bold text-blue-200 mb-2">24/7</div>
              <div className="text-blue-100">AI Monitoring</div>
            </div>
            <div>
              <div className="text-5xl font-bold text-blue-200 mb-2">100%</div>
              <div className="text-blue-100">Automated</div>
            </div>
          </div>
        </div>
      </section>

      {/* Risk Disclaimer */}
      <section className="container mx-auto px-4 py-16">
        <Alert variant="warning" className="max-w-4xl mx-auto">
          <AlertTitle className="text-lg font-bold flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Important Risk Disclosure
          </AlertTitle>
          <AlertDescription className="mt-2 space-y-2">
            <p>
              <strong>Investment Risk:</strong> All investments carry risk. While our AI trading engine is designed
              for consistent returns, past performance does not guarantee future results. Monthly returns shown are
              projections and not guaranteed.
            </p>
            <p>
              <strong>Regulatory Compliance:</strong> ExtraCoin is licensed and regulated by the Conseil du Marché Financier (CMF).
              All funds are held in segregated accounts and insured. We comply with KYC/AML regulations.
            </p>
            <p>
              <strong>Important:</strong> Only invest funds you can afford to lose. Consult with a financial advisor before making
              investment decisions. You can withdraw your principal and returns at any time subject to our terms.
            </p>
          </AlertDescription>
        </Alert>
      </section>

      {/* FAQ Section */}
      <section className="bg-white border-t py-16">
        <div className="container mx-auto px-4 max-w-3xl">
          <h2 className="text-3xl font-bold text-center mb-12">Frequently Asked Questions</h2>
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold mb-2">How does the AI trading engine work?</h3>
              <p className="text-muted-foreground">
                Our AI analyzes 50+ years of historical market data using reinforcement learning and advanced
                quantitative methods. It identifies patterns and executes trades optimized for consistent returns.
                The system runs 24/7 and automatically adjusts to market conditions.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Are the returns guaranteed?</h3>
              <p className="text-muted-foreground">
                While our AI has shown consistent performance, no investment returns can be legally guaranteed.
                The percentages shown are projections based on historical performance. Actual results may vary.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">When can I withdraw my funds?</h3>
              <p className="text-muted-foreground">
                You can request a withdrawal at any time. Withdrawals are typically processed within 1-3 business
                days. There are no lock-in periods or early withdrawal penalties.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Is my investment safe and regulated?</h3>
              <p className="text-muted-foreground">
                Yes. ExtraCoin is licensed by the CMF (Conseil du Marché Financier). All funds are held in
                segregated bank accounts and are insured. We comply with all KYC/AML regulations.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">What payment methods do you accept?</h3>
              <p className="text-muted-foreground">
                We accept cryptocurrency deposits (BTC, ETH, USDT, USDC, etc.) and bank transfers. Credit card
                deposits via Stripe are also available for certain regions.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Do I need to verify my identity (KYC)?</h3>
              <p className="text-muted-foreground">
                Yes. As a CMF-regulated platform, we are required to verify the identity of all investors. This
                includes uploading a government ID and proof of address. The process takes 2-5 minutes.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="gradient-primary py-20 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-4">Ready to Start Investing?</h2>
          <p className="text-xl text-blue-100 mb-8">
            Join hundreds of investors earning consistent monthly returns with our AI trading engine.
          </p>
          <Button
            onClick={() => window.location.href = '/auth/signup'}
            variant="secondary"
            size="xl"
            className="bg-white text-primary hover:bg-blue-50"
          >
            Open Investment Account
          </Button>
          <p className="text-sm text-blue-200 mt-4">
            ✓ CMF Regulated  •  ✓ Secure & Insured  •  ✓ Withdraw Anytime
          </p>
        </div>
      </section>
    </div>
  );
}
