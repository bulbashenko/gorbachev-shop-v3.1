'use client';

import { useTranslations } from 'next-intl';
import { Link } from '../../i18n/routing';

export default function NotFoundPage() {
  const t = useTranslations('NotFoundPage');

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="text-center">
        {/* 404 numbers */}
        <div className="flex justify-center mb-8">
          <div className="text-8xl font-bold animate-fade-in">
            404
          </div>
        </div>

        {/* Error message */}
        <h2 className="text-2xl font-semibold mb-4 animate-slide-up">
          {t('title')}
        </h2>

        <p className="text-gray-600 dark:text-gray-400 mb-8 max-w-md mx-auto animate-slide-up">
          {t('description')}
        </p>

        {/* Home button */}
        <Link
          href="/"
          className="inline-block bg-black dark:bg-white text-white dark:text-black px-6 py-3 rounded-md font-medium transition-transform hover:scale-105 animate-fade-in"
        >
          {t('homeButton')}
        </Link>

        {/* Decorative element */}
        <div className="mt-12">
          <div className="inline-block w-16 h-1 bg-black dark:bg-white rounded-full animate-scale-in"></div>
        </div>
      </div>
    </div>
  );
}