'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslations, useLocale } from 'next-intl';
import { useAuth } from '../../../contexts/AuthContext';
import { Link } from '../../../i18n/routing';
import { FiPackage, FiUsers, FiShoppingBag, FiAlertCircle, FiRefreshCw, FiDollarSign } from 'react-icons/fi';
import { adminService } from '../../../services/admin';

interface OrderStatusStats {
    byStatus: Record<string, number>;
    byPaymentStatus: Record<string, number>;
}

interface DashboardStats {
    overview: {
        totalUsers: number;
        totalProducts: number;
        totalOrders: number;
        totalRevenue: number;
    };
    recent: {
        orders: number;
        revenue: number;
        activeUsers: number;
    };
    inventory: {
        totalProducts: number;
        lowStockProducts: number;
    };
    orders: OrderStatusStats;
}

const defaultStats: DashboardStats = {
    overview: {
        totalUsers: 0,
        totalProducts: 0,
        totalOrders: 0,
        totalRevenue: 0
    },
    recent: {
        orders: 0,
        revenue: 0,
        activeUsers: 0
    },
    inventory: {
        totalProducts: 0,
        lowStockProducts: 0
    },
    orders: {
        byStatus: {},
        byPaymentStatus: {}
    }
};

const AdminDashboard = () => {
    const { isAuthenticated, isAdmin, user, logout } = useAuth();
    const router = useRouter();
    const locale = useLocale();
    const t = useTranslations('Admin');
    const [stats, setStats] = useState<DashboardStats>(defaultStats);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchStats = useCallback(async () => {
        try {
            console.log('Fetching admin stats...');
            setLoading(true);
            setError(null);

            const token = localStorage.getItem('token');
            console.log('Current token:', token ? 'Present' : 'Missing');

            const data = await adminService.getStats();
            console.log('Stats received:', data);
            setStats(data);
        } catch (err: any) {
            console.error('Error fetching stats:', err);
            if (err.message === 'No token found' || err.response?.status === 401) {
                console.log('Authentication error, redirecting to login...');
                logout();
                router.push(`/${locale}/auth`);
                return;
            }
            setError(t('common.error.fetchStats'));
        } finally {
            setLoading(false);
        }
    }, [logout, router, locale, t]);

    useEffect(() => {
        if (!isAuthenticated || !isAdmin) {
            console.log('Not authenticated or not admin, redirecting...');
            router.push(`/${locale}/auth`);
            return;
        }
        console.log('Component mounted, fetching stats...');
        fetchStats();
    }, [isAuthenticated, isAdmin, router, locale, fetchStats]);

    if (!isAuthenticated || !isAdmin || !user) {
        return null;
    }

    const StatCard = ({ title, value, icon, change }: { title: string; value: number; icon: JSX.Element; change?: number }) => (
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300">{title}</h3>
                <div className="text-2xl text-gray-400 dark:text-gray-600">{icon}</div>
            </div>
            <div className="space-y-2">
                {loading ? (
                    <div className="animate-pulse h-9 bg-gray-200 dark:bg-gray-700 rounded"></div>
                ) : (
                    <>
                        <p className="text-3xl font-bold">
                            {title.toLowerCase().includes('revenue') ?
                                `$${value.toLocaleString()}` :
                                value.toLocaleString()}
                        </p>
                        {change !== undefined && (
                            <p className={`text-sm ${change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                {change > 0 ? '+' : ''}{change}% from last month
                            </p>
                        )}
                    </>
                )}
            </div>
        </div>
    );

    const QuickAction = ({ href, icon, children }: { href: string; icon: JSX.Element; children: React.ReactNode }) => (
        <Link
            href={href}
            className="flex items-center space-x-3 p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition-all"
        >
            <div className="p-3 bg-indigo-100 dark:bg-indigo-900 rounded-lg">
                {icon}
            </div>
            <span className="font-medium">{children}</span>
        </Link>
    );

    return (
        <div className="p-6 space-y-6 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">
                        {t('welcome', { name: user.username })}
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400">
                        {new Date().toLocaleDateString(locale, {
                            weekday: 'long',
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric'
                        })}
                    </p>
                </div>
                <button
                    onClick={fetchStats}
                    disabled={loading}
                    className={`p-3 rounded-full bg-white dark:bg-gray-800 shadow-sm hover:shadow-md transition-all
                        ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                    title={t('common.refresh')}
                >
                    <FiRefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                </button>
            </div>

            {/* Error Display */}
            {error && (
                <div className="flex items-center space-x-2 text-red-600 bg-red-50 dark:bg-red-900/50 dark:text-red-400 p-4 rounded-lg">
                    <FiAlertCircle className="flex-shrink-0" />
                    <span>{error}</span>
                </div>
            )}

            {/* Overview Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    title={t('stats.users')}
                    value={stats.overview.totalUsers}
                    icon={<FiUsers />}
                    change={5}
                />
                <StatCard
                    title={t('stats.products')}
                    value={stats.overview.totalProducts}
                    icon={<FiPackage />}
                    change={-2}
                />
                <StatCard
                    title={t('stats.orders')}
                    value={stats.overview.totalOrders}
                    icon={<FiShoppingBag />}
                    change={12}
                />
                <StatCard
                    title={t('stats.revenue')}
                    value={stats.overview.totalRevenue}
                    icon={<FiDollarSign />}
                    change={8}
                />
            </div>

            {/* Quick Actions */}
            <div className="bg-gray-50 dark:bg-gray-900 p-6 rounded-lg">
                <h2 className="text-xl font-semibold mb-4">{t('quickActions')}</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <QuickAction
                        href={`/${locale}/admin/products/new`}
                        icon={<FiPackage className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />}
                    >
                        {t('actions.addProduct')}
                    </QuickAction>
                    <QuickAction
                        href={`/${locale}/admin/orders`}
                        icon={<FiShoppingBag className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />}
                    >
                        {t('actions.viewOrders')}
                    </QuickAction>
                    <QuickAction
                        href={`/${locale}/admin/users`}
                        icon={<FiUsers className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />}
                    >
                        {t('actions.manageUsers')}
                    </QuickAction>
                </div>
            </div>

            {/* Recent Activity and Additional Stats */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Low Stock Products */}
                <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm">
                    <h2 className="text-xl font-semibold mb-4">{t('inventory.lowStock')}</h2>
                    {stats.inventory.lowStockProducts === 0 ? (
                        <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                            {t('inventory.allStocked')}
                        </p>
                    ) : (
                        <div className="text-amber-600 dark:text-amber-400">
                            {t('inventory.lowStockWarning', { count: stats.inventory.lowStockProducts })}
                        </div>
                    )}
                </div>

                {/* Recent Orders */}
                <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm">
                    <h2 className="text-xl font-semibold mb-4">{t('orders.recent')}</h2>
                    {stats.recent.orders === 0 ? (
                        <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                            {t('orders.noRecent')}
                        </p>
                    ) : (
                        <div>
                            {t('orders.recentCount', {
                                count: stats.recent.orders,
                                revenue: stats.recent.revenue.toLocaleString('en-US', {
                                    style: 'currency',
                                    currency: 'USD'
                                })
                            })}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;