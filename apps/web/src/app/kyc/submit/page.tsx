'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Shield, Upload, AlertCircle, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { apiClient } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';

export default function KYCSubmitPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    full_name: '',
    date_of_birth: '',
    nationality: '',
    id_type: 'passport',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    postal_code: '',
    country: '',
    phone: '',
    is_accredited_investor: false,
  });
  const [documents, setDocuments] = useState({
    id_front: null as File | null,
    id_back: null as File | null,
    selfie: null as File | null,
    proof_of_address: null as File | null,
  });
  const [errors, setErrors] = useState<any>({});

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
    }));
    // Clear error for this field
    if (errors[name]) {
      setErrors((prev: any) => ({ ...prev, [name]: null }));
    }
  };

  const handleFileChange = (documentType: string, file: File | null) => {
    setDocuments(prev => ({
      ...prev,
      [documentType]: file,
    }));
  };

  const validateStep1 = () => {
    const newErrors: any = {};
    
    if (!formData.full_name || formData.full_name.length < 3) {
      newErrors.full_name = 'Full name must be at least 3 characters';
    }
    if (!formData.date_of_birth) {
      newErrors.date_of_birth = 'Date of birth is required';
    } else {
      const age = new Date().getFullYear() - new Date(formData.date_of_birth).getFullYear();
      if (age < 18) {
        newErrors.date_of_birth = 'You must be at least 18 years old';
      }
    }
    if (!formData.phone || formData.phone.length < 10) {
      newErrors.phone = 'Valid phone number is required';
    }
    if (!formData.id_type) {
      newErrors.id_type = 'ID type is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep2 = () => {
    const newErrors: any = {};
    
    if (!formData.address_line1 || formData.address_line1.length < 5) {
      newErrors.address_line1 = 'Valid address is required';
    }
    if (!formData.city) {
      newErrors.city = 'City is required';
    }
    if (!formData.postal_code) {
      newErrors.postal_code = 'Postal code is required';
    }
    if (!formData.country || formData.country.length !== 2) {
      newErrors.country = 'Valid 2-letter country code is required (e.g., FR, US)';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep3 = () => {
    const newErrors: any = {};
    
    if (!documents.id_front) {
      newErrors.id_front = 'ID front image is required';
    }
    if (formData.id_type === 'drivers_license' && !documents.id_back) {
      newErrors.id_back = 'ID back image is required for driver\'s license';
    }
    if (!documents.selfie) {
      newErrors.selfie = 'Selfie with ID is required';
    }
    if (!documents.proof_of_address) {
      newErrors.proof_of_address = 'Proof of address is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNextStep = () => {
    if (step === 1 && validateStep1()) {
      setStep(2);
    } else if (step === 2 && validateStep2()) {
      setStep(3);
    }
  };

  const handleSubmit = async () => {
    if (!validateStep3()) {
      return;
    }

    setLoading(true);

    try {
      // Step 1: Submit KYC information
      const kycResponse = await apiClient.post('/api/kyc/submit', formData);
      
      toast({
        title: 'KYC Information Submitted',
        description: 'Now uploading documents...',
      });

      // Step 2: Upload documents
      const uploadPromises = Object.entries(documents).map(async ([docType, file]) => {
        if (file) {
          const formData = new FormData();
          formData.append('file', file);
          
          return apiClient.post(`/api/kyc/upload-document/${docType}`, formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          });
        }
      });

      await Promise.all(uploadPromises);

      toast({
        title: 'Success!',
        description: 'Your KYC application has been submitted for review.',
      });

      // Redirect to KYC status page
      router.push('/kyc');

    } catch (error: any) {
      console.error('KYC submission error:', error);
      toast({
        title: 'Submission Failed',
        description: error.response?.data?.detail || 'Failed to submit KYC. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 py-12">
      <div className="container mx-auto px-4 max-w-3xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-50 border border-green-200 text-green-700 text-sm font-semibold mb-4">
            <Shield className="h-4 w-4" />
            Secure & Encrypted
          </div>
          <h1 className="text-4xl font-bold mb-4">KYC Verification</h1>
          <p className="text-muted-foreground">
            Step {step} of 3
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className={`text-sm font-medium ${step >= 1 ? 'text-primary' : 'text-muted-foreground'}`}>
              Personal Info
            </span>
            <span className={`text-sm font-medium ${step >= 2 ? 'text-primary' : 'text-muted-foreground'}`}>
              Address
            </span>
            <span className={`text-sm font-medium ${step >= 3 ? 'text-primary' : 'text-muted-foreground'}`}>
              Documents
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-primary h-2 rounded-full transition-all duration-300"
              style={{ width: `${(step / 3) * 100}%` }}
            ></div>
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>
              {step === 1 && 'Personal Information'}
              {step === 2 && 'Address Information'}
              {step === 3 && 'Document Upload'}
            </CardTitle>
            <CardDescription>
              {step === 1 && 'Please provide your personal details exactly as they appear on your ID'}
              {step === 2 && 'Enter your current residential address'}
              {step === 3 && 'Upload clear photos of your documents'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Step 1: Personal Information */}
            {step === 1 && (
              <div className="space-y-4">
                <div>
                  <Label htmlFor="full_name">Full Legal Name *</Label>
                  <Input
                    id="full_name"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleInputChange}
                    placeholder="John Doe"
                  />
                  {errors.full_name && <p className="text-sm text-red-600 mt-1">{errors.full_name}</p>}
                </div>

                <div>
                  <Label htmlFor="date_of_birth">Date of Birth *</Label>
                  <Input
                    id="date_of_birth"
                    name="date_of_birth"
                    type="date"
                    value={formData.date_of_birth}
                    onChange={handleInputChange}
                  />
                  {errors.date_of_birth && <p className="text-sm text-red-600 mt-1">{errors.date_of_birth}</p>}
                </div>

                <div>
                  <Label htmlFor="phone">Phone Number *</Label>
                  <Input
                    id="phone"
                    name="phone"
                    type="tel"
                    value={formData.phone}
                    onChange={handleInputChange}
                    placeholder="+33123456789"
                  />
                  {errors.phone && <p className="text-sm text-red-600 mt-1">{errors.phone}</p>}
                </div>

                <div>
                  <Label htmlFor="nationality">Nationality (Optional)</Label>
                  <Input
                    id="nationality"
                    name="nationality"
                    value={formData.nationality}
                    onChange={handleInputChange}
                    placeholder="French"
                  />
                </div>

                <div>
                  <Label htmlFor="id_type">ID Document Type *</Label>
                  <select
                    id="id_type"
                    name="id_type"
                    value={formData.id_type}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="passport">Passport</option>
                    <option value="drivers_license">Driver's License</option>
                    <option value="national_id">National ID Card</option>
                  </select>
                  {errors.id_type && <p className="text-sm text-red-600 mt-1">{errors.id_type}</p>}
                </div>
              </div>
            )}

            {/* Step 2: Address Information */}
            {step === 2 && (
              <div className="space-y-4">
                <div>
                  <Label htmlFor="address_line1">Address Line 1 *</Label>
                  <Input
                    id="address_line1"
                    name="address_line1"
                    value={formData.address_line1}
                    onChange={handleInputChange}
                    placeholder="123 Main Street"
                  />
                  {errors.address_line1 && <p className="text-sm text-red-600 mt-1">{errors.address_line1}</p>}
                </div>

                <div>
                  <Label htmlFor="address_line2">Address Line 2 (Optional)</Label>
                  <Input
                    id="address_line2"
                    name="address_line2"
                    value={formData.address_line2}
                    onChange={handleInputChange}
                    placeholder="Apartment, suite, etc."
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="city">City *</Label>
                    <Input
                      id="city"
                      name="city"
                      value={formData.city}
                      onChange={handleInputChange}
                      placeholder="Paris"
                    />
                    {errors.city && <p className="text-sm text-red-600 mt-1">{errors.city}</p>}
                  </div>

                  <div>
                    <Label htmlFor="state">State/Province (Optional)</Label>
                    <Input
                      id="state"
                      name="state"
                      value={formData.state}
                      onChange={handleInputChange}
                      placeholder="Île-de-France"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="postal_code">Postal Code *</Label>
                    <Input
                      id="postal_code"
                      name="postal_code"
                      value={formData.postal_code}
                      onChange={handleInputChange}
                      placeholder="75001"
                    />
                    {errors.postal_code && <p className="text-sm text-red-600 mt-1">{errors.postal_code}</p>}
                  </div>

                  <div>
                    <Label htmlFor="country">Country Code *</Label>
                    <Input
                      id="country"
                      name="country"
                      value={formData.country}
                      onChange={handleInputChange}
                      placeholder="FR"
                      maxLength={2}
                    />
                    {errors.country && <p className="text-sm text-red-600 mt-1">{errors.country}</p>}
                  </div>
                </div>
              </div>
            )}

            {/* Step 3: Document Upload */}
            {step === 3 && (
              <div className="space-y-6">
                <Alert>
                  <Upload className="h-4 w-4" />
                  <AlertDescription>
                    Please upload clear, colored photos. All text must be readable. Max file size: 10MB per document.
                  </AlertDescription>
                </Alert>

                {/* ID Front */}
                <div>
                  <Label>ID Document (Front) *</Label>
                  <div className="mt-2 border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary transition-colors cursor-pointer">
                    <input
                      type="file"
                      accept="image/*,.pdf"
                      onChange={(e) => handleFileChange('id_front', e.target.files?.[0] || null)}
                      className="hidden"
                      id="id_front"
                    />
                    <label htmlFor="id_front" className="cursor-pointer">
                      <Upload className="h-8 w-8 mx-auto text-gray-400 mb-2" />
                      <p className="text-sm text-muted-foreground">
                        {documents.id_front ? documents.id_front.name : 'Click to upload or drag and drop'}
                      </p>
                    </label>
                  </div>
                  {errors.id_front && <p className="text-sm text-red-600 mt-1">{errors.id_front}</p>}
                </div>

                {/* ID Back (conditional) */}
                {formData.id_type === 'drivers_license' && (
                  <div>
                    <Label>ID Document (Back) *</Label>
                    <div className="mt-2 border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary transition-colors cursor-pointer">
                      <input
                        type="file"
                        accept="image/*,.pdf"
                        onChange={(e) => handleFileChange('id_back', e.target.files?.[0] || null)}
                        className="hidden"
                        id="id_back"
                      />
                      <label htmlFor="id_back" className="cursor-pointer">
                        <Upload className="h-8 w-8 mx-auto text-gray-400 mb-2" />
                        <p className="text-sm text-muted-foreground">
                          {documents.id_back ? documents.id_back.name : 'Click to upload or drag and drop'}
                        </p>
                      </label>
                    </div>
                    {errors.id_back && <p className="text-sm text-red-600 mt-1">{errors.id_back}</p>}
                  </div>
                )}

                {/* Selfie */}
                <div>
                  <Label>Selfie with ID *</Label>
                  <div className="mt-2 border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary transition-colors cursor-pointer">
                    <input
                      type="file"
                      accept="image/*"
                      onChange={(e) => handleFileChange('selfie', e.target.files?.[0] || null)}
                      className="hidden"
                      id="selfie"
                    />
                    <label htmlFor="selfie" className="cursor-pointer">
                      <Upload className="h-8 w-8 mx-auto text-gray-400 mb-2" />
                      <p className="text-sm text-muted-foreground">
                        {documents.selfie ? documents.selfie.name : 'Photo of you holding your ID'}
                      </p>
                    </label>
                  </div>
                  {errors.selfie && <p className="text-sm text-red-600 mt-1">{errors.selfie}</p>}
                </div>

                {/* Proof of Address */}
                <div>
                  <Label>Proof of Address *</Label>
                  <div className="mt-2 border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary transition-colors cursor-pointer">
                    <input
                      type="file"
                      accept="image/*,.pdf"
                      onChange={(e) => handleFileChange('proof_of_address', e.target.files?.[0] || null)}
                      className="hidden"
                      id="proof_of_address"
                    />
                    <label htmlFor="proof_of_address" className="cursor-pointer">
                      <Upload className="h-8 w-8 mx-auto text-gray-400 mb-2" />
                      <p className="text-sm text-muted-foreground">
                        {documents.proof_of_address ? documents.proof_of_address.name : 'Utility bill or bank statement (< 3 months old)'}
                      </p>
                    </label>
                  </div>
                  {errors.proof_of_address && <p className="text-sm text-red-600 mt-1">{errors.proof_of_address}</p>}
                </div>
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="flex justify-between mt-8">
              {step > 1 && (
                <Button variant="outline" onClick={() => setStep(step - 1)} disabled={loading}>
                  Back
                </Button>
              )}
              {step < 3 ? (
                <Button onClick={handleNextStep} className="ml-auto">
                  Next
                </Button>
              ) : (
                <Button onClick={handleSubmit} disabled={loading} className="ml-auto">
                  {loading ? 'Submitting...' : 'Submit Application'}
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Privacy Notice */}
        <Alert className="mt-6">
          <Shield className="h-4 w-4" />
          <AlertDescription className="text-xs">
            Your information is encrypted and stored securely. We comply with GDPR and CMF regulations. 
            Documents are only used for identity verification and will never be shared with third parties.
          </AlertDescription>
        </Alert>
      </div>
    </div>
  );
}
