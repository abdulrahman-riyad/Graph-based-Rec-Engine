'use client'

import { useState } from 'react'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts'
import { TrendingUp, DollarSign, Calendar } from 'lucide-react'

interface RevenueChartProps {
  data: any;
}

export default function RevenueChart({ data }: RevenueChartProps) {
  const [chartType, setChartType] = useState<'area' | 'line'>('area')

  if (!data || !data.daily_revenue) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">Revenue Overview</h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Monthly revenue and profit trends</p>
          </div>
        </div>
        <div className="h-80 flex items-center justify-center">
          <p className="text-gray-500">No revenue data available</p>
        </div>
      </div>
    )
  }

  // Transform data for the chart
  const chartData = data.daily_revenue.map((item: any) => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    revenue: item.revenue,
    orders: item.orders,
    profit: item.revenue * 0.3 // Assuming 30% profit margin
  }))

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload[0]) {
      return (
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
          <p className="font-semibold text-gray-900 dark:text-white">{label}</p>
          <p className="text-sm text-green-600">
            Revenue: ${payload[0].value?.toLocaleString()}
          </p>
          {payload[1] && (
            <p className="text-sm text-blue-600">
              Orders: {payload[1].value}
            </p>
          )}
          {payload[2] && (
            <p className="text-sm text-purple-600">
              Profit: ${payload[2].value?.toLocaleString()}
            </p>
          )}
        </div>
      )
    }
    return null
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Revenue Overview</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Monthly revenue and profit trends</p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => setChartType('area')}
            className={`px-3 py-1 rounded-lg text-sm font-medium transition ${
              chartType === 'area'
                ? 'bg-purple-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
          >
            Area
          </button>
          <button
            onClick={() => setChartType('line')}
            className={`px-3 py-1 rounded-lg text-sm font-medium transition ${
              chartType === 'line'
                ? 'bg-purple-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
          >
            Line
          </button>
        </div>
      </div>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          {chartType === 'area' ? (
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorProfit" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#EC4899" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#EC4899" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
              <XAxis dataKey="date" className="text-xs" />
              <YAxis className="text-xs" />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Area
                type="monotone"
                dataKey="revenue"
                stroke="#8B5CF6"
                fillOpacity={1}
                fill="url(#colorRevenue)"
                strokeWidth={2}
              />
              <Area
                type="monotone"
                dataKey="profit"
                stroke="#EC4899"
                fillOpacity={1}
                fill="url(#colorProfit)"
                strokeWidth={2}
              />
            </AreaChart>
          ) : (
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
              <XAxis dataKey="date" className="text-xs" />
              <YAxis className="text-xs" />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line
                type="monotone"
                dataKey="revenue"
                stroke="#8B5CF6"
                strokeWidth={3}
                dot={{ fill: '#8B5CF6', r: 4 }}
                activeDot={{ r: 6 }}
              />
              <Line
                type="monotone"
                dataKey="orders"
                stroke="#06B6D4"
                strokeWidth={3}
                dot={{ fill: '#06B6D4', r: 4 }}
                activeDot={{ r: 6 }}
              />
              <Line
                type="monotone"
                dataKey="profit"
                stroke="#EC4899"
                strokeWidth={3}
                dot={{ fill: '#EC4899', r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
        <div>
          <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400 mb-1">
            <DollarSign className="w-4 h-4" />
            <span className="text-xs">Total Revenue</span>
          </div>
          <p className="text-xl font-bold text-gray-900 dark:text-white">
            ${data.total_revenue ? (data.total_revenue / 1000).toFixed(1) + 'K' : '0'}
          </p>
        </div>
        <div>
          <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400 mb-1">
            <TrendingUp className="w-4 h-4" />
            <span className="text-xs">Growth Rate</span>
          </div>
          <p className="text-xl font-bold text-green-600">
            +{data.growth_rate ? data.growth_rate.toFixed(1) : '0'}%
          </p>
        </div>
        <div>
          <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400 mb-1">
            <Calendar className="w-4 h-4" />
            <span className="text-xs">Avg Daily</span>
          </div>
          <p className="text-xl font-bold text-gray-900 dark:text-white">
            ${data.avg_order_value ? data.avg_order_value.toFixed(0) : '0'}
          </p>
        </div>
      </div>
    </div>
  )
}