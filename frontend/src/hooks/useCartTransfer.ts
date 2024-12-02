import { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '@/store';
import { transferGuestCart, fetchCart } from '@/store/slices/cartSlice';
import { useAuth } from '@/contexts/AuthContext';

export const useCartTransfer = () => {
    const dispatch = useDispatch<AppDispatch>();
    const { isAuthenticated } = useAuth();

    useEffect(() => {
        let isMounted = true;

        const handleCartTransfer = async () => {
            if (isAuthenticated) {
                try {
                    await dispatch(transferGuestCart()).unwrap();
                    if (isMounted) {
                        dispatch(fetchCart());
                    }
                } catch (error) {
                    console.error('Failed to transfer guest cart:', error);
                    // Even if transfer fails, try to fetch the cart
                    if (isMounted) {
                        dispatch(fetchCart());
                    }
                }
            }
        };

        handleCartTransfer();

        return () => {
            isMounted = false;
        };
    }, [isAuthenticated, dispatch]);
};

export default useCartTransfer;
