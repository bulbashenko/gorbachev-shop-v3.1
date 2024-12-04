'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import { profileService, type MarketingPreferences, type UpdateProfileData, type AddressData } from '@/app/api/services/profile.service';
import AddressModal from '../components/AddressModal';

interface UserProfile {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone: string;
  birth_date: string | null;
  gender: 'M' | 'F' | 'O' | '';
  avatar: string | null;
  is_verified: boolean;
  email_verified: boolean;
  phone_verified: boolean;
  newsletter_subscription: boolean;
  marketing_preferences: MarketingPreferences;
  language_preference: string;
  currency_preference: string;
  addresses: UserAddress[];
  default_shipping_address: UserAddress | null;
  default_billing_address: UserAddress | null;
  has_valid_shipping_address: boolean;
  has_valid_billing_address: boolean;
}

interface UserAddress {
  id: string;
  address_type: 'shipping' | 'billing';
  is_default: boolean;
  full_name: string;
  phone: string;
  country: string;
  city: string;
  street_address: string;
  apartment: string;
  postal_code: string;
  state: string;
  delivery_instructions: string;
  formatted_address: string;
  is_active: boolean;
}

type AddressFormData = AddressData;

export default function ProfileSettings() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('personal');
  const [isAddressModalOpen, setIsAddressModalOpen] = useState(false);
  const [addressModalType, setAddressModalType] = useState<'shipping' | 'billing'>('shipping');
  const [selectedAddress, setSelectedAddress] = useState<UserAddress | null>(null);
  const [formSubmitting, setFormSubmitting] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const data = await profileService.getProfile();
      setProfile(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handlePersonalInfoSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!profile || formSubmitting) return;

    setFormSubmitting(true);
    try {
      const formData = new FormData(e.currentTarget);
      const data: UpdateProfileData = {
        first_name: formData.get('first_name') as string,
        last_name: formData.get('last_name') as string,
        email: formData.get('email') as string,
        phone: formData.get('phone') as string,
        birth_date: formData.get('birth_date') as string || null,
        gender: formData.get('gender') as 'M' | 'F' | 'O' | '',
      };

      const updatedProfile = await profileService.updateProfile(data);
      setProfile(updatedProfile);
      alert('Profile updated successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update profile');
    } finally {
      setFormSubmitting(false);
    }
  };

  const handlePasswordChange = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (formSubmitting) return;

    setFormSubmitting(true);
    try {
      const formData = new FormData(e.currentTarget);
      const data = {
        old_password: formData.get('old_password') as string,
        new_password: formData.get('new_password') as string,
        new_password2: formData.get('new_password2') as string,
      };

      await profileService.changePassword(data);
      alert('Password changed successfully');
      (e.target as HTMLFormElement).reset();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to change password');
    } finally {
      setFormSubmitting(false);
    }
  };

  const handlePreferencesSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!profile || formSubmitting) return;

    setFormSubmitting(true);
    try {
      const formData = new FormData(e.currentTarget);
      const data: UpdateProfileData = {
        language_preference: formData.get('language_preference') as string,
        currency_preference: formData.get('currency_preference') as string,
        newsletter_subscription: formData.get('newsletter') === 'on',
        marketing_preferences: {
          email: formData.get('email_marketing') === 'on',
          sms: formData.get('sms_marketing') === 'on',
          push: formData.get('push_marketing') === 'on',
        },
      };

      const updatedProfile = await profileService.updateProfile(data);
      setProfile(updatedProfile);
      alert('Preferences updated successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update preferences');
    } finally {
      setFormSubmitting(false);
    }
  };

  const handleAddressSubmit = async (data: AddressFormData) => {
    try {
      if (selectedAddress) {
        await profileService.updateAddress(selectedAddress.id, data);
      } else {
        await profileService.addAddress(data);
      }
      await fetchProfile();
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to save address');
    }
  };

  const handleDeleteAddress = async (id: string) => {
    if (!confirm('Are you sure you want to delete this address?')) return;

    try {
      await profileService.deleteAddress(id);
      await fetchProfile();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete address');
    }
  };

  const handleSetDefaultAddress = async (id: string, type: 'shipping' | 'billing') => {
    try {
      await profileService.setDefaultAddress(id, type);
      await fetchProfile();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to set default address');
    }
  };

  const openAddressModal = (type: 'shipping' | 'billing', address?: UserAddress) => {
    setAddressModalType(type);
    setSelectedAddress(address || null);
    setIsAddressModalOpen(true);
  };

  const handleResendVerification = async () => {
    try {
      await profileService.resendVerification();
      alert('Verification email sent successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to resend verification');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#1a1a1a] via-[#1a1a1a] to-[#402218] flex items-center justify-center">
        <div className="text-white text-center">
          <div className="w-8 h-8 border-t-2 border-white rounded-full animate-spin mx-auto mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#1a1a1a] via-[#1a1a1a] to-[#402218] flex items-center justify-center">
        <div className="text-red-500 text-center">
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!profile) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1a1a1a] via-[#1a1a1a] to-[#402218] text-white">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Account Settings</h1>
        
        <div className="flex gap-8">
          {/* Sidebar Navigation */}
          <div className="w-64">
            <nav className="space-y-1">
              <button
                onClick={() => setActiveTab('personal')}
                className={`w-full text-left px-4 py-2 rounded ${
                  activeTab === 'personal' ? 'bg-white/10' : 'hover:bg-white/5'
                }`}
              >
                Personal Information
              </button>
              <button
                onClick={() => setActiveTab('addresses')}
                className={`w-full text-left px-4 py-2 rounded ${
                  activeTab === 'addresses' ? 'bg-white/10' : 'hover:bg-white/5'
                }`}
              >
                Addresses
              </button>
              <button
                onClick={() => setActiveTab('security')}
                className={`w-full text-left px-4 py-2 rounded ${
                  activeTab === 'security' ? 'bg-white/10' : 'hover:bg-white/5'
                }`}
              >
                Security
              </button>
              <button
                onClick={() => setActiveTab('preferences')}
                className={`w-full text-left px-4 py-2 rounded ${
                  activeTab === 'preferences' ? 'bg-white/10' : 'hover:bg-white/5'
                }`}
              >
                Preferences
              </button>
            </nav>
          </div>

          {/* Main Content */}
          <div className="flex-1 bg-white/5 rounded-lg p-6">
            {activeTab === 'personal' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold mb-4">Personal Information</h2>
                
                {/* Avatar Section */}
                <div className="flex items-center gap-4 mb-6">
                  <div className="relative w-20 h-20 rounded-full overflow-hidden bg-gray-700">
                    {profile.avatar ? (
                      <Image
                        src={profile.avatar}
                        alt="Profile"
                        fill
                        className="object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-2xl">
                        {profile.first_name[0]}
                      </div>
                    )}
                  </div>
                  <button className="px-4 py-2 border border-white/30 rounded hover:bg-white/10 transition-colors">
                    Change Photo
                  </button>
                </div>

                {/* Personal Details Form */}
                <form onSubmit={handlePersonalInfoSubmit} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm mb-1">First Name</label>
                      <input
                        type="text"
                        name="first_name"
                        defaultValue={profile.first_name}
                        required
                        className="w-full px-3 py-2 bg-transparent border border-white/30 rounded focus:outline-none focus:border-white"
                      />
                    </div>
                    <div>
                      <label className="block text-sm mb-1">Last Name</label>
                      <input
                        type="text"
                        name="last_name"
                        defaultValue={profile.last_name}
                        required
                        className="w-full px-3 py-2 bg-transparent border border-white/30 rounded focus:outline-none focus:border-white"
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm mb-1">Email</label>
                    <input
                      type="email"
                      name="email"
                      defaultValue={profile.email}
                      required
                      className="w-full px-3 py-2 bg-transparent border border-white/30 rounded focus:outline-none focus:border-white"
                    />
                    {!profile.email_verified && (
                      <div className="flex items-center gap-2 mt-1">
                        <p className="text-yellow-500 text-sm">Email not verified</p>
                        <button
                          type="button"
                          onClick={handleResendVerification}
                          className="text-sm underline"
                        >
                          Resend verification
                        </button>
                      </div>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm mb-1">Phone</label>
                    <input
                      type="tel"
                      name="phone"
                      defaultValue={profile.phone}
                      required
                      className="w-full px-3 py-2 bg-transparent border border-white/30 rounded focus:outline-none focus:border-white"
                    />
                    {!profile.phone_verified && (
                      <p className="text-yellow-500 text-sm mt-1">Phone not verified</p>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm mb-1">Birth Date</label>
                      <input
                        type="date"
                        name="birth_date"
                        defaultValue={profile.birth_date || ''}
                        className="w-full px-3 py-2 bg-transparent border border-white/30 rounded focus:outline-none focus:border-white"
                      />
                    </div>
                    <div>
                      <label className="block text-sm mb-1">Gender</label>
                      <select
                        name="gender"
                        defaultValue={profile.gender}
                        className="w-full px-3 py-2 bg-transparent border border-white/30 rounded focus:outline-none focus:border-white"
                      >
                        <option value="">Select gender</option>
                        <option value="M">Male</option>
                        <option value="F">Female</option>
                        <option value="O">Other</option>
                      </select>
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={formSubmitting}
                    className="w-full bg-white text-black py-2 rounded hover:bg-gray-100 transition-colors disabled:opacity-50"
                  >
                    {formSubmitting ? 'Saving...' : 'Save Changes'}
                  </button>
                </form>
              </div>
            )}

            {activeTab === 'addresses' && (
              <div>
                <h2 className="text-xl font-semibold mb-4">Addresses</h2>
                
                {/* Shipping Addresses */}
                <div className="mb-8">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg">Shipping Addresses</h3>
                    <button
                      onClick={() => openAddressModal('shipping')}
                      className="px-4 py-2 border border-white/30 rounded hover:bg-white/10 transition-colors"
                    >
                      Add New Address
                    </button>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {profile.addresses
                      .filter(addr => addr.address_type === 'shipping')
                      .map(address => (
                        <div
                          key={address.id}
                          className="border border-white/30 rounded p-4"
                        >
                          <div className="flex justify-between items-start mb-2">
                            <h4 className="font-medium">{address.full_name}</h4>
                            {address.is_default && (
                              <span className="text-xs bg-white/20 px-2 py-1 rounded">Default</span>
                            )}
                          </div>
                          <p className="text-sm text-gray-300">{address.formatted_address}</p>
                          <div className="mt-4 flex gap-2">
                            <button
                              onClick={() => openAddressModal('shipping', address)}
                              className="text-sm underline"
                            >
                              Edit
                            </button>
                            <button
                              onClick={() => handleDeleteAddress(address.id)}
                              className="text-sm underline text-red-400"
                            >
                              Delete
                            </button>
                            {!address.is_default && (
                              <button
                                onClick={() => handleSetDefaultAddress(address.id, 'shipping')}
                                className="text-sm underline"
                              >
                                Set as Default
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                  </div>
                </div>

                {/* Billing Addresses */}
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg">Billing Addresses</h3>
                    <button
                      onClick={() => openAddressModal('billing')}
                      className="px-4 py-2 border border-white/30 rounded hover:bg-white/10 transition-colors"
                    >
                      Add New Address
                    </button>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {profile.addresses
                      .filter(addr => addr.address_type === 'billing')
                      .map(address => (
                        <div
                          key={address.id}
                          className="border border-white/30 rounded p-4"
                        >
                          <div className="flex justify-between items-start mb-2">
                            <h4 className="font-medium">{address.full_name}</h4>
                            {address.is_default && (
                              <span className="text-xs bg-white/20 px-2 py-1 rounded">Default</span>
                            )}
                          </div>
                          <p className="text-sm text-gray-300">{address.formatted_address}</p>
                          <div className="mt-4 flex gap-2">
                            <button
                              onClick={() => openAddressModal('billing', address)}
                              className="text-sm underline"
                            >
                              Edit
                            </button>
                            <button
                              onClick={() => handleDeleteAddress(address.id)}
                              className="text-sm underline text-red-400"
                            >
                              Delete
                            </button>
                            {!address.is_default && (
                              <button
                                onClick={() => handleSetDefaultAddress(address.id, 'billing')}
                                className="text-sm underline"
                              >
                                Set as Default
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <div>
                <h2 className="text-xl font-semibold mb-4">Security Settings</h2>
                
                {/* Change Password Form */}
                <form onSubmit={handlePasswordChange} className="space-y-4 max-w-md">
                  <div>
                    <label className="block text-sm mb-1">Current Password</label>
                    <input
                      type="password"
                      name="old_password"
                      required
                      className="w-full px-3 py-2 bg-transparent border border-white/30 rounded focus:outline-none focus:border-white"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm mb-1">New Password</label>
                    <input
                      type="password"
                      name="new_password"
                      required
                      className="w-full px-3 py-2 bg-transparent border border-white/30 rounded focus:outline-none focus:border-white"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm mb-1">Confirm New Password</label>
                    <input
                      type="password"
                      name="new_password2"
                      required
                      className="w-full px-3 py-2 bg-transparent border border-white/30 rounded focus:outline-none focus:border-white"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={formSubmitting}
                    className="w-full bg-white text-black py-2 rounded hover:bg-gray-100 transition-colors disabled:opacity-50"
                  >
                    {formSubmitting ? 'Changing Password...' : 'Change Password'}
                  </button>
                </form>

                {/* Verification Status */}
                <div className="mt-8 space-y-4">
                  <div className="flex items-center justify-between p-4 border border-white/30 rounded">
                    <div>
                      <h3 className="font-medium">Email Verification</h3>
                      <p className="text-sm text-gray-300">{profile.email}</p>
                    </div>
                    {profile.email_verified ? (
                      <span className="text-green-400">Verified</span>
                    ) : (
                      <button
                        onClick={handleResendVerification}
                        className="text-sm underline"
                      >
                        Verify Email
                      </button>
                    )}
                  </div>

                  <div className="flex items-center justify-between p-4 border border-white/30 rounded">
                    <div>
                      <h3 className="font-medium">Phone Verification</h3>
                      <p className="text-sm text-gray-300">{profile.phone}</p>
                    </div>
                    {profile.phone_verified ? (
                      <span className="text-green-400">Verified</span>
                    ) : (
                      <button className="text-sm underline">Verify Phone</button>
                    )}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'preferences' && (
              <div>
                <h2 className="text-xl font-semibold mb-4">Preferences</h2>
                
                <form onSubmit={handlePreferencesSubmit} className="space-y-6">
                  {/* Language & Currency */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm mb-1">Language</label>
                      <select
                        name="language_preference"
                        defaultValue={profile.language_preference}
                        className="w-full px-3 py-2 bg-transparent border border-white/30 rounded focus:outline-none focus:border-white"
                      >
                        <option value="en">English</option>
                        <option value="ru">Russian</option>
                        <option value="sk">Slovak</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm mb-1">Currency</label>
                      <select
                        name="currency_preference"
                        defaultValue={profile.currency_preference}
                        className="w-full px-3 py-2 bg-transparent border border-white/30 rounded focus:outline-none focus:border-white"
                      >
                        <option value="USD">USD</option>
                        <option value="EUR">EUR</option>
                        <option value="RUB">RUB</option>
                      </select>
                    </div>
                  </div>

                  {/* Newsletter & Marketing */}
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        name="newsletter"
                        id="newsletter"
                        defaultChecked={profile.newsletter_subscription}
                        className="w-4 h-4"
                      />
                      <label htmlFor="newsletter">
                        Subscribe to newsletter for updates and promotions
                      </label>
                    </div>

                    <div>
                      <h3 className="font-medium mb-2">Marketing Preferences</h3>
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            name="email_marketing"
                            id="email_marketing"
                            defaultChecked={profile.marketing_preferences?.email}
                            className="w-4 h-4"
                          />
                          <label htmlFor="email_marketing">
                            Receive marketing emails
                          </label>
                        </div>
                        <div className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            name="sms_marketing"
                            id="sms_marketing"
                            defaultChecked={profile.marketing_preferences?.sms}
                            className="w-4 h-4"
                          />
                          <label htmlFor="sms_marketing">
                            Receive SMS marketing
                          </label>
                        </div>
                        <div className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            name="push_marketing"
                            id="push_marketing"
                            defaultChecked={profile.marketing_preferences?.push}
                            className="w-4 h-4"
                          />
                          <label htmlFor="push_marketing">
                            Receive push notifications
                          </label>
                        </div>
                      </div>
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={formSubmitting}
                    className="w-full bg-white text-black py-2 rounded hover:bg-gray-100 transition-colors disabled:opacity-50"
                  >
                    {formSubmitting ? 'Saving...' : 'Save Preferences'}
                  </button>
                </form>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Address Modal */}
      <AddressModal
        isOpen={isAddressModalOpen}
        onClose={() => {
          setIsAddressModalOpen(false);
          setSelectedAddress(null);
        }}
        onSubmit={handleAddressSubmit}
        type={addressModalType}
        initialData={selectedAddress as AddressFormData}
        title={selectedAddress ? 'Edit Address' : 'Add New Address'}
      />
    </div>
  );
}
