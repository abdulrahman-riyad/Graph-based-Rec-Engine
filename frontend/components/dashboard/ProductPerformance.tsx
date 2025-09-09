// ============================================
// frontend/components/dashboard/ProductPerformance.tsx
// ============================================
'use client'

import { useState } from 'react'
import { Package, TrendingUp, TrendingDown, Star, Eye, ShoppingCart } from 'lucide-react'

const mockProducts = [
  {
    id: 1,
    name: 'Premium Wireless Headphones',
    category: 'Electronics',
    price: 199.99,
    rating: 4.8,
    views: 12543,
    sales: 892,
    revenue: 178407,
    trend: 'up',
    change: '+12.3%'
  },
  {
    id: 2,
    name: 'Organic Cotton T-Shirt',
    category: 'Apparel',
    price: 29.99,
    rating: 4.6,
    views: 8923,
    sales: 1245,
    revenue: 37337,
    trend: 'up',
    change: '+8.7%'
  },
  {
    id: 3,
    name: 'Smart Home Speaker',
    category: 'Electronics',
    price: 79.99,
    rating: 4.5,
    views: 10234,
    sales: 567,
    revenue: 45354,
    trend: 'down',
    change: '-3.2%'
  },
  {
    id: 4,
    name: 'Yoga Mat Pro',
    category: 'Sports',
    price: 49.99,
    rating: 4.9,
    views: 6789,
    sales: 423,
    revenue: 21145,
    trend: 'up',
    change: '+15.6%'
  },
  {
    id: 5,
    name: 'Stainless Steel Water Bottle',
    category: 'Home',
    price: 24.99,
    rating: 4.7,
    views: 5432,
    sales: 891,
    revenue: 22266,
    trend: 'up',
    change: '+5.4%'
  }
]

export default function ProductPerformance() {
  const [sortBy, setSortBy] = useState<'revenue' | 'sales' | 'views'>('revenue')

  const sortedProducts = [...mockProducts].sort((a, b) => {
    if (sortBy === 'revenue') return b.revenue - a.revenue
    if (sortBy === 'sales') return b.sales - a.sales
    return b.views - a.views
  })

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Top Products</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Best performing products</p>
        </div>
        <select
          className="px-3 py-2 bg-gray-100 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as any)}
        >
          <option value="revenue">By Revenue</option>
          <option value="sales">By Sales</option>
          <option value="views">By Views</option>
        </select>
      </div>

      <div className="space-y-4">
        {sortedProducts.map((product, index) => (
          <div key={product.id} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:shadow-md transition-all">
            <div className="flex items-center space-x-4">
              <div className="flex items-center justify-center w-12 h-12 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg">
                <Package className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white">{product.name}</h3>
                <div className="flex items-center space-x-4 mt-1">
                  <span className="text-xs text-gray-500 dark:text-gray-400">{product.category}</span>
                  <div className="flex items-center space-x-1">
                    <Star className="w-3 h-3 text-yellow-500 fill-current" />
                    <span className="text-xs text-gray-600 dark:text-gray-400">{product.rating}</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-6">
              <div className="text-right">
                <p className="text-lg font-bold text-gray-900 dark:text-white">
                  ${(product.revenue / 1000).toFixed(1)}K
                </p>
                <div className={`flex items-center justify-end space-x-1 text-sm ${
                  product.trend === 'up' ? 'text-green-600' : 'text-red-600'
                }`}>
                  {product.trend === 'up' ? (
                    <TrendingUp className="w-3 h-3" />
                  ) : (
                    <TrendingDown className="w-3 h-3" />
                  )}
                  <span>{product.change}</span>
                </div>
              </div>

              <div className="flex space-x-3 text-gray-600 dark:text-gray-400">
                <div className="flex items-center space-x-1">
                  <Eye className="w-4 h-4" />
                  <span className="text-sm">{(product.views / 1000).toFixed(1)}K</span>
                </div>
                <div className="flex items-center space-x-1">
                  <ShoppingCart className="w-4 h-4" />
                  <span className="text-sm">{product.sales}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}