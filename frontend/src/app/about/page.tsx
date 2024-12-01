// src/app/page.tsx
'use client';

import React from 'react';
import { useTranslations } from 'next-intl';

const HomePage: React.FC = () => {
  const t = useTranslations();
  
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4">
      <h1 className='font-bold text-4xl'>"Page 1"</h1>
    </div>
  );
};

export default HomePage;
