'use client';

import { useState } from 'react';
import Button from '../../components/Button';
import Link from 'next/link';
import { useTranslations, useLocale } from 'next-intl';
import { dm_mono, pt_mono } from '../../utils/fontConfig';
import { useAuth } from '@/contexts/AuthContext';

export default function AuthPage() {
  const t = useTranslations();
  const locale = useLocale();
  const { login } = useAuth();
  const monoFont = locale === 'ru' || locale === 'en' ? pt_mono : dm_mono;

  const [formData, setFormData] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await login(formData.email, formData.password);
    } catch (error) {
      setError(error instanceof Error ? error.message : t('auth.invalidCredentials'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="min-h-screen flex flex-col items-center">
        <div className="grid grid-cols-1 md:grid-cols-7 gap-[30px]">
          {/* Блок 1: LOG IN */}
          <div className="col-span-1 md:col-span-3 flex flex-col items-center md:items-start text-center md:text-left">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-8">{t('auth.logIn')}</h1>
            {error && (
              <div className="bg-red-500/10 border border-red-500 text-red-500 px-4 py-2 rounded mb-4">
                {error}
              </div>
            )}
            <form onSubmit={handleSubmit} className="w-full grid grid-cols-1 md:grid-cols-7 gap-6">
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder={t('auth.email')}
                className={`${monoFont.className} col-span-1 md:col-span-6 px-4 py-3 border border-[#030303] dark:border-[#ededed] rounded-[6px] bg-transparent focus:outline-none focus:border-gray-300 placeholder-[#030303] dark:placeholder-[#ededed]`}
                required
              />
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder={t('auth.password')}
                className={`${monoFont.className} col-span-1 md:col-span-6 px-4 py-3 border border-[#030303] dark:border-[#ededed] rounded-[6px] bg-transparent focus:outline-none focus:border-gray-300 placeholder-[#030303] dark:placeholder-[#ededed]`}
                required
              />
              <div className="col-span-1 md:col-span-6 flex flex-col items-center md:items-start gap-4">
                <Link href="/forgot-password" className={`${monoFont.className} text-base md:text-md underline`}>
                  {t('auth.forgotPassword')}
                </Link>
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? t('auth.signingIn') : t('auth.signIn')}
                </Button>
              </div>
            </form>
          </div>

          {/* Блок 2: NEW CUSTOMERS */}
          <div className="col-span-1 md:col-span-4 flex flex-col items-center md:items-start text-center md:text-left">
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">{t('auth.newCustomers')}</h2>
            <p className="text-base md:text-lg lg:text-xl mb-8">{t('auth.newCustomersDescription')}</p>
            <Link href="/register">
              <Button>{t('auth.register')}</Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
