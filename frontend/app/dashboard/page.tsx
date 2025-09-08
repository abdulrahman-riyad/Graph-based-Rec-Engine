// frontend/app/dashboard/page.tsx
'use client'

import { useState, useEffect } from 'react'
import CustomerSegments from './components/CustomerSegments'
import RevenueChart from './components/RevenueChart'
import ProductPerformance from './components/ProductPerformance'
import RecommendationEngine from './components/RecommendationEngine'
import { Card } from '@/components/ui/card'
import { fetchDashboardSummary, fetchRevenueAnalytics } from '@/lib/api'
import {
  Users,
  Package,
  ShoppingCart,
  DollarSign,
  TrendingUp,
  Activity,
  AlertCircle,
  CheckCircle
} from 'lucide-react'

export default function Dashboard() {
  const [summary, setSummary] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState('30d')

  useEffect(() => {
    loadDashboardData()
  }, [timeRange])

  const loadDashboardData = async () => {
    try {
      const data = await fetchDashboardSummary()
      setSummary(data)
    } catch (error) {
      console.error('Failed to load dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  const metrics = [
    {
      label: 'Total Revenue (30d)',
      value: `$${(summary?.revenue_30d || 0).toLocaleString()}`,
      change: '+25.3%',
      trend: 'up',
      icon: DollarSign,
      color: 'text-green-600'
    },
    {
      label: 'Active Customers',
      value: (summary?.active_customers_30d || 0).toLocaleString(),
      change: '+12.5%',
      trend: 'up',
      icon: Users,
      color: 'text-blue-600'
    },
    {
      label: 'Total Orders',
      value: (summary?.total_purchases || 0).toLocaleString(),
      change: '+18.2%',
      trend: 'up',
      icon: ShoppingCart,
      color: 'text-purple-600'
    },
    {
      label: 'Products',
      value: (summary?.total_products || 0).toLocaleString(),
      change: '+5.1%',
      trend: 'up',
      icon: Package,
      color: 'text-orange-600'
    }
  ]

  const systemStatus = [
    { name: 'Database', status: 'operational', uptime: '99.9%' },
    { name: 'API', status: 'operational', uptime: '99.8%' },
    { name: 'Analytics', status: 'operational', uptime: '99.7%' },
    { name: 'Recommendations', status: 'operational', uptime: '99.9%' }
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="spinner mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Analytics Dashboard</h1>
          <p className="text-gray-600 mt-1">Real-time insights and performance metrics</p>
        </div>
        <div className="flex space-x-2">
          <select
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
            Export Report
          </button>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <Card key={index} className="p-6">
            <div className="flex items-center justify-between mb-4">
              <metric.icon className={`w-8 h-8 ${metric.color}`} />
              <div className={`flex items-center text-sm ${
                metric.trend === 'up' ? 'text-green-600' : 'text-red-600'
              }`}>
                <TrendingUp className="w-4 h-4 mr-1" />
                {metric.change}
              </div>
            </div>
            <p className="text-2xl font-bold text-gray-800">{metric.value}</p>
            <p className="text-sm text-gray-600 mt-1">{metric.label}</p>
          </Card>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RevenueChart />
        <CustomerSegments />
      </div>

      {/* Product Performance */}
      <ProductPerformance />

      {/* Recommendation Engine */}
      <RecommendationEngine />

      {/* System Status */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-800">System Status</h2>
          <Activity className="w-5 h-5 text-green-600" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {systemStatus.map((service, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center">
                {service.status === 'operational' ? (
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                ) : (
                  <AlertCircle className="w-5 h-5 text-yellow-500 mr-2" />
                )}
                <div>
                  <p className="text-sm font-medium text-gray-800">{service.name}</p>
                  <p className="text-xs text-gray-600">Uptime: {service.uptime}</p>
                </div>
              </div>
              <span className={`px-2 py-1 text-xs rounded-full ${
                service.status === 'operational'
                  ? 'bg-green-100 text-green-800'
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                {service.status}
              </span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}