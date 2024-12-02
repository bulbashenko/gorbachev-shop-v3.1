'use client';

import { ReactNode } from 'react';
import { Provider } from 'react-redux';
import { store } from '@/store';
import { NextIntlClientProvider } from 'next-intl';
import LanguageInitializer from '@/components/LanguageInitializer';

interface LanguageProviderProps {
  children: ReactNode;
  initialLocale: string;
  initialMessages: Record<string, string>;
}

export const LanguageProvider: React.FC<LanguageProviderProps> = ({
  children,
  initialLocale,
  initialMessages,
}) => {
  const timeZone = "Europe/Bratislava";

  return (
    <Provider store={store}>
      <NextIntlClientProvider timeZone={timeZone} locale={initialLocale} messages={initialMessages}>
        <LanguageInitializer />
        {children}
      </NextIntlClientProvider>
    </Provider>
  );
};

export default LanguageProvider;