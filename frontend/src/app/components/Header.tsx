// src/app/components/Header.tsx
'use client';

import Link from 'next/link';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import LanguageMenu from './LanguageMenu';

export default function Header() {
  const { user, isAuthenticated, logout } = useAuth();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const router = useRouter();

  const handleProfileIconClick = () => {
    if (!isAuthenticated) {
      router.push('/auth/login');
    } else {
      router.push('/profile/settings');
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      setIsMenuOpen(false);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <header className="bg-[#1a1a1a] text-white">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="text-2xl font-bold">
            gorbachev.
          </Link>

          <nav className="hidden md:flex items-center space-x-8">
            <Link href="/products" className="hover:text-gray-300">
              All products
            </Link>
            <Link href="/products?category=sweaters" className="hover:text-gray-300">
              Sweaters
            </Link>
            <Link href="/products?category=pants" className="hover:text-gray-300">
              Pants
            </Link>
            <Link href="/products?category=bags" className="hover:text-gray-300">
              Bags
            </Link>
            <Link href="/products?category=t-shirts" className="hover:text-gray-300">
              T-Shirts
            </Link>
            <Link href="/products?category=accessories" className="hover:text-gray-300">
              Accessories
            </Link>
            <Link href="/about" className="hover:text-gray-300">
              About
            </Link>
          </nav>

          <div className="flex items-center space-x-6">
            <LanguageMenu />

            <div className="relative">
              <button
                onClick={handleProfileIconClick}
                className="flex items-center space-x-2 hover:text-gray-300"
              >
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
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                </svg>
                {isAuthenticated && (
                  <>
                    <span className="text-sm">{user?.first_name}</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setIsMenuOpen(!isMenuOpen);
                      }}
                    >
                      <svg
                        className={`w-4 h-4 transition-transform ${isMenuOpen ? 'rotate-180' : ''}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 9l-7 7-7-7"
                        />
                      </svg>
                    </button>
                  </>
                )}
              </button>

              {isAuthenticated && isMenuOpen && (
                <div
                  className="absolute right-0 mt-2 w-48 bg-[#1a1a1a] border border-white/10 rounded shadow-lg py-1 z-50"
                  onClick={(e) => e.stopPropagation()}
                >
                  <Link
                    href="/profile/settings"
                    className="block px-4 py-2 hover:bg-white/10"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Settings
                  </Link>
                  <Link
                    href="/profile/orders"
                    className="block px-4 py-2 hover:bg-white/10"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Orders
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="block w-full text-left px-4 py-2 hover:bg-white/10 text-red-400"
                  >
                    Logout
                  </button>
                </div>
              )}
            </div>

            <Link href="/cart" className="hover:text-gray-300">
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
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}