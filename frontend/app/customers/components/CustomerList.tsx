// ===========================================
// frontend/app/customers/components/CustomerList.tsx
// ===========================================
'use client'

import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { fetchCustomers } from '@/lib/api'
import { User, Mail, DollarSign, ShoppingBag } from 'lucide-react'

interface CustomerListProps {
  searchTerm: string
  segment: string
  onSelectCustomer: (customer: any) => void
}

export default function CustomerList({ searchTerm, segment, onSelectCustomer }: CustomerListProps) {
  const [customers, setCustomers] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadCustomers()
  }, [segment])

  const loadCustomers = async () => {
    try {
      const data = await fetchCustomers(50, 0, segment === 'all' ? undefined : segment)
      setCustomers(data)
    } catch (error) {
      console.error('Failed to load customers:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredCustomers = customers.filter(c =>
    c.customer_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.email?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading) {
    return (
      <Card className="p-6">
        <div className="text-center">Loading customers...</div>
      </Card>
    )
  }

  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold mb-4">Customer List</h2>

      <div className="space-y-3">
        {filteredCustomers.map((customer) => (
          <div
            key={customer.customer_id}
            onClick={() => onSelectCustomer(customer)}
            className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-blue-100 rounded-full">
                  <User className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <p className="font-medium">{customer.customer_id}</p>
                  <p className="text-sm text-gray-600">{customer.country || 'Unknown'}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-semibold">${customer.total_spent?.toFixed(2) || '0.00'}</p>
                <p className="text-sm text-gray-600">{customer.purchase_count || 0} orders</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}