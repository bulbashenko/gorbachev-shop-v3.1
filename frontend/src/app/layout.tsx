// src/app/layout.tsx
import type { Metadata } from "next";
import { DM_Sans, PT_Sans } from "next/font/google";
import "./globals.css";
import { ReactNode } from 'react';
import { cookies } from 'next/headers';
import Providers from './providers/LanguageProvider';
import { ThemeProvider } from "./providers/ThemeProvider";
import FontProvider from "./providers/FontProvider";
import Header from "./components/Header";
import MobileNavigationMenu from "./components/MobileNavigationMenu";
import BottomNav from "./components/BottomNav";
import { AuthProvider } from '@/contexts/AuthContext';
import CartProvider from './CartProvider';

const dm_sans = DM_Sans({
  weight: ['400', '700'],
  style: ['normal', 'italic'],
  subsets: ['latin'],
  display: 'swap'
});

const pt_sans = PT_Sans({
  weight: ['400', '700'],
  style: ['normal', 'italic'],
  subsets: ['cyrillic'],
  display: 'swap'
});

export const metadata: Metadata = {
  title: "Gorbachev Shop",
  description: "Modern fashion e-commerce platform",
};

export default async function RootLayout({ children }: { children: ReactNode }) {
  const nextCookies = await cookies();
  const localeFromCookie = nextCookies.get('NEXT_LOCALE')?.value || 'en';

  let messages;
  try {
    messages = (await import(`../messages/${localeFromCookie}.json`)).default;
  } catch (error) {
    console.error(`Error loading messages for locale ${localeFromCookie}:`, error);
    messages = (await import(`../messages/en.json`)).default;
  }

  return (
    <html lang={localeFromCookie}>
      <body>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <AuthProvider>
            <Providers initialLocale={localeFromCookie} initialMessages={messages}>
              <CartProvider>
                <FontProvider dmSansClassName={dm_sans.className} ptSansClassName={pt_sans.className}>
                  <Header />
                  <MobileNavigationMenu />
                  {children}
                  <BottomNav />
                </FontProvider>
              </CartProvider>
            </Providers>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}