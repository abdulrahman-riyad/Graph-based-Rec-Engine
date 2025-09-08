# scripts/test_endpoints.py
"""
Test script to verify all API endpoints are working
"""

import requests
import json
from datetime import datetime, timedelta
from colorama import init, Fore, Style

init()

BASE_URL = "http://localhost:8000/api/v1"


def test_endpoint(name, method, endpoint, data=None):
    """Test a single endpoint"""
    print(f"\n{Fore.YELLOW}Testing: {name}{Style.RESET_ALL}")
    print(f"  Endpoint: {method} {endpoint}")

    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}")
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        else:
            print(f"  {Fore.RED}✗ Unsupported method{Style.RESET_ALL}")
            return False

        if response.status_code == 200:
            print(f"  {Fore.GREEN}✓ Success (200){Style.RESET_ALL}")

            # Show sample response
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print(f"  Response: {len(data)} items")
                print(f"  Sample: {json.dumps(data[0], indent=2)[:200]}...")
            elif isinstance(data, dict):
                print(f"  Response keys: {list(data.keys())}")

            return True
        else:
            print(f"  {Fore.RED}✗ Failed ({response.status_code}){Style.RESET_ALL}")
            print(f"  Error: {response.text[:200]}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"  {Fore.RED}✗ Connection failed - Is the backend running?{Style.RESET_ALL}")
        return False
    except Exception as e:
        print(f"  {Fore.RED}✗ Error: {e}{Style.RESET_ALL}")
        return False


def main():
    print(f"{Fore.CYAN}{'=' * 60}")
    print("E-COMMERCE API ENDPOINT TESTER")
    print(f"{'=' * 60}{Style.RESET_ALL}")

    # Track results
    results = []

    # Test Health Check
    results.append(test_endpoint(
        "Health Check",
        "GET",
        "/health"
    ))

    # Test Analytics Endpoints
    results.append(test_endpoint(
        "Dashboard Summary",
        "GET",
        "/analytics/dashboard-summary"
    ))

    results.append(test_endpoint(
        "Customer Segments",
        "GET",
        "/analytics/customer-segments"
    ))

    results.append(test_endpoint(
        "Revenue Analytics",
        "POST",
        "/analytics/revenue",
        {
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": datetime.now().isoformat()
        }
    ))

    results.append(test_endpoint(
        "Basket Analysis",
        "GET",
        "/analytics/basket-analysis"
    ))

    # Test Product Endpoints
    results.append(test_endpoint(
        "Get Products",
        "GET",
        "/products?limit=5"
    ))

    # Test Customer Endpoints
    results.append(test_endpoint(
        "Get Customers",
        "GET",
        "/customers?limit=5"
    ))

    # Test Recommendation Endpoints
    results.append(test_endpoint(
        "Popular Products",
        "GET",
        "/recommendations/popular?limit=5"
    ))

    # Get a sample customer for recommendation test
    try:
        customers_response = requests.get(f"{BASE_URL}/customers?limit=1")
        if customers_response.status_code == 200:
            customers = customers_response.json()
            if customers and len(customers) > 0:
                customer_id = customers[0]['customer_id']

                results.append(test_endpoint(
                    f"Recommendations for {customer_id}",
                    "POST",
                    "/recommendations",
                    {
                        "customer_id": customer_id,
                        "algorithm": "hybrid",
                        "limit": 5,
                        "include_explanation": True
                    }
                ))
    except:
        print(f"{Fore.YELLOW}  Skipping customer recommendation test{Style.RESET_ALL}")

    # Summary
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print("TEST SUMMARY")
    print(f"{'=' * 60}{Style.RESET_ALL}")

    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"{Fore.GREEN}✓ All tests passed! ({passed}/{total}){Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠ {passed}/{total} tests passed{Style.RESET_ALL}")
        print(f"{Fore.RED}✗ {total - passed} tests failed{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}API Documentation available at: {Fore.WHITE}http://localhost:8000/docs{Style.RESET_ALL}")


if __name__ == "__main__":
    main()