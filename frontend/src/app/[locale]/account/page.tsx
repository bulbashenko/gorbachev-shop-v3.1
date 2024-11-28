'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslations, useLocale } from 'next-intl';
import { useAuth } from '../../../contexts/AuthContext';
import { FiUser, FiMail, FiCalendar, FiBox, FiHeart } from 'react-icons/fi';

const AccountPage = () => {
    const t = useTranslations('Account');
    const locale = useLocale();
    const router = useRouter();
    const { isAuthenticated, user, logout } = useAuth();
    const [activeTab, setActiveTab] = useState('profile');

    // Защита страницы
    useEffect(() => {
        if (!isAuthenticated) {
            router.push(`/${locale}/auth`);
        }
    }, [isAuthenticated, router, locale]);

    const handleLogout = () => {
        logout();
    };

    if (!isAuthenticated || !user) {
        return null;
    }

    // Format the date to locale string
    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString(locale, {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    const tabs = [
        { id: 'profile', icon: <FiUser />, label: t('tabs.profile') },
        { id: 'orders', icon: <FiBox />, label: t('tabs.orders') },
        { id: 'favorites', icon: <FiHeart />, label: t('tabs.favorites') },
    ];

    const renderTabContent = () => {
        switch (activeTab) {
            case 'profile':
                return (
                    <div className="space-y-6">
                        <h2 className="text-2xl font-bold">{t('profile.title')}</h2>
                        <div className="grid md:grid-cols-2 gap-6">
                            <div className="space-y-4">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">{t('profile.email')}</label>
                                    <div className="flex items-center p-3 border rounded-md dark:border-gray-700">
                                        <FiMail className="w-5 h-5 mr-2 text-gray-400" />
                                        <span>{user.email}</span>
                                    </div>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">{t('profile.username')}</label>
                                    <div className="flex items-center p-3 border rounded-md dark:border-gray-700">
                                        <FiUser className="w-5 h-5 mr-2 text-gray-400" />
                                        <span>{user.username}</span>
                                    </div>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">{t('profile.joinDate')}</label>
                                    <div className="flex items-center p-3 border rounded-md dark:border-gray-700">
                                        <FiCalendar className="w-5 h-5 mr-2 text-gray-400" />
                                        <span>{formatDate(user.created_at)}</span>
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-4">
                                <button
                                    onClick={() => {/* Добавить логику изменения пароля */ }}
                                    className="w-full px-4 py-2 text-sm font-medium text-center border rounded-md hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800"
                                >
                                    {t('profile.changePassword')}
                                </button>
                                <button
                                    onClick={handleLogout}
                                    className="w-full px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700"
                                >
                                    {t('profile.logout')}
                                </button>
                            </div>
                        </div>
                    </div>
                );
            case 'orders':
                return (
                    <div className="space-y-6">
                        <h2 className="text-2xl font-bold">{t('orders.title')}</h2>
                        <div className="space-y-4">
                            <div className="text-center text-gray-500 dark:text-gray-400">
                                {t('orders.noOrders')}
                            </div>
                        </div>
                    </div>
                );
            case 'favorites':
                return (
                    <div className="space-y-6">
                        <h2 className="text-2xl font-bold">{t('favorites.title')}</h2>
                        <div className="space-y-4">
                            <div className="text-center text-gray-500 dark:text-gray-400">
                                {t('favorites.noItems')}
                            </div>
                        </div>
                    </div>
                );
            default:
                return null;
        }
    };

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="flex flex-col md:flex-row gap-8">
                {/* Боковое меню */}
                <div className="w-full md:w-64">
                    <nav className="space-y-2">
                        {tabs.map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`w-full flex items-center space-x-3 px-4 py-3 text-left rounded-lg transition-colors ${activeTab === tab.id
                                    ? 'bg-indigo-50 text-indigo-600 dark:bg-gray-800 dark:text-indigo-400'
                                    : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                                    }`}
                            >
                                <span className="flex-shrink-0">{tab.icon}</span>
                                <span>{tab.label}</span>
                            </button>
                        ))}
                    </nav>
                </div>

                {/* Основной контент */}
                <div className="flex-1 min-w-0">
                    <div className="bg-white dark:bg-black rounded-lg shadow-sm p-6 border dark:border-gray-800">
                        {renderTabContent()}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AccountPage;