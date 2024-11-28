import { UserLogin, UserRegister, AuthResponse, User, ApiError } from '../types/auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_PREFIX = '/api';

export const authService = {
    async login(credentials: UserLogin): Promise<AuthResponse> {
        try {
            console.log('Login attempt with URL:', `${API_URL}${API_PREFIX}/auth/login`);
            console.log('Credentials:', credentials);

            const formData = new URLSearchParams();
            formData.append('username', credentials.email);
            formData.append('password', credentials.password);

            const response = await fetch(`${API_URL}${API_PREFIX}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData,
                credentials: 'include',  // Important for cookies if used
            });

            console.log('Response status:', response.status);

            if (!response.ok) {
                const errorData = await response.json();
                console.error('Login error response:', errorData);
                throw new Error(errorData.detail || 'Failed to login');
            }

            const data = await response.json();
            console.log('Login successful, setting token');
            this.setToken(data.access_token);
            return data;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    },

    async register(userData: UserRegister): Promise<AuthResponse> {
        try {
            console.log('Register attempt with URL:', `${API_URL}${API_PREFIX}/auth/register`);
            const response = await fetch(`${API_URL}${API_PREFIX}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData),
            });

            if (!response.ok) {
                const error: ApiError = await response.json();
                throw new Error(error.detail || 'Failed to register');
            }

            return this.login({
                email: userData.email,
                password: userData.password,
            });
        } catch (error) {
            console.error('Registration error:', error);
            throw error;
        }
    },

    async getCurrentUser(): Promise<User> {
        const token = this.getToken();
        if (!token) throw new Error('No token found');

        const response = await fetch(`${API_URL}${API_PREFIX}/users/me`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            if (response.status === 401) {
                this.logout();
                throw new Error('Session expired');
            }
            throw new Error('Failed to fetch user data');
        }

        return response.json();
    },

    setToken(token: string): void {
        localStorage.setItem('token', token);
    },

    getToken(): string | null {
        return localStorage.getItem('token');
    },

    logout(): void {
        localStorage.removeItem('token');
    },

    isAuthenticated(): boolean {
        const token = this.getToken();
        if (!token) return false;

        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            const expiry = payload.exp * 1000; // Convert to milliseconds
            return Date.now() < expiry;
        } catch {
            return false;
        }
    },
}