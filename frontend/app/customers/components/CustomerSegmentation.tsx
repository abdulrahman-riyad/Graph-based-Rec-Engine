// ===========================================
// frontend/app/customers/components/CustomerSegmentation.tsx
// ===========================================
'use client'

import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { fetchCustomerSegments } from '@/lib/api'
import { Users, TrendingUp, AlertCircle, Star } from 'lucide-react'

export default function CustomerSegmentation() {
  const [segments, setSegments] = useState<any[]>([])

  useEffect(() => {
    loadSegments()
  }, [])

  const loadSegments = async () => {
    try {
      const data = await fetchCustomerSegments()
      setSegments(data)
    } catch (error) {
      console.error('Failed to load segments:', error)
    }
  }

  const getSegmentIcon = (name: string) => {
    if (name.includes('Champion')) return <Star className="w-5 h-5 text-yellow-500" />
    if (name.includes('Risk')) return <AlertCircle className="w-5 h-5 text-red-500" />
    if (name.includes('Loyal')) return <TrendingUp className="w-5 h-5 text-green-500" />
    return <Users className="w-5 h-5 text-blue-500" />
  }

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">Customer Segments</h3>

      <div className="space-y-3">
        {segments.map((segment) => (
          <div key={segment.segment_name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              {getSegmentIcon(segment.segment_name)}
              <div>
                <p className="font-medium">{segment.segment_name}</p>
                <p className="text-sm text-gray-600">{segment.percentage?.toFixed(1)}% of customers</p>
              </div>
            </div>
            <p className="font-semibold">{segment.customer_count}</p>
          </div>
        ))}
      </div>
    </Card>
  )
}