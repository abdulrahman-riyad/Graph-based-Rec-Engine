// frontend/app/dashboard/components/RecommendationEngine.tsx
'use client'

import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { fetchCustomers, fetchRecommendations } from '@/lib/api'
import {
  Sparkles,
  User,
  Package,
  ArrowRight,
  RefreshCw,
  Settings,
  Info,
  Star,
  TrendingUp
} from 'lucide-react'

interface Customer {
  customer_id: string
  email?: string
  segment?: string
  lifetime_value: number
  purchase_count: number
}

interface Recommendation {
  sku: string
  title: string
  price: number
  category: string
  score: number
  confidence: number
  explanation?: string[]
}

export default function RecommendationEngine() {
  const [customers, setCustomers] = useState<Customer[]>([])
  const [selectedCustomer, setSelectedCustomer] = useState<string | null>(null)
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [loading, setLoading] = useState(false)
  const [algorithm, setAlgorithm] = useState('hybrid')
  const [showExplanations, setShowExplanations] = useState(true)

  useEffect(() => {
    loadCustomers()
  }, [])

  useEffect(() => {
    if (selectedCustomer) {
      generateRecommendations()
    }
  }, [selectedCustomer, algorithm])

  const loadCustomers = async () => {
    try {
      const data = await fetchCustomers(10)
      setCustomers(data)
      if (data.length > 0) {
        setSelectedCustomer(data[0].customer_id)
      }
    } catch (error) {
      console.error('Failed to load customers:', error)
    }
  }

  const generateRecommendations = async () => {
    if (!selectedCustomer) return

    setLoading(true)
    try {
      const data = await fetchRecommendations(selectedCustomer, algorithm, 6, showExplanations)
      setRecommendations(data)
    } catch (error) {
      console.error('Failed to generate recommendations:', error)
    } finally {
      setLoading(false)
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600'
    if (confidence >= 0.6) return 'text-yellow-600'
    return 'text-gray-600'
  }

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.8) return 'High'
    if (confidence >= 0.6) return 'Medium'
    return 'Low'
  }

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-800">Recommendation Engine</h2>
          <p className="text-sm text-gray-600 mt-1">AI-powered product recommendations</p>
        </div>
        <div className="flex items-center space-x-2">
          <Sparkles className="w-5 h-5 text-purple-600" />
          <span className="text-sm font-medium text-purple-600">AI Powered</span>
        </div>
      </div>

      {/* Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
        {/* Customer Selector */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Customer
          </label>
          <select
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={selectedCustomer || ''}
            onChange={(e) => setSelectedCustomer(e.target.value)}
          >
            <option value="">Choose a customer...</option>
            {customers.map((customer) => (
              <option key={customer.customer_id} value={customer.customer_id}>
                {customer.customer_id} - {customer.segment || 'Regular'}
                (LTV: ${customer.lifetime_value?.toFixed(0)})
              </option>
            ))}
          </select>
        </div>

        {/* Algorithm Selector */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Algorithm
          </label>
          <select
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={algorithm}
            onChange={(e) => setAlgorithm(e.target.value)}
          >
            <option value="hybrid">Hybrid (Best Performance)</option>
            <option value="collaborative">Collaborative Filtering</option>
            <option value="content">Content-Based</option>
            <option value="graph">Graph-Based</option>
            <option value="trending">Trending Products</option>
          </select>
        </div>

        {/* Options */}
        <div className="flex items-end space-x-2">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={showExplanations}
              onChange={(e) => setShowExplanations(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Show Explanations</span>
          </label>
          <button
            onClick={generateRecommendations}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </button>
        </div>
      </div>

      {/* Selected Customer Info */}
      {selectedCustomer && (
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <User className="w-5 h-5 text-gray-600 mr-2" />
              <div>
                <p className="font-medium text-gray-800">Customer: {selectedCustomer}</p>
                <p className="text-sm text-gray-600">
                  {customers.find(c => c.customer_id === selectedCustomer)?.segment || 'Regular'} Segment
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">Lifetime Value</p>
              <p className="font-semibold text-gray-800">
                ${customers.find(c => c.customer_id === selectedCustomer)?.lifetime_value?.toFixed(2)}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Recommendations */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="spinner mx-auto mb-4"></div>
            <p className="text-gray-600">Generating recommendations...</p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {recommendations.map((rec, index) => (
            <div key={index} className="border rounded-lg p-4 hover:shadow-lg transition-all">
              <div className="flex items-start justify-between mb-3">
                <Package className="w-8 h-8 text-gray-400" />
                <div className="flex items-center space-x-1">
                  <Star className="w-4 h-4 text-yellow-500" />
                  <span className="text-sm font-medium">{(rec.score * 5).toFixed(1)}</span>
                </div>
              </div>

              <h3 className="font-semibold text-gray-800 mb-1 line-clamp-2">
                {rec.title}
              </h3>
              <p className="text-sm text-gray-500 mb-2">{rec.category}</p>

              <div className="flex items-center justify-between mb-3">
                <span className="text-xl font-bold text-gray-800">
                  ${rec.price?.toFixed(2)}
                </span>
                <div className={`text-sm font-medium ${getConfidenceColor(rec.confidence)}`}>
                  {getConfidenceLabel(rec.confidence)} Confidence
                </div>
              </div>

              {/* Confidence Bar */}
              <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                <div
                  className={`h-2 rounded-full ${
                    rec.confidence >= 0.8 ? 'bg-green-500' :
                    rec.confidence >= 0.6 ? 'bg-yellow-500' : 'bg-gray-500'
                  }`}
                  style={{ width: `${rec.confidence * 100}%` }}
                />
              </div>

              {/* Explanations */}
              {showExplanations && rec.explanation && rec.explanation.length > 0 && (
                <div className="mt-3 pt-3 border-t">
                  <div className="flex items-start">
                    <Info className="w-4 h-4 text-gray-400 mr-2 mt-0.5 flex-shrink-0" />
                    <div className="text-xs text-gray-600 space-y-1">
                      {rec.explanation.slice(0, 2).map((exp, i) => (
                        <p key={i}>• {exp}</p>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              <button className="w-full mt-3 px-3 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition flex items-center justify-center">
                View Product
                <ArrowRight className="w-4 h-4 ml-2" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Algorithm Info */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <div className="flex items-start">
          <Settings className="w-5 h-5 text-blue-600 mr-2 mt-0.5" />
          <div>
            <p className="font-medium text-blue-900 mb-1">Algorithm: {algorithm}</p>
            <p className="text-sm text-blue-700">
              {algorithm === 'hybrid' && 'Combines multiple algorithms for best accuracy'}
              {algorithm === 'collaborative' && 'Based on similar customer preferences'}
              {algorithm === 'content' && 'Based on product features and attributes'}
              {algorithm === 'graph' && 'Uses graph relationships and patterns'}
              {algorithm === 'trending' && 'Shows currently popular products'}
            </p>
          </div>
        </div>
      </div>
    </Card>
  )
}