'use client'

import { useEffect, useState } from 'react'
import { Card } from '@/components/ui/card'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'
import { fetchCustomerSegments } from '@/lib/api'
import { Users, TrendingUp, AlertCircle, Star } from 'lucide-react'

// Remove unused Legend import

interface Segment {
  segment_name: string
  customer_count: number
  percentage?: number
  avg_lifetime_value: number
  avg_purchase_frequency: number
  total_revenue: float
  growth_rate?: number
}

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#6B7280']

const segmentIcons: Record<string, React.ComponentType> = {
  'Champions': Star,
  'Loyal Customers': TrendingUp,
  'At Risk': AlertCircle,
  'New Customers': Users
}

// Fix the CustomTooltip any types
interface TooltipPayload {
  name: string
  value: number
  payload: {
    percentage?: number
  }
}

const CustomTooltip = ({
  active,
  payload
}: {
  active?: boolean
  payload?: TooltipPayload[]
}) => {
  if (active && payload && payload[0]) {
    return (
      <div className="bg-white p-3 shadow-lg rounded-lg border">
        <p className="font-semibold">{payload[0].name}</p>
        <p className="text-sm text-gray-600">
          Customers: {payload[0].value.toLocaleString()}
        </p>
        <p className="text-sm text-gray-600">
          Percentage: {payload[0].payload.percentage?.toFixed(1)}%
        </p>
      </div>
    )
  }
  return null
}


export default function CustomerSegments() {
  const [segments, setSegments] = useState<Segment[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedSegment, setSelectedSegment] = useState<Segment | null>(null)

  useEffect(() => {
    loadSegments()
  }, [])

  const loadSegments = async () => {
    try {
      const data = await fetchCustomerSegments()
      setSegments(data)
      if (data.length > 0) {
        setSelectedSegment(data[0])
      }
    } catch (error) {
      console.error('Failed to load customer segments:', error)
    } finally {
      setLoading(false)
    }
  }

  const chartData = segments.map(segment => ({
    name: segment.segment_name,
    value: segment.customer_count,
    percentage: segment.percentage || 0
  }))

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload[0]) {
      return (
        <div className="bg-white p-3 shadow-lg rounded-lg border">
          <p className="font-semibold">{payload[0].name}</p>
          <p className="text-sm text-gray-600">
            Customers: {payload[0].value.toLocaleString()}
          </p>
          <p className="text-sm text-gray-600">
            Percentage: {payload[0].payload.percentage?.toFixed(1)}%
          </p>
        </div>
      )
    }
    return null
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
        <h2 className="text-xl font-semibold text-gray-800">Customer Segments</h2>
        <Users className="w-5 h-5 text-gray-400" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pie Chart */}
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percentage }) => `${name}: ${percentage?.toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                    onClick={() => setSelectedSegment(segments[index])}
                    style={{ cursor: 'pointer' }}
                  />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Segment Details */}
        <div className="space-y-3">
          {segments.map((segment, index) => {
            const Icon = segmentIcons[segment.segment_name] || Users
            const isSelected = selectedSegment?.segment_name === segment.segment_name

            return (
              <div
                key={index}
                className={`p-3 rounded-lg border cursor-pointer transition-all ${
                  isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:bg-gray-50'
                }`}
                onClick={() => setSelectedSegment(segment)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div
                      className="w-3 h-3 rounded-full mr-3"
                      style={{ backgroundColor: COLORS[index % COLORS.length] }}
                    />
                    <Icon className="w-4 h-4 mr-2 text-gray-600" />
                    <div>
                      <p className="font-medium text-gray-800">{segment.segment_name}</p>
                      <p className="text-sm text-gray-600">
                        {segment.customer_count.toLocaleString()} customers
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-800">
                      ${segment.avg_lifetime_value.toFixed(0)}
                    </p>
                    <p className="text-xs text-gray-600">Avg LTV</p>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Selected Segment Details */}
      {selectedSegment && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-semibold text-gray-800 mb-2">{selectedSegment.segment_name}</h3>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-600">Total Customers</p>
              <p className="font-semibold">{selectedSegment.customer_count.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Avg Lifetime Value</p>
              <p className="font-semibold">${selectedSegment.avg_lifetime_value.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Percentage</p>
              <p className="font-semibold">{selectedSegment.percentage?.toFixed(1)}%</p>
            </div>
          </div>
        </div>
      )}
    </Card>
  )
}