// frontend/app/products/page.tsx
'use client'

import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import ProductGrid from './components/ProductGrid'
import ProductDetails from './components/ProductDetails'
import ProductFilters from './components/ProductFilters'
import ProductMetrics from './components/ProductMetrics'
import { fetchProducts, fetchDashboardSummary } from '@/lib/api'
import { Package, TrendingUp, Star, DollarSign } from 'lucide-react'

export default function ProductsPage() {
  const [selectedProduct, setSelectedProduct] = useState<any>(null)
  const [category, setCategory] = useState('all')
  const [sortBy, setSortBy] = useState('popularity')
  const [searchTerm, setSearchTerm] = useState('')
  const [metrics, setMetrics] = useState<any>(null)

  useEffect(() => {
    loadMetrics()
  }, [])

  const loadMetrics = async () => {
    try {
      const data = await fetchDashboardSummary()
      setMetrics({
        total: data.total_products,
        active: Math.floor(data.total_products * 0.85),
        avg_rating: 4.2,
        top_category: 'Electronics'
      })
    } catch (error) {
      console.error('Failed to load metrics:', error)
    }
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Product Catalog</h1>
        <p className="text-gray-600 mt-2">Manage and analyze your product inventory</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Products</p>
              <p className="text-2xl font-bold">{metrics?.total?.toLocaleString() || '0'}</p>
            </div>
            <Package className="w-8 h-8 text-purple-600" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Active Products</p>
              <p className="text-2xl font-bold">{metrics?.active?.toLocaleString() || '0'}</p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-600" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg Rating</p>
              <p className="text-2xl font-bold">{metrics?.avg_rating || '0'}</p>
            </div>
            <Star className="w-8 h-8 text-yellow-500" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Top Category</p>
              <p className="text-lg font-bold">{metrics?.top_category || 'N/A'}</p>
            </div>
            <DollarSign className="w-8 h-8 text-blue-600" />
          </div>
        </Card>
      </div>

      {/* Search and Filters */}
      <div className="flex gap-4 mb-6">
        <input
          type="text"
          placeholder="Search products..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="popularity">Most Popular</option>
          <option value="price_low">Price: Low to High</option>
          <option value="price_high">Price: High to Low</option>
          <option value="rating">Highest Rated</option>
          <option value="newest">Newest First</option>
        </select>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1">
          <ProductFilters
            category={category}
            onCategoryChange={setCategory}
          />
        </div>
        <div className="lg:col-span-3 space-y-6">
          <ProductGrid
            searchTerm={searchTerm}
            category={category}
            sortBy={sortBy}
            onSelectProduct={setSelectedProduct}
          />
          {selectedProduct && (
            <ProductDetails product={selectedProduct} />
          )}
          <ProductMetrics productId={selectedProduct?.sku} />
        </div>
      </div>
    </div>
  )
}