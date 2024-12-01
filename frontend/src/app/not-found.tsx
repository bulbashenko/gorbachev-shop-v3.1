'use client';

import { useTranslations } from 'next-intl';
import Link from 'next/link';

export default function NotFoundPage() {
  const t = useTranslations();

  return (
    <div className="min-h-screen flex justify-center py-4 px-4">
      <div className="text-center">
        {/* 404 numbers */}
        <div className="flex justify-center mb-8">
          <div className="text-8xl font-bold">
            404
          </div>
        </div>

        {/* Error message */}
        <h2 className="text-2xl font-semibold mb-4">
          {t('title')}
        </h2>

        <p className="text-gray-600 dark:text-gray-400 mb-8 max-w-md mx-auto">
          {t('description')}
        </p>

        {/* Home button */}
        <Link
          href="/"
          className="inline-block bg-black dark:bg-white text-white dark:text-black px-6 py-3 rounded-md font-medium"
        >
          {t('homeButton')}
        </Link>

        {/* Decorative element */}
        <div className="mt-12">
          <div className="inline-block w-16 h-1 bg-black dark:bg-white rounded-full"></div>
        </div>
      </div>
    </div>
  );
}