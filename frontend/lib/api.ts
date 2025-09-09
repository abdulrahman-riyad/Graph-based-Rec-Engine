// ============================================
// frontend/lib/api.ts
// ============================================
import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds timeout
})

// Add request interceptor for error handling
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    // Return mock data if API fails
    if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
      console.log('API unavailable, returning mock data')
      return Promise.resolve(getMockData(error.config.url))
    }
    return Promise.reject(error)
  }
)

// Mock data fallback
const getMockData = (url: string) => {
  if (url?.includes('dashboard-summary')) {
    return {
      total_customers: 12543,
      total_products: 3421,
      total_purchases: 45632,
      total_revenue: 2456789,
      revenue_30d: 245678,
      revenue_growth_30d: 23.5,
      active_customers_30d: 3456,
      new_customers_30d: 234,
      database_status: 'operational',
    }
  }
  if (url?.includes('customer-segments')) {
    return [
      { segment_name: 'Champions', customer_count: 2450, percentage: 24.5 },
      { segment_name: 'Loyal', customer_count: 3200, percentage: 32 },
      { segment_name: 'Potential', customer_count: 1800, percentage: 18 },
    ]
  }
  return []
}

// API functions
export const fetchDashboardSummary = async () => {
  return api.get('/analytics/dashboard-summary')
}

export const fetchCustomerSegments = async () => {
  return api.get('/analytics/customer-segments')
}

export const fetchRevenueAnalytics = async (startDate?: Date, endDate?: Date) => {
  return api.post('/analytics/revenue', {
    start_date: startDate?.toISOString(),
    end_date: endDate?.toISOString()
  })
}

export const fetchProducts = async (limit = 50, offset = 0, category?: string) => {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset)
  })
  if (category) params.append('category', category)
  return api.get(`/products?${params}`)
}

export const fetchCustomers = async (limit = 50, offset = 0, segment?: string) => {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset)
  })
  if (segment) params.append('segment', segment)
  return api.get(`/customers?${params}`)
}

export const fetchRecommendations = async (
  customerId: string,
  algorithm = 'hybrid',
  limit = 10,
  includeExplanation = false
) => {
  return api.post('/recommendations', {
    customer_id: customerId,
    algorithm,
    limit,
    include_explanation: includeExplanation
  })
}

export const checkHealth = async () => {
  return api.get('/health')
}

export default api