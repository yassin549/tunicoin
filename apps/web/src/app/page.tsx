import Link from 'next/link';
import { ArrowRight, Bot, BarChart3, Shield, Zap, LineChart, Globe } from 'lucide-react';
import { Header } from '@/components/layout/header';
import { Footer } from '@/components/layout/footer';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Header */}
      <Header />

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="mx-auto max-w-3xl">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-50 border border-green-200 text-green-700 text-sm font-semibold mb-4">
            <Shield className="h-4 w-4" />
            Regulated by CMF
          </div>
          <h1 className="mb-6 text-5xl font-bold leading-tight text-gray-900 md:text-6xl">
            Trade & Invest with
            <br />
            <span className="gradient-text">AI-Powered Technology</span>
          </h1>
          <p className="mb-8 text-xl text-gray-600">
            Practice CFD trading risk-free OR invest real money with our proven AI engine. 
            Two powerful platforms, one account.
          </p>
          <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
            <Link href="/invest">
              <Button size="xl" className="group bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800">
                Start Investing
                <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
              </Button>
            </Link>
            <Link href="/pricing">
              <Button variant="outline" size="xl">
                Practice Trading Free
              </Button>
            </Link>
          </div>
          <div className="mt-8 max-w-2xl mx-auto text-sm text-muted-foreground">
            <p>
              ✓ <strong>Practice Trading:</strong> Risk-free simulation with virtual funds
              <br />
              ✓ <strong>Real Investment:</strong> CMF-regulated with AI-powered returns
            </p>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="bg-white py-20">
        <div className="container mx-auto px-4">
          <h2 className="mb-12 text-center text-4xl font-bold text-gray-900">
            Everything You Need to Trade
          </h2>
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            <FeatureCard
              icon={<Bot className="h-8 w-8" />}
              title="AI Trading Agents"
              description="Subscribe to algorithmic strategies that trade automatically with explainable decisions."
            />
            <FeatureCard
              icon={<BarChart3 className="h-8 w-8" />}
              title="Advanced Analytics"
              description="Backtest strategies with comprehensive metrics: CAGR, Sharpe, Max Drawdown, and more."
            />
            <FeatureCard
              icon={<LineChart className="h-8 w-8" />}
              title="Professional Charts"
              description="TradingView-powered charts with 20+ indicators, drawing tools, and real-time updates."
            />
            <FeatureCard
              icon={<Shield className="h-8 w-8" />}
              title="Risk-Free Learning"
              description="Practice with virtual funds. All trades are simulated with realistic market conditions."
            />
            <FeatureCard
              icon={<Zap className="h-8 w-8" />}
              title="Real-Time Execution"
              description="Realistic order execution with slippage modeling, fees, and margin requirements."
            />
            <FeatureCard
              icon={<Globe className="h-8 w-8" />}
              title="Multiple Markets"
              description="Trade crypto, forex, indices, and futures—all in one simulated environment."
            />
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20">
        <div className="container mx-auto px-4">
          <h2 className="mb-12 text-center text-4xl font-bold text-gray-900">
            How It Works
          </h2>
          <div className="grid gap-12 md:grid-cols-3 max-w-5xl mx-auto">
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-primary text-2xl font-bold mb-4">
                1
              </div>
              <h3 className="text-xl font-semibold mb-3">Create Account</h3>
              <p className="text-muted-foreground">
                Sign up for free and get instant access to your simulated trading account with
                $10,000 virtual balance.
              </p>
            </div>
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-primary text-2xl font-bold mb-4">
                2
              </div>
              <h3 className="text-xl font-semibold mb-3">Choose Strategy</h3>
              <p className="text-muted-foreground">
                Subscribe to AI trading bots or trade manually using professional charts and
                advanced order types.
              </p>
            </div>
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 text-primary text-2xl font-bold mb-4">
                3
              </div>
              <h3 className="text-xl font-semibold mb-3">Learn & Improve</h3>
              <p className="text-muted-foreground">
                Monitor performance, backtest strategies, and refine your approach—all risk-free with
                no real money.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="gradient-primary py-20 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="mb-6 text-4xl font-bold">Ready to Start Trading?</h2>
          <p className="mb-8 text-xl text-blue-100">
            Join thousands of traders learning CFD trading in a safe environment.
          </p>
          <Link href="/auth/signup">
            <Button variant="secondary" size="xl" className="bg-white text-primary hover:bg-blue-50">
              Create Free Account
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <Footer />
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="card-hover rounded-xl border bg-white p-6">
      <div className="mb-4 inline-flex rounded-lg bg-primary-100 p-3 text-primary-600">{icon}</div>
      <h3 className="mb-2 text-xl font-semibold text-gray-900">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}
