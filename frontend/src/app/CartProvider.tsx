// src/app/CartProvider.tsx
'use client';

import { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '@/store';
import { fetchCart } from '@/store/slices/cartSlice';
import { useAuth } from '@/contexts/AuthContext';
import { useCartTransfer } from '@/hooks/useCartTransfer';

export default function CartProvider({ children }: { children: React.ReactNode }) {
    const dispatch = useDispatch<AppDispatch>();
    const { isAuthenticated, isLoading } = useAuth();

    // Handle cart transfer when user logs in
    useCartTransfer();

    useEffect(() => {
        let isMounted = true;

        const initializeCart = async () => {
            // Wait for auth check to complete
            if (!isLoading) {
                try {
                    if (isMounted) {
                        await dispatch(fetchCart()).unwrap();
                    }
                } catch (error) {
                    console.error('Failed to initialize cart:', error);
                }
            }
        };

        initializeCart();

        return () => {
            isMounted = false;
        };
    }, [dispatch, isLoading, isAuthenticated]);

    return children;
}