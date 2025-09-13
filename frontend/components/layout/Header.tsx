'use client'

import { Bell, Search, Moon, Sun, User } from 'lucide-react'
import { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

export default function Header() {
  const [darkMode, setDarkMode] = useState(false)
  const pathname = usePathname()

  // Apply dark mode class to body when darkMode changes
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [darkMode])

  // Check if a navigation item is active
  const isActive = (path: string) => {
    return pathname === path
  }

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between px-6 py-4">
        {/* Logo and Navigation */}
        <div className="flex items-center space-x-6">
          <Link href="/dashboard" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">EI</span>
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              E-Commerce Intelligence
            </span>
          </Link>

          {/* Navigation Links - Hidden on mobile, shown on desktop */}
          <nav className="hidden md:flex items-center space-x-4">
            <Link
              href="/dashboard"
              className={`px-3 py-2 rounded-md text-sm font-medium transition ${
                isActive('/dashboard')
                  ? 'text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/20'
                  : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              Dashboard
            </Link>
            <Link
              href="/analytics"
              className={`px-3 py-2 rounded-md text-sm font-medium transition ${
                isActive('/analytics')
                  ? 'text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/20'
                  : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              Analytics
            </Link>
            <Link
              href="/products"
              className={`px-3 py-2 rounded-md text-sm font-medium transition ${
                isActive('/products')
                  ? 'text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/20'
                  : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              Products
            </Link>
            <Link
              href="/customers"
              className={`px-3 py-2 rounded-md text-sm font-medium transition ${
                isActive('/customers')
                  ? 'text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/20'
                  : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              Customers
            </Link>
          </nav>
        </div>

        {/* Search and Actions */}
        <div className="flex items-center space-x-4">
          {/* Search - Hidden on mobile, shown on desktop */}
          <div className="hidden md:block">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search products, customers, orders..."
                className="w-64 pl-10 pr-4 py-2 bg-gray-100 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-4">
            <button className="relative p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>

            <button
              onClick={() => setDarkMode(!darkMode)}
              className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
            >
              {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>

            <div className="flex items-center space-x-3 pl-4 border-l border-gray-200 dark:border-gray-700">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full flex items-center justify-center">
                <User className="w-6 h-6 text-white" />
              </div>
              <div className="hidden md:block">
                <p className="text-sm font-semibold text-gray-700 dark:text-gray-300">Admin User</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">admin@ecommerce.com</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Navigation - Shown on mobile, hidden on desktop */}
      <nav className="md:hidden p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="grid grid-cols-4 gap-2">
          <Link
            href="/dashboard"
            className={`flex flex-col items-center p-2 rounded-md text-sm font-medium transition ${
              isActive('/dashboard')
                ? 'text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/20'
                : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            <span>Dashboard</span>
          </Link>
          <Link
            href="/analytics"
            className={`flex flex-col items-center p-2 rounded-md text-sm font-medium transition ${
              isActive('/analytics')
                ? 'text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/20'
                : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            <span>Analytics</span>
          </Link>
          <Link
            href="/products"
            className={`flex flex-col items-center p-2 rounded-md text-sm font-medium transition ${
              isActive('/products')
                ? 'text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/20'
                : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            <span>Products</span>
          </Link>
          <Link
            href="/customers"
            className={`flex flex-col items-center p-2 rounded-md text-sm font-medium transition ${
              isActive('/customers')
                ? 'text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/20'
                : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            <span>Customers</span>
          </Link>
        </div>
      </nav>
    </header>
  )
}