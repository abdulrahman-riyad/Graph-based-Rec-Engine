// frontend/lib/api.ts
import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Dashboard
export const fetchDashboardSummary = async () => {
  const response = await api.get('/analytics/dashboard-summary')
  return response.data
}

// Analytics
export const fetchCustomerSegments = async () => {
  const response = await api.get('/analytics/customer-segments')
  return response.data
}

export const fetchRevenueAnalytics = async (startDate?: Date, endDate?: Date) => {
  const response = await api.post('/analytics/revenue', {
    start_date: startDate?.toISOString(),
    end_date: endDate?.toISOString()
  })
  return response.data
}

export const fetchBasketAnalysis = async () => {
  const response = await api.get('/analytics/basket-analysis')
  return response.data
}

export const fetchProductPerformance = async (sku: string) => {
  const response = await api.get(`/analytics/product/${sku}/performance`)
  return response.data
}

// Products
export const fetchProducts = async (limit = 50, offset = 0, category?: string) => {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset)
  })
  if (category) params.append('category', category)

  const response = await api.get(`/products?${params}`)
  return response.data
}

export const fetchProduct = async (sku: string) => {
  const response = await api.get(`/products/${sku}`)
  return response.data
}

export const fetchSimilarProducts = async (sku: string, limit = 10) => {
  const response = await api.get(`/products/${sku}/similar?limit=${limit}`)
  return response.data
}

export const fetchProductReviews = async (sku: string, limit = 20, offset = 0) => {
  const response = await api.get(`/products/${sku}/reviews?limit=${limit}&offset=${offset}`)
  return response.data
}

// Customers
export const fetchCustomers = async (limit = 50, offset = 0, segment?: string) => {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset)
  })
  if (segment) params.append('segment', segment)

  const response = await api.get(`/customers?${params}`)
  return response.data
}

export const fetchCustomer = async (id: string) => {
  const response = await api.get(`/customers/${id}`)
  return response.data
}

export const fetchCustomerPurchaseHistory = async (id: string, limit = 20, offset = 0) => {
  const response = await api.get(`/customers/${id}/purchase-history?limit=${limit}&offset=${offset}`)
  return response.data
}

export const fetchCustomerAnalytics = async (id: string) => {
  const response = await api.get(`/customers/${id}/analytics`)
  return response.data
}

// Recommendations
export const fetchRecommendations = async (
  customerId: string,
  algorithm = 'hybrid',
  limit = 10,
  includeExplanation = false
) => {
  const response = await api.post('/recommendations', {
    customer_id: customerId,
    algorithm,
    limit,
    include_explanation: includeExplanation
  })
  return response.data
}

export const fetchPopularProducts = async (limit = 10, category?: string) => {
  const params = new URLSearchParams({ limit: String(limit) })
  if (category) params.append('category', category)

  const response = await api.get(`/recommendations/popular?${params}`)
  return response.data
}

export const fetchTrendingProducts = async (limit = 10, days = 7) => {
  const response = await api.get(`/recommendations/trending?limit=${limit}&days=${days}`)
  return response.data
}

export const fetchCrossSellProducts = async (productSku: string, limit = 5) => {
  const response = await api.post('/recommendations/cross-sell', {
    product_sku: productSku
  }, {
    params: { limit }
  })
  return response.data
}

// Health Check
export const checkHealth = async () => {
  const response = await api.get('/health')
  return response.data
}

export default api