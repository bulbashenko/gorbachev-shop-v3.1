// src/app/components/ThemeSwitcher.tsx
'use client';

import React from 'react';
import { useTheme } from 'next-themes';
import { SunIcon, MoonIcon } from '@heroicons/react/24/solid'; // Иконки для переключателя
import { useTranslations } from 'next-intl';


const ThemeSwitcher: React.FC = () => {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const t = useTranslations();

  const toggleTheme = () => {
    setTheme(resolvedTheme === 'dark' ? 'light' : 'dark');
  };

  return (
    <div className="flex items-center space-x-2 mt-4">
      <span className="text-sm">{t("theme")}</span>
      <button
        onClick={toggleTheme}
        className="relative inline-flex items-center h-6 rounded-full w-11 bg-gray-300 dark:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        <span
          className={`${
            resolvedTheme === 'dark' ? 'translate-x-6' : 'translate-x-1'
          } inline-block w-4 h-4 transform bg-white rounded-full transition-transform`}
        />
        <span className="sr-only">Toggle theme</span>
      </button>
      {resolvedTheme === 'dark' ? (
        <MoonIcon className="w-5 h-5 text-gray-200" />
      ) : (
        <SunIcon className="w-5 h-5 text-yellow-500" />
      )}
    </div>
  );
};

export default ThemeSwitcher;
