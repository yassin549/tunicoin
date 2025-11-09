'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, TrendingUp, Wallet, DollarSign, Clock, AlertCircle, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useAuth } from '@/lib/auth-context';
import { investmentApi, type InvestmentAccount, type Deposit, type InvestmentReturn } from '@/lib/investment-api';
import { useToast } from '@/hooks/use-toast';
import { PortfolioChart } from '@/components/investment/portfolio-chart';

interface PortfolioDataPoint {
  time: string;
  value: number;
}

export default function InvestmentDashboardPage() {
  const router = useRouter();
  const { user, isLoading } = useAuth();
  const { toast } = useToast();
  const [isLoadingData, setIsLoadingData] = useState(true);
  const [account, setAccount] = useState<InvestmentAccount | null>(null);
  const [deposits, setDeposits] = useState<Deposit[]>([]);
  const [returns, setReturns] = useState<InvestmentReturn[]>([]);
  const [portfolioData, setPortfolioData] = useState<PortfolioDataPoint[]>([]);

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/auth/signin?redirect=/dashboard/investments');
    }
  }, [user, isLoading, router]);

  // Generate portfolio history from deposits and returns
  const generatePortfolioHistory = (
    deposits: Deposit[],
    returns: InvestmentReturn[],
    account: InvestmentAccount
  ): PortfolioDataPoint[] => {
    if (!account || deposits.length === 0) return [];

    const history: PortfolioDataPoint[] = [];
    const events: Array<{ date: Date; type: 'deposit' | 'return'; amount: number }> = [];

    // Add confirmed deposits
    deposits
      .filter(d => d.status === 'confirmed' && d.confirmed_at)
      .forEach(d => {
        events.push({
          date: new Date(d.confirmed_at!),
          type: 'deposit',
          amount: d.amount,
        });
      });

    // Add returns
    returns.forEach(r => {
      events.push({
        date: new Date(r.created_at),
        type: 'return',
        amount: r.amount,
      });
    });

    // Sort events by date
    events.sort((a, b) => a.date.getTime() - b.date.getTime());

    // Generate cumulative balance over time
    let balance = 0;
    events.forEach(event => {
      balance += event.amount;
      history.push({
        time: event.date.toISOString(),
        value: balance,
      });
    });

    // Add current balance as the last point
    if (history.length > 0 && account.balance) {
      const lastPoint = history[history.length - 1];
      if (Math.abs(lastPoint.value - account.balance) > 0.01) {
        history.push({
          time: new Date().toISOString(),
          value: account.balance,
        });
      }
    }

    return history;
  };

  // Fetch investment data
  useEffect(() => {
    const fetchInvestmentData = async () => {
      if (!user) return;
      
      try {
        setIsLoadingData(true);
        
        // Fetch investment accounts
        const accounts = await investmentApi.getMyAccounts();
        
        if (accounts.length > 0) {
          const primaryAccount = accounts[0]; // Use first active account
          setAccount(primaryAccount);
          
          // Fetch deposits and returns for this account
          const [depositsData, returnsData] = await Promise.all([
            investmentApi.getDeposits(primaryAccount.id),
            investmentApi.getReturns(primaryAccount.id),
          ]);
          
          setDeposits(depositsData);
          setReturns(returnsData);
          
          // Generate portfolio history
          const history = generatePortfolioHistory(depositsData, returnsData, primaryAccount);
          setPortfolioData(history);
        }
      } catch (error: any) {
        console.error('Failed to fetch investment data:', error);
        toast({
          title: 'Error',
          description: error.response?.data?.detail || 'Failed to load investment data',
          variant: 'destructive',
        });
      } finally {
        setIsLoadingData(false);
      }
    };

    if (user && !isLoading) {
      fetchInvestmentData();
    }
  }, [user, isLoading, toast]);

  if (isLoading || !user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Header */}
      <div className="border-b bg-white/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back
                </Button>
              </Link>
              <div>
                <h1 className="text-2xl font-bold gradient-text">Investment Dashboard</h1>
                <p className="text-sm text-muted-foreground">Manage your investments and track performance</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">Welcome back,</span>
              <span className="font-semibold">{user.full_name || user.email}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        {/* KYC Warning Alert */}
        {!isLoadingData && account?.status === 'pending_kyc' && (
          <Alert className="mb-6 border-yellow-500 bg-yellow-50">
            <AlertCircle className="h-4 w-4 text-yellow-600" />
            <AlertDescription className="text-yellow-900">
              Your KYC verification is pending. Complete KYC to activate your investment account.
              <Link href="/kyc" className="ml-2 font-semibold underline hover:no-underline">
                Complete KYC Now
              </Link>
            </AlertDescription>
          </Alert>
        )}

        {/* No Account Alert */}
        {!isLoadingData && !account && (
          <Alert className="mb-6 border-blue-500 bg-blue-50">
            <AlertCircle className="h-4 w-4 text-blue-600" />
            <AlertDescription className="text-blue-900">
              You don't have an investment account yet. Choose a tier and create your account to start investing.
              <Link href="/invest" className="ml-2 font-semibold underline hover:no-underline">
                View Investment Tiers
              </Link>
            </AlertDescription>
          </Alert>
        )}

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Balance Card */}
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Balance</CardTitle>
              <Wallet className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {isLoadingData ? (
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              ) : (
                <>
                  <div className="text-2xl font-bold">
                    ${account?.balance?.toFixed(2) || '0.00'}
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Available for withdrawal
                  </p>
                </>
              )}
            </CardContent>
          </Card>

          {/* Total Invested Card */}
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Invested</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {isLoadingData ? (
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              ) : (
                <>
                  <div className="text-2xl font-bold">
                    ${account?.total_invested?.toFixed(2) || '0.00'}
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Initial deposits
                  </p>
                </>
              )}
            </CardContent>
          </Card>

          {/* Total Returns Card */}
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Returns</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {isLoadingData ? (
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              ) : (
                <>
                  <div className="text-2xl font-bold text-green-600">
                    +${account?.total_returns?.toFixed(2) || '0.00'}
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    <span className="text-green-600 font-semibold">
                      +{account && account.total_invested > 0 
                        ? ((account.total_returns / account.total_invested) * 100).toFixed(1)
                        : '0.0'}%
                    </span> lifetime ROI
                  </p>
                </>
              )}
            </CardContent>
          </Card>

          {/* Account Status Card */}
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Account Status</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {isLoadingData ? (
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              ) : (
                <>
                  <div className={`text-2xl font-bold ${
                    account?.status === 'active' ? 'text-green-600' :
                    account?.status === 'pending_kyc' ? 'text-yellow-600' :
                    'text-gray-600'
                  }`}>
                    {account?.status === 'active' ? 'Active' :
                     account?.status === 'pending_kyc' ? 'Pending KYC' :
                     account?.status === 'suspended' ? 'Suspended' :
                     'No Account'}
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {account?.status === 'active' ? 'Account is active' :
                     account?.status === 'pending_kyc' ? 'Complete KYC to activate' :
                     !account ? 'Create an account to start' :
                     'Contact support'}
                  </p>
                </>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Main Dashboard Sections */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Portfolio & Performance */}
          <div className="lg:col-span-2 space-y-6">
            {/* Portfolio Performance Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Portfolio Performance</CardTitle>
                <CardDescription>Track your investment growth over time</CardDescription>
              </CardHeader>
              <CardContent>
                <PortfolioChart data={portfolioData} isLoading={isLoadingData} />
              </CardContent>
            </Card>

            {/* Deposits History */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Deposits</CardTitle>
                <CardDescription>Your deposit transaction history</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center py-8 text-muted-foreground">
                    <Wallet className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No deposits yet</p>
                    <p className="text-xs mt-1">Start investing by making your first deposit</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Returns History */}
            <Card>
              <CardHeader>
                <CardTitle>Investment Returns</CardTitle>
                <CardDescription>Returns earned from your investments</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-muted-foreground">
                  <TrendingUp className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No returns yet</p>
                  <p className="text-xs mt-1">Returns will appear here once generated</p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Actions & Info */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>Manage your investments</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button className="w-full" size="lg" disabled>
                  <DollarSign className="mr-2 h-5 w-5" />
                  Make Deposit
                </Button>
                <Button className="w-full" size="lg" variant="outline" disabled>
                  <Wallet className="mr-2 h-5 w-5" />
                  Request Payout
                </Button>
                <div className="pt-2">
                  <Link href="/kyc">
                    <Button className="w-full" variant="default" size="lg">
                      Complete KYC Verification
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>

            {/* Account Details */}
            <Card>
              <CardHeader>
                <CardTitle>Account Details</CardTitle>
                <CardDescription>Your investment account info</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {isLoadingData ? (
                  <div className="flex justify-center py-4">
                    <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                  </div>
                ) : (
                  <>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Tier:</span>
                      <span className="font-semibold">{account?.tier_name || 'No tier selected'}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Account Status:</span>
                      <span className={`font-semibold ${
                        account?.status === 'active' ? 'text-green-600' :
                        account?.status === 'pending_kyc' ? 'text-yellow-600' :
                        'text-gray-600'
                      }`}>
                        {account?.status === 'active' ? 'Active' :
                         account?.status === 'pending_kyc' ? 'Pending KYC' :
                         account?.status === 'suspended' ? 'Suspended' :
                         'No Account'}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Member Since:</span>
                      <span className="font-semibold">
                        {new Date(user.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    {account && (
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Account Created:</span>
                        <span className="font-semibold">
                          {new Date(account.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    )}
                  </>
                )}
              </CardContent>
            </Card>

            {/* Help Card */}
            <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
              <CardHeader>
                <CardTitle className="text-blue-900">Need Help?</CardTitle>
                <CardDescription className="text-blue-700">We're here to assist you</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-blue-800 mb-4">
                  Have questions about your investments or need assistance?
                </p>
                <Button variant="outline" className="w-full border-blue-300 hover:bg-blue-100">
                  Contact Support
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
