// src/app/profile/orders/page.tsx
'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import { ordersService, type Order, type OrderTracking } from '@/app/api/services/orders.service';

const statusColors: Record<Order['status'], { bg: string; text: string; border: string }> = {
    awaiting_payment: { bg: 'bg-yellow-500/10', text: 'text-yellow-500', border: 'border-yellow-500/20' },
    processing: { bg: 'bg-blue-500/10', text: 'text-blue-500', border: 'border-blue-500/20' },
    confirmed: { bg: 'bg-green-500/10', text: 'text-green-500', border: 'border-green-500/20' },
    assembling: { bg: 'bg-purple-500/10', text: 'text-purple-500', border: 'border-purple-500/20' },
    shipped: { bg: 'bg-indigo-500/10', text: 'text-indigo-500', border: 'border-indigo-500/20' },
    delivered: { bg: 'bg-green-500/10', text: 'text-green-500', border: 'border-green-500/20' },
    cancelled: { bg: 'bg-red-500/10', text: 'text-red-500', border: 'border-red-500/20' },
    returned: { bg: 'bg-gray-500/10', text: 'text-gray-500', border: 'border-gray-500/20' }
};

const statusLabels: Record<Order['status'], string> = {
    awaiting_payment: 'Ожидает оплаты',
    processing: 'Обработка',
    confirmed: 'Подтвержден',
    assembling: 'Комплектация',
    shipped: 'Отправлен',
    delivered: 'Доставлен',
    cancelled: 'Отменен',
    returned: 'Возвращен'
};

