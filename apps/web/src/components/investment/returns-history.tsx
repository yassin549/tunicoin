'use client';

import { useMemo } from 'react';
import { format } from 'date-fns';
import { TrendingUp, Calendar } from 'lucide-react';

interface InvestmentReturn {
  id: string;
  investment_account_id: string;
  amount: number;
  return_rate: number;
  period_start: string;
  period_end: string;
  created_at: string;
}

interface ReturnsHistoryProps {
  returns: InvestmentReturn[];
  isLoading?: boolean;
}

export function ReturnsHistory({ returns, isLoading = false }: ReturnsHistoryProps) {
  // Calculate total returns
  const totalReturns = useMemo(() => {
    return returns.reduce((sum, r) => sum + r.amount, 0);
  }, [returns]);

  // Group returns by month for better organization
  const groupedReturns = useMemo(() => {
    if (!returns || returns.length === 0) return {};

    const groups: Record<string, InvestmentReturn[]> = {};
    
    returns.forEach((ret) => {
      const monthKey = format(new Date(ret.created_at), 'MMMM yyyy');
      if (!groups[monthKey]) {
        groups[monthKey] = [];
      }
      groups[monthKey].push(ret);
    });

    return groups;
  }, [returns]);

  const monthKeys = Object.keys(groupedReturns).sort((a, b) => {
    return new Date(b).getTime() - new Date(a).getTime();
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
          <p className="text-sm text-muted-foreground">Loading returns...</p>
        </div>
      </div>
    );
  }

  if (!returns || returns.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <TrendingUp className="h-12 w-12 mx-auto mb-2 opacity-50" />
        <p className="text-sm font-medium">No returns yet</p>
        <p className="text-xs mt-1">Returns will appear here once generated</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-green-700 font-medium">Total Returns Earned</p>
            <p className="text-2xl font-bold text-green-900 mt-1">
              +${totalReturns.toFixed(2)}
            </p>
          </div>
          <div className="bg-green-500 rounded-full p-3">
            <TrendingUp className="h-6 w-6 text-white" />
          </div>
        </div>
        <div className="mt-3 flex items-center gap-4 text-xs text-green-700">
          <div>
            <span className="font-semibold">{returns.length}</span> payments
          </div>
          <div>•</div>
          <div>
            Latest: {format(new Date(returns[0].created_at), 'MMM d, yyyy')}
          </div>
        </div>
      </div>

      {/* Returns by Month */}
      <div className="space-y-4">
        {monthKeys.map((monthKey) => {
          const monthReturns = groupedReturns[monthKey];
          const monthTotal = monthReturns.reduce((sum, r) => sum + r.amount, 0);

          return (
            <div key={monthKey} className="space-y-2">
              {/* Month Header */}
              <div className="flex items-center justify-between py-2 border-b">
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <h3 className="font-semibold text-sm">{monthKey}</h3>
                </div>
                <div className="text-sm font-semibold text-green-600">
                  +${monthTotal.toFixed(2)}
                </div>
              </div>

              {/* Returns List */}
              <div className="space-y-2">
                {monthReturns.map((ret) => (
                  <div
                    key={ret.id}
                    className="flex items-center justify-between p-3 rounded-lg border hover:bg-muted/20 transition-colors"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <div className="h-2 w-2 bg-green-500 rounded-full"></div>
                        <p className="text-sm font-medium">
                          Return Payment
                        </p>
                      </div>
                      <div className="mt-1 flex items-center gap-3 text-xs text-muted-foreground">
                        <span>
                          {format(new Date(ret.period_start), 'MMM d')} -{' '}
                          {format(new Date(ret.period_end), 'MMM d, yyyy')}
                        </span>
                        <span>•</span>
                        <span className="font-medium text-green-600">
                          {(ret.return_rate * 100).toFixed(2)}% rate
                        </span>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-green-600">
                        +${ret.amount.toFixed(2)}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {format(new Date(ret.created_at), 'MMM d, h:mm a')}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer Stats */}
      <div className="grid grid-cols-3 gap-4 pt-4 border-t">
        <div className="text-center">
          <p className="text-xs text-muted-foreground">Total Payments</p>
          <p className="text-lg font-bold text-foreground">{returns.length}</p>
        </div>
        <div className="text-center">
          <p className="text-xs text-muted-foreground">Average Return</p>
          <p className="text-lg font-bold text-green-600">
            {returns.length > 0 
              ? `$${(totalReturns / returns.length).toFixed(2)}`
              : '$0.00'}
          </p>
        </div>
        <div className="text-center">
          <p className="text-xs text-muted-foreground">Avg Rate</p>
          <p className="text-lg font-bold text-green-600">
            {returns.length > 0
              ? `${((returns.reduce((sum, r) => sum + r.return_rate, 0) / returns.length) * 100).toFixed(2)}%`
              : '0.00%'}
          </p>
        </div>
      </div>
    </div>
  );
}
