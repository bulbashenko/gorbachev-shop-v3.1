'use client';

import Link from 'next/link';
import { useTranslations, useLocale } from 'next-intl';
import { dm_mono, pt_mono } from '../../utils/fontConfig';
import Button from '../../components/Button';

export default function LoginPage() {
  const t = useTranslations();
  const locale = useLocale();
  const monoFont = locale === 'ru' || locale === 'en' ? pt_mono : dm_mono;

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="min-h-screen flex flex-col items-center">
        <div className="grid grid-cols-1 md:grid-cols-7 gap-[30px]">
          {/* Блок 1: LOG IN */}
          <div className="col-span-1 md:col-span-3 flex flex-col items-center md:items-start text-center md:text-left">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-8">{t('auth.logIn')}</h1>
            <form className="w-full grid grid-cols-1 md:grid-cols-7 gap-6">
              <input
                type="email"
                placeholder={t('auth.email')}
                className={`${monoFont.className} col-span-1 md:col-span-6 px-4 py-3 border border-[#030303] dark:border-[#ededed] rounded-[6px] bg-transparent focus:outline-none focus:border-gray-300 placeholder-[#030303] dark:placeholder-[#ededed]`}
              />
              <input
                type="password"
                placeholder={t('auth.password')}
                className={`${monoFont.className} col-span-1 md:col-span-6 px-4 py-3 border border-[#030303] dark:border-[#ededed] rounded-[6px] bg-transparent focus:outline-none focus:border-gray-300 placeholder-[#030303] dark:placeholder-[#ededed]`}
              />
              <div className="col-span-1 md:col-span-6 flex flex-col items-center md:items-start gap-4">
                <Link href="/forgot-password" className={`${monoFont.className} text-base md:text-md underline`}>
                  {t('auth.forgotPassword')}
                </Link>
                <Button>{t('auth.signIn')}</Button>
              </div>
            </form>
          </div>

          {/* Блок 2: NEW CUSTOMERS */}
          <div className="col-span-1 md:col-span-4 flex flex-col items-center md:items-start text-center md:text-left">
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">{t('auth.newCustomers')}</h2>
            <p className="text-base md:text-lg lg:text-xl mb-8">{t('auth.newCustomersDescription')}</p>
            <Link href="/auth/register">
              <Button>{t('auth.register')}</Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
