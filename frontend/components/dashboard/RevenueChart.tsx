// ============================================
// frontend/components/dashboard/RevenueChart.tsx
// ============================================
'use client'

import { useState, useEffect } from 'react'
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

const generateMockData = () => {
  const days = 30
  const data = []
  const baseRevenue = 5000

  for (let i = 0; i < days; i++) {
    const date = new Date()
    date.setDate(date.getDate() - (days - i))
    data.push({
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      revenue: baseRevenue + Math.random() * 3000 + (i * 50),
      orders: Math.floor(50 + Math.random() * 30 + (i * 2)),
      profit: (baseRevenue + Math.random() * 3000) * 0.3
    })
  }
  return data
}

export default function RevenueChart() {
  const [data, setData] = useState<any[]>([])
  const [chartType, setChartType] = useState<'area' | 'line'>('area')

  useEffect(() => {
    setData(generateMockData())
  }, [])

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
            <AreaChart data={data}>
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
            <LineChart data={data}>
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
          <p className="text-xl font-bold text-gray-900 dark:text-white">$234.5K</p>
        </div>
        <div>
          <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400 mb-1">
            <TrendingUp className="w-4 h-4" />
            <span className="text-xs">Growth Rate</span>
          </div>
          <p className="text-xl font-bold text-green-600">+23.5%</p>
        </div>
        <div>
          <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400 mb-1">
            <Calendar className="w-4 h-4" />
            <span className="text-xs">Avg Daily</span>
          </div>
          <p className="text-xl font-bold text-gray-900 dark:text-white">$7.8K</p>
        </div>
      </div>
    </div>
  )
}