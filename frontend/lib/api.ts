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
      console.error('API failed, using mock data. Check if backend is running on port 8000!')
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
  if (url?.includes('revenue')) {
    // Generate 30 days of revenue data
    const days = 30
    const data = []
    const baseRevenue = 5000

    for (let i = 0; i < days; i++) {
      const date = new Date()
      date.setDate(date.getDate() - (days - i))
      data.push({
        date: date.toISOString(),
        revenue: baseRevenue + Math.random() * 3000 + (i * 50),
        orders: Math.floor(50 + Math.random() * 30 + (i * 2)),
      })
    }

    return {
      total_revenue: 234500,
      order_count: 4567,
      avg_order_value: 51.23,
      growth_rate: 23.5,
      daily_revenue: data,
    }
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
  const params: any = {}
  if (startDate) params.start_date = startDate.toISOString()
  if (endDate) params.end_date = endDate.toISOString()

  return api.get('/analytics/revenue', { params })
}

export const fetchProducts = async (limit = 50, offset = 0, category?: string) => {
  const params: any = {
    limit,
    offset
  }
  if (category) params.category = category
  return api.get('/products', { params })
}

export const fetchCustomers = async (limit = 50, offset = 0, segment?: string) => {
  const params: any = {
    limit,
    offset
  }
  if (segment) params.segment = segment
  return api.get('/customers', { params })
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