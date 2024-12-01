// src/components/Header.tsx

'use client'

import { useTranslations } from 'next-intl';
import Link from 'next/link';
import navigationLinks from '../utils/navigationLinks';
import {
  FiUser,
  FiHeart,
  FiShoppingCart,
  FiSearch,
} from 'react-icons/fi';
import LanguageMenu from './LanguageMenu'; // Импорт компонента LanguageMenu

export default function Header() {
  const t = useTranslations(); // Использует текущий контекст перевода
  const totalQuantity = 0;

  return (
    <header className="">
      <div className="container mx-auto py-4 px-6">
        {/* Mobile Header */}
        <div className="flex items-center justify-center lg:hidden">
          <div className="text-2xl font-bold">
            <Link href="/" className="cursor-pointer">
              gorbachev
            </Link>
          </div>
        </div>

        {/* Desktop Header */}
        <div className="hidden lg:flex items-center justify-between">
          <div className="text-2xl font-bold">
            <Link href="/" className="cursor-pointer">
              gorbachev
            </Link>
          </div>

          <nav className="flex space-x-6">
            {navigationLinks.map(({ href, labelKey }) => (
              <Link
                key={href}
                href={href}
                className="text-base lg:text-sm xl:text-lg" // Изменён размер текста
              >
                {t(labelKey)}
              </Link>
            ))}
            <Link href="/information" className="text-base lg:text-sm xl:text-lg">
              {t('navigation.information')}
            </Link>
          </nav>

          <div className="flex items-center space-x-4 relative">
            {/* Search Icon */}
            <Link href="/search" className="relative">
              <FiSearch className="w-6 h-6" />
            </Link>

            {/* Account Link */}
            <Link href="/auth" className="relative">
              <FiUser className="w-6 h-6" />
            </Link>

            {/* Favorites Icon */}
            <Link href="/favorites" className="relative">
              <FiHeart className="w-6 h-6" />
            </Link>

            {/* Cart Icon */}
            <Link href="/cart" className="relative">
              <FiShoppingCart className="w-6 h-6" />
              {totalQuantity > 0 && (
                <span className="absolute -top-2 -right-2 inline-flex items-center justify-center px-1.5 py-1 text-xs font-bold leading-none text-red-100 bg-red-600 rounded-full">
                  {totalQuantity}
                </span>
              )}
            </Link>

            {/* Language Menu */}
            <LanguageMenu /> {/* Добавлен компонент LanguageMenu */}
          </div>
        </div>
      </div>
    </header>
  );
}
