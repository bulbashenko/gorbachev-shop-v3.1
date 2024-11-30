'use client';

import { ReactNode, useEffect, useState } from 'react';
import { Provider, useSelector } from 'react-redux';
import store, { RootState } from '@/store';
import { NextIntlClientProvider } from 'next-intl';
import LanguageInitializer from '@/components/LanguageInitializer';

interface ProvidersProps {
  children: ReactNode;
  initialLocale: string;
  initialMessages: Record<string, string>;
}

const Providers: React.FC<ProvidersProps> = ({ children, initialLocale, initialMessages }) => {
  return (
    <Provider store={store}>
      <LanguageProvider initialLocale={initialLocale} initialMessages={initialMessages}>
        {children}
      </LanguageProvider>
    </Provider>
  );
};

interface LanguageProviderProps {
  children: ReactNode;
  initialLocale: string;
  initialMessages: Record<string, string>;
}

const timeZone = "Europe/Bratislava"

const LanguageProvider: React.FC<LanguageProviderProps> = ({ children, initialLocale, initialMessages }) => {
  const localeFromRedux = useSelector((state: RootState) => state.language.locale);
  const [locale, setLocale] = useState(initialLocale);
  const [messages, setMessages] = useState(initialMessages);

  useEffect(() => {
    if (localeFromRedux !== locale) {
      import(`../../messages/${localeFromRedux}.json`)
        .then((msgs) => {
          setLocale(localeFromRedux);
          setMessages(msgs.default);
        })
        .catch((error) => {
          console.error(`Locale loading error ${localeFromRedux}:`, error);
        });
    }
  }, [localeFromRedux, locale]);

  return (
    <NextIntlClientProvider timeZone={timeZone} locale={locale} messages={messages}>
      <LanguageInitializer />
      {children}
    </NextIntlClientProvider>
  );
};

export default Providers;
