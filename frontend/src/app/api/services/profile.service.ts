import { authService } from './auth.service';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export interface MarketingPreferences {
  email: boolean;
  sms: boolean;
  push: boolean;
}

export interface AddressData {
  id?: string;
  full_name: string;
  phone: string;
  country: string;
  city: string;
  street_address: string;
  apartment?: string;
  postal_code: string;
  state: string;
  delivery_instructions?: string;
  is_default: boolean;
  address_type?: 'shipping' | 'billing';
  formatted_address?: string;
  is_active?: boolean;
}

export interface UpdateProfileData {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  birth_date?: string | null;
  gender?: 'M' | 'F' | 'O' | '';
  marketing_preferences?: MarketingPreferences;
  newsletter_subscription?: boolean;
  language_preference?: string;
  currency_preference?: string;
}

export const profileService = {
  async getProfile() {
    const token = authService.getToken();
    if (!token) {
      throw new Error('Not authenticated');
    }

    const response = await fetch(`${API_URL}/users/users/me/`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });

    if (!response.ok) {
      if (response.status === 401) {
        authService.logout();
        throw new Error('Session expired');
      }
      throw new Error('Failed to fetch profile');
    }

    return response.json();
  },

  async updateProfile(data: UpdateProfileData) {
    const token = authService.getToken();
    if (!token) {
      throw new Error('Not authenticated');
    }

    const response = await fetch(`${API_URL}/users/users/me/`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
      credentials: 'include',
    });

    if (!response.ok) {
      if (response.status === 401) {
        authService.logout();
        throw new Error('Session expired');
      }
      throw new Error('Failed to update profile');
    }

    return response.json();
  },

  async changePassword(data: { old_password: string; new_password: string; new_password2: string }) {
    const token = authService.getToken();
    if (!token) {
      throw new Error('Not authenticated');
    }
  
    const response = await fetch(`${API_URL}/users/users/change_password/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data), // Убедитесь, что данные отправляются корректно
      credentials: 'include',
    });
  
    if (!response.ok) {
      const errorDetails = await response.json().catch(() => null);
      console.error('Server error:', errorDetails);
      if (response.status === 401) {
        authService.logout();
        throw new Error('Session expired');
      }
      throw new Error('Failed to change password');
    }
  }, 

  async updateAddress(id: string, data: AddressData) {
    const token = authService.getToken();
    if (!token) {
      throw new Error('Not authenticated');
    }

    const response = await fetch(`${API_URL}/users/addresses/${id}/`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error('Failed to update address');
    }

    return response.json();
  },

  async addAddress(data: AddressData) {
    const token = authService.getToken();
    if (!token) {
      throw new Error('Not authenticated');
    }

    const response = await fetch(`${API_URL}/users/addresses/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error('Failed to add address');
    }

    return response.json();
  },

  async deleteAddress(id: string) {
    const token = authService.getToken();
    if (!token) {
      throw new Error('Not authenticated');
    }

    const response = await fetch(`${API_URL}/users/addresses/${id}/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error('Failed to delete address');
    }
  },

  async setDefaultAddress(id: string, type: 'shipping' | 'billing') {
    const token = authService.getToken();
    if (!token) {
      throw new Error('Not authenticated');
    }

    const response = await fetch(`${API_URL}/users/addresses/${id}/set_default/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ address_type: type }),
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error('Failed to set default address');
    }

    return response.json();
  },

  async resendVerification() {
    const token = authService.getToken();
    if (!token) {
      throw new Error('Not authenticated');
    }

    const response = await fetch(`${API_URL}/users/users/resend_verification/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error('Failed to resend verification email');
    }
  }
};
