'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { ArrowLeft, Mail, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { authApi, getErrorMessage } from '@/lib/api-client';

export default function VerifyEmailPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<'pending' | 'success' | 'error'>('pending');
  const [message, setMessage] = useState('');
  const email = searchParams.get('email');
  const token = searchParams.get('token');

  useEffect(() => {
    // If token is provided in URL, verify immediately
    if (token) {
      verifyEmail(token);
    }
  }, [token]);

  const verifyEmail = async (verificationToken: string) => {
    try {
      await authApi.verifyEmail(verificationToken);
      setStatus('success');
      setMessage('Your email has been verified successfully!');
      
      // Redirect to sign in after 3 seconds
      setTimeout(() => {
        router.push('/auth/signin');
      }, 3000);
    } catch (err) {
      setStatus('error');
      setMessage(getErrorMessage(err));
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Back Link */}
        <Link
          href="/"
          className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-6 transition-colors"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to home
        </Link>

        {/* Verification Card */}
        <Card>
          <CardHeader className="space-y-1">
            <div className="flex justify-center mb-4">
              {status === 'pending' && <Loader2 className="h-16 w-16 text-primary animate-spin" />}
              {status === 'success' && <CheckCircle className="h-16 w-16 text-green-500" />}
              {status === 'error' && <AlertCircle className="h-16 w-16 text-destructive" />}
            </div>
            <CardTitle className="text-3xl font-bold text-center gradient-text">
              {status === 'pending' && 'Verify Your Email'}
              {status === 'success' && 'Email Verified!'}
              {status === 'error' && 'Verification Failed'}
            </CardTitle>
            <CardDescription className="text-center">
              {status === 'pending' && !token && email && `Check your inbox at ${email}`}
              {status === 'pending' && token && 'Verifying your email...'}
              {status === 'success' && 'Your account is now active'}
              {status === 'error' && 'Something went wrong'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Pending State */}
            {status === 'pending' && !token && (
              <div className="space-y-4">
                <Alert variant="info">
                  <Mail className="h-4 w-4" />
                  <AlertTitle>Check your email</AlertTitle>
                  <AlertDescription>
                    We've sent a verification link to <strong>{email}</strong>. Click the link in
                    the email to verify your account.
                  </AlertDescription>
                </Alert>

                <div className="text-center space-y-2">
                  <p className="text-sm text-muted-foreground">Didn't receive the email?</p>
                  <Button variant="outline" size="sm">
                    Resend verification email
                  </Button>
                </div>
              </div>
            )}

            {/* Verifying State */}
            {status === 'pending' && token && (
              <div className="text-center py-4">
                <p className="text-sm text-muted-foreground">Please wait while we verify your email...</p>
              </div>
            )}

            {/* Success State */}
            {status === 'success' && (
              <div className="space-y-4">
                <Alert variant="default" className="border-green-500 bg-green-50">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-900">
                    {message}
                  </AlertDescription>
                </Alert>

                <div className="text-center space-y-4">
                  <p className="text-sm text-muted-foreground">
                    Redirecting to sign in page in 3 seconds...
                  </p>
                  <Button onClick={() => router.push('/auth/signin')} className="w-full">
                    Continue to Sign In
                  </Button>
                </div>
              </div>
            )}

            {/* Error State */}
            {status === 'error' && (
              <div className="space-y-4">
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>Verification failed</AlertTitle>
                  <AlertDescription>{message}</AlertDescription>
                </Alert>

                <div className="space-y-2">
                  <Button onClick={() => router.push('/auth/signup')} variant="outline" className="w-full">
                    Try signing up again
                  </Button>
                  <Button onClick={() => router.push('/auth/signin')} className="w-full">
                    Back to Sign In
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
