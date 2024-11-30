// components/Header.tsx
"use client"
import { useState } from 'react'
import Link from 'next/link'
import { FaSearch, FaUser, FaHeart, FaShoppingCart, FaCog, FaBars, FaTimes } from 'react-icons/fa'

const Header: React.FC = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  return (
    <header className="container mx-auto py-4 flex justify-between items-center text-lg">
      {/* Левая зона: Логотип */}
      <div className="flex items-center">
        <Link href="/" className="text-2xl font-bold tracking-wide">
          gorbachev
        </Link>
      </div>

      {/* Центральная зона: Навигация и Поиск (скрыто на мобильных устройствах) */}
      <div className={`flex items-center space-x-8 ${isMobileMenuOpen ? 'block' : 'hidden md:flex'}`}>
        {/* Навигационное меню */}
        <nav className="flex flex-col md:flex-row space-y-2 md:space-y-0 md:space-x-5">
          <Link href="/catalog" className="hover:text-gray-300">
            Catalog
          </Link>
          <Link href="/about" className="hover:text-gray-300">
            About
          </Link>
          <Link href="/link1" className="hover:text-gray-300">
            Link1
          </Link>
          <Link href="/link2" className="hover:text-gray-300">
            Link2
          </Link>
        </nav>

        {/* Поисковая строка */}
        <div className="flex items-cente rounded-md px-3 mt-4 md:mt-0">
          <FaSearch className="text-white mr-2" />
          <input
            type="text"
            placeholder="Search..."
            className="bg-transparent focus:outline-none text-white placeholder-gray-400 text-base"
          />
        </div>
      </div>

      {/* Правая зона: Иконки действий и Мобильное меню */}
      <div className="flex items-center space-x-5">
        <FaUser className="hover:text-gray-300 cursor-pointer hidden md:block text-xl" />
        <FaHeart className="hover:text-gray-300 cursor-pointer hidden md:block text-xl" />
        <FaShoppingCart className="hover:text-gray-300 cursor-pointer hidden md:block text-xl" />
        <FaCog className="hover:text-gray-300 cursor-pointer hidden md:block text-xl" />

        {/* Кнопка мобильного меню */}
        <button
          className="md:hidden focus:outline-none"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          aria-label="Toggle mobile menu"
        >
          {isMobileMenuOpen ? <FaTimes size={24} /> : <FaBars size={24} />}
        </button>
      </div>
    </header>
  )
}

export default Header
