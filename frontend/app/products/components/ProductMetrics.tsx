// ===========================================
// frontend/app/products/components/ProductMetrics.tsx
// ===========================================
'use client'

import { Card } from '@/components/ui/card'
import { TrendingUp, Eye, ShoppingCart, DollarSign } from 'lucide-react'

interface ProductMetricsProps {
  productId?: string
}

export default function ProductMetrics({ productId }: ProductMetricsProps) {
  const metrics = [
    { label: 'Conversion Rate', value: '3.2%', icon: ShoppingCart, trend: '+0.5%' },
    { label: 'View to Cart', value: '12.5%', icon: Eye, trend: '+2.1%' },
    { label: 'Avg Order Value', value: '$85.50', icon: DollarSign, trend: '+$5.20' },
    { label: 'Return Rate', value: '2.1%', icon: TrendingUp, trend: '-0.3%' }
  ]

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">
        {productId ? 'Product Performance' : 'Overall Performance'}
      </h3>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {metrics.map((metric) => {
          const Icon = metric.icon
          const isPositive = metric.trend.startsWith('+') || metric.trend.startsWith('-0')

          return (
            <div key={metric.label} className="text-center">
              <div className="flex justify-center mb-2">
                <Icon className="w-6 h-6 text-gray-400" />
              </div>
              <p className="text-2xl font-bold">{metric.value}</p>
              <p className="text-sm text-gray-600">{metric.label}</p>
              <p className={`text-xs mt-1 ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                {metric.trend}
              </p>
            </div>
          )
        })}
      </div>
    </Card>
  )
}