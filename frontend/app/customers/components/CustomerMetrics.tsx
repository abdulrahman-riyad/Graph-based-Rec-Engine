// ===========================================
// frontend/app/customers/components/CustomerMetrics.tsx
// ===========================================
'use client'

import { Card } from '@/components/ui/card'
import { TrendingUp, ShoppingCart, Clock, DollarSign } from 'lucide-react'

interface CustomerMetricsProps {
  customerId?: string
}

export default function CustomerMetrics({ customerId }: CustomerMetricsProps) {
  const metrics = [
    { label: 'Avg Order Value', value: '$124.50', icon: DollarSign, trend: '+12%' },
    { label: 'Purchase Frequency', value: '2.3/month', icon: ShoppingCart, trend: '+5%' },
    { label: 'Customer Since', value: '18 months', icon: Clock, trend: null },
    { label: 'Lifetime Value', value: '$2,845', icon: TrendingUp, trend: '+23%' }
  ]

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">
        {customerId ? 'Customer Metrics' : 'Average Metrics'}
      </h3>

      <div className="space-y-3">
        {metrics.map((metric) => {
          const Icon = metric.icon
          return (
            <div key={metric.label} className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Icon className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-600">{metric.label}</span>
              </div>
              <div className="text-right">
                <p className="font-semibold">{metric.value}</p>
                {metric.trend && (
                  <p className="text-xs text-green-600">{metric.trend}</p>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </Card>
  )
}