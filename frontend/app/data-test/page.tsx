// frontend/app/data-test/page.tsx
'use client'

import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'

export default function DataTestPage() {
  const [backendData, setBackendData] = useState<any>(null)
  const [apiData, setApiData] = useState<any>(null)
  const [error, setError] = useState<string>('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Test direct backend call
    fetch('http://localhost:8000/api/v1/analytics/dashboard-summary')
      .then(res => res.json())
      .then(data => {
        setBackendData(data)
      })
      .catch(err => {
        setError('Direct backend call failed: ' + err.toString())
      })

    // Test through API wrapper
    import('@/lib/api').then(({ fetchDashboardSummary }) => {
      fetchDashboardSummary()
        .then(data => {
          setApiData(data)
          setLoading(false)
        })
        .catch(err => {
          setError(prev => prev + '\nAPI wrapper call failed: ' + err.toString())
          setLoading(false)
        })
    })
  }, [])

  const isRealData = (data: any) => {
    return data && data.total_customers > 0 && !data.database_status
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Data Connection Test</h1>

      {error && (
        <Card className="p-4 mb-4 bg-red-50 border-red-200">
          <h3 className="font-semibold text-red-800">Errors:</h3>
          <pre className="text-sm text-red-600 whitespace-pre-wrap">{error}</pre>
        </Card>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Direct Backend Call</h2>
          {backendData ? (
            <>
              <div className={`mb-4 p-2 rounded ${isRealData(backendData) ? 'bg-green-100' : 'bg-yellow-100'}`}>
                <p className="font-semibold">
                  {isRealData(backendData) ? '✅ Real Data' : '⚠️ Mock or Empty Data'}
                </p>
              </div>
              <pre className="bg-gray-100 p-3 rounded text-xs overflow-auto">
                {JSON.stringify(backendData, null, 2)}
              </pre>
            </>
          ) : (
            <p className="text-gray-500">No data received</p>
          )}
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">API Wrapper Call</h2>
          {apiData ? (
            <>
              <div className={`mb-4 p-2 rounded ${isRealData(apiData) ? 'bg-green-100' : 'bg-yellow-100'}`}>
                <p className="font-semibold">
                  {isRealData(apiData) ? '✅ Real Data' : '⚠️ Mock or Empty Data'}
                </p>
              </div>
              <pre className="bg-gray-100 p-3 rounded text-xs overflow-auto">
                {JSON.stringify(apiData, null, 2)}
              </pre>
            </>
          ) : (
            <p className="text-gray-500">{loading ? 'Loading...' : 'No data received'}</p>
          )}
        </Card>
      </div>

      <Card className="mt-6 p-6">
        <h2 className="text-xl font-semibold mb-4">Troubleshooting Guide</h2>
        <ol className="space-y-2 text-sm">
          <li>1. ✅ Ensure backend is running: <code className="bg-gray-100 px-2 py-1 rounded">cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000</code></li>
          <li>2. ✅ Check backend directly: <a href="http://localhost:8000/api/v1/analytics/dashboard-summary" target="_blank" className="text-blue-600 underline">http://localhost:8000/api/v1/analytics/dashboard-summary</a></li>
          <li>3. ✅ If showing zeros, load data: <code className="bg-gray-100 px-2 py-1 rounded">python enhanced_data_loader.py</code></li>
          <li>4. ✅ Clear browser cache: Ctrl+Shift+R</li>
          <li>5. ✅ Check DevTools Console for errors (F12)</li>
        </ol>
      </Card>
    </div>
  )
}
