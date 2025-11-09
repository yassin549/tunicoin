'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Shield, AlertCircle, Loader2, Copy, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { authApi, getErrorMessage } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';

export default function TwoFactorAuthPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [mode, setMode] = useState<'setup' | 'verify'>('verify');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [code, setCode] = useState('');
  const [qrCode, setQrCode] = useState('');
  const [secret, setSecret] = useState('');
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [copied, setCopied] = useState(false);

  const handleEnable2FA = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await authApi.enable2FA();
      setQrCode(response.qr_code);
      setSecret(response.secret);
      setBackupCodes(response.backup_codes || []);
      setMode('setup');
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerify2FA = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!code || code.length !== 6) {
      setError('Please enter a valid 6-digit code');
      return;
    }

    setIsLoading(true);

    try {
      await authApi.verify2FA(code);
      
      toast({
        title: '2FA verified!',
        description: 'Two-factor authentication enabled successfully.',
        variant: 'default',
      });

      router.push('/dashboard');
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    toast({
      title: 'Copied!',
      description: 'Secret key copied to clipboard',
      variant: 'default',
    });
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Back Link */}
        <Link
          href="/auth/signin"
          className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-6 transition-colors"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to sign in
        </Link>

        {/* 2FA Card */}
        <Card>
          <CardHeader className="space-y-1">
            <div className="flex justify-center mb-4">
              <Shield className="h-16 w-16 text-primary" />
            </div>
            <CardTitle className="text-3xl font-bold text-center gradient-text">
              Two-Factor Authentication
            </CardTitle>
            <CardDescription className="text-center">
              {mode === 'verify'
                ? 'Enter the 6-digit code from your authenticator app'
                : 'Scan the QR code with your authenticator app'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {mode === 'verify' ? (
              <form onSubmit={handleVerify2FA} className="space-y-4">
                {/* Error Alert */}
                {error && (
                  <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                {/* Code Input */}
                <div className="space-y-2">
                  <Label htmlFor="code">Authentication Code</Label>
                  <Input
                    id="code"
                    type="text"
                    placeholder="000000"
                    maxLength={6}
                    className="text-center text-2xl tracking-widest"
                    value={code}
                    onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
                    disabled={isLoading}
                    required
                  />
                  <p className="text-xs text-muted-foreground text-center">
                    Enter the 6-digit code from your authenticator app
                  </p>
                </div>

                {/* Submit Button */}
                <Button type="submit" className="w-full" size="lg" disabled={isLoading}>
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Verifying...
                    </>
                  ) : (
                    'Verify & Continue'
                  )}
                </Button>

                {/* Setup Link */}
                <div className="text-center">
                  <button
                    type="button"
                    onClick={handleEnable2FA}
                    className="text-sm text-primary hover:underline"
                  >
                    Need to set up 2FA?
                  </button>
                </div>
              </form>
            ) : (
              <div className="space-y-4">
                {/* QR Code */}
                {qrCode && (
                  <div className="flex justify-center py-4">
                    <div className="bg-white p-4 rounded-lg border-2 border-gray-200">
                      <img src={qrCode} alt="2FA QR Code" className="w-48 h-48" />
                    </div>
                  </div>
                )}

                {/* Manual Entry */}
                {secret && (
                  <div className="space-y-2">
                    <Label>Manual Entry Key</Label>
                    <div className="flex gap-2">
                      <Input value={secret} readOnly className="font-mono text-sm" />
                      <Button
                        type="button"
                        variant="outline"
                        size="icon"
                        onClick={() => copyToClipboard(secret)}
                      >
                        {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                      </Button>
                    </div>
                  </div>
                )}

                {/* Backup Codes */}
                {backupCodes.length > 0 && (
                  <Alert>
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>Save your backup codes</AlertTitle>
                    <AlertDescription className="space-y-2">
                      <p className="text-xs">
                        Store these codes in a safe place. Each can be used once if you lose access
                        to your authenticator.
                      </p>
                      <div className="grid grid-cols-2 gap-2 mt-2 font-mono text-xs">
                        {backupCodes.map((code, i) => (
                          <div key={i} className="bg-muted p-2 rounded">
                            {code}
                          </div>
                        ))}
                      </div>
                    </AlertDescription>
                  </Alert>
                )}

                {/* Next Step */}
                <div className="space-y-2">
                  <Button
                    onClick={() => setMode('verify')}
                    className="w-full"
                    size="lg"
                  >
                    Continue to Verification
                  </Button>
                  <p className="text-xs text-center text-muted-foreground">
                    Scan the QR code and enter the code from your app
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Apps Recommendation */}
        <div className="mt-6 text-center">
          <p className="text-xs text-muted-foreground mb-2">Recommended authenticator apps:</p>
          <p className="text-xs text-muted-foreground">
            Google Authenticator • Microsoft Authenticator • Authy
          </p>
        </div>
      </div>
    </div>
  );
}
