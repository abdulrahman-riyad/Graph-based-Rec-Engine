// ===========================================
// frontend/app/analytics/components/ConversionFunnel.tsx
// ===========================================
'use client'

import { Card } from '@/components/ui/card'
import { BarChart3 } from 'lucide-react'

interface ConversionFunnelProps {
  timeRange: string
}

export default function ConversionFunnel({ timeRange }: ConversionFunnelProps) {
  const funnelData = [
    { stage: 'Visitors', count: 10000, percentage: 100 },
    { stage: 'Product Views', count: 4500, percentage: 45 },
    { stage: 'Add to Cart', count: 1200, percentage: 12 },
    { stage: 'Checkout', count: 800, percentage: 8 },
    { stage: 'Purchase', count: 320, percentage: 3.2 }
  ]

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Conversion Funnel</h3>
        <BarChart3 className="w-5 h-5 text-orange-600" />
      </div>

      <div className="space-y-3">
        {funnelData.map((stage, index) => (
          <div key={stage.stage}>
            <div className="flex justify-between mb-1">
              <span className="text-sm font-medium">{stage.stage}</span>
              <span className="text-sm text-gray-600">{stage.count.toLocaleString()} ({stage.percentage}%)</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full"
                style={{ width: `${stage.percentage}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}