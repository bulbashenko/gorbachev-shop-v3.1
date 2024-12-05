import type { Metadata } from "next";
import "./globals.css";

import { ReactNode } from 'react';
import { cookies } from 'next/headers';

import Providers from './providers/LanguageProvider';
import { ThemeProvider } from "./providers/ThemeProvider";
import FontProvider from "./providers/FontProvider";

import Header from "./components/Header";
import MobileNavigationMenu from "./components/MobileNavigationMenu";
import BottomNav from "./components/BottomNav";
import { dm_sans, pt_sans } from './utils/fontConfig'
import { AuthProvider } from "@/contexts/AuthContext";

export const metadata: Metadata = {
  title: "Create Next App",
  description: "Generated by create next app",
};

export default async function RootLayout({ children }: { children: ReactNode }) {
  const nextCookies = await cookies();
  const localeFromCookie = nextCookies.get('NEXT_LOCALE')?.value || 'en';

  let messages;
  try {
    messages = (await import(`../messages/${localeFromCookie}.json`)).default;
  } catch (error) {
    console.error(`Ошибка загрузки сообщений для локали ${localeFromCookie}:`, error);
    messages = (await import(`../messages/en.json`)).default;
  }

  // Определяем класс шрифта для локали
  const fontClassName =
    localeFromCookie === 'ru' ? pt_sans.className : dm_sans.className;

  return (
    <html lang={localeFromCookie} className={fontClassName}>
      <body>
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
        >
          <AuthProvider>
          <Providers initialLocale={localeFromCookie} initialMessages={messages}>
            <FontProvider
              fonts={{
                en: dm_sans.className,
                ru: pt_sans.className,
                default: dm_sans.className,
              }}
            >
              <Header />
              <MobileNavigationMenu />
              {children}
              <BottomNav />
            </FontProvider>
          </Providers>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}

