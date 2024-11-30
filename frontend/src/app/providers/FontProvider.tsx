'use client';

import React, { useEffect } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';

interface FontProviderProps {
  children: React.ReactNode;
  dmSansClassName: string;
  ptSansClassName: string;
}

const FontProvider: React.FC<FontProviderProps> = ({ children, dmSansClassName, ptSansClassName }) => {
  const locale = useSelector((state: RootState) => state.language.locale);

  useEffect(() => {
    const root = document.documentElement;

    // Удаляем предыдущие классы шрифтов
    root.classList.remove(dmSansClassName, ptSansClassName);

    // Добавляем класс шрифта на основе локали
    if (locale === 'ru') {
      root.classList.add(ptSansClassName);
    } else {
      root.classList.add(dmSansClassName);
    }
  }, [locale, dmSansClassName, ptSansClassName]);

  return <>{children}</>;
};

export default FontProvider;
