// ============================================
// frontend/components/dashboard/RecommendationEngine.tsx
// ============================================
'use client'

import { useState } from 'react'
import { Sparkles, Brain, Zap, RefreshCw, Settings, ChevronRight } from 'lucide-react'

const mockRecommendations = [
  {
    id: 1,
    product: 'Smart Watch Pro',
    customer: 'John Doe',
    score: 0.92,
    reason: 'Based on purchase history',
    price: 299.99,
    category: 'Electronics'
  },
  {
    id: 2,
    product: 'Running Shoes Elite',
    customer: 'Jane Smith',
    score: 0.88,
    reason: 'Frequently viewed similar items',
    price: 149.99,
    category: 'Sports'
  },
  {
    id: 3,
    product: 'Coffee Maker Deluxe',
    customer: 'Mike Johnson',
    score: 0.85,
    reason: 'Popular in customer segment',
    price: 89.99,
    category: 'Home'
  }
]

export default function RecommendationEngine() {
  const [algorithm, setAlgorithm] = useState('hybrid')
  const [loading, setLoading] = useState(false)

  const handleRefresh = () => {
    setLoading(true)
    setTimeout(() => setLoading(false), 1000)
  }

  return (
    <div className="bg-gradient-to-br from-purple-900 via-purple-800 to-pink-800 rounded-xl shadow-lg p-6 text-white">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-3 bg-white/10 backdrop-blur rounded-lg">
            <Brain className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold">AI Recommendation Engine</h2>
            <p className="text-sm text-purple-200">Powered by advanced ML algorithms</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <select
            className="px-3 py-2 bg-white/10 backdrop-blur border border-white/20 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-white/50"
            value={algorithm}
            onChange={(e) => setAlgorithm(e.target.value)}
          >
            <option value="hybrid">Hybrid Algorithm</option>
            <option value="collaborative">Collaborative</option>
            <option value="content">Content-Based</option>
            <option value="graph">Graph-Based</option>
          </select>
          <button
            onClick={handleRefresh}
            className={`p-2 bg-white/10 backdrop-blur rounded-lg hover:bg-white/20 transition ${
              loading ? 'animate-spin' : ''
            }`}
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button className="p-2 bg-white/10 backdrop-blur rounded-lg hover:bg-white/20 transition">
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {mockRecommendations.map((rec) => (
          <div
            key={rec.id}
            className="bg-white/10 backdrop-blur rounded-lg p-4 hover:bg-white/20 transition-all cursor-pointer group"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="p-2 bg-white/10 rounded-lg">
                <Sparkles className="w-5 h-5" />
              </div>
              <div className="text-right">
                <div className="text-xs text-purple-200">Confidence</div>
                <div className="text-lg font-bold">{(rec.score * 100).toFixed(0)}%</div>
              </div>
            </div>

            <h3 className="font-semibold mb-1">{rec.product}</h3>
            <p className="text-sm text-purple-200 mb-2">For: {rec.customer}</p>
            <p className="text-xs text-purple-300 mb-3">{rec.reason}</p>

            <div className="flex items-center justify-between">
              <span className="text-lg font-bold">${rec.price}</span>
              <ChevronRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 p-4 bg-white/5 backdrop-blur rounded-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Zap className="w-5 h-5 text-yellow-400" />
            <div>
              <p className="text-sm font-semibold">Performance Metrics</p>
              <p className="text-xs text-purple-200">Last updated: 2 minutes ago</p>
            </div>
          </div>
          <div className="flex space-x-6 text-sm">
            <div>
              <span className="text-purple-200">Accuracy:</span>
              <span className="font-bold ml-1">94.2%</span>
            </div>
            <div>
              <span className="text-purple-200">CTR:</span>
              <span className="font-bold ml-1">12.5%</span>
            </div>
            <div>
              <span className="text-purple-200">Conversion:</span>
              <span className="font-bold ml-1">8.3%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
