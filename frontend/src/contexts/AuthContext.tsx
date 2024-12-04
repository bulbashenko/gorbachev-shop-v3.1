// src/contexts/AuthContext.tsx
'use client';

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '@/app/api/services/auth.service';

interface User {
    id: string;
    email: string;
    username: string;
    first_name: string;
    last_name: string;
    is_verified: boolean;
}

interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    login: (email: string, password: string) => Promise<void>;
    logout: () => void;
    checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();

    const refreshToken = async () => {
        try {
            const refreshToken = authService.getRefreshToken();
            if (!refreshToken) {
                throw new Error('No refresh token');
            }

            const response = await fetch(`${API_URL}/users/auth/refresh/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ refresh: refreshToken }),
            });

            if (!response.ok) {
                throw new Error('Token refresh failed');
            }

            const data = await response.json();
            localStorage.setItem('access_token', data.access);
            return data.access;
        } catch (error) {
            console.error('Token refresh failed:', error);
            throw error;
        }
    };

    const checkAuth = useCallback(async () => {
        try {
            const currentToken = authService.getToken();

            if (!currentToken) {
                setUser(null);
                setIsLoading(false);
                return;
            }

            const tryRequest = async (accessToken: string) => {
                const response = await fetch(`${API_URL}/users/users/me/`, {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`,
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include',
                });

                if (response.ok) {
                    const userData = await response.json();
                    setUser(userData);
                    return true;
                }
                return false;
            };

            // Первая попытка с текущим токеном
            let success = await tryRequest(currentToken);

            // Если не удалось, пробуем обновить токен
            if (!success) {
                try {
                    const newToken = await refreshToken();
                    success = await tryRequest(newToken);
                } catch {
                    // Если не удалось обновить токен, очищаем авторизацию
                    authService.logout();
                    setUser(null);
                }
            }

            if (!success) {
                authService.logout();
                setUser(null);
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            authService.logout();
            setUser(null);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        checkAuth();
    }, [checkAuth]);

    const login = async (email: string, password: string) => {
        setIsLoading(true);
        try {
            await authService.login({ email, password });
            await checkAuth();
            router.push('/');
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        } finally {
            setIsLoading(false);
        }
    };

    const logout = () => {
        authService.logout();
        setUser(null);
        router.push('/auth/login');
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                isAuthenticated: !!user,
                isLoading,
                login,
                logout,
                checkAuth,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}