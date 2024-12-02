// src/components/LanguageSwitcher.tsx
'use client';

import { useDispatch, useSelector } from 'react-redux';
import { setLocale } from '../../store/slices/languageSlice';
import { RootState } from '../../store';

const LanguageSwitcher: React.FC = () => {
  const dispatch = useDispatch();
  const locale = useSelector((state: RootState) => state.language.locale);

  const changeLanguage = (newLocale: string) => {
    dispatch(setLocale(newLocale));
  };

  return (
    <div className="mt-6 flex space-x-4">
      <button
        className={`px-4 py-2 rounded ${
          locale === 'en' ? 'bg-red-500 text-white' : 'bg-gray-500'
        }`}
        onClick={() => changeLanguage('en')}
      >
        English
      </button>
      <button
        className={`px-4 py-2 rounded ${
          locale === 'ru' ? 'bg-red-500 text-white' : 'bg-gray-500'
        }`}
        onClick={() => changeLanguage('ru')}
      >
        Русский
      </button>
      <button
        className={`px-4 py-2 rounded ${
          locale === 'sk' ? 'bg-red-500 text-white' : 'bg-gray-500'
        }`}
        onClick={() => changeLanguage('sk')}
      >
        Slovensky
      </button>
    </div>
  );
};

export default LanguageSwitcher;
