// frontend/src/app/[locale]/layout.tsx

import { NextIntlClientProvider } from 'next-intl';
import { getMessages, getTranslations } from 'next-intl/server';
import { notFound } from 'next/navigation';
import { routing } from '../../i18n/routing';
import { Montserrat } from 'next/font/google'
import "./globals.css"
import { ThemeProvider } from './components/theme-provider';
import { AuthProvider } from '../../contexts/AuthContext';
import Header from './components/header';
import NavigationMenu from './components/navigation-menu';

const montserrat = Montserrat({
  weight: ['400', '700'],
  style: ['normal', 'italic'],
  subsets: ['latin'],
  display: 'swap'
})

export async function generateMetadata({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: 'Metadata' });

  return {
    title: t('title'),
    description: t('description')
  };
}

export default async function RootLayout({ children, params }: Readonly<{ children: React.ReactNode; }> & { params: Promise<{ locale: string }> }) {
  const { locale } = await params;

  if (!routing.locales.includes(locale as any)) {
    notFound();
  }

  const messages = await getMessages();

  return (
    <html lang={locale} suppressHydrationWarning>
      <body className={montserrat.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme='system'
        >
          <NextIntlClientProvider messages={messages}>
            <AuthProvider>
              <Header />
              <NavigationMenu />
              {children}
            </AuthProvider>
          </NextIntlClientProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}