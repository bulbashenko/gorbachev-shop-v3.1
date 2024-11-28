// /components/theme-switcher.tsx

'use client';

import { useTheme } from 'next-themes';
import { useState, useEffect } from 'react';
import { FaSun, FaMoon } from 'react-icons/fa';

export default function ThemeSwitcher() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // После монтирования мы можем получить доступ к теме
  useEffect(() => setMounted(true), []);

  if (!mounted) return null;

  const isDark = theme === 'dark';

  const toggleTheme = () => {
    setTheme(isDark ? 'light' : 'dark');
  };

  return (
    <button
      onClick={toggleTheme}
      aria-label="Toggle Dark Mode"
      className="p-2 rounded-full"
    >
      {isDark ? (
          <FaSun className="w-6 h-6" />
      ) : (
          <FaMoon className="w-6 h-6" />
      )}
    </button>
  );
}
