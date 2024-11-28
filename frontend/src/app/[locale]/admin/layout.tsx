'use client';

import React from 'react';
import { useTranslations } from 'next-intl';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '../../../contexts/AuthContext';
import { Link } from '../../../i18n/routing';
import { FiHome, FiBox, FiUsers, FiShoppingBag, FiSettings, FiLogOut } from 'react-icons/fi';

const AdminLayout = ({ children }: { children: React.ReactNode }) => {
    const t = useTranslations('Admin');
    const router = useRouter();
    const pathname = usePathname();
    const { user, logout, isAuthenticated, isAdmin } = useAuth();

    // Protect admin routes
    React.useEffect(() => {
        if (!isAuthenticated || !isAdmin) {
            router.push('/auth');
        }
    }, [isAuthenticated, isAdmin, router]);

    if (!isAuthenticated || !isAdmin) {
        return null;
    }

    const navigation = [
        { name: t('nav.dashboard'), href: '/admin', icon: FiHome },
        { name: t('nav.products'), href: '/admin/products', icon: FiBox },
        { name: t('nav.orders'), href: '/admin/orders', icon: FiShoppingBag },
        { name: t('nav.users'), href: '/admin/users', icon: FiUsers },
        { name: t('nav.settings'), href: '/admin/settings', icon: FiSettings },
    ];

    const isActive = (path: string) => {
        // Remove locale prefix from pathname for comparison
        const currentPath = pathname.split('/').slice(2).join('/');
        const targetPath = path.startsWith('/') ? path.slice(1) : path;
        return currentPath === targetPath || currentPath.startsWith(targetPath + '/');
    };

    return (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
            {/* Sidebar */}
            <div className="fixed inset-y-0 left-0 w-64 bg-[#1a1d24] shadow-lg">
                <div className="flex flex-col h-full">
                    {/* Admin Header */}
                    <div className="px-4 py-6 border-b border-gray-700/50">
                        <h2 className="text-xl font-bold text-white">
                            {t('title')}
                        </h2>
                        <p className="mt-1 text-sm text-gray-400">
                            {user?.username}
                        </p>
                    </div>

                    {/* Navigation */}
                    <nav className="flex-1 px-2 py-4 space-y-1">
                        {navigation.map((item) => {
                            const Icon = item.icon;
                            const active = isActive(item.href);
                            return (
                                <Link
                                    key={item.name}
                                    href={item.href}
                                    className={`w-full flex items-center px-4 py-2.5 text-sm rounded-lg transition-all duration-200 ${
                                        active
                                            ? 'bg-[#2a2f3a] text-white'
                                            : 'text-gray-400 hover:bg-[#2a2f3a] hover:text-white'
                                    }`}
                                >
                                    <Icon className={`w-5 h-5 mr-3 ${active ? 'text-white' : 'text-gray-400'}`} />
                                    {item.name}
                                </Link>
                            );
                        })}
                    </nav>

                    {/* Logout Button */}
                    <div className="p-4 border-t border-gray-700/50">
                        <button
                            onClick={logout}
                            className="w-full flex items-center px-4 py-2.5 text-sm text-red-400 hover:bg-[#2a2f3a] rounded-lg transition-all duration-200"
                        >
                            <FiLogOut className="w-5 h-5 mr-3" />
                            {t('nav.logout')}
                        </button>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="pl-64">
                <main className="p-8">
                    {children}
                </main>
            </div>
        </div>
    );
};

export default AdminLayout;