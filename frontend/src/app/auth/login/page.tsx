'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';

export default function LoginPage() {
  const { login } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await login(formData.email, formData.password);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Invalid email or password');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1a1a1a] via-[#1a1a1a] to-[#402218] flex items-center justify-center p-4">
      <div className="w-full max-w-[1000px] flex gap-16">
        {/* Login Section */}
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-white mb-8">LOG IN</h1>
          {error && (
            <div className="bg-red-500/10 border border-red-500 text-red-500 px-4 py-2 rounded mb-4">
              {error}
            </div>
          )}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="Email"
                required
                className="w-full px-4 py-3 bg-transparent border border-white/30 text-white placeholder-white/50 focus:outline-none focus:border-white transition-colors"
              />
            </div>
            <div>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Password"
                required
                className="w-full px-4 py-3 bg-transparent border border-white/30 text-white placeholder-white/50 focus:outline-none focus:border-white transition-colors"
              />
            </div>
            <div className="flex items-center justify-between">
              <Link 
                href="/auth/forgot-password"
                className="text-white/70 hover:text-white transition-colors text-sm"
              >
                Forgot your password?
              </Link>
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-white text-black py-3 text-sm font-medium hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
        </div>

        {/* New Customers Section */}
        <div className="flex-1">
          <h2 className="text-3xl font-bold text-white mb-6">NEW CUSTOMERS</h2>
          <p className="text-white/70 mb-8 leading-relaxed">
            Sign up for early Sale access plus tailored new arrivals, trends and promotions. To opt out, click unsubscribe in our emails.
          </p>
          <Link
            href="/auth/register"
            className="inline-block px-8 py-3 border border-white text-white font-medium hover:bg-white hover:text-black transition-colors"
          >
            Register
          </Link>
        </div>
      </div>
    </div>
  );
}
