"""
Quick test script to verify backend is working after cleanup
"""
import requests
import json

API_BASE = "http://localhost:8080"

def test_health():
    """Test health endpoint"""
    print("Testing /health...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        print(f"  Status: {response.status_code}")
        print(f"  Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_favorites():
    """Test favorites endpoint"""
    print("\nTesting /favorites...")
    try:
        response = requests.get(f"{API_BASE}/favorites", timeout=5)
        print(f"  Status: {response.status_code}")
        data = response.json()
        print(f"  Found {len(data)} tracked wallets")
        return response.status_code == 200
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_trades():
    """Test trades endpoint"""
    print("\nTesting /trades...")
    try:
        response = requests.get(f"{API_BASE}/trades?page=1&page_size=10", timeout=5)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Total results: {data.get('total_results', 0)}")
            print(f"  Items returned: {len(data.get('items', []))}")
        return response.status_code == 200
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_markets():
    """Test markets endpoint"""
    print("\nTesting /markets...")
    try:
        response = requests.get(f"{API_BASE}/markets", timeout=5)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Found {len(data)} distinct markets")
        return response.status_code == 200
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Backend API Test Suite")
    print("=" * 60)
    
    results = {
        "Health Check": test_health(),
        "Favorites": test_favorites(),
        "Trades": test_trades(),
        "Markets": test_markets()
    }
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(results.values())
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed! Backend is working correctly.")
    else:
        print("❌ Some tests failed. Check the backend logs.")
    print("=" * 60)

if __name__ == "__main__":
    main()
