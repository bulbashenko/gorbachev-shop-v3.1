'use client';

import React from 'react';
import { useTranslations } from 'next-intl';
import { useEffect, useState, useCallback } from 'react';
import { adminService } from '@/services/admin';
import { Order, OrderStats, FilterState, OrderStatus, PaymentStatus } from '@/types/orders';
import { FiPackage, FiTruck, FiCheck, FiX, FiClock } from 'react-icons/fi';
import Image from 'next/image';
import { useAuth } from '@/contexts/useAuth';
import { useRouter } from 'next/navigation';

const INITIAL_FILTERS: FilterState = {
    status: '',
    payment_status: '',
    from_date: undefined,
    to_date: undefined,
    page: 1,
    limit: 10
};

function OrdersPage() {
    const t = useTranslations('Admin');
    const router = useRouter();
    const { user } = useAuth();
    const [orders, setOrders] = useState<Order[]>([]);
    const [stats, setStats] = useState<OrderStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [totalOrders, setTotalOrders] = useState(0);
    const [filters, setFilters] = useState<FilterState>(INITIAL_FILTERS);

    // Redirect if not admin
    useEffect(() => {
        if (user && !user.is_superuser) {
            router.push('/');
        }
    }, [user, router]);

    const fetchOrderStats = async () => {
        try {
            const stats = await adminService.getOrderStats();
            setStats(stats);
        } catch (err) {
            console.error('Failed to fetch order stats:', err);
            // Don't set error state here as it's not critical
        }
    };

    const fetchOrders = useCallback(async () => {
        try {
            setLoading(true);
            const response = await adminService.getOrders(filters);
            setOrders(response.orders);
            setTotalOrders(response.total);
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load orders');
        } finally {
            setLoading(false);
        }
    }, [filters]);

    useEffect(() => {
        fetchOrders();
        fetchOrderStats();
    }, [fetchOrders]);

    const formatDate = (dateString: string): string => {
        try {
            return new Date(dateString).toLocaleString();
        } catch {
            return dateString;
        }
    };

    const getStatusColor = (status: OrderStatus): string => {
        const colors: Record<OrderStatus, string> = {
            pending: 'bg-yellow-100 text-yellow-800',
            processing: 'bg-blue-100 text-blue-800',
            shipped: 'bg-purple-100 text-purple-800',
            delivered: 'bg-green-100 text-green-800',
            cancelled: 'bg-red-100 text-red-800'
        };
        return colors[status];
    };

    const getPaymentStatusColor = (status: PaymentStatus): string => {
        const colors: Record<PaymentStatus, string> = {
            pending: 'bg-yellow-100 text-yellow-800',
            paid: 'bg-green-100 text-green-800',
            failed: 'bg-red-100 text-red-800',
            refunded: 'bg-purple-100 text-purple-800'
        };
        return colors[status];
    };

    const getStatusIcon = (status: OrderStatus) => {
        const icons: Record<OrderStatus, JSX.Element> = {
            pending: <FiClock className="text-yellow-500" />,
            processing: <FiPackage className="text-blue-500" />,
            shipped: <FiTruck className="text-purple-500" />,
            delivered: <FiCheck className="text-green-500" />,
            cancelled: <FiX className="text-red-500" />
        };
        return icons[status];
    };

    const handleStatusChange = async (orderId: number, newStatus: OrderStatus) => {
        try {
            await adminService.updateOrderStatus(orderId, newStatus);
            setOrders(orders.map(order =>
                order.id === orderId ? { ...order, status: newStatus } : order
            ));
            // Refresh stats after status update
            fetchOrderStats();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to update order status');
        }
    };

    const handlePaymentStatusChange = async (orderId: number, newStatus: PaymentStatus) => {
        try {
            await adminService.updateOrderPaymentStatus(orderId, newStatus);
            setOrders(orders.map(order =>
                order.id === orderId ? { ...order, payment_status: newStatus } : order
            ));
            // Refresh stats after payment status update
            fetchOrderStats();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to update payment status');
        }
    };

    const handleFilterChange = (key: keyof FilterState, value: any) => {
        setFilters(prev => ({
            ...prev,
            [key]: value === '' ? undefined : value,
            page: key === 'page' ? value : 1 // Reset page when other filters change
        }));
    };

    const validateDateRange = (): boolean => {
        if (!filters.from_date || !filters.to_date) return true;
        return new Date(filters.from_date) <= new Date(filters.to_date);
    };

    const renderStats = () => {
        if (!stats) return null;

        return (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">
                        {t('orders.recentOrders')}
                    </h3>
                    <p className="text-2xl font-bold">{stats.recentOrders}</p>
                </div>
                <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">
                        {t('orders.totalRevenue')}
                    </h3>
                    <p className="text-2xl font-bold">${stats.totalRevenue.toFixed(2)}</p>
                </div>
                <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">
                        {t('orders.averageOrder')}
                    </h3>
                    <p className="text-2xl font-bold">${stats.averageOrderValue.toFixed(2)}</p>
                </div>
                <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">
                        {t('orders.pendingOrders')}
                    </h3>
                    <p className="text-2xl font-bold">{stats.byStatus?.pending || 0}</p>
                </div>
            </div>
        );
    };

    const renderFilters = () => {
        const dateRangeError = !validateDateRange();

        return (
            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow mb-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                        <label className="block text-sm font-medium mb-1">{t('orders.filterStatus')}</label>
                        <select
                            value={filters.status}
                            onChange={(e) => handleFilterChange('status', e.target.value)}
                            className="w-full rounded-lg border border-gray-300 dark:border-gray-600 p-2"
                        >
                            <option value="">{t('orders.allStatuses')}</option>
                            <option value="pending">{t('orders.statusPending')}</option>
                            <option value="processing">{t('orders.statusProcessing')}</option>
                            <option value="shipped">{t('orders.statusShipped')}</option>
                            <option value="delivered">{t('orders.statusDelivered')}</option>
                            <option value="cancelled">{t('orders.statusCancelled')}</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-1">{t('orders.filterPayment')}</label>
                        <select
                            value={filters.payment_status}
                            onChange={(e) => handleFilterChange('payment_status', e.target.value)}
                            className="w-full rounded-lg border border-gray-300 dark:border-gray-600 p-2"
                        >
                            <option value="">{t('orders.allPaymentStatuses')}</option>
                            <option value="pending">{t('orders.paymentPending')}</option>
                            <option value="paid">{t('orders.paymentPaid')}</option>
                            <option value="failed">{t('orders.paymentFailed')}</option>
                            <option value="refunded">{t('orders.paymentRefunded')}</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-1">{t('orders.fromDate')}</label>
                        <input
                            type="date"
                            value={filters.from_date || ''}
                            onChange={(e) => handleFilterChange('from_date', e.target.value)}
                            className={`w-full rounded-lg border ${dateRangeError ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'} p-2`}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-1">{t('orders.toDate')}</label>
                        <input
                            type="date"
                            value={filters.to_date || ''}
                            onChange={(e) => handleFilterChange('to_date', e.target.value)}
                            className={`w-full rounded-lg border ${dateRangeError ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'} p-2`}
                        />
                    </div>
                </div>
                {dateRangeError && (
                    <p className="text-red-500 text-sm mt-2">{t('orders.invalidDateRange')}</p>
                )}
            </div>
        );
    };

    const renderPagination = () => {
        const totalPages = Math.ceil(totalOrders / filters.limit);
        return (
            <div className="flex justify-between items-center mt-6">
                <div>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                        {t('orders.showing')} {(filters.page - 1) * filters.limit + 1} - {Math.min(filters.page * filters.limit, totalOrders)} {t('orders.of')} {totalOrders}
                    </span>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={() => handleFilterChange('page', filters.page - 1)}
                        disabled={filters.page === 1}
                        className="px-4 py-2 border rounded-lg disabled:opacity-50"
                    >
                        {t('orders.previous')}
                    </button>
                    <button
                        onClick={() => handleFilterChange('page', filters.page + 1)}
                        disabled={filters.page >= totalPages}
                        className="px-4 py-2 border rounded-lg disabled:opacity-50"
                    >
                        {t('orders.next')}
                    </button>
                </div>
            </div>
        );
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 dark:border-white" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-50 dark:bg-red-900 text-red-600 dark:text-red-200 p-4 rounded-lg">
                {error}
            </div>
        );
    }

    return (
        <div className="space-y-6 p-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold">{t('orders.title')}</h1>
                <button
                    onClick={() => {
                        fetchOrders();
                        fetchOrderStats();
                    }}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                    {t('orders.refresh')}
                </button>
            </div>

            {renderStats()}
            {renderFilters()}

            <div className="grid gap-4">
                {orders.map((order) => (
                    <div
                        key={order.id}
                        className="bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition-shadow p-6"
                    >
                        <div className="flex justify-between items-start mb-4">
                            <div>
                                <h3 className="text-lg font-semibold">
                                    {t('orders.orderNumber', { number: order.id })}
                                </h3>
                                <p className="text-sm text-gray-500 dark:text-gray-400">
                                    {formatDate(order.created_at)}
                                </p>
                            </div>
                            <div className="flex items-center space-x-4">
                                <select
                                    value={order.payment_status as PaymentStatus}
                                    onChange={(e) => handlePaymentStatusChange(order.id, e.target.value as PaymentStatus)}
                                    className={`px-3 py-1 rounded-full text-sm font-medium ${getPaymentStatusColor(order.payment_status as PaymentStatus)}`}
                                >
                                    <option value="pending">{t('orders.paymentPending')}</option>
                                    <option value="paid">{t('orders.paymentPaid')}</option>
                                    <option value="failed">{t('orders.paymentFailed')}</option>
                                    <option value="refunded">{t('orders.paymentRefunded')}</option>
                                </select>
                                <select
                                    value={order.status as OrderStatus}
                                    onChange={(e) => handleStatusChange(order.id, e.target.value as OrderStatus)}
                                    className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(order.status as OrderStatus)}`}
                                >
                                    <option value="pending">{t('orders.statusPending')}</option>
                                    <option value="processing">{t('orders.statusProcessing')}</option>
                                    <option value="shipped">{t('orders.statusShipped')}</option>
                                    <option value="delivered">{t('orders.statusDelivered')}</option>
                                    <option value="cancelled">{t('orders.statusCancelled')}</option>
                                </select>
                                <span className="text-2xl">{getStatusIcon(order.status as OrderStatus)}</span>
                            </div>
                        </div>

                        <div className="grid md:grid-cols-2 gap-4 border-t dark:border-gray-700 pt-4">
                            <div>
                                <p className="text-sm font-medium mb-1">{t('orders.customer')}</p>
                                <p className="font-medium">{order.user?.username || t('orders.unknownUser')}</p>
                                <p className="text-sm text-gray-500 dark:text-gray-400">{order.user?.email || t('orders.noEmail')}</p>
                            </div>
                            <div className="text-right">
                                <p className="text-sm font-medium mb-1">{t('orders.total')}</p>
                                <p className="text-xl font-bold">${Number(order.total_amount).toFixed(2)}</p>
                            </div>
                        </div>

                        {order.items && order.items.length > 0 && (
                            <div className="mt-4 space-y-3">
                                {order.items.map((item) => (
                                    <div
                                        key={`${order.id}-${item.product_id}`}
                                        className="flex items-center space-x-4 bg-gray-50 dark:bg-gray-700 p-3 rounded-lg"
                                    >
                                        {item.product?.image_url && (
                                            <Image
                                                src={item.product.image_url}
                                                alt={item.product.name || t('orders.productImage')}
                                                width={64}
                                                height={64}
                                                className="object-cover rounded-lg"
                                                priority={false}
                                            />
                                        )}
                                        <div className="flex-1">
                                            <p className="font-medium">{item.product?.name || t('orders.unknownProduct')}</p>
                                            <p className="text-sm text-gray-500 dark:text-gray-400">
                                                {t('orders.quantity')}: {item.quantity} x ${Number(item.price).toFixed(2)}
                                            </p>
                                        </div>
                                        <div className="text-right">
                                            <p className="font-medium">
                                                ${(Number(item.quantity) * Number(item.price)).toFixed(2)}
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                ))}

                {orders.length === 0 && (
                    <div className="text-center py-12 bg-gray-50 dark:bg-gray-800 rounded-lg">
                        <p className="text-gray-500 dark:text-gray-400">{t('orders.noOrders')}</p>
                    </div>
                )}
            </div>

            {renderPagination()}
        </div>
    );
}

export default OrdersPage;