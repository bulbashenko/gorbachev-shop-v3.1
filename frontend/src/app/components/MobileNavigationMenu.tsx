// NavigationMenu.tsx
"use client"
import Link from 'next/link';
import navigationLinks from '../utils/navigationLinks';
import { useTranslations } from 'next-intl';

export default function MobileNavigationMenu() {
    const t = useTranslations();
    return (
        <nav className="my-4">
            <div className="flex md:hidden scrollbar-hide overflow-x-auto space-x-4 px-4">
                {navigationLinks.map(({href, mobLabelKey, icon}) => (
                    <div key={href} className="flex-shrink-0 text-center">
                        <Link href={href}>
                            <div className="w-20 h-20 bg-transparent border-black dark:border-white border-2 rounded-full flex items-center justify-center text-2xl">
                                {icon}
                            </div>
                            <span className="block mt-2 text-md">
                                {/* Используем mobLabelKey для мобильных устройств */}
                                {t(mobLabelKey)}
                            </span>
                        </Link>
                    </div>
                ))}
            </div>
        </nav>
    );
};