export default function OrdersPage() {
    const [orders, setOrders] = useState<Order[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [selectedOrder, setSelectedOrder] = useState<string | null>(null);
    const [trackingData, setTrackingData] = useState<Record<string, OrderTracking>>({});
    const [cancelLoading, setCancelLoading] = useState<string | null>(null);

    useEffect(() => {
        fetchOrders();
    }, []);

    const fetchOrders = async () => {
        try {
            const response = await ordersService.getOrders();
            setOrders(response.results || []);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load orders');
        } finally {
            setIsLoading(false);
        }
    };

    const handleOrderSelect = async (orderId: string) => {
        if (selectedOrder === orderId) {
            setSelectedOrder(null);
            return;
        }

        setSelectedOrder(orderId);

        // Получаем данные отслеживания только если заказ отправлен
        const order = orders.find(o => o.id === orderId);
        if (order?.status === 'shipped' && !trackingData[orderId]) {
            try {
                const tracking = await ordersService.getOrderTracking(orderId);
                setTrackingData(prev => ({ ...prev, [orderId]: tracking }));
            } catch (error) {
                console.error('Failed to fetch tracking:', error);
            }
        }
    };

    const handleCancelOrder = async (orderId: string) => {
        if (!window.confirm('Вы уверены, что хотите отменить этот заказ?')) {
            return;
        }

        setCancelLoading(orderId);
        try {
            await ordersService.cancelOrder(orderId);
            await fetchOrders(); // Обновляем список заказов
            setSelectedOrder(null);
        } catch (err) {
            alert(err instanceof Error ? err.message : 'Failed to cancel order');
        } finally {
            setCancelLoading(null);
        }
    };

    if (isLoading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-[#1a1a1a] via-[#1a1a1a] to-[#402218] p-8">
                <div className="max-w-6xl mx-auto">
                    <div className="flex justify-center items-center h-64">
                        <div className="w-8 h-8 border-t-2 border-white rounded-full animate-spin"></div>
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-[#1a1a1a] via-[#1a1a1a] to-[#402218] p-8">
                <div className="max-w-6xl mx-auto">
                    <div className="bg-red-500/10 border border-red-500 text-red-500 p-4 rounded">
                        {error}
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-[#1a1a1a] via-[#1a1a1a] to-[#402218] p-8">
            <div className="max-w-6xl mx-auto">
                <h1 className="text-3xl font-bold text-white mb-8">Мои заказы</h1>

                {orders.length === 0 ? (
                    <div className="text-center py-12">
                        <p className="text-gray-400 mb-6">У вас пока нет заказов</p>
                        <Link
                            href="/products"
                            className="inline-block px-6 py-3 bg-white text-black rounded hover:bg-gray-100 transition-colors"
                        >
                            Начать покупки
                        </Link>
                    </div>
                ) : (
                    <div className="space-y-6">
                        {orders.map((order) => (
                            <div
                                key={order.id}
                                className="bg-white/5 rounded-lg overflow-hidden"
                            >
                                {/* Шапка заказа */}
                                <div className="p-6 border-b border-white/10">
                                    <div className="flex items-center justify-between flex-wrap gap-4">
                                        <div>
                                            <h3 className="text-xl font-semibold text-white mb-1">
                                                Заказ #{order.order_number}
                                            </h3>
                                            <p className="text-gray-400">
                                                {format(new Date(order.created_at), 'd MMMM yyyy, HH:mm', { locale: ru })}
                                            </p>
                                        </div>

                                        <div className="flex items-center gap-4">
                                            <span className={`px-4 py-2 rounded-lg text-sm font-medium ${statusColors[order.status].bg} ${statusColors[order.status].text} border ${statusColors[order.status].border}`}>
                                                {statusLabels[order.status]}
                                            </span>
                                            <button
                                                onClick={() => handleOrderSelect(order.id)}
                                                className="text-gray-400 hover:text-white transition-colors"
                                            >
                                                {selectedOrder === order.id ? 'Скрыть детали' : 'Показать детали'}
                                            </button>
                                        </div>
                                    </div>
                                </div>

                                {/* Детали заказа */}
                                {selectedOrder === order.id && (
                                    <div className="p-6 space-y-6">
                                        {/* Список товаров */}
                                        <div className="space-y-4">
                                            {order.items.map((item) => (
                                                <div key={item.id} className="flex items-center gap-6 bg-white/5 rounded-lg p-4">
                                                    <div className="w-24 h-24 bg-gray-800 rounded-lg overflow-hidden relative flex-shrink-0">
                                                        <Image
                                                            src={item.product_image}
                                                            alt={item.product_name}
                                                            fill
                                                            className="object-cover"
                                                        />
                                                    </div>
                                                    <div className="flex-grow">
                                                        <h4 className="text-white font-medium mb-2">{item.product_name}</h4>
                                                        <div className="grid grid-cols-2 gap-4 text-sm">
                                                            <div>
                                                                <p className="text-gray-400">Размер: <span className="text-white">{item.size}</span></p>
                                                                <p className="text-gray-400">Цвет: <span className="text-white">{item.color}</span></p>
                                                            </div>
                                                            <div className="text-right">
                                                                <p className="text-gray-400">Количество: <span className="text-white">{item.quantity} шт.</span></p>
                                                                <p className="text-gray-400">Цена: <span className="text-white">{item.price} ₽</span></p>
                                                                <p className="font-medium text-white">Итого: {item.total} ₽</p>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>

                                        {/* Детали доставки и оплаты */}
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                            {/* Информация о доставке */}
                                            <div className="bg-white/5 rounded-lg p-6">
                                                <h4 className="text-white font-medium mb-4">Информация о доставке</h4>
                                                <div className="space-y-3">
                                                    <p className="text-gray-400">
                                                        Адрес: <span className="text-white">{order.shipping_address_details}</span>
                                                    </p>
                                                    <p className="text-gray-400">
                                                        Метод: <span className="text-white">{order.shipping_method}</span>
                                                    </p>
                                                    {order.tracking_number && (
                                                        <p className="text-gray-400">
                                                            Трек-номер: <span className="text-white">{order.tracking_number}</span>
                                                        </p>
                                                    )}
                                                </div>
                                            </div>

                                            {/* Информация об оплате */}
                                            <div className="bg-white/5 rounded-lg p-6">
                                                <h4 className="text-white font-medium mb-4">Информация об оплате</h4>
                                                <div className="space-y-3">
                                                    <p className="text-gray-400">
                                                        Статус: <span className="text-white">{order.payment_status}</span>
                                                    </p>
                                                    <p className="text-gray-400">
                                                        Подытог: <span className="text-white">{order.subtotal} ₽</span>
                                                    </p>
                                                    <p className="text-gray-400">
                                                        Доставка: <span className="text-white">{order.shipping_cost} ₽</span>
                                                    </p>
                                                    <p className="text-gray-400">
                                                        Налог: <span className="text-white">{order.tax} ₽</span>
                                                    </p>
                                                    <p className="text-lg font-medium text-white">
                                                        Итого: {order.total} ₽
                                                    </p>
                                                </div>
                                            </div>
                                        </div>

                                        {/* История статусов */}
                                        {order.status_history.length > 0 && (
                                            <div className="bg-white/5 rounded-lg p-6">
                                                <h4 className="text-white font-medium mb-4">История заказа</h4>
                                                <div className="relative">
                                                    {/* Вертикальная линия */}
                                                    <div className="absolute left-2.5 top-3 bottom-3 w-0.5 bg-white/10"></div>

                                                    <div className="space-y-6">
                                                        {order.status_history.map((status, index) => (
                                                            <div key={index} className="relative pl-8">
                                                                {/* Точка на линии */}
                                                                <div className="absolute left-0 top-2 w-5 h-5 rounded-full bg-white/10 border-2 border-white/30"></div>

                                                                <div>
                                                                    <p className="text-white font-medium">
                                                                        {statusLabels[status.status as Order['status']]}
                                                                    </p>
                                                                    <p className="text-sm text-gray-400">
                                                                        {format(new Date(status.created_at), 'd MMMM yyyy, HH:mm', { locale: ru })}
                                                                    </p>
                                                                    {status.notes && (
                                                                        <p className="mt-1 text-gray-400">{status.notes}</p>
                                                                    )}
                                                                </div>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>
                                            </div>
                                        )}

                                        {/* Кнопки действий */}
                                        <div className="flex justify-end gap-4">
                                            {order.status === 'awaiting_payment' && (
                                                <button
                                                    className="px-6 py-3 bg-white text-black rounded hover:bg-gray-100 transition-colors"
                                                >
                                                    Оплатить
                                                </button>
                                            )}

                                            {['awaiting_payment', 'processing', 'confirmed'].includes(order.status) && (
                                                <button
                                                    onClick={() => handleCancelOrder(order.id)}
                                                    disabled={cancelLoading === order.id}
                                                    className="px-6 py-3 border border-red-500 text-red-500 rounded hover:bg-red-500/10 transition-colors disabled:opacity-50"
                                                >
                                                    {cancelLoading === order.id ? 'Отмена...' : 'Отменить заказ'}
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}