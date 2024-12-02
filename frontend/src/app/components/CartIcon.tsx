'use client';

import Link from 'next/link';
import { useSelector } from 'react-redux';
import { RootState } from '@/store';

export default function CartIcon() {
    const cart = useSelector((state: RootState) => state.cart.data);

    return (
        <Link href="/cart" className="relative hover:text-gray-300">
            <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
            >
                <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
                />
            </svg>
            {cart && cart.total_items > 0 && (
                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                    {cart.total_items}
                </span>
            )}
        </Link>
    );
}
