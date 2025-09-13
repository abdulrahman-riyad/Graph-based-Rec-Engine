'use client'

import { useState } from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import { Users, Star, TrendingUp, AlertCircle } from 'lucide-react'

interface CustomerSegmentsProps {
  data: any[];
}

const segmentIcons: Record<string, any> = {
  'Champions': Star,
  'Loyal Customers': TrendingUp,
  'At Risk': AlertCircle,
  'New Customers': Users,
  'Potential Loyalists': Users
}

export default function CustomerSegments({ data }: CustomerSegmentsProps) {
  const [activeSegment, setActiveSegment] = useState(data[0] || {})

  if (!data || data.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">Customer Segments</h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">RFM analysis breakdown</p>
          </div>
          <Users className="w-5 h-5 text-gray-400" />
        </div>
        <div className="h-64 flex items-center justify-center">
          <p className="text-gray-500">No customer segment data available</p>
        </div>
      </div>
    )
  }

  const colors = ['#8B5CF6', '#06B6D4', '#10B981', '#F59E0B', '#EF4444', '#6366F1', '#EC4899']

  // Prepare data for the chart
  const chartData = data.map((segment, index) => ({
    name: segment.segment_name,
    value: segment.customer_count,
    percentage: segment.percentage,
    color: colors[index % colors.length]
  }))

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload[0]) {
      const segment = payload[0].payload
      return (
        <div className="bg-white dark:bg-gray-800 p-3 shadow-lg rounded-lg border border-gray-200 dark:border-gray-700">
          <p className="font-semibold text-gray-900 dark:text-white">{segment.name}</p>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Customers: {segment.value.toLocaleString()}
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Percentage: {segment.percentage}%
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
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.color}
                    className="hover:opacity-80 transition-opacity cursor-pointer"
                    onClick={() => setActiveSegment(data[index])}
                  />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Segment Details */}
        <div className="space-y-3">
          {data.map((segment, index) => {
            const Icon = segmentIcons[segment.segment_name] || Users
            return (
              <div
                key={segment.segment_name}
                className={`flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all ${
                  activeSegment.segment_name === segment.segment_name
                    ? 'bg-gray-100 dark:bg-gray-700 shadow-sm'
                    : 'hover:bg-gray-50 dark:hover:bg-gray-700/50'
                }`}
                onClick={() => setActiveSegment(segment)}
              >
                <div className="flex items-center space-x-3">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: colors[index % colors.length] }}
                  />
                  <Icon className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                  <div>
                    <p className="text-sm font-semibold text-gray-900 dark:text-white">
                      {segment.segment_name}
                    </p>
                    <p className="text-xs text-gray-600 dark:text-gray-400">
                      {segment.customer_count.toLocaleString()} customers
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