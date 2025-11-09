'use client';

import { useState, useMemo } from 'react';
import { format } from 'date-fns';
import { ArrowUpDown, ArrowUp, ArrowDown, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface Deposit {
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

interface DepositsTableProps {
  deposits: Deposit[];
  isLoading?: boolean;
}

type SortField = 'created_at' | 'amount' | 'status';
type SortOrder = 'asc' | 'desc';

export function DepositsTable({ deposits, isLoading = false }: DepositsTableProps) {
  const [sortField, setSortField] = useState<SortField>('created_at');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');

  // Sort deposits
  const sortedDeposits = useMemo(() => {
    if (!deposits || deposits.length === 0) return [];

    return [...deposits].sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sortField) {
        case 'created_at':
          aValue = new Date(a.created_at).getTime();
          bValue = new Date(b.created_at).getTime();
          break;
        case 'amount':
          aValue = a.amount;
          bValue = b.amount;
          break;
        case 'status':
          aValue = a.status;
          bValue = b.status;
          break;
        default:
          return 0;
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });
  }, [deposits, sortField, sortOrder]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      // Toggle order if same field
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      // Set new field with default desc order
      setSortField(field);
      setSortOrder('desc');
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      pending: {
        label: 'Pending',
        className: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      },
      confirming: {
        label: 'Confirming',
        className: 'bg-blue-100 text-blue-800 border-blue-200',
      },
      confirmed: {
        label: 'Confirmed',
        className: 'bg-green-100 text-green-800 border-green-200',
      },
      failed: {
        label: 'Failed',
        className: 'bg-red-100 text-red-800 border-red-200',
      },
      cancelled: {
        label: 'Cancelled',
        className: 'bg-gray-100 text-gray-800 border-gray-200',
      },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pending;

    return (
      <span
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${config.className}`}
      >
        {config.label}
      </span>
    );
  };

  const getCurrencyIcon = (currency: string) => {
    const icons: Record<string, string> = {
      BTC: '₿',
      ETH: 'Ξ',
      USDT: '₮',
      USDC: '$',
      LTC: 'Ł',
      TRX: 'T',
      BNB: 'B',
    };
    return icons[currency.toUpperCase()] || currency;
  };

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) {
      return <ArrowUpDown className="ml-1 h-3 w-3 opacity-50" />;
    }
    return sortOrder === 'asc' ? (
      <ArrowUp className="ml-1 h-3 w-3" />
    ) : (
      <ArrowDown className="ml-1 h-3 w-3" />
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
          <p className="text-sm text-muted-foreground">Loading deposits...</p>
        </div>
      </div>
    );
  }

  if (!deposits || deposits.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <svg
          className="h-12 w-12 mx-auto mb-2 opacity-50"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
          />
        </svg>
        <p className="text-sm font-medium">No deposits yet</p>
        <p className="text-xs mt-1">Start investing by making your first deposit</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Table */}
      <div className="rounded-lg border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-muted/50 border-b">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  <button
                    onClick={() => handleSort('created_at')}
                    className="flex items-center hover:text-foreground transition-colors"
                  >
                    Date
                    <SortIcon field="created_at" />
                  </button>
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  <button
                    onClick={() => handleSort('amount')}
                    className="flex items-center hover:text-foreground transition-colors"
                  >
                    Amount
                    <SortIcon field="amount" />
                  </button>
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Currency
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  <button
                    onClick={() => handleSort('status')}
                    className="flex items-center hover:text-foreground transition-colors"
                  >
                    Status
                    <SortIcon field="status" />
                  </button>
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Confirmed
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sortedDeposits.map((deposit) => (
                <tr key={deposit.id} className="hover:bg-muted/20 transition-colors">
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="text-sm font-medium text-foreground">
                      {format(new Date(deposit.created_at), 'MMM d, yyyy')}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {format(new Date(deposit.created_at), 'h:mm a')}
                    </div>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="text-sm font-semibold text-foreground">
                      ${deposit.amount.toFixed(2)}
                    </div>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-lg mr-1">{getCurrencyIcon(deposit.currency)}</span>
                      <span className="text-sm font-medium text-foreground">
                        {deposit.currency.toUpperCase()}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    {getStatusBadge(deposit.status)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    {deposit.confirmed_at ? (
                      <div className="text-sm text-muted-foreground">
                        {format(new Date(deposit.confirmed_at), 'MMM d, yyyy')}
                      </div>
                    ) : (
                      <span className="text-xs text-muted-foreground">-</span>
                    )}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-right">
                    {deposit.payment_url && (
                      <a
                        href={deposit.payment_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center text-xs text-primary hover:text-primary/80 transition-colors"
                      >
                        View
                        <ExternalLink className="ml-1 h-3 w-3" />
                      </a>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Summary */}
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <div>
          Showing <span className="font-medium text-foreground">{deposits.length}</span> deposit
          {deposits.length !== 1 ? 's' : ''}
        </div>
        <div className="flex items-center gap-4">
          <div>
            Total:{' '}
            <span className="font-semibold text-foreground">
              ${deposits.reduce((sum, d) => sum + (d.status === 'confirmed' ? d.amount : 0), 0).toFixed(2)}
            </span>
          </div>
          <div>
            Confirmed:{' '}
            <span className="font-semibold text-green-600">
              {deposits.filter((d) => d.status === 'confirmed').length}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
