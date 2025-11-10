'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import {
  DollarSign,
  Search,
  Eye,
  CheckCircle,
  XCircle,
  Clock,
  Loader2,
  Calendar,
  ChevronLeft,
  ChevronRight,
  AlertCircle,
  ExternalLink,
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';
import { format } from 'date-fns';

interface Payout {
  id: string;
  investment_account_id: string;
  user_email?: string;
  user_name?: string;
  amount: number;
  payout_method: string;
  currency: string;
  destination: string;
  status: string;
  admin_notes?: string;
  processed_at?: string;
  created_at: string;
}

export default function AdminPayoutsPage() {
  const { toast } = useToast();
  const [payouts, setPayouts] = useState<Payout[]>([]);
  const [selectedPayout, setSelectedPayout] = useState<Payout | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('pending');
  const [adminNotes, setAdminNotes] = useState('');
  const [page, setPage] = useState(0);
  const [total, setTotal] = useState(0);
  const [limit] = useState(20);
  const [stats, setStats] = useState({
    pending_count: 0,
    pending_amount: 0,
    approved_count: 0,
    approved_amount: 0,
  });

  useEffect(() => {
    fetchPayouts();
    fetchStats();
  }, [page, filterStatus]);

  const fetchPayouts = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.get('/api/admin/payouts', {
        params: {
          status: filterStatus === 'all' ? undefined : filterStatus,
          limit,
          offset: page * limit,
        },
      });
      setPayouts(response.data.payouts);
      setTotal(response.data.total);
    } catch (error: any) {
      console.error('Failed to fetch payouts:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to load payouts',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await apiClient.get('/api/admin/payouts/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch payout stats:', error);
    }
  };

  const handleViewPayout = (payout: Payout) => {
    setSelectedPayout(payout);
    setAdminNotes(payout.admin_notes || '');
  };

  const handleApprovePayout = async () => {
    if (!selectedPayout) return;

    try {
      setIsProcessing(true);
      await apiClient.post(`/api/admin/payouts/${selectedPayout.id}/approve`, {
        admin_notes: adminNotes,
      });
      toast({
        title: 'Success',
        description: 'Payout approved successfully',
      });
      setSelectedPayout(null);
      fetchPayouts();
      fetchStats();
    } catch (error: any) {
      console.error('Failed to approve payout:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to approve payout',
        variant: 'destructive',
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRejectPayout = async () => {
    if (!selectedPayout) return;

    if (!adminNotes.trim()) {
      toast({
        title: 'Required',
        description: 'Please provide a reason for rejection',
        variant: 'destructive',
      });
      return;
    }

    try {
      setIsProcessing(true);
      await apiClient.post(`/api/admin/payouts/${selectedPayout.id}/reject`, {
        admin_notes: adminNotes,
      });
      toast({
        title: 'Success',
        description: 'Payout rejected',
      });
      setSelectedPayout(null);
      fetchPayouts();
      fetchStats();
    } catch (error: any) {
      console.error('Failed to reject payout:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to reject payout',
        variant: 'destructive',
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const filteredPayouts = payouts.filter((payout) => {
    const matchesSearch =
      searchQuery === '' ||
      payout.user_email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      payout.user_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      payout.destination.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesSearch;
  });

  const totalPages = Math.ceil(total / limit);

  const getStatusBadge = (status: string) => {
    const config = {
      approved: { label: 'Approved', className: 'bg-green-600' },
      pending: { label: 'Pending', className: 'bg-yellow-600' },
      rejected: { label: 'Rejected', className: 'bg-red-600' },
      completed: { label: 'Completed', className: 'bg-blue-600' },
    };

    const badge = config[status as keyof typeof config] || config.pending;
    return <Badge className={badge.className}>{badge.label}</Badge>;
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
    return icons[currency] || currency;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold gradient-text">Payout Management</h1>
        <p className="text-muted-foreground mt-1">
          Review and process withdrawal requests
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Pending
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {stats.pending_count}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              ${stats.pending_amount.toLocaleString()}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <CheckCircle className="h-4 w-4" />
              Approved
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {stats.approved_count}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              ${stats.approved_amount.toLocaleString()}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <CardTitle>Search and Filter</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by email, name, or wallet address..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Status Filter */}
            <div className="flex gap-2">
              <Button
                variant={filterStatus === 'all' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilterStatus('all')}
              >
                All
              </Button>
              <Button
                variant={filterStatus === 'pending' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilterStatus('pending')}
              >
                Pending
              </Button>
              <Button
                variant={filterStatus === 'approved' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilterStatus('approved')}
              >
                Approved
              </Button>
              <Button
                variant={filterStatus === 'rejected' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilterStatus('rejected')}
              >
                Rejected
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Payouts List */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Payout Requests ({total})</CardTitle>
              <CardDescription>
                Showing {page * limit + 1} to {Math.min((page + 1) * limit, total)} of {total}{' '}
                payouts
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : filteredPayouts.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <DollarSign className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No payout requests found</p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredPayouts.map((payout) => (
                <div
                  key={payout.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-start gap-4 flex-1 min-w-0">
                    <div className="p-2 bg-orange-100 rounded-lg">
                      <DollarSign className="h-5 w-5 text-orange-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="font-semibold text-foreground">
                          ${payout.amount.toFixed(2)}
                        </p>
                        <span className="text-sm text-muted-foreground">
                          {getCurrencyIcon(payout.currency)} {payout.currency}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground truncate">
                        {payout.user_email || payout.user_name || 'Unknown User'}
                      </p>
                      <div className="flex items-center gap-3 mt-2 flex-wrap">
                        {getStatusBadge(payout.status)}
                        <span className="text-xs text-muted-foreground font-mono truncate max-w-[200px]">
                          {payout.destination}
                        </span>
                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {format(new Date(payout.created_at), 'MMM d, yyyy HH:mm')}
                        </span>
                      </div>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleViewPayout(payout)}
                  >
                    <Eye className="h-4 w-4 mr-1" />
                    Review
                  </Button>
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-6 pt-6 border-t">
              <p className="text-sm text-muted-foreground">
                Page {page + 1} of {totalPages}
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(page - 1)}
                  disabled={page === 0}
                >
                  <ChevronLeft className="h-4 w-4 mr-1" />
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(page + 1)}
                  disabled={page >= totalPages - 1}
                >
                  Next
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Payout Review Modal */}
      {selectedPayout && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <Card className="max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Payout Request Review</CardTitle>
                  <CardDescription>${selectedPayout.amount.toFixed(2)}</CardDescription>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSelectedPayout(null)}
                  disabled={isProcessing}
                >
                  ×
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Status and Date */}
                <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium">Status:</span>
                    {getStatusBadge(selectedPayout.status)}
                  </div>
                  <span className="text-sm text-muted-foreground">
                    Requested: {format(new Date(selectedPayout.created_at), 'MMM d, yyyy HH:mm')}
                  </span>
                </div>

                {/* Payout Information */}
                <div className="space-y-3">
                  <h3 className="font-semibold text-lg">Payout Details</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Amount (USD)</p>
                      <p className="font-medium text-lg">
                        ${selectedPayout.amount.toFixed(2)}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Currency</p>
                      <p className="font-medium text-lg">
                        {getCurrencyIcon(selectedPayout.currency)} {selectedPayout.currency}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Method</p>
                      <p className="font-medium capitalize">{selectedPayout.payout_method}</p>
                    </div>
                    <div className="col-span-2">
                      <p className="text-muted-foreground">Destination Address</p>
                      <p className="font-mono text-xs break-all mt-1">
                        {selectedPayout.destination}
                      </p>
                    </div>
                  </div>
                </div>

                {/* User Information */}
                <div className="space-y-3 border-t pt-6">
                  <h3 className="font-semibold text-lg">User Information</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Email</p>
                      <p className="font-medium">
                        {selectedPayout.user_email || 'N/A'}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Name</p>
                      <p className="font-medium">
                        {selectedPayout.user_name || 'N/A'}
                      </p>
                    </div>
                    <div className="col-span-2">
                      <p className="text-muted-foreground">Account ID</p>
                      <p className="font-mono text-xs">
                        {selectedPayout.investment_account_id}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Processing Info */}
                {selectedPayout.processed_at && (
                  <div className="space-y-3 border-t pt-6">
                    <h3 className="font-semibold text-lg flex items-center gap-2">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      Processing Details
                    </h3>
                    <div className="text-sm">
                      <p className="text-muted-foreground">Processed At</p>
                      <p className="font-medium">
                        {format(
                          new Date(selectedPayout.processed_at),
                          'MMM d, yyyy HH:mm:ss'
                        )}
                      </p>
                    </div>
                  </div>
                )}

                {/* Admin Notes */}
                <div className="space-y-3 border-t pt-6">
                  <h3 className="font-semibold text-lg">Admin Notes</h3>
                  {selectedPayout.admin_notes && (
                    <div className="p-3 bg-muted rounded-lg mb-3">
                      <p className="text-xs text-muted-foreground mb-1">Previous Notes:</p>
                      <p className="text-sm">{selectedPayout.admin_notes}</p>
                    </div>
                  )}
                  <Textarea
                    placeholder="Add notes about this payout (required for rejection)..."
                    value={adminNotes}
                    onChange={(e) => setAdminNotes(e.target.value)}
                    rows={4}
                    disabled={isProcessing || selectedPayout.status !== 'pending'}
                  />
                </div>

                {/* Action Buttons */}
                {selectedPayout.status === 'pending' && (
                  <div className="flex gap-3 border-t pt-6">
                    <Button
                      onClick={handleApprovePayout}
                      disabled={isProcessing}
                      className="flex-1 bg-green-600 hover:bg-green-700"
                    >
                      {isProcessing ? (
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      ) : (
                        <CheckCircle className="h-4 w-4 mr-2" />
                      )}
                      Approve Payout
                    </Button>
                    <Button
                      onClick={handleRejectPayout}
                      disabled={isProcessing}
                      variant="destructive"
                      className="flex-1"
                    >
                      {isProcessing ? (
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      ) : (
                        <XCircle className="h-4 w-4 mr-2" />
                      )}
                      Reject Payout
                    </Button>
                  </div>
                )}

                {selectedPayout.status !== 'pending' && (
                  <div className="flex items-center gap-2 p-4 bg-muted rounded-lg">
                    <AlertCircle className="h-5 w-5 text-muted-foreground" />
                    <p className="text-sm text-muted-foreground">
                      This payout has already been {selectedPayout.status}
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
