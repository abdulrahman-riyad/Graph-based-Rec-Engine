// ===========================================
// frontend/app/analytics/components/RevenueMetrics.tsx
// ===========================================
'use client'

import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { fetchRevenueAnalytics } from '@/lib/api'
import { TrendingUp, DollarSign } from 'lucide-react'

interface RevenueMetricsProps {
  timeRange: string
}

export default function RevenueMetrics({ timeRange }: RevenueMetricsProps) {
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadRevenue()
  }, [timeRange])

  const loadRevenue = async () => {
    try {
      const days = parseInt(timeRange) || 30
      const endDate = new Date()
      const startDate = new Date()
      startDate.setDate(startDate.getDate() - days)

      const response = await fetchRevenueAnalytics(startDate, endDate)

      if (response?.daily_breakdown) {
        const chartData = response.daily_breakdown.dates.map((date: string, i: number) => ({
          date: new Date(date).toLocaleDateString('en', { month: 'short', day: 'numeric' }),
          revenue: response.daily_breakdown.revenues[i] || 0
        }))
        setData(chartData)
      }
    } catch (error) {
      console.error('Failed to load revenue:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Revenue Trends</h3>
        <DollarSign className="w-5 h-5 text-green-600" />
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="revenue" stroke="#10B981" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  )
}