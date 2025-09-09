// ============================================
// frontend/app/dashboard/page.tsx
// ============================================
'use client'

import { useState, useEffect } from 'react'
import StatsCard from '@/components/dashboard/StatsCard'
import RevenueChart from '@/components/dashboard/RevenueChart'
import CustomerSegments from '@/components/dashboard/CustomerSegments'
import ProductPerformance from '@/components/dashboard/ProductPerformance'
import RecommendationEngine from '@/components/dashboard/RecommendationEngine'
import ActivityFeed from '@/components/dashboard/ActivityFeed'
import { fetchDashboardSummary } from '@/lib/api'
import {
  TrendingUp,
  Users,
  ShoppingBag,
  DollarSign,
  Package,
  Activity,
  Zap,
  Award
} from 'lucide-react'

interface DashboardData {
  total_customers: number
  total_products: number
  total_purchases: number
  total_revenue: number
  revenue_30d: number
  revenue_growth_30d: number
  active_customers_30d: number
  new_customers_30d: number
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState('30d')

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      const response = await fetchDashboardSummary()
      setData(response)
    } catch (error) {
      console.error('Failed to load dashboard:', error)
      // Use mock data if API fails
      setData({
        total_customers: 12543,
        total_products: 3421,
        total_purchases: 45632,
        total_revenue: 2456789,
        revenue_30d: 245678,
        revenue_growth_30d: 23.5,
        active_customers_30d: 3456,
        new_customers_30d: 234
      })
    } finally {
      setLoading(false)
    }
  }

  const stats = [
    {
      title: 'Total Revenue',
      value: `$${((data?.total_revenue || 0) / 1000).toFixed(1)}K`,
      change: `+${data?.revenue_growth_30d || 23.5}%`,
      icon: DollarSign,
      color: 'from-purple-500 to-pink-500',
      trend: 'up'
    },
    {
      title: 'Active Customers',
      value: (data?.active_customers_30d || 0).toLocaleString(),
      change: '+12.3%',
      icon: Users,
      color: 'from-blue-500 to-cyan-500',
      trend: 'up'
    },
    {
      title: 'Total Orders',
      value: (data?.total_purchases || 0).toLocaleString(),
      change: '+18.2%',
      icon: ShoppingBag,
      color: 'from-green-500 to-emerald-500',
      trend: 'up'
    },
    {
      title: 'Products',
      value: (data?.total_products || 0).toLocaleString(),
      change: '+5.4%',
      icon: Package,
      color: 'from-orange-500 to-red-500',
      trend: 'up'
    }
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading analytics...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-slide-in">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            Analytics Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Real-time insights and AI-powered recommendations
          </p>
        </div>
        <div className="flex space-x-3">
          <select
            className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
          <button className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:shadow-lg transition-all duration-300">
            Export Report
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <StatsCard key={index} {...stat} />
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RevenueChart />
        <CustomerSegments />
      </div>

      {/* Performance and Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ProductPerformance />
        </div>
        <div>
          <ActivityFeed />
        </div>
      </div>

      {/* Recommendation Engine */}
      <RecommendationEngine />
    </div>
  )
}
