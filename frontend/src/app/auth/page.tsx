'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function AuthPage() {
  const router = useRouter();

  useEffect(() => {
    // Перенаправление на страницу /auth/login
    router.push('/auth/login');
  }, [router]);

  // Заглушка, пока выполняется перенаправление
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-white text-center">
        <div className="w-8 h-8 border-t-2 border-white rounded-full animate-spin mx-auto mb-4"></div>
        <p>Redirecting...</p>
      </div>
    </div>
  );
}
