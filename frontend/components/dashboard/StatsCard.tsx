// ============================================
// frontend/components/dashboard/StatsCard.tsx
// ============================================
import { LucideIcon } from 'lucide-react'

interface StatsCardProps {
  title: string
  value: string
  change: string
  icon: LucideIcon
  color: string
  trend: 'up' | 'down'
}

export default function StatsCard({ title, value, change, icon: Icon, color, trend }: StatsCardProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm hover-lift border border-gray-200 dark:border-gray-700">
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className={`p-3 rounded-lg bg-gradient-to-r ${color}`}>
            <Icon className="w-6 h-6 text-white" />
          </div>
          <span className={`text-sm font-semibold ${
            trend === 'up' ? 'text-green-600' : 'text-red-600'
          }`}>
            {change}
          </span>
        </div>
        <h3 className="text-2xl font-bold text-gray-900 dark:text-white">{value}</h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{title}</p>
      </div>
    </div>
  )
}