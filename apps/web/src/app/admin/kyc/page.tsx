'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import {
  FileCheck,
  Search,
  Eye,
  CheckCircle,
  XCircle,
  Loader2,
  Calendar,
  User,
  ChevronLeft,
  ChevronRight,
  AlertCircle,
  Image as ImageIcon,
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';
import { format } from 'date-fns';

interface KYCSubmission {
  id: string;
  user_id: string;
  user_email?: string;
  full_name: string;
  date_of_birth: string;
  country: string;
  address: string;
  city: string;
  postal_code: string;
  phone_number: string;
  id_type: string;
  id_number: string;
  id_front_url?: string;
  id_back_url?: string;
  selfie_url?: string;
  proof_of_address_url?: string;
  status: string;
  admin_notes?: string;
  created_at: string;
  updated_at: string;
}

export default function AdminKYCPage() {
  const { toast } = useToast();
  const [submissions, setSubmissions] = useState<KYCSubmission[]>([]);
  const [selectedSubmission, setSelectedSubmission] = useState<KYCSubmission | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('pending');
  const [adminNotes, setAdminNotes] = useState('');
  const [page, setPage] = useState(0);
  const [total, setTotal] = useState(0);
  const [limit] = useState(20);

  useEffect(() => {
    fetchSubmissions();
  }, [page, filterStatus]);

  const fetchSubmissions = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.get('/api/admin/kyc/submissions', {
        params: {
          status: filterStatus === 'all' ? undefined : filterStatus,
          limit,
          offset: page * limit,
        },
      });
      setSubmissions(response.data.submissions);
      setTotal(response.data.total);
    } catch (error: any) {
      console.error('Failed to fetch KYC submissions:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to load KYC submissions',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleViewSubmission = (submission: KYCSubmission) => {
    setSelectedSubmission(submission);
    setAdminNotes(submission.admin_notes || '');
  };

  const handleApprove = async () => {
    if (!selectedSubmission) return;

    try {
      setIsProcessing(true);
      await apiClient.post(`/api/admin/kyc/submissions/${selectedSubmission.id}/approve`, {
        admin_notes: adminNotes,
      });
      toast({
        title: 'Success',
        description: 'KYC submission approved successfully',
      });
      setSelectedSubmission(null);
      fetchSubmissions();
    } catch (error: any) {
      console.error('Failed to approve KYC:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to approve KYC submission',
        variant: 'destructive',
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReject = async () => {
    if (!selectedSubmission) return;

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
      await apiClient.post(`/api/admin/kyc/submissions/${selectedSubmission.id}/reject`, {
        admin_notes: adminNotes,
      });
      toast({
        title: 'Success',
        description: 'KYC submission rejected',
      });
      setSelectedSubmission(null);
      fetchSubmissions();
    } catch (error: any) {
      console.error('Failed to reject KYC:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to reject KYC submission',
        variant: 'destructive',
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const filteredSubmissions = submissions.filter((submission) => {
    const matchesSearch =
      searchQuery === '' ||
      submission.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      submission.user_email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      submission.country.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesSearch;
  });

  const totalPages = Math.ceil(total / limit);

  const getStatusBadge = (status: string) => {
    const config = {
      approved: { label: 'Approved', variant: 'default', className: 'bg-green-600' },
      pending: { label: 'Pending', variant: 'outline', className: 'bg-yellow-600' },
      rejected: { label: 'Rejected', variant: 'destructive', className: 'bg-red-600' },
      needs_review: { label: 'Needs Review', variant: 'outline', className: 'bg-orange-600' },
    };

    const badge = config[status as keyof typeof config] || config.pending;
    return <Badge className={badge.className}>{badge.label}</Badge>;
  };

  const getIdTypeName = (type: string) => {
    const types: Record<string, string> = {
      passport: 'Passport',
      drivers_license: "Driver's License",
      national_id: 'National ID',
    };
    return types[type] || type;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold gradient-text">KYC Verification</h1>
        <p className="text-muted-foreground mt-1">
          Review and approve customer identity verification
        </p>
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
                placeholder="Search by name, email, or country..."
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

      {/* Submissions List */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>KYC Submissions ({total})</CardTitle>
              <CardDescription>
                Showing {page * limit + 1} to {Math.min((page + 1) * limit, total)} of {total}{' '}
                submissions
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : filteredSubmissions.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <FileCheck className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No KYC submissions found</p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredSubmissions.map((submission) => (
                <div
                  key={submission.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-start gap-4 flex-1 min-w-0">
                    <div className="p-2 bg-purple-100 rounded-lg">
                      <FileCheck className="h-5 w-5 text-purple-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="font-semibold text-foreground truncate">
                          {submission.full_name}
                        </p>
                      </div>
                      <p className="text-sm text-muted-foreground truncate">
                        {submission.user_email}
                      </p>
                      <div className="flex items-center gap-3 mt-2 flex-wrap">
                        {getStatusBadge(submission.status)}
                        <span className="text-xs text-muted-foreground">
                          {getIdTypeName(submission.id_type)}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {submission.country}
                        </span>
                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {format(new Date(submission.created_at), 'MMM d, yyyy')}
                        </span>
                      </div>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleViewSubmission(submission)}
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

      {/* Review Modal */}
      {selectedSubmission && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <Card className="max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>KYC Submission Review</CardTitle>
                  <CardDescription>{selectedSubmission.full_name}</CardDescription>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSelectedSubmission(null)}
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
                    {getStatusBadge(selectedSubmission.status)}
                  </div>
                  <span className="text-sm text-muted-foreground">
                    Submitted: {format(new Date(selectedSubmission.created_at), 'MMM d, yyyy HH:mm')}
                  </span>
                </div>

                {/* Personal Information */}
                <div className="space-y-3">
                  <h3 className="font-semibold text-lg">Personal Information</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Full Name</p>
                      <p className="font-medium">{selectedSubmission.full_name}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Email</p>
                      <p className="font-medium">{selectedSubmission.user_email}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Date of Birth</p>
                      <p className="font-medium">
                        {format(new Date(selectedSubmission.date_of_birth), 'MMM d, yyyy')}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Phone Number</p>
                      <p className="font-medium">{selectedSubmission.phone_number}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Country</p>
                      <p className="font-medium">{selectedSubmission.country}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">City</p>
                      <p className="font-medium">{selectedSubmission.city}</p>
                    </div>
                    <div className="col-span-2">
                      <p className="text-muted-foreground">Address</p>
                      <p className="font-medium">
                        {selectedSubmission.address}, {selectedSubmission.postal_code}
                      </p>
                    </div>
                  </div>
                </div>

                {/* ID Information */}
                <div className="space-y-3 border-t pt-6">
                  <h3 className="font-semibold text-lg">Identity Document</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">ID Type</p>
                      <p className="font-medium">{getIdTypeName(selectedSubmission.id_type)}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">ID Number</p>
                      <p className="font-medium font-mono">{selectedSubmission.id_number}</p>
                    </div>
                  </div>
                </div>

                {/* Document Images */}
                <div className="space-y-3 border-t pt-6">
                  <h3 className="font-semibold text-lg">Uploaded Documents</h3>
                  <div className="grid grid-cols-2 gap-4">
                    {selectedSubmission.id_front_url && (
                      <div className="border rounded-lg p-3">
                        <p className="text-xs text-muted-foreground mb-2 flex items-center gap-1">
                          <ImageIcon className="h-3 w-3" />
                          ID Front
                        </p>
                        <a
                          href={selectedSubmission.id_front_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-primary hover:underline"
                        >
                          View Document
                        </a>
                      </div>
                    )}
                    {selectedSubmission.id_back_url && (
                      <div className="border rounded-lg p-3">
                        <p className="text-xs text-muted-foreground mb-2 flex items-center gap-1">
                          <ImageIcon className="h-3 w-3" />
                          ID Back
                        </p>
                        <a
                          href={selectedSubmission.id_back_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-primary hover:underline"
                        >
                          View Document
                        </a>
                      </div>
                    )}
                    {selectedSubmission.selfie_url && (
                      <div className="border rounded-lg p-3">
                        <p className="text-xs text-muted-foreground mb-2 flex items-center gap-1">
                          <ImageIcon className="h-3 w-3" />
                          Selfie
                        </p>
                        <a
                          href={selectedSubmission.selfie_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-primary hover:underline"
                        >
                          View Document
                        </a>
                      </div>
                    )}
                    {selectedSubmission.proof_of_address_url && (
                      <div className="border rounded-lg p-3">
                        <p className="text-xs text-muted-foreground mb-2 flex items-center gap-1">
                          <ImageIcon className="h-3 w-3" />
                          Proof of Address
                        </p>
                        <a
                          href={selectedSubmission.proof_of_address_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-primary hover:underline"
                        >
                          View Document
                        </a>
                      </div>
                    )}
                  </div>
                </div>

                {/* Admin Notes */}
                <div className="space-y-3 border-t pt-6">
                  <h3 className="font-semibold text-lg">Admin Notes</h3>
                  {selectedSubmission.admin_notes && (
                    <div className="p-3 bg-muted rounded-lg mb-3">
                      <p className="text-xs text-muted-foreground mb-1">Previous Notes:</p>
                      <p className="text-sm">{selectedSubmission.admin_notes}</p>
                    </div>
                  )}
                  <Textarea
                    placeholder="Add notes about this verification (required for rejection)..."
                    value={adminNotes}
                    onChange={(e) => setAdminNotes(e.target.value)}
                    rows={4}
                    disabled={isProcessing || selectedSubmission.status !== 'pending'}
                  />
                </div>

                {/* Action Buttons */}
                {selectedSubmission.status === 'pending' && (
                  <div className="flex gap-3 border-t pt-6">
                    <Button
                      onClick={handleApprove}
                      disabled={isProcessing}
                      className="flex-1 bg-green-600 hover:bg-green-700"
                    >
                      {isProcessing ? (
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      ) : (
                        <CheckCircle className="h-4 w-4 mr-2" />
                      )}
                      Approve KYC
                    </Button>
                    <Button
                      onClick={handleReject}
                      disabled={isProcessing}
                      variant="destructive"
                      className="flex-1"
                    >
                      {isProcessing ? (
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      ) : (
                        <XCircle className="h-4 w-4 mr-2" />
                      )}
                      Reject KYC
                    </Button>
                  </div>
                )}

                {selectedSubmission.status !== 'pending' && (
                  <div className="flex items-center gap-2 p-4 bg-muted rounded-lg">
                    <AlertCircle className="h-5 w-5 text-muted-foreground" />
                    <p className="text-sm text-muted-foreground">
                      This submission has already been {selectedSubmission.status}
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
