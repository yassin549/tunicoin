'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import {
  Layers,
  Plus,
  Edit,
  Loader2,
  DollarSign,
  Percent,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  XCircle,
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';

interface InvestmentTier {
  id: string;
  name: string;
  description: string;
  min_deposit: number;
  return_rate: number;
  is_active: boolean;
}

export default function AdminTiersPage() {
  const { toast } = useToast();
  const [tiers, setTiers] = useState<InvestmentTier[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingTier, setEditingTier] = useState<InvestmentTier | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    min_deposit: '',
    return_rate: '',
    is_active: true,
  });

  useEffect(() => {
    fetchTiers();
  }, []);

  const fetchTiers = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.get('/api/admin/tiers');
      setTiers(response.data.tiers);
    } catch (error: any) {
      console.error('Failed to fetch tiers:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to load tiers',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateTier = () => {
    setEditingTier(null);
    setFormData({
      name: '',
      description: '',
      min_deposit: '',
      return_rate: '',
      is_active: true,
    });
    setShowModal(true);
  };

  const handleEditTier = (tier: InvestmentTier) => {
    setEditingTier(tier);
    setFormData({
      name: tier.name,
      description: tier.description,
      min_deposit: tier.min_deposit.toString(),
      return_rate: tier.return_rate.toString(),
      is_active: tier.is_active,
    });
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      toast({
        title: 'Validation Error',
        description: 'Tier name is required',
        variant: 'destructive',
      });
      return;
    }

    if (!formData.min_deposit || parseFloat(formData.min_deposit) <= 0) {
      toast({
        title: 'Validation Error',
        description: 'Minimum deposit must be greater than 0',
        variant: 'destructive',
      });
      return;
    }

    if (!formData.return_rate || parseFloat(formData.return_rate) <= 0) {
      toast({
        title: 'Validation Error',
        description: 'Return rate must be greater than 0',
        variant: 'destructive',
      });
      return;
    }

    try {
      setIsProcessing(true);

      const payload = {
        name: formData.name,
        description: formData.description,
        min_deposit: parseFloat(formData.min_deposit),
        return_rate: parseFloat(formData.return_rate),
        is_active: formData.is_active,
      };

      if (editingTier) {
        await apiClient.put(`/api/admin/tiers/${editingTier.id}`, payload);
        toast({
          title: 'Success',
          description: 'Tier updated successfully',
        });
      } else {
        await apiClient.post('/api/admin/tiers', payload);
        toast({
          title: 'Success',
          description: 'Tier created successfully',
        });
      }

      setShowModal(false);
      fetchTiers();
    } catch (error: any) {
      console.error('Failed to save tier:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to save tier',
        variant: 'destructive',
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleToggleStatus = async (tier: InvestmentTier) => {
    try {
      await apiClient.patch(`/api/admin/tiers/${tier.id}/toggle-status`);
      toast({
        title: 'Success',
        description: `Tier ${tier.is_active ? 'deactivated' : 'activated'} successfully`,
      });
      fetchTiers();
    } catch (error: any) {
      console.error('Failed to toggle tier status:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to update tier status',
        variant: 'destructive',
      });
    }
  };

  const getTierColor = (index: number) => {
    const colors = ['blue', 'purple', 'emerald', 'orange'];
    return colors[index % colors.length];
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text">Investment Tier Management</h1>
          <p className="text-muted-foreground mt-1">
            Manage investment tiers, rates, and minimum deposits
          </p>
        </div>
        <Button onClick={handleCreateTier}>
          <Plus className="h-4 w-4 mr-2" />
          Create Tier
        </Button>
      </div>

      {/* Tiers Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {isLoading ? (
          <div className="col-span-full flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : tiers.length === 0 ? (
          <div className="col-span-full text-center py-12 text-muted-foreground">
            <Layers className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No investment tiers found</p>
            <Button onClick={handleCreateTier} variant="outline" className="mt-4">
              <Plus className="h-4 w-4 mr-2" />
              Create Your First Tier
            </Button>
          </div>
        ) : (
          tiers.map((tier, index) => {
            const color = getTierColor(index);
            return (
              <Card key={tier.id} className={`border-${color}-200 relative`}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        {tier.name}
                        {tier.is_active ? (
                          <Badge className="bg-green-600">Active</Badge>
                        ) : (
                          <Badge className="bg-gray-600">Inactive</Badge>
                        )}
                      </CardTitle>
                      <CardDescription className="mt-2">
                        {tier.description}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Min Deposit */}
                  <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
                    <div className={`p-2 bg-${color}-100 rounded-lg`}>
                      <DollarSign className={`h-5 w-5 text-${color}-600`} />
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Min. Deposit</p>
                      <p className="text-lg font-bold">
                        ${tier.min_deposit.toLocaleString()}
                      </p>
                    </div>
                  </div>

                  {/* Return Rate */}
                  <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
                    <div className={`p-2 bg-${color}-100 rounded-lg`}>
                      <TrendingUp className={`h-5 w-5 text-${color}-600`} />
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Monthly Return</p>
                      <p className="text-lg font-bold text-green-600">
                        {tier.return_rate}%
                      </p>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 pt-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEditTier(tier)}
                      className="flex-1"
                    >
                      <Edit className="h-4 w-4 mr-1" />
                      Edit
                    </Button>
                    <Button
                      variant={tier.is_active ? 'destructive' : 'default'}
                      size="sm"
                      onClick={() => handleToggleStatus(tier)}
                      className="flex-1"
                    >
                      {tier.is_active ? (
                        <>
                          <XCircle className="h-4 w-4 mr-1" />
                          Deactivate
                        </>
                      ) : (
                        <>
                          <CheckCircle className="h-4 w-4 mr-1" />
                          Activate
                        </>
                      )}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })
        )}
      </div>

      {/* Information Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-blue-600" />
            Tier Management Guidelines
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li className="flex items-start gap-2">
              <span className="font-bold text-foreground">•</span>
              <span>
                <strong>Minimum Deposit:</strong> The minimum amount required to access this tier
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold text-foreground">•</span>
              <span>
                <strong>Return Rate:</strong> Monthly percentage return on the invested balance
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold text-foreground">•</span>
              <span>
                <strong>Active Status:</strong> Only active tiers are visible to users for new investments
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold text-foreground">•</span>
              <span>
                Existing accounts in deactivated tiers will continue with their current rates
              </span>
            </li>
          </ul>
        </CardContent>
      </Card>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <Card className="max-w-lg w-full">
            <CardHeader>
              <CardTitle>
                {editingTier ? 'Edit Investment Tier' : 'Create Investment Tier'}
              </CardTitle>
              <CardDescription>
                {editingTier
                  ? 'Update tier details and return rates'
                  : 'Add a new investment tier for users'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Name */}
                <div>
                  <label className="text-sm font-medium mb-2 block">Tier Name *</label>
                  <Input
                    placeholder="e.g., Premium, Professional"
                    value={formData.name}
                    onChange={(e) =>
                      setFormData({ ...formData, name: e.target.value })
                    }
                    disabled={isProcessing}
                  />
                </div>

                {/* Description */}
                <div>
                  <label className="text-sm font-medium mb-2 block">Description</label>
                  <Textarea
                    placeholder="Brief description of this tier..."
                    value={formData.description}
                    onChange={(e) =>
                      setFormData({ ...formData, description: e.target.value })
                    }
                    disabled={isProcessing}
                    rows={3}
                  />
                </div>

                {/* Min Deposit */}
                <div>
                  <label className="text-sm font-medium mb-2 block flex items-center gap-2">
                    <DollarSign className="h-4 w-4" />
                    Minimum Deposit (USD) *
                  </label>
                  <Input
                    type="number"
                    placeholder="100"
                    value={formData.min_deposit}
                    onChange={(e) =>
                      setFormData({ ...formData, min_deposit: e.target.value })
                    }
                    disabled={isProcessing}
                    step="0.01"
                    min="0"
                  />
                </div>

                {/* Return Rate */}
                <div>
                  <label className="text-sm font-medium mb-2 block flex items-center gap-2">
                    <Percent className="h-4 w-4" />
                    Monthly Return Rate (%) *
                  </label>
                  <Input
                    type="number"
                    placeholder="25"
                    value={formData.return_rate}
                    onChange={(e) =>
                      setFormData({ ...formData, return_rate: e.target.value })
                    }
                    disabled={isProcessing}
                    step="0.1"
                    min="0"
                    max="100"
                  />
                </div>

                {/* Active Status */}
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={formData.is_active}
                    onChange={(e) =>
                      setFormData({ ...formData, is_active: e.target.checked })
                    }
                    disabled={isProcessing}
                    className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  />
                  <label htmlFor="is_active" className="text-sm font-medium">
                    Active (visible to users)
                  </label>
                </div>

                {/* Actions */}
                <div className="flex gap-3 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowModal(false)}
                    disabled={isProcessing}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button type="submit" disabled={isProcessing} className="flex-1">
                    {isProcessing ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Saving...
                      </>
                    ) : editingTier ? (
                      'Update Tier'
                    ) : (
                      'Create Tier'
                    )}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
