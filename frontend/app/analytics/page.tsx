// frontend/app/analytics/page.tsx
'use client'

import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import RevenueMetrics from './components/RevenueMetrics'
import CustomerAnalytics from './components/CustomerAnalytics'
import ProductAnalytics from './components/ProductAnalytics'
import ConversionFunnel from './components/ConversionFunnel'
import { fetchDashboardSummary, fetchRevenueAnalytics } from '@/lib/api'
import { BarChart3, TrendingUp, Users, Package } from 'lucide-react'

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState('30d')
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<any>(null)

  useEffect(() => {
    loadAnalytics()
  }, [timeRange])

  const loadAnalytics = async () => {
    try {
      const summary = await fetchDashboardSummary()
      setData(summary)
    } catch (error) {
      console.error('Failed to load analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
        <p className="text-gray-600 mt-2">Comprehensive business intelligence and insights</p>
      </div>

      {/* Time Range Selector */}
      <div className="mb-6 flex justify-end">
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
          <option value="90d">Last 90 days</option>
          <option value="1y">Last year</option>
        </select>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Revenue (30d)</p>
              <p className="text-2xl font-bold">${data?.revenue_30d?.toLocaleString() || '0'}</p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-600" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Customers</p>
              <p className="text-2xl font-bold">{data?.total_customers?.toLocaleString() || '0'}</p>
            </div>
            <Users className="w-8 h-8 text-blue-600" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Products</p>
              <p className="text-2xl font-bold">{data?.total_products?.toLocaleString() || '0'}</p>
            </div>
            <Package className="w-8 h-8 text-purple-600" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Conversion Rate</p>
              <p className="text-2xl font-bold">3.2%</p>
            </div>
            <BarChart3 className="w-8 h-8 text-orange-600" />
          </div>
        </Card>
      </div>

      {/* Analytics Components */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RevenueMetrics timeRange={timeRange} />
        <CustomerAnalytics timeRange={timeRange} />
        <ProductAnalytics timeRange={timeRange} />
        <ConversionFunnel timeRange={timeRange} />
      </div>
    </div>
  )
}