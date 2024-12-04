// src/components/LanguageMenu.tsx
'use client';

import { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { setLocale } from '../../store/slices/languageSlice';
import { RootState } from '../../store';

const languages = [
  { code: 'en', label: 'EN' },
  { code: 'ru', label: 'RU' },
  { code: 'sk', label: 'SK' }
];

const LanguageMenu: React.FC = () => {
  const dispatch = useDispatch();
  const locale = useSelector((state: RootState) => state.language.locale);
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const toggleMenu = () => {
    setIsOpen((prev) => !prev);
  };

  const changeLanguage = (newLocale: string) => {
    dispatch(setLocale(newLocale));
    setIsOpen(false);
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    } else {
      document.removeEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={toggleMenu}
        className="flex items-center px-4 py-2 rounded focus:outline-none"
      >
        <span>
          {languages.find((lang) => lang.code === locale)?.label || 'EN'}
        </span>
        <svg
          className={`w-4 h-4 ml-2 transition-transform duration-200 ${
            isOpen ? 'transform rotate-180' : ''
          }`}
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 rounded shadow-lg z-50 bg-background">
          {languages.map((language) => (
            <div
              key={language.code}
              onClick={() => changeLanguage(language.code)}
              className={`w-full text-left px-4 py-2 hover:bg-secondary cursor-pointer ${
                locale === language.code ? 'font-semibold' : ''
              }`}
            >
              {language.label}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default LanguageMenu;
