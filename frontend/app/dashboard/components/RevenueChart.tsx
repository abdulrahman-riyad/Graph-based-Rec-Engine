// frontend/app/dashboard/components/RevenueChart.tsx
'use client'

import { useEffect, useState } from 'react'
import { Card } from '@/components/ui/card'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  Area,
  AreaChart
} from 'recharts'
import { fetchRevenueAnalytics } from '@/lib/api'
import { DollarSign, TrendingUp, Calendar, BarChart3 } from 'lucide-react'

interface RevenueData {
  date: string
  revenue: number
  orders: number
  customers: number
}

export default function RevenueChart() {
  const [data, setData] = useState<RevenueData[]>([])
  const [loading, setLoading] = useState(true)
  const [chartType, setChartType] = useState<'line' | 'bar' | 'area'>('area')
  const [timeRange, setTimeRange] = useState(30)
  const [summary, setSummary] = useState({
    total: 0,
    average: 0,
    trend: 'stable'
  })

  useEffect(() => {
    loadRevenueData()
  }, [timeRange])

  const loadRevenueData = async () => {
    try {
      const endDate = new Date()
      const startDate = new Date()
      startDate.setDate(startDate.getDate() - timeRange)

      const response = await fetchRevenueAnalytics(startDate, endDate)

      // Transform data for chart
      const chartData = response.daily_breakdown.dates.map((date: string, index: number) => ({
        date: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        revenue: response.daily_breakdown.revenues[index] || 0,
        orders: response.daily_breakdown.orders[index] || 0,
        customers: response.daily_breakdown.customers[index] || 0
      }))

      setData(chartData)
      setSummary({
        total: response.summary.total_revenue,
        average: response.summary.avg_daily_revenue,
        trend: response.summary.trend
      })
    } catch (error) {
      console.error('Failed to load revenue data:', error)
    } finally {
      setLoading(false)
    }
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload[0]) {
      return (
        <div className="bg-white p-3 shadow-lg rounded-lg border">
          <p className="font-semibold">{label}</p>
          <p className="text-sm text-blue-600">
            Revenue: ${payload[0].value?.toLocaleString()}
          </p>
          {payload[1] && (
            <p className="text-sm text-green-600">
              Orders: {payload[1].value?.toLocaleString()}
            </p>
          )}
          {payload[2] && (
            <p className="text-sm text-purple-600">
              Customers: {payload[2].value?.toLocaleString()}
            </p>
          )}
        </div>
      )
    }
    return null
  }

  const renderChart = () => {
    switch (chartType) {
      case 'line':
        return (
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line
              type="monotone"
              dataKey="revenue"
              stroke="#3B82F6"
              name="Revenue ($)"
              strokeWidth={2}
            />
            <Line
              type="monotone"
              dataKey="orders"
              stroke="#10B981"
              name="Orders"
              strokeWidth={2}
            />
          </LineChart>
        )

      case 'bar':
        return (
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar dataKey="revenue" fill="#3B82F6" name="Revenue ($)" />
            <Bar dataKey="orders" fill="#10B981" name="Orders" />
          </BarChart>
        )

      case 'area':
      default:
        return (
          <AreaChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Area
              type="monotone"
              dataKey="revenue"
              stroke="#3B82F6"
              fill="#3B82F6"
              fillOpacity={0.3}
              name="Revenue ($)"
            />
            <Area
              type="monotone"
              dataKey="orders"
              stroke="#10B981"
              fill="#10B981"
              fillOpacity={0.3}
              name="Orders"
            />
          </AreaChart>
        )
    }
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
        <div>
          <h2 className="text-xl font-semibold text-gray-800">Revenue Analytics</h2>
          <p className="text-sm text-gray-600 mt-1">Track your revenue performance over time</p>
        </div>
        <div className="flex space-x-2">
          {/* Time Range Selector */}
          <select
            className="px-3 py-1 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={timeRange}
            onChange={(e) => setTimeRange(Number(e.target.value))}
          >
            <option value={7}>7 days</option>
            <option value={30}>30 days</option>
            <option value={90}>90 days</option>
          </select>

          {/* Chart Type Selector */}
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              className={`p-1 rounded ${chartType === 'area' ? 'bg-white shadow' : ''}`}
              onClick={() => setChartType('area')}
            >
              <BarChart3 className="w-4 h-4" />
            </button>
            <button
              className={`p-1 rounded ${chartType === 'line' ? 'bg-white shadow' : ''}`}
              onClick={() => setChartType('line')}
            >
              <TrendingUp className="w-4 h-4" />
            </button>
            <button
              className={`p-1 rounded ${chartType === 'bar' ? 'bg-white shadow' : ''}`}
              onClick={() => setChartType('bar')}
            >
              <BarChart3 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="p-3 bg-blue-50 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Revenue</p>
              <p className="text-xl font-bold text-gray-800">
                ${summary.total.toLocaleString()}
              </p>
            </div>
            <DollarSign className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        <div className="p-3 bg-green-50 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Daily Average</p>
              <p className="text-xl font-bold text-gray-800">
                ${summary.average.toLocaleString()}
              </p>
            </div>
            <Calendar className="w-8 h-8 text-green-500" />
          </div>
        </div>
        <div className="p-3 bg-purple-50 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Trend</p>
              <p className="text-xl font-bold text-gray-800 capitalize">
                {summary.trend}
              </p>
            </div>
            <TrendingUp className={`w-8 h-8 ${
              summary.trend === 'increasing' ? 'text-green-500' :
              summary.trend === 'decreasing' ? 'text-red-500' : 'text-gray-500'
            }`} />
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          {renderChart()}
        </ResponsiveContainer>
      </div>
    </Card>
  )
}