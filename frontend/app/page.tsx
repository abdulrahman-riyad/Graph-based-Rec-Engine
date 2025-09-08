// frontend/app/page.tsx
'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { 
  TrendingUp, 
  Users, 
  Package, 
  ShoppingCart,
  ArrowRight,
  Activity,
  DollarSign,
  Eye
} from 'lucide-react'
import { Card } from '@/components/ui/card'
import { fetchDashboardSummary } from '@/lib/api'

interface DashboardSummary {
  total_customers: number
  total_products: number
  total_purchases: number
  active_customers_30d: number
  revenue_30d: number
  recent_orders_7d: number
}

export default function Home() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchDashboardSummary()
        setSummary(data)
      } catch (error) {
        console.error('Failed to load dashboard summary:', error)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  const stats = [
    {
      title: 'Total Customers',
      value: summary?.total_customers || 0,
      icon: Users,
      color: 'bg-blue-500',
      change: '+12%',
      trend: 'up'
    },
    {
      title: 'Total Products',
      value: summary?.total_products || 0,
      icon: Package,
      color: 'bg-green-500',
      change: '+5%',
      trend: 'up'
    },
    {
      title: 'Total Orders',
      value: summary?.total_purchases || 0,
      icon: ShoppingCart,
      color: 'bg-purple-500',
      change: '+18%',
      trend: 'up'
    },
    {
      title: 'Revenue (30d)',
      value: `$${(summary?.revenue_30d || 0).toLocaleString()}`,
      icon: DollarSign,
      color: 'bg-yellow-500',
      change: '+25%',
      trend: 'up'
    }
  ]

  const quickActions = [
    {
      title: 'View Analytics Dashboard',
      description: 'Monitor real-time metrics and KPIs',
      icon: Activity,
      href: '/dashboard',
      color: 'text-blue-600'
    },
    {
      title: 'Product Recommendations',
      description: 'AI-powered product suggestions',
      icon: Eye,
      href: '/products',
      color: 'text-green-600'
    },
    {
      title: 'Customer Segments',
      description: 'Analyze customer behavior patterns',
      icon: Users,
      href: '/customers',
      color: 'text-purple-600'
    }
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Welcome to E-Commerce Intelligence Platform</h1>
        <p className="text-gray-600 mt-2">Advanced analytics and recommendations for your business</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, index) => (
          <Card key={index} className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900 mt-2">{stat.value.toLocaleString()}</p>
                <div className="flex items-center mt-2">
                  <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
                  <span className="text-sm text-green-500">{stat.change}</span>
                </div>
              </div>
              <div className={`p-3 rounded-full ${stat.color} bg-opacity-10`}>
                <stat.icon className={`w-6 h-6 ${stat.color.replace('bg-', 'text-')}`} />
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {quickActions.map((action, index) => (
            <Link key={index} href={action.href}>
              <Card className="p-6 hover:shadow-lg transition-shadow cursor-pointer">
                <div className="flex items-start">
                  <action.icon className={`w-6 h-6 ${action.color} mr-3 mt-1`} />
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-800 mb-1">{action.title}</h3>
                    <p className="text-sm text-gray-600 mb-3">{action.description}</p>
                    <div className="flex items-center text-blue-600 text-sm font-medium">
                      <span>Get Started</span>
                      <ArrowRight className="w-4 h-4 ml-1" />
                    </div>
                  </div>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Recent Activity</h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
              <span className="text-sm text-gray-700">New customer registered</span>
            </div>
            <span className="text-sm text-gray-500">2 minutes ago</span>
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
              <span className="text-sm text-gray-700">Order #1234 completed</span>
            </div>
            <span className="text-sm text-gray-500">5 minutes ago</span>
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-purple-500 rounded-full mr-3"></div>
              <span className="text-sm text-gray-700">Product recommendation generated</span>
            </div>
            <span className="text-sm text-gray-500">10 minutes ago</span>
          </div>
        </div>
      </Card>
    </div>
  )
}