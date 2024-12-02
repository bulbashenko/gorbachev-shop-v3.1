'use client';

import { useCartTransfer } from '@/hooks/useCartTransfer';
import { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '@/store';
import { fetchCart } from '@/store/slices/cartSlice';
import { useAuth } from '@/contexts/AuthContext';

export default function CartProvider({ children }: { children: React.ReactNode }) {
    const dispatch = useDispatch<AppDispatch>();
    const { isAuthenticated, isLoading } = useAuth();
    useCartTransfer(); // Handle cart transfer when user logs in

    useEffect(() => {
        let isMounted = true;

        const initializeCart = async () => {
            try {
                // Ждем пока закончится проверка авторизации
                if (!isLoading) {
                    if (isMounted) {
                        await dispatch(fetchCart()).unwrap();
                    }
                }
            } catch (error) {
                console.error('Failed to initialize cart:', error);
            }
        };

        initializeCart();

        return () => {
            isMounted = false;
        };
    }, [dispatch, isLoading, isAuthenticated]);

    return children;
}