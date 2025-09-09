// frontend/app/dashboard/components/ProductPerformance.tsx
'use client'

import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { fetchProducts } from '@/lib/api'
import {
  Package,
  TrendingUp,
  TrendingDown,
  Star,
  Eye,
  ShoppingCart,
  DollarSign
} from 'lucide-react'

interface Product {
  sku: string
  title: string
  category: string
  price: number
  rating: number
  view_count: number
  purchase_count: number
  revenue: number
  trend: 'up' | 'down' | 'stable'
}

export default function ProductPerformance() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [sortBy, setSortBy] = useState<'revenue' | 'purchases' | 'views'>('revenue')
  const [timeRange, setTimeRange] = useState('30d')

  useEffect(() => {
    loadProducts()
  }, [sortBy, timeRange])

  const loadProducts = async () => {
    try {
      const data = await fetchProducts(10, 0)
      setProducts(data)
    } catch (error) {
      console.error('Failed to load products:', error)
    } finally {
      setLoading(false)
    }
  }

  const getTrendIcon = (trend: string) => {
    if (trend === 'up') return <TrendingUp className="w-4 h-4 text-green-600" />
    if (trend === 'down') return <TrendingDown className="w-4 h-4 text-red-600" />
    return <span className="w-4 h-4 text-gray-400">—</span>
  }

  if (loading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="spinner"></div>
        </div>
      </Card>
    )
  }

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-800">Product Performance</h2>
          <p className="text-sm text-gray-600 mt-1">Top performing products</p>
        </div>
        <div className="flex space-x-2">
          <select
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
          >
            <option value="revenue">By Revenue</option>
            <option value="purchases">By Purchases</option>
            <option value="views">By Views</option>
          </select>
          <select
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b">
              <th className="text-left py-3 px-4">Product</th>
              <th className="text-center py-3 px-4">Category</th>
              <th className="text-center py-3 px-4">Price</th>
              <th className="text-center py-3 px-4">Rating</th>
              <th className="text-center py-3 px-4">Views</th>
              <th className="text-center py-3 px-4">Purchases</th>
              <th className="text-right py-3 px-4">Revenue</th>
              <th className="text-center py-3 px-4">Trend</th>
            </tr>
          </thead>
          <tbody>
            {products.map((product, index) => (
              <tr key={product.sku} className="border-b hover:bg-gray-50">
                <td className="py-3 px-4">
                  <div className="flex items-center">
                    <Package className="w-8 h-8 text-gray-400 mr-3" />
                    <div>
                      <p className="font-medium text-gray-800 line-clamp-1">{product.title}</p>
                      <p className="text-sm text-gray-500">SKU: {product.sku}</p>
                    </div>
                  </div>
                </td>
                <td className="text-center py-3 px-4">
                  <span className="px-2 py-1 bg-gray-100 rounded-full text-sm">
                    {product.category}
                  </span>
                </td>
                <td className="text-center py-3 px-4">
                  ${product.price?.toFixed(2)}
                </td>
                <td className="text-center py-3 px-4">
                  <div className="flex items-center justify-center">
                    <Star className="w-4 h-4 text-yellow-500 mr-1" />
                    <span>{product.rating?.toFixed(1)}</span>
                  </div>
                </td>
                <td className="text-center py-3 px-4">
                  <div className="flex items-center justify-center">
                    <Eye className="w-4 h-4 text-gray-400 mr-1" />
                    <span>{product.view_count?.toLocaleString()}</span>
                  </div>
                </td>
                <td className="text-center py-3 px-4">
                  <div className="flex items-center justify-center">
                    <ShoppingCart className="w-4 h-4 text-gray-400 mr-1" />
                    <span>{product.purchase_count?.toLocaleString()}</span>
                  </div>
                </td>
                <td className="text-right py-3 px-4 font-semibold">
                  ${product.revenue?.toLocaleString()}
                </td>
                <td className="text-center py-3 px-4">
                  {getTrendIcon(product.trend)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  )
}