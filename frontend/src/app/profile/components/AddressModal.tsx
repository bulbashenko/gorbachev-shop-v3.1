'use client';

import { useState } from 'react';
import type { AddressData } from '@/app/api/services/profile.service';

interface AddressModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: AddressData) => Promise<void>;
  type: 'shipping' | 'billing';
  initialData?: AddressData;
  title: string;
}

export default function AddressModal({
  isOpen,
  onClose,
  onSubmit,
  type,
  initialData,
  title
}: AddressModalProps) {
  const [formData, setFormData] = useState<AddressData>(
    initialData || {
      full_name: '',
      phone: '',
      country: '',
      city: '',
      street_address: '',
      apartment: '',
      postal_code: '',
      state: '',
      delivery_instructions: '',
      is_default: false,
      address_type: type,
    }
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await onSubmit(formData);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save address');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-[#1a1a1a] rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-semibold mb-4 text-white">{title}</h2>
        
        {error && (
          <div className="bg-red-500/10 border border-red-500 text-red-500 px-4 py-2 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-white mb-1">Full Name</label>
            <input
              type="text"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 bg-transparent border border-white/30 rounded text-white focus:outline-none focus:border-white"
            />
          </div>

          <div>
            <label className="block text-sm text-white mb-1">Phone</label>
            <input
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 bg-transparent border border-white/30 rounded text-white focus:outline-none focus:border-white"
            />
          </div>

          <div>
            <label className="block text-sm text-white mb-1">Country</label>
            <input
              type="text"
              name="country"
              value={formData.country}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 bg-transparent border border-white/30 rounded text-white focus:outline-none focus:border-white"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-white mb-1">City</label>
              <input
                type="text"
                name="city"
                value={formData.city}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 bg-transparent border border-white/30 rounded text-white focus:outline-none focus:border-white"
              />
            </div>
            <div>
              <label className="block text-sm text-white mb-1">State</label>
              <input
                type="text"
                name="state"
                value={formData.state || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 bg-transparent border border-white/30 rounded text-white focus:outline-none focus:border-white"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm text-white mb-1">Street Address</label>
            <input
              type="text"
              name="street_address"
              value={formData.street_address}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 bg-transparent border border-white/30 rounded text-white focus:outline-none focus:border-white"
            />
          </div>

          <div>
            <label className="block text-sm text-white mb-1">Apartment (optional)</label>
            <input
              type="text"
              name="apartment"
              value={formData.apartment || ''}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-transparent border border-white/30 rounded text-white focus:outline-none focus:border-white"
            />
          </div>

          <div>
            <label className="block text-sm text-white mb-1">Postal Code</label>
            <input
              type="text"
              name="postal_code"
              value={formData.postal_code}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 bg-transparent border border-white/30 rounded text-white focus:outline-none focus:border-white"
            />
          </div>

          {type === 'shipping' && (
            <div>
              <label className="block text-sm text-white mb-1">Delivery Instructions (optional)</label>
              <textarea
                name="delivery_instructions"
                value={formData.delivery_instructions || ''}
                onChange={handleChange}
                rows={3}
                className="w-full px-3 py-2 bg-transparent border border-white/30 rounded text-white focus:outline-none focus:border-white"
              />
            </div>
          )}

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              name="is_default"
              id="is_default"
              checked={formData.is_default}
              onChange={handleChange}
              className="w-4 h-4"
            />
            <label htmlFor="is_default" className="text-sm text-white">
              Set as default {type} address
            </label>
          </div>

          <div className="flex justify-end gap-4 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-white hover:bg-white/10 rounded transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-white text-black rounded hover:bg-gray-100 transition-colors disabled:opacity-50"
            >
              {loading ? 'Saving...' : 'Save Address'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
