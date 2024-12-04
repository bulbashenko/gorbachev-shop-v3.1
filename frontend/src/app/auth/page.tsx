'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function AuthPage() {
  const router = useRouter();

  useEffect(() => {
    const checkUser = async () => {
      try {
        // Try to get user info to check if logged in
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/users/users/me/`, {
          credentials: 'include',
        });
        
        if (response.ok) {
          // If user is already logged in, redirect to home
          router.push('/');
        } else {
          // If not logged in, redirect to login
          router.push('/auth/login');
        }
      } catch {
        // In case of any error, default to login page
        router.push('/auth/login');
      }
    };

    checkUser();
  }, [router]);

  // Show loading state while checking
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0D0D0D] to-[#1A1A1A] flex items-center justify-center">
      <div className="text-white text-center">
        <div className="w-8 h-8 border-t-2 border-white rounded-full animate-spin mx-auto mb-4"></div>
        <p>Loading...</p>
      </div>
    </div>
  );
}
