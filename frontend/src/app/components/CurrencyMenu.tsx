// src/components/CurrencyMenu.tsx
'use client';

import { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { setCurrency } from '../../store/slices/currencySlice';
import { RootState } from '../../store';

const currencies = [
  { code: 'USD', label: 'USD' },
  { code: 'EUR', label: 'EUR' },
  { code: 'RUB', label: 'RUB' },
];

const CurrencyMenu: React.FC = () => {
  const dispatch = useDispatch();
  const currency = useSelector((state: RootState) => state.currency.currency);
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const toggleMenu = () => {
    setIsOpen((prev) => !prev);
  };

  const changeCurrency = (newCurrency: string) => {
    dispatch(setCurrency(newCurrency));
    setIsOpen(false);
  };

  // Закрыть меню при клике вне его области
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
        className="flex items-center focus:outline-none"
      >
        <span>
          {currencies.find((curr) => curr.code === currency)?.label || 'USD'}
        </span>
        {/* Добавляем стрелочку */}
        <svg
          className={`w-4 h-4 ml-1 transition-transform duration-200 ${
            isOpen ? 'transform rotate-180' : ''
          }`}
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 rounded shadow-lg z-50">
          {currencies.map((curr) => (
            <button
              key={curr.code}
              onClick={() => changeCurrency(curr.code)}
              className={`w-full text-left px-4 py-2 hover:bg-secondary ${
                currency === curr.code ? 'font-semibold' : ''
              }`}
            >
              {curr.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default CurrencyMenu;
