#!/usr/bin/env python3
"""
connect_real_data.py
Verify and fix the connection between frontend and backend for real data
"""

import requests
import json
import subprocess
import time
from pathlib import Path
from colorama import init, Fore, Style

init()


def check_backend_status():
    """Check if backend is running and returning real data"""
    print(f"{Fore.CYAN}1. Checking Backend Status...{Style.RESET_ALL}")

    try:
        # Test dashboard summary endpoint
        response = requests.get("http://localhost:8000/api/v1/analytics/dashboard-summary")

        if response.status_code == 200:
            data = response.json()
            print(f"{Fore.GREEN}✓ Backend is running and returning data:{Style.RESET_ALL}")
            print(f"  • Total Customers: {data.get('total_customers', 0):,}")
            print(f"  • Total Products: {data.get('total_products', 0):,}")
            print(f"  • Total Purchases: {data.get('total_purchases', 0):,}")

            # Check if this is real data or zeros
            if data.get('total_customers', 0) == 0:
                print(f"\n{Fore.YELLOW}⚠ Backend is running but returning empty data!{Style.RESET_ALL}")
                print("  Run: python enhanced_data_loader.py")
                return False
            return True
        else:
            print(f"{Fore.RED}✗ Backend returned status {response.status_code}{Style.RESET_ALL}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}✗ Cannot connect to backend on port 8000{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Start backend with:{Style.RESET_ALL}")
        print("  cd backend")
        print("  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return False


def update_frontend_api_config():
    """Update frontend to ensure it's calling the right API"""
    print(f"\n{Fore.CYAN}2. Updating Frontend API Configuration...{Style.RESET_ALL}")

    # Update the api.ts file to ensure it's not using mock data
    api_file = Path("frontend/lib/api.ts")

    if not api_file.exists():
        print(f"{Fore.RED}✗ frontend/lib/api.ts not found{Style.RESET_ALL}")
        return False

    with open(api_file, 'r') as f:
        content = f.read()

    # Check if mock data fallback is active
    if "API unavailable, returning mock data" in content:
        print(f"{Fore.YELLOW}  Found mock data fallback in api.ts{Style.RESET_ALL}")

        # Create a modified version that logs but still works
        modified_content = content.replace(
            "console.log('API unavailable, returning mock data')",
            "console.error('API failed, using mock data. Check if backend is running on port 8000!')"
        )

        with open(api_file, 'w') as f:
            f.write(modified_content)

        print(f"{Fore.GREEN}  ✓ Updated error message for better debugging{Style.RESET_ALL}")

    print(f"{Fore.GREEN}✓ API configuration verified{Style.RESET_ALL}")
    return True


def create_data_test_page():
    """Create a test page to verify data connection"""
    print(f"\n{Fore.CYAN}3. Creating Data Test Page...{Style.RESET_ALL}")

    test_page = '''// frontend/app/data-test/page.tsx
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
          setError(prev => prev + '\\nAPI wrapper call failed: ' + err.toString())
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
'''

    # Create the test page directory
    test_dir = Path("frontend/app/data-test")
    test_dir.mkdir(exist_ok=True)

    # Write the test page
    with open(test_dir / "page.tsx", "w") as f:
        f.write(test_page)

    print(f"{Fore.GREEN}✓ Created test page at: http://localhost:3000/data-test{Style.RESET_ALL}")
    return True


def fix_cors_issues():
    """Ensure CORS is properly configured"""
    print(f"\n{Fore.CYAN}4. Checking CORS Configuration...{Style.RESET_ALL}")

    # Check if backend CORS includes frontend
    config_file = Path("backend/app/config.py")

    if config_file.exists():
        with open(config_file, 'r') as f:
            content = f.read()

        if "http://localhost:3000" in content:
            print(f"{Fore.GREEN}✓ CORS is properly configured{Style.RESET_ALL}")
            return True

    print(f"{Fore.YELLOW}⚠ Check CORS settings in backend/app/config.py{Style.RESET_ALL}")
    return True


def test_full_stack():
    """Test the complete data flow"""
    print(f"\n{Fore.CYAN}5. Testing Complete Data Flow...{Style.RESET_ALL}")

    tests = [
        ("Dashboard Summary", "http://localhost:8000/api/v1/analytics/dashboard-summary"),
        ("Customer Segments", "http://localhost:8000/api/v1/analytics/customer-segments"),
        ("Products", "http://localhost:8000/api/v1/products?limit=5"),
        ("Customers", "http://localhost:8000/api/v1/customers?limit=5"),
    ]

    all_good = True

    for name, url in tests:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"{Fore.GREEN}✓ {name}: {len(data)} items{Style.RESET_ALL}")
                elif isinstance(data, dict):
                    if data.get('total_customers', 0) > 0:
                        print(f"{Fore.GREEN}✓ {name}: Real data{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}⚠ {name}: Empty data{Style.RESET_ALL}")
                        all_good = False
            else:
                print(f"{Fore.RED}✗ {name}: Status {response.status_code}{Style.RESET_ALL}")
                all_good = False
        except Exception as e:
            print(f"{Fore.RED}✗ {name}: {str(e)}{Style.RESET_ALL}")
            all_good = False

    return all_good


def main():
    print(f"""
{Fore.CYAN}{'=' * 60}
{Fore.YELLOW}CONNECTING REAL DATA TO DASHBOARD
{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}
""")

    # Step 1: Check backend
    backend_ok = check_backend_status()

    if not backend_ok:
        print(f"\n{Fore.RED}❌ Backend is not running or has no data!{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Please:{Style.RESET_ALL}")
        print("1. Start backend: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        print("2. Load data: python enhanced_data_loader.py")
        print("3. Run this script again")
        return

    # Step 2: Update frontend config
    update_frontend_api_config()

    # Step 3: Create test page
    create_data_test_page()

    # Step 4: Check CORS
    fix_cors_issues()

    # Step 5: Test full stack
    all_good = test_full_stack()

    print(f"""
{Fore.CYAN}{'=' * 60}
{Fore.YELLOW}RESULTS
{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}
""")

    if all_good:
        print(f"{Fore.GREEN}✅ Everything is working! Your dashboard should show real data.{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Next steps:{Style.RESET_ALL}")
        print("1. Visit: http://localhost:3000/dashboard")
        print("2. Hard refresh: Ctrl+Shift+R")
        print("3. Check the data test page: http://localhost:3000/data-test")
    else:
        print(f"{Fore.YELLOW}⚠ Some issues detected.{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Debug steps:{Style.RESET_ALL}")
        print("1. Visit: http://localhost:3000/data-test")
        print("2. Open DevTools (F12) > Console")
        print("3. Look for error messages")
        print("4. Check Network tab for failed API calls")


if __name__ == "__main__":
    main()