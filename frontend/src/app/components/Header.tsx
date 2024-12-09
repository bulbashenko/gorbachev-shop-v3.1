// src/components/Header.tsx

'use client';

import { useTranslations } from 'next-intl';
import Link from 'next/link';
import navigationLinks from '../utils/navigationLinks';
import { FiUser, FiHeart, FiShoppingCart, FiSearch } from 'react-icons/fi';
import LanguageMenu from './LanguageMenu';
import CurrencyMenu from './CurrencyMenu';
import ThemeSwitcher from './ThemeSwitcher';
import { dm_sans } from '../utils/fontConfig';
import { useAuth } from '@/contexts/AuthContext'; // Предполагается, что у вас есть такой хук

export default function Header() {
  const t = useTranslations();
  const totalQuantity = 0;

  // Получаем информацию о том, аутентифицирован ли пользователь
  const { isAuthenticated } = useAuth();

  return (
    <header className="">
      <div className="container mx-auto py-4 px-4">
        {/* Mobile Header */}
        <div className="flex items-center justify-center lg:hidden">
          <div className="text-2xl font-bold">
            <Link href="/" className={`${dm_sans.className} cursor-pointer`}>
              gorbachev.
            </Link>
          </div>
        </div>

        {/* Desktop Header */}
        <div className="hidden lg:flex items-center justify-between">
          {/* Блок 1: Логотип */}
          <div className="text-2xl font-bold">
            <Link href="/" className={`${dm_sans.className} cursor-pointer`}>
              gorbachev.
            </Link>
          </div>

          {/* Блок 2: Ссылки на товары */}
          <nav className="flex space-x-6">
            {navigationLinks.map(({ href, labelKey }) => (
              <Link
                key={href}
                href={href}
                className="text-base lg:text-sm xl:text-lg"
              >
                {t(labelKey)}
              </Link>
            ))}
            <Link href="/about" className="text-base lg:text-sm xl:text-lg">
              {t('navigation.information')}
            </Link>
          </nav>

          {/* Блок 3: Иконки: аккаунт, поиск, избранное, корзина */}
          <div className="flex items-center space-x-4">
            <Link href="/search" className="relative">
              <FiSearch className="w-6 h-6" />
            </Link>
            {/* Проверяем состояние аутентификации:
                Если isAuthenticated = true, ссылаемся на /profile,
                иначе – на /auth */}
            <Link href={isAuthenticated ? "/profile" : "/auth"} className="relative">
              <FiUser className="w-6 h-6" />
            </Link>
            <Link href="/favorites" className="relative">
              <FiHeart className="w-6 h-6" />
            </Link>
            <Link href="/cart" className="relative">
              <FiShoppingCart className="w-6 h-6" />
              {totalQuantity > 0 && (
                <span className="absolute -top-2 -right-2 inline-flex items-center justify-center px-1.5 py-1 text-xs font-bold leading-none text-red-100 bg-red-600 rounded-full">
                  {totalQuantity}
                </span>
              )}
            </Link>
          </div>

          {/* Блок 4: Переключатели */}
          <div className="flex items-center space-x-4">
            <LanguageMenu />
            <CurrencyMenu />
            <ThemeSwitcher />
          </div>
        </div>
      </div>
    </header>
  );
}
