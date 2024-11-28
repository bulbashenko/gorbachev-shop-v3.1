'use client';

import { useState, useEffect } from 'react';
import { useLocale, useTranslations } from 'next-intl';
import {
  routing,
  Link,
  usePathname,
} from '../../../i18n/routing';
import ThemeSwitcher from '../components/theme-switcher';
import { useAuth } from '../../../contexts/AuthContext';
import links from '../utils/navigationLinks';
import {
  FiUser,
  FiHeart,
  FiShoppingCart,
  FiMoreVertical,
  FiX,
  FiSearch,
  FiLogOut,
} from 'react-icons/fi';
import { motion, AnimatePresence } from 'framer-motion';

export default function Header() {
  const t = useTranslations('Header');
  const locale = useLocale();
  const locales = routing.locales;
  const pathname = usePathname();
  const { isAuthenticated, logout } = useAuth();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isLangMenuOpen, setIsLangMenuOpen] = useState(false);
  const [isMobileLangMenuOpen, setIsMobileLangMenuOpen] = useState(false);
  const totalQuantity = 0;

  useEffect(() => {
    if (isMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
  }, [isMenuOpen]);

  const menuVariants = {
    hidden: {
      opacity: 0,
      height: 0,
      transition: { duration: 0.2 },
    },
    visible: {
      opacity: 1,
      height: 'auto',
      transition: { duration: 0.2 },
    },
  };

  const handleLogout = () => {
    logout();
    if (isMenuOpen) {
      setIsMenuOpen(false);
    }
  };

  const AuthButtons = () => {
    if (isAuthenticated) {
      return (
        <>
          <Link href="/account" className="relative">
            <FiUser className="w-6 h-6" />
          </Link>
          <button onClick={handleLogout} className="relative">
            <FiLogOut className="w-6 h-6" />
          </button>
        </>
      );
    }
    return (
      <Link href="/auth" className="relative">
        <FiUser className="w-6 h-6" />
      </Link>
    );
  };

  return (
    <header className="">
      <div className="container mx-auto py-4 px-6">
        {/* Мобильная версия хедера */}
        <div className="flex items-center justify-between lg:hidden">
          <button onClick={() => setIsMenuOpen(true)}>
            <FiMoreVertical className="w-6 h-6" />
          </button>

          <div className="text-2xl font-bold">
            <Link href="/" className="cursor-pointer">
              gorbachev
            </Link>
          </div>

          <div className="flex items-center space-x-4 relative">
            <AuthButtons />
            {/* Иконка корзины */}
            <Link href="/cart" className="relative">
              <FiShoppingCart className="w-6 h-6" />
              {totalQuantity > 0 && (
                <span className="absolute -top-2 -right-2 inline-flex items-center justify-center px-1.5 py-1 text-xs font-bold leading-none text-red-100 bg-red-600 rounded-full">
                  {totalQuantity}
                </span>
              )}
            </Link>
          </div>
        </div>

        {/* Десктопная версия хедера */}
        <div className="hidden lg:flex items-center justify-between">
          <div className="text-2xl font-bold">
            <Link href="/" className="cursor-pointer">
              gorbachev
            </Link>
          </div>

          <nav className="flex space-x-6">
            {links.map(({ href, labelKey }) => (
              <Link key={href} href={href} className="text-lg">
                {t(labelKey)}
              </Link>
            ))}
            <Link href="/information" className="text-lg block lg:hidden xl:block">
              {t('information')}
            </Link>
          </nav>

          <div className='flex items-center space-x-4 relative'>
            <ThemeSwitcher />

            {/* Меню выбора языка */}
            <div
              className="relative"
              onMouseEnter={() => setIsLangMenuOpen(true)}
              onMouseLeave={() => setIsLangMenuOpen(false)}
            >
              <button
                onClick={() => setIsLangMenuOpen(!isLangMenuOpen)}
                className="p-1 rounded flex items-center"
              >
                {locale.toUpperCase()}
                <svg
                  className={`w-4 h-4 ml-1 transition-transform ${isLangMenuOpen ? 'transform rotate-180' : ''
                    }`}
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </button>

              <AnimatePresence>
                {isLangMenuOpen && (
                  <motion.ul
                    className="mt-2 w-full bg-white dark:bg-black rounded shadow-lg overflow-hidden absolute left-0 z-50"
                    initial="hidden"
                    animate="visible"
                    exit="hidden"
                    variants={menuVariants}
                  >
                    {locales.map((lng) => (
                      <li key={lng}>
                        <Link
                          href={pathname}
                          locale={lng}
                          onClick={() => {
                            setIsLangMenuOpen(false);
                          }}
                          className={`block px-4 py-2 hover:bg-gray-100 dark:hover:bg-zinc-900 ${lng === locale ? 'font-bold' : ''
                            }`}
                        >
                          {lng.toUpperCase()}
                        </Link>
                      </li>
                    ))}
                  </motion.ul>
                )}
              </AnimatePresence>
            </div>
          </div>

          <div className="flex items-center space-x-4 relative">
            {/* Иконка поиска */}
            <Link href="/search" className="relative">
              <FiSearch className="w-6 h-6" />
            </Link>

            <AuthButtons />

            {/* Иконка избранного */}
            {isAuthenticated && (
              <Link href="/favorites" className="relative">
                <FiHeart className="w-6 h-6" />
              </Link>
            )}

            {/* Иконка корзины */}
            <Link href="/cart" className="relative">
              <FiShoppingCart className="w-6 h-6" />
              {totalQuantity > 0 && (
                <span className="absolute -top-2 -right-2 inline-flex items-center justify-center px-1.5 py-1 text-xs font-bold leading-none text-red-100 bg-red-600 rounded-full">
                  {totalQuantity}
                </span>
              )}
            </Link>
          </div>
        </div>
      </div>

      {/* Затемнение фона при открытом боковом меню */}
      <div
        className={`fixed inset-0 bg-black ${isMenuOpen ? 'opacity-50' : 'opacity-0 pointer-events-none'
          } transition-opacity duration-300`}
        onClick={() => setIsMenuOpen(false)}
      ></div>

      {/* Боковое меню для мобильной версии */}
      <div
        className={`fixed top-0 left-0 h-full w-64 bg-white dark:bg-black p-6 transform transition-transform duration-300 ease-in-out z-50 ${isMenuOpen ? 'translate-x-0' : '-translate-x-full'
          }`}
      >
        <button className="absolute top-4 right-4" onClick={() => setIsMenuOpen(false)}>
          <FiX className="w-6 h-6" />
        </button>

        <nav className="mt-8 flex flex-col space-y-4">
          {links.map(({ href, labelKey }) => (
            <Link key={href} href={href} className="text-xl">
              {t(labelKey)}
            </Link>
          ))}
          <Link href="/information" className="text-lg">
            {t('information')}
          </Link>
        </nav>

        <div className="mt-8">
          {/* Меню выбора языка */}
          <div className="mb-4">
            <div>
              <button
                onClick={() => setIsMobileLangMenuOpen(!isMobileLangMenuOpen)}
                className="bg-white dark:bg-black text-black dark:text-white p-2 rounded w-full flex items-center justify-between"
              >
                {locale.toUpperCase()}
                <svg
                  className={`w-4 h-4 ml-1 transition-transform ${isMobileLangMenuOpen ? 'transform rotate-180' : ''
                    }`}
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </button>
              <AnimatePresence>
                {isMobileLangMenuOpen && (
                  <motion.ul
                    className="mt-2 w-full bg-white dark:bg-black rounded overflow-hidden"
                    initial="hidden"
                    animate="visible"
                    exit="hidden"
                    variants={menuVariants}
                  >
                    {locales.map((lng) => (
                      <li key={lng}>
                        <Link
                          href={pathname}
                          locale={lng}
                          onClick={() => {
                            setIsMobileLangMenuOpen(false);
                            setIsMenuOpen(false);
                          }}
                          className={`block px-4 py-2 hover:bg-gray-100 dark:hover:bg-zinc-900 ${lng === locale ? 'font-bold' : ''
                            }`}
                        >
                          {lng.toUpperCase()}
                        </Link>
                      </li>
                    ))}
                  </motion.ul>
                )}
              </AnimatePresence>
            </div>
          </div>

          <div className='flex space-x-4'>
            {isAuthenticated ? (
              <>
                <Link href="/account" className="flex items-center">
                  <FiUser className="w-6 h-6" />
                </Link>
                <button onClick={handleLogout} className="flex items-center">
                  <FiLogOut className="w-6 h-6" />
                </button>
              </>
            ) : (
              <Link href="/auth" className="flex items-center">
                <FiUser className="w-6 h-6" />
              </Link>
            )}

            {isAuthenticated && (
              <Link href="/favorites" className='flex items-center'>
                <FiHeart className='w-6 h-6' />
              </Link>
            )}

            <div className="flex items-center">
              <ThemeSwitcher />
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}