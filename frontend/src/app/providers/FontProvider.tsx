'use client';

import React, { useEffect, createContext, useContext } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';

interface FontContextValue {
  currentFontClass: string;
}

const FontContext = createContext<FontContextValue | undefined>(undefined);

export const useFont = () => {
  const context = useContext(FontContext);
  if (!context) {
    throw new Error('useFont must be used within a FontProvider');
  }
  return context;
};

interface FontProviderProps {
  children: React.ReactNode;
  fonts: Record<string, string>; // { locale: fontClassName }
}

const FontProvider: React.FC<FontProviderProps> = ({ children, fonts }) => {
  const locale = useSelector((state: RootState) => state.language.locale);

  const currentFontClass = fonts[locale] || fonts.default;

  useEffect(() => {
    const root = document.documentElement;

    // Удаляем все классы шрифтов
    Object.values(fonts).forEach(fontClass => root.classList.remove(fontClass));

    // Добавляем класс для текущей локали
    root.classList.add(currentFontClass);
  }, [locale, fonts]);

  return (
    <FontContext.Provider value={{ currentFontClass }}>
      {children}
    </FontContext.Provider>
  );
};

export default FontProvider;
