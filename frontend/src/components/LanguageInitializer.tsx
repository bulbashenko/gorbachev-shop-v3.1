// src/components/LanguageInitializer.tsx
'use client';

import { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { setLocale } from '../store/slices/languageSlice';
import Cookies from '../../node_modules/@types/js-cookie';

const LanguageInitializer: React.FC = () => {
  const dispatch = useDispatch();

  useEffect(() => {
    const localeFromCookie = Cookies.get('NEXT_LOCALE');
    if (!localeFromCookie) {
      const browserLocale = navigator.language.split('-')[0];
      dispatch(setLocale(browserLocale));
      Cookies.set('NEXT_LOCALE', browserLocale);
    } else {
      dispatch(setLocale(localeFromCookie));
    }
  }, [dispatch]);

  return null;
};

export default LanguageInitializer;
