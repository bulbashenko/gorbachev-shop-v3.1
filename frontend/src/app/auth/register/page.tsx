'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authService, type RegisterData } from '@/app/api/services/auth.service';

export default function RegisterPage() {
  const router = useRouter();
  const [formData, setFormData] = useState<RegisterData>({
    email: '',
    username: '',
    password: '',
    password2: '',
    first_name: '',
    last_name: '',
    terms_accepted: false,
    newsletter_subscription: false,
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setFormData({
      ...formData,
      [e.target.name]: value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    if (formData.password !== formData.password2) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }

    try {
      await authService.register(formData);
      router.push('/auth/login?registered=true');
    } catch (error) {
      if (error instanceof Error && error.message.toLowerCase().includes('already exists')) {
        setError('Account already exists. Please login.');
        setTimeout(() => {
          router.push('/auth/login');
        }, 2000);
      } else {
        setError(error instanceof Error ? error.message : 'Registration failed. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1a1a1a] via-[#1a1a1a] to-[#402218] flex items-center justify-center p-4">
      <div className="w-full max-w-[1000px] flex gap-16">
        {/* Register Section */}
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-white mb-8">CREATE ACCOUNT</h1>
          {error && (
            <div className="bg-red-500/10 border border-red-500 text-red-500 px-4 py-2 rounded mb-4">
              {error}
            </div>
          )}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <input
                type="text"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                placeholder="First Name"
                required
                className="w-full px-4 py-3 bg-transparent border border-white/30 text-white placeholder-white/50 focus:outline-none focus:border-white transition-colors"
              />
              <input
                type="text"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                placeholder="Last Name"
                required
                className="w-full px-4 py-3 bg-transparent border border-white/30 text-white placeholder-white/50 focus:outline-none focus:border-white transition-colors"
              />
            </div>
            <div>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                placeholder="Username"
                required
                className="w-full px-4 py-3 bg-transparent border border-white/30 text-white placeholder-white/50 focus:outline-none focus:border-white transition-colors"
              />
            </div>
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
            <div>
              <input
                type="password"
                name="password2"
                value={formData.password2}
                onChange={handleChange}
                placeholder="Confirm Password"
                required
                className="w-full px-4 py-3 bg-transparent border border-white/30 text-white placeholder-white/50 focus:outline-none focus:border-white transition-colors"
              />
            </div>
            <div className="space-y-3">
              <label className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  name="newsletter_subscription"
                  checked={formData.newsletter_subscription}
                  onChange={handleChange}
                  className="form-checkbox bg-transparent border-white/30 text-white focus:ring-0 rounded-sm"
                />
                <span className="text-white/70">Subscribe to our newsletter</span>
              </label>
              <label className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  name="terms_accepted"
                  checked={formData.terms_accepted}
                  onChange={handleChange}
                  required
                  className="form-checkbox bg-transparent border-white/30 text-white focus:ring-0 rounded-sm"
                />
                <span className="text-white/70">I agree to the Terms and Conditions</span>
              </label>
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-white text-black py-3 text-sm font-medium hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Creating Account...' : 'Create Account'}
            </button>
          </form>
        </div>

        {/* Existing Customers Section */}
        <div className="flex-1">
          <h2 className="text-3xl font-bold text-white mb-6">EXISTING CUSTOMERS</h2>
          <p className="text-white/70 mb-8 leading-relaxed">
            If you already have an account with us, please log in to access your profile, view your orders, and more.
          </p>
          <Link
            href="/auth/login"
            className="inline-block px-8 py-3 border border-white text-white font-medium hover:bg-white hover:text-black transition-colors"
          >
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
}
