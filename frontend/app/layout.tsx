// frontend/app/layout.tsx
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Link from 'next/link'
import { Home, Package, Users, BarChart3, Settings, Menu } from 'lucide-react'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'E-Commerce Intelligence Platform',
  description: 'Advanced recommendation engine and analytics for e-commerce',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="flex h-screen bg-gray-50">
          {/* Sidebar */}
          <aside className="w-64 bg-white shadow-md">
            <div className="p-4">
              <h1 className="text-xl font-bold text-gray-800">E-Commerce AI</h1>
              <p className="text-sm text-gray-600">Intelligence Platform</p>
            </div>
            
            <nav className="mt-8">
              <Link href="/" className="flex items-center px-4 py-3 text-gray-700 hover:bg-gray-100 hover:text-gray-900">
                <Home className="w-5 h-5 mr-3" />
                Overview
              </Link>
              <Link href="/dashboard" className="flex items-center px-4 py-3 text-gray-700 hover:bg-gray-100 hover:text-gray-900">
                <BarChart3 className="w-5 h-5 mr-3" />
                Dashboard
              </Link>
              <Link href="/products" className="flex items-center px-4 py-3 text-gray-700 hover:bg-gray-100 hover:text-gray-900">
                <Package className="w-5 h-5 mr-3" />
                Products
              </Link>
              <Link href="/customers" className="flex items-center px-4 py-3 text-gray-700 hover:bg-gray-100 hover:text-gray-900">
                <Users className="w-5 h-5 mr-3" />
                Customers
              </Link>
              <Link href="/settings" className="flex items-center px-4 py-3 text-gray-700 hover:bg-gray-100 hover:text-gray-900">
                <Settings className="w-5 h-5 mr-3" />
                Settings
              </Link>
            </nav>
          </aside>

          {/* Main Content */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Top Bar */}
            <header className="bg-white shadow-sm">
              <div className="flex items-center justify-between px-6 py-4">
                <button className="text-gray-500 hover:text-gray-700 lg:hidden">
                  <Menu className="w-6 h-6" />
                </button>
                
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-600">Welcome back!</span>
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
                    U
                  </div>
                </div>
              </div>
            </header>

            {/* Page Content */}
            <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50">
              <div className="container mx-auto px-6 py-8">
                {children}
              </div>
            </main>
          </div>
        </div>
      </body>
    </html>
  )
}