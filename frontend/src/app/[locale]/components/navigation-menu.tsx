import Link from 'next/link';
import links from '../utils/navigationLinks';
import { useTranslations } from 'next-intl';

const NavigationMenu = () => {
    const t = useTranslations('Header');
    return (
    <nav className="my-4">
        <div className="flex md:hidden scrollbar-hide overflow-x-auto space-x-4 px-4">
        {links.map((link) => (
            <div key={link.href} className="flex-shrink-0 text-center">
            <Link href={link.href}>
                <div className="w-16 h-16 bg-transparent border-black dark:border-white border-2 rounded-full flex items-center justify-center text-xl">
                {link.icon}
                </div>
                <span className="block mt-2 text-md">{t(link.smallLabelKey)}</span>
            </Link>
            </div>
        ))}
        </div>
    </nav>
    );
};

export default NavigationMenu;