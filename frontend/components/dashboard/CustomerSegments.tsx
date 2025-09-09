// ============================================
// frontend/components/dashboard/CustomerSegments.tsx
// ============================================
'use client'

import { useEffect, useState } from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import { Users, Star, TrendingUp, AlertCircle } from 'lucide-react'

const mockSegments = [
  { name: 'Champions', value: 2450, percentage: 24.5, color: '#8B5CF6' },
  { name: 'Loyal', value: 3200, percentage: 32, color: '#06B6D4' },
  { name: 'Potential', value: 1800, percentage: 18, color: '#10B981' },
  { name: 'New', value: 1550, percentage: 15.5, color: '#F59E0B' },
  { name: 'At Risk', value: 1000, percentage: 10, color: '#EF4444' }
]

const segmentIcons: Record<string, any> = {
  'Champions': Star,
  'Loyal': TrendingUp,
  'At Risk': AlertCircle,
  'New': Users,
  'Potential': Users
}

export default function CustomerSegments() {
  const [activeSegment, setActiveSegment] = useState(mockSegments[0])

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload[0]) {
      return (
        <div className="bg-white dark:bg-gray-800 p-3 shadow-lg rounded-lg border border-gray-200 dark:border-gray-700">
          <p className="font-semibold text-gray-900 dark:text-white">{payload[0].name}</p>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Customers: {payload[0].value.toLocaleString()}
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Percentage: {payload[0].payload.percentage}%
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Customer Segments</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">RFM analysis breakdown</p>
        </div>
        <Users className="w-5 h-5 text-gray-400" />
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Chart */}
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={mockSegments}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {mockSegments.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.color}
                    className="hover:opacity-80 transition-opacity cursor-pointer"
                    onClick={() => setActiveSegment(entry)}
                  />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Segment Details */}
        <div className="space-y-3">
          {mockSegments.map((segment) => {
            const Icon = segmentIcons[segment.name] || Users
            return (
              <div
                key={segment.name}
                className={`flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all ${
                  activeSegment.name === segment.name
                    ? 'bg-gray-100 dark:bg-gray-700 shadow-sm'
                    : 'hover:bg-gray-50 dark:hover:bg-gray-700/50'
                }`}
                onClick={() => setActiveSegment(segment)}
              >
                <div className="flex items-center space-x-3">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: segment.color }}
                  />
                  <Icon className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                  <div>
                    <p className="text-sm font-semibold text-gray-900 dark:text-white">
                      {segment.name}
                    </p>
                    <p className="text-xs text-gray-600 dark:text-gray-400">
                      {segment.value.toLocaleString()} customers
                    </p>
                  </div>
                </div>
                <span className="text-sm font-bold text-gray-900 dark:text-white">
                  {segment.percentage}%
                </span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
