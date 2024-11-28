'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { authService } from '../services/auth';
import { User } from '../types/auth';
import { useRouter } from 'next/navigation';
import { useLocale } from 'next-intl';

interface AuthContextType {
    isAuthenticated: boolean;
    user: User | null;
    isAdmin: boolean;
    login: (token: string) => Promise<void>;
    logout: () => void;
    checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [user, setUser] = useState<User | null>(null);
    const [isAdmin, setIsAdmin] = useState(false);
    const router = useRouter();
    const locale = useLocale();

    const checkAuth = async () => {
        try {
            if (authService.isAuthenticated()) {
                const userData = await authService.getCurrentUser();
                setUser(userData);
                setIsAdmin(userData.is_superuser);
                setIsAuthenticated(true);
            } else {
                setUser(null);
                setIsAdmin(false);
                setIsAuthenticated(false);
            }
        } catch (error) {
            setUser(null);
            setIsAdmin(false);
            setIsAuthenticated(false);
        }
    };

    const logout = () => {
        authService.logout();
        setUser(null);
        setIsAdmin(false);
        setIsAuthenticated(false);
        router.push(`/${locale}/auth`);
    };

    const login = async (token: string) => {
        try {
            await authService.setToken(token);
            const userData = await authService.getCurrentUser();
            setUser(userData);
            setIsAdmin(userData.is_superuser);
            setIsAuthenticated(true);

            // Redirect admin to admin panel, regular users to account page
            if (userData.is_superuser) {
                router.push(`/${locale}/admin`);
            } else {
                router.push(`/${locale}/account`);
            }
        } catch (error) {
            setUser(null);
            setIsAdmin(false);
            setIsAuthenticated(false);
            throw error;
        }
    };

    useEffect(() => {
        checkAuth();
    }, []);

    return (
        <AuthContext.Provider value={{ isAuthenticated, user, isAdmin, login, logout, checkAuth }}>
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