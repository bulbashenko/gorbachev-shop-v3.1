'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '@/store';
import {
    fetchCart,
    removeFromCart,
    updateItemQuantity,
    clearCart,
    validateCart
} from '@/store/slices/cartSlice';
import { FiMinus, FiPlus, FiTrash2 } from 'react-icons/fi';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';

export default function CartPage() {
    const dispatch = useDispatch<AppDispatch>();
    const router = useRouter();
    const { isAuthenticated } = useAuth();

    const {
        data: cart,
        loading,
        error,
        removingItem,
        updatingQuantity
    } = useSelector((state: RootState) => state.cart);

    useEffect(() => {
        dispatch(fetchCart());
    }, [dispatch]);

    const handleQuantityChange = async (cartId: string, itemId: string, currentQuantity: number, delta: number) => {
        const newQuantity = currentQuantity + delta;
        if (newQuantity < 1) return;

        try {
            await dispatch(updateItemQuantity({
                cartId,
                itemId,
                data: { quantity: newQuantity }
            })).unwrap();
            // Refresh cart data after successful update
            dispatch(fetchCart());
        } catch (error) {
            console.error('Failed to update quantity:', error);
        }
    };

    const handleRemoveItem = async (cartId: string, itemId: string) => {
        try {
            await dispatch(removeFromCart({ cartId, itemId })).unwrap();
            // Refresh cart data after successful removal
            dispatch(fetchCart());
        } catch (error) {
            console.error('Failed to remove item:', error);
        }
    };

    const handleClearCart = async () => {
        if (window.confirm('Are you sure you want to clear your cart?')) {
            try {
                await dispatch(clearCart()).unwrap();
                // Refresh cart data after successful clear
                dispatch(fetchCart());
            } catch (error) {
                console.error('Failed to clear cart:', error);
            }
        }
    };

    const handleCheckout = async () => {
        try {
            if (!isAuthenticated) {
                router.push('/auth/login?redirect=/cart');
                return;
            }

            const validation = await dispatch(validateCart()).unwrap();
            if (validation.status === 'Cart is valid') {
                router.push('/checkout');
            }
        } catch (error) {
            console.error('Cart validation failed:', error);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <div className="text-foreground">
                    <div className="w-8 h-8 border-t-2 border-current rounded-full animate-spin"></div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-background p-6">
                <div className="max-w-4xl mx-auto">
                    <div className="bg-red-500/10 border border-red-500 text-red-500 p-4 rounded">
                        {error}
                    </div>
                </div>
            </div>
        );
    }

    if (!cart || cart.items.length === 0) {
        return (
            <div className="min-h-screen bg-background p-6">
                <div className="max-w-4xl mx-auto text-center">
                    <h1 className="text-2xl font-bold text-foreground mb-4">Your Cart is Empty</h1>
                    <p className="text-foreground/70 mb-8">Start shopping to add items to your cart!</p>
                    <Link
                        href="/products"
                        className="inline-block px-6 py-3 bg-foreground text-background hover:bg-foreground/90 transition-colors"
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
                    <button
                        onClick={handleClearCart}
                        className="text-red-500 hover:text-red-600 transition-colors"
                    >
                        Clear Cart
                    </button>
                </div>

                {/* Cart Items */}
                <div className="space-y-4 mb-8">
                    {cart.items.map((item) => (
                        <div
                            key={item.id}
                            className="flex items-center gap-6 bg-secondary p-4 rounded-lg"
                        >
                            {/* Product Image */}
                            <div className="w-24 h-24 bg-background rounded-lg overflow-hidden relative flex-shrink-0">
                                <Image
                                    src={item.variant.product_image || '/placeholder.png'}
                                    alt={item.variant.product_name}
                                    fill
                                    className="object-cover"
                                />
                            </div>

                            {/* Product Details */}
                            <div className="flex-grow">
                                <h3 className="text-foreground font-medium mb-1">
                                    {item.variant.product_name}
                                </h3>
                                <div className="grid grid-cols-2 gap-4 text-sm">
                                    <div>
                                        <p className="text-foreground/70">Size: <span className="text-foreground">{item.variant.size.name}</span></p>
                                        <p className="text-foreground/70">Color: <span className="text-foreground">{item.variant.color.name}</span></p>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-foreground/70">Price: <span className="text-foreground">${item.variant.price}</span></p>
                                        <p className="font-medium text-foreground">Total: ${item.total}</p>
                                    </div>
                                </div>

                                {/* Quantity Controls */}
                                <div className="flex items-center justify-between mt-4">
                                    <div className="flex items-center gap-4">
                                        <button
                                            onClick={() => handleQuantityChange(cart.id, item.id, item.quantity, -1)}
                                            disabled={updatingQuantity}
                                            className="p-1 hover:bg-background/50 rounded transition-colors disabled:opacity-50"
                                        >
                                            <FiMinus />
                                        </button>
                                        <span className="text-foreground min-w-[2rem] text-center">
                                            {item.quantity}
                                        </span>
                                        <button
                                            onClick={() => handleQuantityChange(cart.id, item.id, item.quantity, 1)}
                                            disabled={updatingQuantity || item.quantity >= item.variant.stock}
                                            className="p-1 hover:bg-background/50 rounded transition-colors disabled:opacity-50"
                                        >
                                            <FiPlus />
                                        </button>
                                    </div>
                                    <button
                                        onClick={() => handleRemoveItem(cart.id, item.id)}
                                        disabled={removingItem}
                                        className="text-red-500 hover:text-red-600 transition-colors disabled:opacity-50"
                                    >
                                        <FiTrash2 size={20} />
                                    </button>
                                </div>

                                {/* Stock Warning */}
                                {item.quantity >= item.variant.stock && (
                                    <p className="text-yellow-500 text-sm mt-2">
                                        Maximum available quantity reached
                                    </p>
                                )}
                            </div>
                        </div>
                    ))}
                </div>

                {/* Cart Summary */}
                <div className="bg-secondary p-6 rounded-lg">
                    <div className="space-y-2 mb-6">
                        <div className="flex justify-between text-foreground/70">
                            <span>Subtotal</span>
                            <span className="text-foreground">${cart.subtotal}</span>
                        </div>
                        <div className="flex justify-between text-foreground/70">
                            <span>Shipping</span>
                            <span className="text-foreground">Calculated at checkout</span>
                        </div>
                        <div className="flex justify-between text-foreground font-medium text-lg pt-4 border-t border-foreground/10">
                            <span>Total</span>
                            <span>${cart.total_price}</span>
                        </div>
                    </div>

                    <div className="flex flex-col gap-4">
                        <button
                            onClick={handleCheckout}
                            className="w-full bg-foreground text-background py-3 font-medium hover:bg-foreground/90 transition-colors"
                        >
                            {isAuthenticated ? 'Proceed to Checkout' : 'Sign in to Checkout'}
                        </button>
                        <Link
                            href="/products"
                            className="w-full text-center py-3 border border-foreground text-foreground hover:bg-secondary transition-colors"
                        >
                            Continue Shopping
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
