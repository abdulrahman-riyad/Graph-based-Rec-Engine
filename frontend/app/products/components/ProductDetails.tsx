// ===========================================
// frontend/app/products/components/ProductDetails.tsx
// ===========================================
'use client'

import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { fetchRecommendations } from '@/lib/api'
import { Package, Star, TrendingUp, Tag, BarChart3, Users } from 'lucide-react'

interface ProductDetailsProps {
  product: any
}

export default function ProductDetails({ product }: ProductDetailsProps) {
  const [relatedProducts, setRelatedProducts] = useState<any[]>([])

  useEffect(() => {
    // In a real app, this would fetch products frequently bought with this one
    setRelatedProducts([])
  }, [product])

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">Product Details</h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div>
            <p className="text-sm text-gray-600 mb-1">Product Name</p>
            <p className="font-medium">{product.title || product.sku}</p>
          </div>

          <div>
            <p className="text-sm text-gray-600 mb-1">SKU</p>
            <p className="font-medium">{product.sku}</p>
          </div>

          <div>
            <p className="text-sm text-gray-600 mb-1">Category</p>
            <p className="font-medium">{product.category || 'Uncategorized'}</p>
          </div>

          <div>
            <p className="text-sm text-gray-600 mb-1">Brand</p>
            <p className="font-medium">{product.brand || 'Unknown'}</p>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <p className="text-sm text-gray-600 mb-1">Price</p>
            <p className="text-2xl font-bold text-gray-900">${product.price?.toFixed(2) || '0.00'}</p>
          </div>

          <div>
            <p className="text-sm text-gray-600 mb-1">Rating</p>
            <div className="flex items-center space-x-2">
              <div className="flex">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className={`w-4 h-4 ${
                      i < Math.floor(product.rating || 4)
                        ? 'text-yellow-500 fill-current'
                        : 'text-gray-300'
                    }`}
                  />
                ))}
              </div>
              <span className="text-sm text-gray-600">
                ({product.review_count || 0} reviews)
              </span>
            </div>
          </div>

          <div>
            <p className="text-sm text-gray-600 mb-1">Sales Performance</p>
            <div className="flex items-center space-x-4">
              <span className="text-sm">
                <span className="font-semibold">{product.purchase_count || 0}</span> sold
              </span>
              <span className="text-sm">
                <span className="font-semibold">{product.view_count || 0}</span> views
              </span>
            </div>
          </div>

          <div>
            <p className="text-sm text-gray-600 mb-1">Popularity Score</p>
            <div className="flex items-center space-x-2">
              <div className="flex-1 bg-gray-200 rounded-full h-2">
                <div
                  className="bg-purple-600 h-2 rounded-full"
                  style={{ width: `${Math.min((product.popularity_score || 0) * 10, 100)}%` }}
                />
              </div>
              <span className="text-sm font-medium">{product.popularity_score || 0}</span>
            </div>
          </div>
        </div>
      </div>
    </Card>
  )
}