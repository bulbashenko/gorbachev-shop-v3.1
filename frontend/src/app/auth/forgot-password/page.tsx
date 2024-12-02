'use client';

import { useState } from 'react';
import Link from 'next/link';
import { authService, type ResetPasswordData } from '@/app/api/services/auth.service';

export default function ForgotPasswordPage() {
  const [formData, setFormData] = useState<ResetPasswordData>({
    email: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
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
    setSuccess(false);

    try {
      await authService.requestPasswordReset(formData);
      setSuccess(true);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to send reset password email. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0D0D0D] flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-md space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-white">RESET PASSWORD</h1>
          {!success && (
            <p className="mt-4 text-gray-400">
              Enter your email address and we&apos;ll send you instructions to reset your password.
            </p>
          )}
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500 text-red-500 px-4 py-2 rounded">
            {error}
          </div>
        )}

        {success ? (
          <div className="text-center space-y-6">
            <div className="bg-green-500/10 border border-green-500 text-green-500 px-4 py-2 rounded">
              Password reset instructions have been sent to your email.
              Please check your inbox and follow the instructions.
            </div>
            <Link
              href="/auth/login"
              className="inline-block w-full text-center bg-white text-black py-2 rounded hover:bg-gray-100 transition-colors"
            >
              Return to Login
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="Email"
                required
                className="w-full px-4 py-2 bg-transparent border border-gray-700 text-white rounded focus:outline-none focus:border-white transition-colors"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-white text-black py-2 rounded hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Sending...' : 'Send Reset Link'}
            </button>

            <div className="text-center">
              <Link 
                href="/auth/login"
                className="text-gray-400 hover:text-white transition-colors"
              >
                Back to Login
              </Link>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
