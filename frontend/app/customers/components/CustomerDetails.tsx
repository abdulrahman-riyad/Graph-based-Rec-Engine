// ===========================================
// frontend/app/customers/components/CustomerDetails.tsx
// ===========================================
'use client'

import { Card } from '@/components/ui/card'
import { User, Mail, MapPin, Calendar, DollarSign, ShoppingBag } from 'lucide-react'

interface CustomerDetailsProps {
  customer: any
}

export default function CustomerDetails({ customer }: CustomerDetailsProps) {
  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">Customer Details</h3>

      <div className="space-y-4">
        <div className="flex items-center space-x-3">
          <User className="w-5 h-5 text-gray-400" />
          <div>
            <p className="text-sm text-gray-600">Customer ID</p>
            <p className="font-medium">{customer.customer_id}</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <MapPin className="w-5 h-5 text-gray-400" />
          <div>
            <p className="text-sm text-gray-600">Country</p>
            <p className="font-medium">{customer.country || 'Unknown'}</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <DollarSign className="w-5 h-5 text-gray-400" />
          <div>
            <p className="text-sm text-gray-600">Total Spent</p>
            <p className="font-medium">${customer.total_spent?.toFixed(2) || '0.00'}</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <ShoppingBag className="w-5 h-5 text-gray-400" />
          <div>
            <p className="text-sm text-gray-600">Total Orders</p>
            <p className="font-medium">{customer.purchase_count || 0}</p>
          </div>
        </div>

        <div className="pt-4 border-t">
          <p className="text-sm text-gray-600 mb-2">Segment</p>
          <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
            {customer.segment || 'Regular'}
          </span>
        </div>
      </div>
    </Card>
  )
}