'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Users,
  Wallet,
  TrendingUp,
  DollarSign,
  Activity,
  CheckCircle,
  Clock,
  AlertCircle,
  Loader2,
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';

interface AdminStats {
  total_users: number;
  active_investments: number;
  pending_kyc: number;
  total_deposits: number;
  total_deposits_amount: number;
  total_returns: number;
  total_returns_amount: number;
  pending_payouts: number;
  pending_payouts_amount: number;
}

interface RecentActivity {
  id: string;
  type: 'user' | 'deposit' | 'return' | 'payout' | 'kyc';
  description: string;
  timestamp: string;
  status?: string;
}

export default function AdminDashboardPage() {
  const { toast } = useToast();
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.get('/api/admin/dashboard/stats');
      setStats(response.data);
      
      // Fetch recent activity
      const activityResponse = await apiClient.get('/api/admin/dashboard/activity');
      setRecentActivity(activityResponse.data);
    } catch (error: any) {
      console.error('Failed to fetch dashboard data:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to load dashboard data',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Users',
      value: stats?.total_users || 0,
      icon: Users,
      description: 'Registered users',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Active Investments',
      value: stats?.active_investments || 0,
      icon: Activity,
      description: 'Active investment accounts',
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Pending KYC',
      value: stats?.pending_kyc || 0,
      icon: Clock,
      description: 'Awaiting verification',
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
    },
    {
      title: 'Total Deposits',
      value: `$${(stats?.total_deposits_amount || 0).toLocaleString()}`,
      icon: Wallet,
      description: `${stats?.total_deposits || 0} transactions`,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: 'Total Returns',
      value: `$${(stats?.total_returns_amount || 0).toLocaleString()}`,
      icon: TrendingUp,
      description: `${stats?.total_returns || 0} payments`,
      color: 'text-emerald-600',
      bgColor: 'bg-emerald-50',
    },
    {
      title: 'Pending Payouts',
      value: `$${(stats?.pending_payouts_amount || 0).toLocaleString()}`,
      icon: DollarSign,
      description: `${stats?.pending_payouts || 0} requests`,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
  ];

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'user':
        return <Users className="h-4 w-4" />;
      case 'deposit':
        return <Wallet className="h-4 w-4" />;
      case 'return':
        return <TrendingUp className="h-4 w-4" />;
      case 'payout':
        return <DollarSign className="h-4 w-4" />;
      case 'kyc':
        return <CheckCircle className="h-4 w-4" />;
      default:
        return <Activity className="h-4 w-4" />;
    }
  };

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'user':
        return 'bg-blue-100 text-blue-600';
      case 'deposit':
        return 'bg-purple-100 text-purple-600';
      case 'return':
        return 'bg-green-100 text-green-600';
      case 'payout':
        return 'bg-orange-100 text-orange-600';
      case 'kyc':
        return 'bg-yellow-100 text-yellow-600';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold gradient-text">Admin Dashboard</h1>
        <p className="text-muted-foreground mt-1">
          Platform overview and key metrics
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {statCards.map((stat, index) => (
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                <stat.icon className={`h-5 w-5 ${stat.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground mt-1">
                {stat.description}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Latest platform events and updates</CardDescription>
        </CardHeader>
        <CardContent>
          {recentActivity.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Activity className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No recent activity</p>
            </div>
          ) : (
            <div className="space-y-3">
              {recentActivity.map((activity) => (
                <div
                  key={activity.id}
                  className="flex items-start gap-3 p-3 rounded-lg border hover:bg-muted/50 transition-colors"
                >
                  <div className={`p-2 rounded-lg ${getActivityColor(activity.type)}`}>
                    {getActivityIcon(activity.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground">
                      {activity.description}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {new Date(activity.timestamp).toLocaleString()}
                    </p>
                  </div>
                  {activity.status && (
                    <span
                      className={`text-xs px-2 py-1 rounded-full ${
                        activity.status === 'completed'
                          ? 'bg-green-100 text-green-700'
                          : activity.status === 'pending'
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-red-100 text-red-700'
                      }`}
                    >
                      {activity.status}
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common administrative tasks</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <button className="p-4 border border-gray-200 rounded-lg hover:bg-muted/50 transition-colors text-left">
              <CheckCircle className="h-6 w-6 text-green-600 mb-2" />
              <div className="font-medium">Review KYC</div>
              <div className="text-xs text-muted-foreground mt-1">
                {stats?.pending_kyc || 0} pending
              </div>
            </button>
            <button className="p-4 border border-gray-200 rounded-lg hover:bg-muted/50 transition-colors text-left">
              <DollarSign className="h-6 w-6 text-orange-600 mb-2" />
              <div className="font-medium">Process Payouts</div>
              <div className="text-xs text-muted-foreground mt-1">
                {stats?.pending_payouts || 0} pending
              </div>
            </button>
            <button className="p-4 border border-gray-200 rounded-lg hover:bg-muted/50 transition-colors text-left">
              <TrendingUp className="h-6 w-6 text-emerald-600 mb-2" />
              <div className="font-medium">Generate Returns</div>
              <div className="text-xs text-muted-foreground mt-1">
                Bulk processing
              </div>
            </button>
            <button className="p-4 border border-gray-200 rounded-lg hover:bg-muted/50 transition-colors text-left">
              <Users className="h-6 w-6 text-blue-600 mb-2" />
              <div className="font-medium">Manage Users</div>
              <div className="text-xs text-muted-foreground mt-1">
                {stats?.total_users || 0} total
              </div>
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
