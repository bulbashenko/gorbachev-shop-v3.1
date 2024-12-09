'use client';

import Link from 'next/link';

export default function OrdersPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1a1a1a] via-[#1a1a1a] to-[#402218] p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8">Мои заказы</h1>
        <div className="text-center py-12">
          <p className="text-gray-400 mb-6">У вас пока нет заказов</p>
          <Link
            href="/products"
            className="inline-block px-6 py-3 bg-white text-black rounded hover:bg-gray-100 transition-colors"
          >
            Начать покупки
          </Link>
        </div>
      </div>
    </div>
  );
}
