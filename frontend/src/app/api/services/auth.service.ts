// src/app/api/services/auth.service.ts
export interface LoginData {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  password2: string;
  first_name: string;
  last_name: string;
  phone?: string;
  newsletter_subscription?: boolean;
  marketing_preferences?: Record<string, unknown>;
  terms_accepted: boolean;
  language_preference?: string;
  currency_preference?: string;
}

export interface ResetPasswordData {
  email: string;
}

export interface NewPasswordData {
  token: string;
  new_password: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export const authService = {
  async login(data: LoginData) {
    console.log('Making login request to:', `${API_URL}/users/auth/login/`);
    console.log('With data:', data);

    const response = await fetch(`${API_URL}/users/auth/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
      credentials: 'include',
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Login failed');
    }

    const responseData = await response.json();

    // Save tokens to localStorage
    if (responseData.access) {
      localStorage.setItem('access_token', responseData.access);
    }
    if (responseData.refresh) {
      localStorage.setItem('refresh_token', responseData.refresh);
    }

    return responseData;
  },

  async register(data: RegisterData) {
    const response = await fetch(`${API_URL}/users/auth/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('Server error response:', errorData);
      throw new Error(errorData.detail || 'Registration failed');
    }

    return response.json();
  },

  async requestPasswordReset(data: ResetPasswordData) {
    const response = await fetch(`${API_URL}/users/users/request_password_reset/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error('Password reset request failed');
    }
  },

  async resetPassword(data: NewPasswordData) {
    const response = await fetch(`${API_URL}/users/users/reset_password/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error('Setting new password failed');
    }
  },

  async verifyEmail(token: string) {
    const response = await fetch(`${API_URL}/users/users/verify_email/?token=${token}`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error('Email verification failed');
    }
  },

  getToken() {
    return typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  },

  getRefreshToken() {
    return typeof window !== 'undefined' ? localStorage.getItem('refresh_token') : null;
  },

  isAuthenticated() {
    return !!this.getToken();
  },

  logout() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }
};