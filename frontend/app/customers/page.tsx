// frontend/app/customers/page.tsx
'use client'

import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import CustomerList from './components/CustomerList'
import CustomerDetails from './components/CustomerDetails'
import CustomerSegmentation from './components/CustomerSegmentation'
import CustomerMetrics from './components/CustomerMetrics'
import { fetchCustomers, fetchCustomerSegments } from '@/lib/api'
import { Users, UserPlus, TrendingUp, Award } from 'lucide-react'

export default function CustomersPage() {
  const [selectedCustomer, setSelectedCustomer] = useState<any>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [segment, setSegment] = useState('all')
  const [metrics, setMetrics] = useState<any>(null)

  useEffect(() => {
    loadMetrics()
  }, [])

  const loadMetrics = async () => {
    try {
      const segments = await fetchCustomerSegments()
      const totalCustomers = segments.reduce((sum: number, seg: any) => sum + seg.customer_count, 0)
      setMetrics({
        total: totalCustomers,
        new_this_month: Math.floor(totalCustomers * 0.08),
        active_rate: 68.5,
        retention_rate: 85.2
      })
    } catch (error) {
      console.error('Failed to load metrics:', error)
    }
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Customer Management</h1>
        <p className="text-gray-600 mt-2">Manage and analyze your customer base</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Customers</p>
              <p className="text-2xl font-bold">{metrics?.total?.toLocaleString() || '0'}</p>
            </div>
            <Users className="w-8 h-8 text-blue-600" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">New This Month</p>
              <p className="text-2xl font-bold">{metrics?.new_this_month || '0'}</p>
            </div>
            <UserPlus className="w-8 h-8 text-green-600" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Active Rate</p>
              <p className="text-2xl font-bold">{metrics?.active_rate || '0'}%</p>
            </div>
            <TrendingUp className="w-8 h-8 text-purple-600" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Retention Rate</p>
              <p className="text-2xl font-bold">{metrics?.retention_rate || '0'}%</p>
            </div>
            <Award className="w-8 h-8 text-orange-600" />
          </div>
        </Card>
      </div>

      {/* Search and Filters */}
      <div className="flex gap-4 mb-6">
        <input
          type="text"
          placeholder="Search customers..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <select
          value={segment}
          onChange={(e) => setSegment(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="all">All Segments</option>
          <option value="champions">Champions</option>
          <option value="loyal">Loyal Customers</option>
          <option value="potential">Potential Loyalists</option>
          <option value="new">New Customers</option>
          <option value="at_risk">At Risk</option>
        </select>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <CustomerList
            searchTerm={searchTerm}
            segment={segment}
            onSelectCustomer={setSelectedCustomer}
          />
        </div>
        <div className="space-y-6">
          {selectedCustomer ? (
            <CustomerDetails customer={selectedCustomer} />
          ) : (
            <CustomerSegmentation />
          )}
          <CustomerMetrics customerId={selectedCustomer?.customer_id} />
        </div>
      </div>
    </div>
  )
}