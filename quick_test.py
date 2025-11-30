"""Quick test to verify normalization fixes."""
import requests

API_URL = "http://localhost:8000"

# Test health
print("Testing API...")
try:
    r = requests.get(f"{API_URL}/health", timeout=2)
    print(f"Health: {r.json()}")
    
    # Test register
    print("\nRegistering test cow...")
    with open("processed_results/cattle_0100_DSCF3856_enhanced.jpg", 'rb') as f:
        files = {'file': ('test.jpg', f, 'image/jpeg')}
        data = {'cow_name': 'TestBessie'}
        r = requests.post(f"{API_URL}/register", files=files, data=data, timeout=10)
        print(f"Register status: {r.status_code}")
        if r.status_code == 200:
            print(f"Result: {r.json()}")
        else:
            print(f"Error: {r.text}")
            
except Exception as e:
    print(f"Error: {e}")
