// ===========================================
// frontend/app/products/components/ProductFilters.tsx
// ===========================================
'use client'

import { Card } from '@/components/ui/card'
import { Filter, Package, Star } from 'lucide-react'

interface ProductFiltersProps {
  category: string
  onCategoryChange: (category: string) => void
}

export default function ProductFilters({ category, onCategoryChange }: ProductFiltersProps) {
  const categories = [
    { value: 'all', label: 'All Categories', count: 7833 },
    { value: 'Amazon Fashion', label: 'Fashion', count: 2450 },
    { value: 'Health and Personal Care', label: 'Health & Care', count: 2380 },
    { value: 'electronics', label: 'Electronics', count: 1845 },
    { value: 'home', label: 'Home & Garden', count: 892 },
    { value: 'sports', label: 'Sports & Outdoors', count: 266 }
  ]

  const priceRanges = [
    { label: 'Under $25', value: '0-25' },
    { label: '$25 - $50', value: '25-50' },
    { label: '$50 - $100', value: '50-100' },
    { label: 'Over $100', value: '100+' }
  ]

  return (
    <Card className="p-6">
      <div className="flex items-center space-x-2 mb-4">
        <Filter className="w-5 h-5 text-gray-600" />
        <h3 className="text-lg font-semibold">Filters</h3>
      </div>

      <div className="space-y-6">
        <div>
          <h4 className="font-medium mb-3">Categories</h4>
          <div className="space-y-2">
            {categories.map((cat) => (
              <label
                key={cat.value}
                className="flex items-center justify-between cursor-pointer hover:bg-gray-50 p-2 rounded"
              >
                <div className="flex items-center">
                  <input
                    type="radio"
                    name="category"
                    value={cat.value}
                    checked={category === cat.value}
                    onChange={(e) => onCategoryChange(e.target.value)}
                    className="mr-2"
                  />
                  <span className="text-sm">{cat.label}</span>
                </div>
                <span className="text-xs text-gray-500">{cat.count}</span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <h4 className="font-medium mb-3">Price Range</h4>
          <div className="space-y-2">
            {priceRanges.map((range) => (
              <label
                key={range.value}
                className="flex items-center cursor-pointer hover:bg-gray-50 p-2 rounded"
              >
                <input
                  type="checkbox"
                  value={range.value}
                  className="mr-2"
                />
                <span className="text-sm">{range.label}</span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <h4 className="font-medium mb-3">Rating</h4>
          <div className="space-y-2">
            {[4, 3, 2, 1].map((stars) => (
              <label
                key={stars}
                className="flex items-center cursor-pointer hover:bg-gray-50 p-2 rounded"
              >
                <input type="checkbox" className="mr-2" />
                <div className="flex items-center">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      className={`w-3 h-3 ${
                        i < stars ? 'text-yellow-500 fill-current' : 'text-gray-300'
                      }`}
                    />
                  ))}
                  <span className="text-sm ml-1">& up</span>
                </div>
              </label>
            ))}
          </div>
        </div>
      </div>
    </Card>
  )
}