// src/app/page.tsx
'use client';

import LanguageSwitcher from './components/LanguageSwitcher';
import { useTranslations } from 'next-intl';
import ThemeSwitcher from './components/ThemeSwitcher';

const HomePage: React.FC = () => {
  const t = useTranslations();
  
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4">
      <h1 className='font-bold text-4xl'>{t("hello")}</h1>
      {t("welcome")}
      <LanguageSwitcher />
      <ThemeSwitcher />
    </div>
  );
};

export default HomePage;
