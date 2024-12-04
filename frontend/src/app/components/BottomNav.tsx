// components/BottomNav.tsx
"use client";
import React from 'react';
import Link from 'next/link';
import { FiBook, FiHeart, FiShoppingCart, FiSettings } from 'react-icons/fi';

type MenuItem = 'catalog' | 'wishlist' | 'cart' | 'settings';

interface MenuItemType {
  key: MenuItem;
  label: string;
  icon: JSX.Element;
  href: string;
}

const menuItems: MenuItemType[] = [
  {
    key: 'catalog',
    label: 'Catalog',
    icon: <FiBook size={28} />,
    href: '/catalog',
  },
  {
    key: 'wishlist',
    label: 'Wishlist',
    icon: <FiHeart size={28} />,
    href: '/wishlist',
  },
  {
    key: 'cart',
    label: 'Cart',
    icon: <FiShoppingCart size={28} />,
    href: '/cart',
  },
  {
    key: 'settings',
    label: 'Settings',
    icon: <FiSettings size={28} />,
    href: '/settings',
  },
];

const BottomNav: React.FC = () => {
  return (
    <nav
      className="
        fixed bottom-0 left-0 right-0 flex justify-around items-center py-3 bg-background
        shadow-[0_-4px_45px_rgba(0,0,0,0.05)] z-50
        block lg:hidden
      "
    >
      {menuItems.map((item) => (
        <Link
          href={item.href}
          key={item.key}
          className="flex flex-col items-center text-center"
          aria-label={item.label}
        >
          {item.icon}
          <span className="text-xs mt-1">{item.label}</span>
        </Link>
      ))}
    </nav>
  );
};

export default BottomNav;
