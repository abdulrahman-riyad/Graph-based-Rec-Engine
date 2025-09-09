// ============================================
// frontend/components/dashboard/ActivityFeed.tsx
// ============================================
'use client'

import { ShoppingCart, User, Package, DollarSign, TrendingUp } from 'lucide-react'

const activities = [
  {
    id: 1,
    type: 'order',
    message: 'New order #12345',
    value: '$234.50',
    time: '2 minutes ago',
    icon: ShoppingCart,
    color: 'text-blue-600 bg-blue-100'
  },
  {
    id: 2,
    type: 'customer',
    message: 'New customer registered',
    value: 'Sarah Johnson',
    time: '5 minutes ago',
    icon: User,
    color: 'text-green-600 bg-green-100'
  },
  {
    id: 3,
    type: 'product',
    message: 'Low stock alert',
    value: 'Wireless Mouse',
    time: '10 minutes ago',
    icon: Package,
    color: 'text-orange-600 bg-orange-100'
  },
  {
    id: 4,
    type: 'revenue',
    message: 'Daily target achieved',
    value: '105% completed',
    time: '1 hour ago',
    icon: TrendingUp,
    color: 'text-purple-600 bg-purple-100'
  },
  {
    id: 5,
    type: 'payment',
    message: 'Payment received',
    value: '$1,234.00',
    time: '2 hours ago',
    icon: DollarSign,
    color: 'text-green-600 bg-green-100'
  }
]

export default function ActivityFeed() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">Recent Activity</h2>
        <button className="text-sm text-purple-600 hover:text-purple-700 font-medium">
          View All
        </button>
      </div>

      <div className="space-y-4">
        {activities.map((activity) => {
          const Icon = activity.icon
          return (
            <div key={activity.id} className="flex items-start space-x-3">
              <div className={`p-2 rounded-lg ${activity.color}`}>
                <Icon className="w-4 h-4" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {activity.message}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {activity.value}
                </p>
              </div>
              <span className="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">
                {activity.time}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
