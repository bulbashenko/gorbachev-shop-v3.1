'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch } from '@/store';
import {
    fetchCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    validateCart,
    selectCart,
    selectCartLoading,
    selectRemovingItem,
} from '@/store/slices/cartSlice';
import { FiMinus, FiPlus, FiTrash2 } from 'react-icons/fi';
import Link from 'next/link';
import { throttle } from 'lodash';
import { useAuth } from '@/contexts/AuthContext';
import ProductImage from '@/components/ProductImage';

// ... rest of the file content remains exactly the same ...

interface CartItem {
    id: string;
    quantity: number;
    total: string;
    variant: {
        id: string;
        stock: number;
        product: {
            name: string;
            price: string;
            images?: Array<{
                id: string;
                image: string;
                is_main?: boolean;
            }>;
        };
        size: {
            name: string;
        };
        color: {
            name: string;
        };
    };
}

interface Cart {
    id: string;
    items: CartItem[];
}

interface ValidationResponse {
    status: string;
}

function debounce<F extends (...args: Parameters<F>) => ReturnType<F>>(
    func: F,
    wait: number
): (...args: Parameters<F>) => void {
    let timeout: NodeJS.Timeout;
    return (...args: Parameters<F>) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}

export default function CartPage() {
    const dispatch = useDispatch<AppDispatch>();
    const router = useRouter();
    const { isAuthenticated } = useAuth();

    const cart = useSelector(selectCart) as Cart | null;
    const loading = useSelector(selectCartLoading);
    const removingItem = useSelector(selectRemovingItem);

    const [localQuantities, setLocalQuantities] = useState<Record<string, number>>({});
    const [optimisticCart, setOptimisticCart] = useState<Record<string, number>>({});
    const [optimisticPrices, setOptimisticPrices] = useState<Record<string, string>>({});
    const [optimisticTotalPrice, setOptimisticTotalPrice] = useState<string>("0.00");

    const getDisplayQuantity = useCallback((itemId: string, baseQuantity: number): number => {
        return optimisticCart[itemId] ?? localQuantities[itemId] ?? baseQuantity;
    }, [optimisticCart, localQuantities]);

    const calculateItemPrice = useCallback((price: string | undefined, quantity: number): string => {
        const numericPrice = price ? parseFloat(price) : 0;
        return (numericPrice * quantity).toFixed(2);
    }, []);

    const calculateTotalPrice = useCallback((): string => {
        if (!cart?.items?.length) return "0.00";

        const total = cart.items.reduce((sum, item) => {
            const quantity = getDisplayQuantity(item.id, item.quantity);
            const price = item.variant?.product?.price;
            
            if (!price) return sum;

            const itemPrice = optimisticPrices[item.id]
                ? parseFloat(optimisticPrices[item.id])
                : parseFloat(calculateItemPrice(price, quantity));

            return sum + itemPrice;
        }, 0);

        return total.toFixed(2);
    }, [cart?.items, getDisplayQuantity, optimisticPrices, calculateItemPrice]);

    const throttledFetchCart = useCallback(
        throttle(() => {
            dispatch(fetchCart());
        }, 2000, { leading: false, trailing: true }),
        [dispatch]
    );

    const debouncedUpdateQuantity = useCallback(
        debounce((itemId: string, quantity: number) => {
            if (!cart?.id) return;

            dispatch(updateQuantity({
                cartId: cart.id,
                itemId,
                data: { quantity }
            })).unwrap()
                .catch((error: Error) => {
                    console.error('Error updating quantity:', error);
                    const originalQuantity = cart.items.find(item => item.id === itemId)?.quantity;
                    if (originalQuantity) {
                        setLocalQuantities(prev => ({
                            ...prev,
                            [itemId]: originalQuantity
                        }));
                        setOptimisticCart(prev => {
                            const next = { ...prev };
                            delete next[itemId];
                            return next;
                        });
                        setOptimisticPrices(prev => {
                            const next = { ...prev };
                            delete next[itemId];
                            return next;
                        });
                    }
                });
        }, 1000),
        [cart?.id, dispatch]
    );

    const handleQuantityChange = useCallback((itemId: string, delta: number) => {
        const item = cart?.items?.find(i => i.id === itemId);
        if (!item || !cart) return;

        const currentQty = getDisplayQuantity(itemId, item.quantity);
        const newQty = Math.max(1, Math.min(currentQty + delta, item.variant.stock ?? Infinity));

        if (newQty !== currentQty) {
            console.log('Updating quantity:', { itemId, currentQty, newQty }); // Debug log

            // Update local states
            setLocalQuantities(prev => ({
                ...prev,
                [itemId]: newQty
            }));

            setOptimisticCart(prev => ({
                ...prev,
                [itemId]: newQty,
            }));

            // Calculate and update the new item price
            if (item.variant?.product?.price) {
                const itemPrice = parseFloat(item.variant.product.price) * newQty;
                setOptimisticPrices(prev => ({
                    ...prev,
                    [itemId]: itemPrice.toFixed(2)
                }));

                // Calculate new total price considering all items
                const newTotal = cart.items.reduce((sum, cartItem) => {
                    if (cartItem.id === itemId) {
                        return sum + itemPrice;
                    } else {
                        const currentQuantity = getDisplayQuantity(cartItem.id, cartItem.quantity);
                        const currentPrice = cartItem.variant?.product?.price 
                            ? parseFloat(cartItem.variant.product.price) * currentQuantity
                            : 0;
                        return sum + currentPrice;
                    }
                }, 0);

                setOptimisticTotalPrice(newTotal.toFixed(2));
            }

            // Send update to server
            if (cart?.id) {
                debouncedUpdateQuantity(itemId, newQty);
            }
        }
    }, [cart, debouncedUpdateQuantity, getDisplayQuantity]);

    const handleRemoveItem = async (cartId: string, itemId: string) => {
        try {
            await dispatch(removeFromCart({ cartId, itemId })).unwrap();
            setOptimisticCart(prev => {
                const next = { ...prev };
                delete next[itemId];
                return next;
            });
            setOptimisticPrices(prev => {
                const next = { ...prev };
                delete next[itemId];
                return next;
            });
            setOptimisticTotalPrice(calculateTotalPrice());
        } catch (error) {
            if (error instanceof Error) {
                console.error('Error removing item:', error);
            }
        }
    };

    const handleClearCart = async () => {
        try {
            await dispatch(clearCart()).unwrap();
            setOptimisticCart({});
            setOptimisticPrices({});
            setLocalQuantities({});
            setOptimisticTotalPrice("0.00");
        } catch (error) {
            if (error instanceof Error) {
                console.error('Error clearing cart:', error);
            }
        }
    };

    const handleCheckout = async () => {
        if (!isAuthenticated) {
            router.push('/auth/login?redirect=/cart');
            return;
        }

        try {
            const validation = await dispatch(validateCart()).unwrap() as ValidationResponse;
            if (validation.status === 'Cart is valid') {
                router.push('/checkout');
            }
        } catch (error) {
            if (error instanceof Error) {
                console.error('Error validating cart:', error);
            }
            dispatch(fetchCart());
        }
    };

    useEffect(() => {
        dispatch(fetchCart());
    }, [dispatch]);

    useEffect(() => {
        if (cart?.items) {
            // Initialize local quantities
            const quantities = cart.items.reduce((acc, item) => ({
                ...acc,
                [item.id]: item.quantity
            }), {} as Record<string, number>);
            setLocalQuantities(quantities);

            // Calculate initial total if no optimistic updates are pending
            if (Object.keys(optimisticCart).length === 0) {
                const initialPrices = cart.items.reduce((acc, item) => ({
                    ...acc,
                    [item.id]: item.total
                }), {});
                setOptimisticPrices(initialPrices);

                const total = cart.items.reduce((sum, item) => 
                    sum + parseFloat(item.total), 0
                ).toFixed(2);
                setOptimisticTotalPrice(total);
            }
        }
    }, [cart?.items, optimisticCart]);

    useEffect(() => {
        return () => {
            throttledFetchCart.cancel();
        };
    }, [throttledFetchCart]);

    if (loading) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <div className="w-8 h-8 border-t-2 border-foreground rounded-full animate-spin"></div>
            </div>
        );
    }

    if (!cart?.items?.length) {
        return (
            <div className="min-h-screen bg-background p-6">
                <div className="max-w-4xl mx-auto text-center">
                    <h1 className="text-2xl font-bold text-foreground mb-4">Your Cart is Empty</h1>
                    <p className="text-foreground/70 mb-8">Start shopping to add items to your cart!</p>
                    <Link
                        href="/products"
                        className="inline-block px-6 py-3 bg-foreground text-background rounded hover:bg-foreground/90 transition-colors"
                    >
                        Continue Shopping
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-background p-6">
            <div className="max-w-4xl mx-auto">
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-2xl font-bold text-foreground">Shopping Cart</h1>
                    <div className="flex items-center gap-4">
                        <div className="text-lg font-semibold">
                            Total: ${optimisticTotalPrice}
                        </div>
                        <button
                            onClick={handleClearCart}
                            className="text-red-500 hover:text-red-600 transition-colors"
                        >
                            Clear Cart
                        </button>
                    </div>
                </div>

                <div className="space-y-4 mb-8">
                    {cart.items.map((item: CartItem) => {
                        const mainImage = item.variant?.product?.images?.find(img => img?.is_main)?.image
                            || item.variant?.product?.images?.[0]?.image
                            || '/images/placeholder.jpg';

                        const quantity = getDisplayQuantity(item.id, item.quantity);

                        return (
                            <div
                                key={item.id}
                                className="flex items-center gap-6 bg-secondary p-4 rounded-lg"
                            >
                                <div className="w-24 h-24 bg-background rounded-lg overflow-hidden relative flex-shrink-0">
                                    <ProductImage
                                        src={mainImage}
                                        alt={item.variant?.product?.name || 'Product'}
                                        fallback="/images/placeholder.jpg"
                                    />
                                </div>

                                <div className="flex-grow">
                                    <h3 className="text-foreground font-medium mb-1">
                                        {item.variant?.product?.name}
                                    </h3>
                                    <div className="grid grid-cols-2 gap-4 text-sm">
                                        <div>
                                            <p className="text-foreground/70">Size: <span className="text-foreground">{item.variant?.size?.name}</span></p>
                                            <p className="text-foreground/70">Color: <span className="text-foreground">{item.variant?.color?.name}</span></p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-foreground/70">
                                                Price: <span className="text-foreground">
                                                    ${item.variant?.product?.price}
                                                </span>
                                            </p>
                                            <p className="font-medium text-foreground">
                                                Total: ${optimisticPrices[item.id] || item.total}
                                            </p>
                                        </div>
                                    </div>

                                    <div className="flex items-center justify-between mt-4">
                                        <div className="flex items-center gap-4">
                                            <button
                                                onClick={() => handleQuantityChange(item.id, -1)}
                                                disabled={quantity <= 1}
                                                className="p-2 hover:bg-background/50 rounded transition-colors disabled:opacity-50"
                                                aria-label="Decrease quantity"
                                            >
                                                <FiMinus size={16} />
                                            </button>
                                            <span className="text-foreground min-w-[2rem] text-center">
                                                {quantity}
                                            </span>
                                            <button
                                                onClick={() => handleQuantityChange(item.id, 1)}
                                                disabled={quantity >= (item.variant.stock ?? Infinity)}
                                                className="p-2 hover:bg-background/50 rounded transition-colors disabled:opacity-50"
                                                aria-label="Increase quantity"
                                            >
                                                <FiPlus size={16} />
                                            </button>
                                        </div>
                                        <button
                                            onClick={() => cart?.id && handleRemoveItem(cart.id, item.id)}
                                            disabled={removingItem === true}
                                            className="text-red-500 hover:text-red-600 transition-colors disabled:opacity-50"
                                            aria-label="Remove item"
                                        >
                                            <FiTrash2 size={20} />
                                        </button>
                                    </div>

                                    {item.variant?.stock != null && quantity >= item.variant.stock && (
                                        <p className="text-yellow-500 text-sm mt-2">
                                            Maximum available quantity reached
                                        </p>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>

                <div className="bg-secondary p-6 rounded-lg">
                    <div className="space-y-2 mb-6">
                        <div className="flex justify-between text-foreground font-medium text-xl pt-4">
                            <span>Total</span>
                            <span>${optimisticTotalPrice}</span>
                        </div>
                    </div>

                    <div className="flex flex-col gap-4">
                        <button
                            onClick={handleCheckout}
                            className="w-full bg-foreground text-background py-3 rounded font-medium hover:bg-foreground/90 transition-colors disabled:opacity-50"
                            disabled={!cart?.items?.length}
                        >
                            {isAuthenticated ? 'Proceed to Checkout' : 'Sign in to Checkout'}
                        </button>
                        <Link
                            href="/products"
                            className="w-full text-center py-3 border border-foreground rounded text-foreground hover:bg-secondary transition-colors"
                        >
                            Continue Shopping
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
