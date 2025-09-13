// ===========================================
// frontend/app/analytics/components/CustomerAnalytics.tsx
// ===========================================
'use client'

import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import { fetchCustomerSegments } from '@/lib/api'
import { Users } from 'lucide-react'

interface CustomerAnalyticsProps {
  timeRange: string
}

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']

export default function CustomerAnalytics({ timeRange }: CustomerAnalyticsProps) {
  const [segments, setSegments] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadSegments()
  }, [])

  const loadSegments = async () => {
    try {
      const data = await fetchCustomerSegments()
      setSegments(data)
    } catch (error) {
      console.error('Failed to load segments:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Customer Segments</h3>
        <Users className="w-5 h-5 text-blue-600" />
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={segments}
            dataKey="customer_count"
            nameKey="segment_name"
            cx="50%"
            cy="50%"
            outerRadius={100}
          >
            {segments.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </Card>
  )
}