// ===========================================
// frontend/app/products/components/ProductGrid.tsx
// ===========================================
'use client'

import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { fetchProducts } from '@/lib/api'
import { Package, Star, TrendingUp, ShoppingCart } from 'lucide-react'

interface ProductGridProps {
  searchTerm: string
  category: string
  sortBy: string
  onSelectProduct: (product: any) => void
}

export default function ProductGrid({ searchTerm, category, sortBy, onSelectProduct }: ProductGridProps) {
  const [products, setProducts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadProducts()
  }, [category, sortBy])

  const loadProducts = async () => {
    try {
      const data = await fetchProducts(50, 0, category === 'all' ? undefined : category)
      setProducts(data)
    } catch (error) {
      console.error('Failed to load products:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredProducts = products.filter(p =>
    p.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.sku?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading) {
    return (
      <Card className="p-6">
        <div className="text-center">Loading products...</div>
      </Card>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {filteredProducts.map((product) => (
        <Card
          key={product.sku}
          className="p-4 hover:shadow-lg transition cursor-pointer"
          onClick={() => onSelectProduct(product)}
        >
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Package className="w-6 h-6 text-purple-600" />
            </div>
            {product.popularity_score > 50 && (
              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                Trending
              </span>
            )}
          </div>

          <h3 className="font-semibold text-gray-900 mb-1 line-clamp-2">
            {product.title || product.sku}
          </h3>

          <p className="text-sm text-gray-600 mb-3">
            {product.category || 'Uncategorized'}
          </p>

          <div className="flex items-center justify-between">
            <p className="text-xl font-bold text-gray-900">
              ${product.price?.toFixed(2) || '0.00'}
            </p>
            <div className="flex items-center space-x-1">
              <Star className="w-4 h-4 text-yellow-500 fill-current" />
              <span className="text-sm text-gray-600">
                {product.rating?.toFixed(1) || '4.0'}
              </span>
            </div>
          </div>

          <div className="mt-3 pt-3 border-t flex items-center justify-between text-sm text-gray-600">
            <span>SKU: {product.sku}</span>
            <span>{product.purchase_count || 0} sold</span>
          </div>
        </Card>
      ))}
    </div>
  )
}