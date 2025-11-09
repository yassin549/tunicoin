'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Shield, FileText, Upload, CheckCircle, Clock, XCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { apiClient } from '@/lib/api-client';

export default function KYCPage() {
  const router = useRouter();
  const [kycStatus, setKycStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkKYCStatus();
  }, []);

  const checkKYCStatus = async () => {
    try {
      const response = await apiClient.get('/api/kyc/status');
      setKycStatus(response.data);
    } catch (error: any) {
      if (error.response?.status !== 404) {
        console.error('Error fetching KYC status:', error);
      }
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'approved':
        return (
          <div className="flex items-center gap-2 text-green-600 font-semibold">
            <CheckCircle className="h-5 w-5" />
            <span>Verified</span>
          </div>
        );
      case 'pending':
        return (
          <div className="flex items-center gap-2 text-yellow-600 font-semibold">
            <Clock className="h-5 w-5" />
            <span>Under Review</span>
          </div>
        );
      case 'rejected':
        return (
          <div className="flex items-center gap-2 text-red-600 font-semibold">
            <XCircle className="h-5 w-5" />
            <span>Rejected</span>
          </div>
        );
      case 'needs_review':
        return (
          <div className="flex items-center gap-2 text-orange-600 font-semibold">
            <Clock className="h-5 w-5" />
            <span>Additional Info Needed</span>
          </div>
        );
      default:
        return null;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading KYC status...</p>
        </div>
      </div>
    );
  }

  // If KYC already submitted
  if (kycStatus) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 py-12">
        <div className="container mx-auto px-4 max-w-4xl">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-2xl">KYC Verification Status</CardTitle>
                  <CardDescription>Your identity verification application</CardDescription>
                </div>
                {getStatusBadge(kycStatus.status)}
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Status Messages */}
              {kycStatus.status === 'approved' && (
                <Alert className="bg-green-50 border-green-200">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-800">
                    <strong>Congratulations!</strong> Your identity has been verified. You can now make investments.
                  </AlertDescription>
                </Alert>
              )}

              {kycStatus.status === 'pending' && (
                <Alert className="bg-yellow-50 border-yellow-200">
                  <Clock className="h-4 w-4 text-yellow-600" />
                  <AlertDescription className="text-yellow-800">
                    <strong>Under Review.</strong> Our team is reviewing your submission. This usually takes 1-3 business days.
                  </AlertDescription>
                </Alert>
              )}

              {kycStatus.status === 'rejected' && (
                <Alert variant="destructive">
                  <XCircle className="h-4 w-4" />
                  <AlertDescription>
                    <strong>Verification Failed.</strong> {kycStatus.rejection_reason || 'Please resubmit with correct information.'}
                  </AlertDescription>
                </Alert>
              )}

              {kycStatus.status === 'needs_review' && (
                <Alert className="bg-orange-50 border-orange-200">
                  <Clock className="h-4 w-4 text-orange-600" />
                  <AlertDescription className="text-orange-800">
                    <strong>Additional Information Required.</strong> {kycStatus.rejection_reason || 'Please update your submission.'}
                  </AlertDescription>
                </Alert>
              )}

              {/* Submission Details */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Full Name</p>
                  <p className="font-semibold">{kycStatus.full_name}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Date of Birth</p>
                  <p className="font-semibold">{new Date(kycStatus.date_of_birth).toLocaleDateString()}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Country</p>
                  <p className="font-semibold">{kycStatus.country}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">ID Type</p>
                  <p className="font-semibold capitalize">{kycStatus.id_type.replace('_', ' ')}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Submitted</p>
                  <p className="font-semibold">{new Date(kycStatus.submitted_at).toLocaleString()}</p>
                </div>
                {kycStatus.reviewed_at && (
                  <div>
                    <p className="text-sm text-muted-foreground">Reviewed</p>
                    <p className="font-semibold">{new Date(kycStatus.reviewed_at).toLocaleString()}</p>
                  </div>
                )}
              </div>

              {/* Documents Uploaded */}
              {kycStatus.documents && Object.keys(kycStatus.documents).length > 0 && (
                <div>
                  <h3 className="font-semibold mb-2">Documents Uploaded</h3>
                  <div className="flex flex-wrap gap-2">
                    {Object.keys(kycStatus.documents).map((docType) => (
                      <div key={docType} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                        {docType.replace('_', ' ').toUpperCase()}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-4 pt-4">
                {(kycStatus.status === 'rejected' || kycStatus.status === 'needs_review') && (
                  <Button onClick={() => router.push('/kyc/submit')}>
                    Resubmit Application
                  </Button>
                )}
                <Button variant="outline" onClick={() => router.push('/invest')}>
                  {kycStatus.status === 'approved' ? 'Start Investing' : 'Back to Investment Plans'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // No KYC submitted yet - show info page
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-50 border border-green-200 text-green-700 text-sm font-semibold mb-4">
            <Shield className="h-4 w-4" />
            CMF Regulated - Identity Verification Required
          </div>
          <h1 className="text-4xl font-bold mb-4">KYC Verification</h1>
          <p className="text-xl text-muted-foreground">
            Verify your identity to start investing with ExtraCoin
          </p>
        </div>

        {/* Why KYC Card */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Why do we need verification?</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground">
              As a CMF (Conseil du Marché Financier) regulated investment platform, we are legally required
              to verify the identity of all investors. This process helps us:
            </p>
            <ul className="space-y-2 ml-6 list-disc text-muted-foreground">
              <li>Comply with anti-money laundering (AML) regulations</li>
              <li>Prevent financial fraud and identity theft</li>
              <li>Ensure the security of your investments</li>
              <li>Meet international KYC standards</li>
            </ul>
            <Alert className="bg-blue-50 border-blue-200">
              <Shield className="h-4 w-4 text-blue-600" />
              <AlertDescription className="text-blue-800">
                Your information is encrypted and stored securely. We never share your data with third parties
                without your consent.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>

        {/* Requirements */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>What you'll need</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-primary/10 text-primary mb-3">
                  <FileText className="h-6 w-6" />
                </div>
                <h3 className="font-semibold mb-2">Personal Information</h3>
                <p className="text-sm text-muted-foreground">
                  Full name, date of birth, address, and contact details
                </p>
              </div>
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-primary/10 text-primary mb-3">
                  <Upload className="h-6 w-6" />
                </div>
                <h3 className="font-semibold mb-2">Government ID</h3>
                <p className="text-sm text-muted-foreground">
                  Passport, driver's license, or national ID card
                </p>
              </div>
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-primary/10 text-primary mb-3">
                  <CheckCircle className="h-6 w-6" />
                </div>
                <h3 className="font-semibold mb-2">Proof of Address</h3>
                <p className="text-sm text-muted-foreground">
                  Utility bill or bank statement (less than 3 months old)
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Process Timeline */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Verification Process</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center font-bold">
                  1
                </div>
                <div>
                  <h4 className="font-semibold">Submit Information</h4>
                  <p className="text-sm text-muted-foreground">
                    Fill out the form with your personal details (2-3 minutes)
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center font-bold">
                  2
                </div>
                <div>
                  <h4 className="font-semibold">Upload Documents</h4>
                  <p className="text-sm text-muted-foreground">
                    Take photos of your ID and proof of address (5 minutes)
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center font-bold">
                  3
                </div>
                <div>
                  <h4 className="font-semibold">Review & Approval</h4>
                  <p className="text-sm text-muted-foreground">
                    Our team reviews your submission (1-3 business days)
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-600 text-white flex items-center justify-center font-bold">
                  ✓
                </div>
                <div>
                  <h4 className="font-semibold">Start Investing</h4>
                  <p className="text-sm text-muted-foreground">
                    Once approved, you can immediately start investing
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* CTA */}
        <div className="text-center">
          <Button size="lg" onClick={() => router.push('/kyc/submit')} className="px-8">
            Start Verification
          </Button>
          <p className="text-sm text-muted-foreground mt-4">
            Takes about 5-10 minutes to complete
          </p>
        </div>
      </div>
    </div>
  );
}
