// frontend/app/dashboard/components/ProductPerformance.tsx
'use client'

import { useEffect, useState } from 'react'
import { Card } from '@/components/ui/card'
import { Table } from '@/components/ui/table'
import { fetchProducts, fetchProductPerformance } from '@/lib/api'
import {
  Package,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Users,
  Star,
  ArrowUpRight,
  ArrowDownRight,
  MoreVertical
} from 'lucide-react'

interface Product {
  sku: string
  title: string
  price: number
  category: string
  rating: number
  popularity_score: number
}

interface Performance {
  revenue: number
  units_sold: number
  unique_customers: number
  trend: string
}

export default function ProductPerformance() {
  const [products, setProducts] = useState<Product[]>([])
  const [selectedProduct, setSelectedProduct] = useState<string | null>(null)
  const [performance, setPerformance] = useState<Performance | null>(null)
  const [loading, setLoading] = useState(true)
  const [view, setView] = useState<'table' | 'grid'>('table')

  useEffect(() => {
    loadProducts()
  }, [])

  useEffect(() => {
    if (selectedProduct) {
      loadProductPerformance(selectedProduct)
    }
  }, [selectedProduct])

  const loadProducts = async () => {
    try {
      const data = await fetchProducts(10)
      setProducts(data)
      if (data.length > 0) {
        setSelectedProduct(data[0].sku)
      }
    } catch (error) {
      console.error('Failed to load products:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadProductPerformance = async (sku: string) => {
    try {
      const data = await fetchProductPerformance(sku)
      setPerformance(data)
    } catch (error) {
      console.error('Failed to load product performance:', error)
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'increasing':
        return <ArrowUpRight className="w-4 h-4 text-green-500" />
      case 'decreasing':
        return <ArrowDownRight className="w-4 h-4 text-red-500" />
      default:
        return <TrendingUp className="w-4 h-4 text-gray-500" />
    }
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
          <p className="text-sm text-gray-600 mt-1">Monitor your top performing products</p>
        </div>
        <div className="flex space-x-2">
          <button
            className={`px-3 py-1 text-sm border rounded-lg transition ${
              view === 'table'
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
            }`}
            onClick={() => setView('table')}
          >
            Table View
          </button>
          <button
            className={`px-3 py-1 text-sm border rounded-lg transition ${
              view === 'grid'
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
            }`}
            onClick={() => setView('grid')}
          >
            Grid View
          </button>
        </div>
      </div>

      {view === 'table' ? (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 px-4 font-medium text-gray-700">Product</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Category</th>
                <th className="text-right py-3 px-4 font-medium text-gray-700">Price</th>
                <th className="text-right py-3 px-4 font-medium text-gray-700">Rating</th>
                <th className="text-right py-3 px-4 font-medium text-gray-700">Popularity</th>
                <th className="text-center py-3 px-4 font-medium text-gray-700">Trend</th>
                <th className="text-center py-3 px-4 font-medium text-gray-700">Actions</th>
              </tr>
            </thead>
            <tbody>
              {products.map((product, index) => (
                <tr
                  key={index}
                  className="border-b hover:bg-gray-50 cursor-pointer"
                  onClick={() => setSelectedProduct(product.sku)}
                >
                  <td className="py-3 px-4">
                    <div className="flex items-center">
                      <Package className="w-8 h-8 text-gray-400 mr-3" />
                      <div>
                        <p className="font-medium text-gray-800">{product.title}</p>
                        <p className="text-sm text-gray-500">{product.sku}</p>
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-full">
                      {product.category}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right font-medium">
                    ${product.price?.toFixed(2)}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <div className="flex items-center justify-end">
                      <Star className="w-4 h-4 text-yellow-500 mr-1" />
                      <span>{product.rating?.toFixed(1) || 'N/A'}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <div className="flex items-center justify-end">
                      <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${Math.min(product.popularity_score || 0, 100)}%` }}
                        />
                      </div>
                      <span className="text-sm">{product.popularity_score?.toFixed(0) || 0}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-center">
                    {getTrendIcon('stable')}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <button className="text-gray-400 hover:text-gray-600">
                      <MoreVertical className="w-5 h-5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {products.map((product, index) => (
            <div
              key={index}
              className={`p-4 border rounded-lg cursor-pointer transition-all ${
                selectedProduct === product.sku
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:shadow-lg'
              }`}
              onClick={() => setSelectedProduct(product.sku)}
            >
              <div className="flex items-start justify-between mb-3">
                <Package className="w-10 h-10 text-gray-400" />
                {getTrendIcon('stable')}
              </div>
              <h3 className="font-semibold text-gray-800 mb-1">{product.title}</h3>
              <p className="text-sm text-gray-500 mb-3">{product.sku}</p>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Price</span>
                  <span className="font-medium">${product.price?.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Rating</span>
                  <div className="flex items-center">
                    <Star className="w-3 h-3 text-yellow-500 mr-1" />
                    <span className="font-medium">{product.rating?.toFixed(1) || 'N/A'}</span>
                  </div>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Category</span>
                  <span className="font-medium">{product.category}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Performance Details */}
      {selectedProduct && performance && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-semibold text-gray-800 mb-4">Performance Metrics</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white p-3 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Revenue</p>
                  <p className="text-xl font-bold text-gray-800">
                    ${performance.revenue?.toLocaleString()}
                  </p>
                </div>
                <DollarSign className="w-8 h-8 text-green-500" />
              </div>
            </div>
            <div className="bg-white p-3 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Units Sold</p>
                  <p className="text-xl font-bold text-gray-800">
                    {performance.units_sold?.toLocaleString()}
                  </p>
                </div>
                <Package className="w-8 h-8 text-blue-500" />
              </div>
            </div>
            <div className="bg-white p-3 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Customers</p>
                  <p className="text-xl font-bold text-gray-800">
                    {performance.unique_customers?.toLocaleString()}
                  </p>
                </div>
                <Users className="w-8 h-8 text-purple-500" />
              </div>
            </div>
            <div className="bg-white p-3 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Trend</p>
                  <p className="text-xl font-bold text-gray-800 capitalize">
                    {performance.trend}
                  </p>
                </div>
                {getTrendIcon(performance.trend)}
              </div>
            </div>
          </div>
        </div>
      )}
    </Card>
  )
}