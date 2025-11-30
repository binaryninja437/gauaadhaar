"""Simple test for ChromaDB API endpoints."""

import requests

API_URL = "http://localhost:8000"

print("\n" + "=" * 70)
print("Testing ChromaDB Integration")
print("=" * 70 + "\n")

# Test 1: Health check
print("1. Health Check...")
response = requests.get(f"{API_URL}/health")
data = response.json()
print(f"   Status: {data['status']}")
print(f"   Collection Loaded: {data['collection_loaded']}")
print(f"   Cattle Count: {data['cattle_count']}\n")

# Test 2: Register Bessie
print("2. Registering Bessie...")
with open("processed_results/cattle_0100_DSCF3856_enhanced.jpg", 'rb') as f:
    files = {'file': f}
    form_data = {'cow_name': 'Bessie'}
    response = requests.post(f"{API_URL}/register", files=files, data=form_data)
    
if response.status_code == 200:
    result = response.json()
    print(f"   SUCCESS! Cow ID: {result['cow_id']}")
    print(f"   Name: {result['cow_name']}")
    print(f"   Dimensions: {result['vector_dimensions']}\n")
else:
    print(f"   ERROR: {response.text}\n")

# Test 3: Register Daisy
print("3. Registering Daisy...")
with open("processed_results/cattle_0200_DSCF3868_enhanced.jpg", 'rb') as f:
    files = {'file': f}
    form_data = {'cow_name': 'Daisy'}
    response = requests.post(f"{API_URL}/register", files=files, data=form_data)
    
if response.status_code == 200:
    result = response.json()
    print(f"   SUCCESS! Cow ID: {result['cow_id']}")
    print(f"   Name: {result['cow_name']}\n")
else:
    print(f"   ERROR: {response.text}\n")

# Test 4: Identify Bessie
print("4. Identifying Bessie (different photo)...")
with open("processed_results/cattle_0100_DSCF3858_enhanced.jpg", 'rb') as f:
    files = {'file': f}
    response = requests.post(f"{API_URL}/identify", files=files)
    
if response.status_code == 200:
    result = response.json()
    if result['match_found']:
        print(f"   MATCH! Identified as: {result['cow_name']}")
        print(f"   Confidence: {result['confidence']:.4f}")
        print(f"   Distance: {result['distance']:.4f}\n")
    else:
        print(f"   NO MATCH: {result.get('message', 'Unknown')}\n")
else:
    print(f"   ERROR: {response.text}\n")

# Test 5: Identify Daisy
print("5. Identifying Daisy (different photo)...")
with open("processed_results/cattle_0200_DSCF3870_enhanced.jpg", 'rb') as f:
    files = {'file': f}
    response = requests.post(f"{API_URL}/identify", files=files)
    
if response.status_code == 200:
    result = response.json()
    if result['match_found']:
        print(f"   MATCH! Identified as: {result['cow_name']}")
        print(f"   Confidence: {result['confidence']:.4f}")
        print(f"   Distance: {result['distance']:.4f}\n")
    else:
        print(f"   NO MATCH: {result.get('message', 'Unknown')}\n")
else:
    print(f"   ERROR: {response.text}\n")

# Final health check
print("6. Final Health Check...")
response = requests.get(f"{API_URL}/health")
data = response.json()
print(f"   Cattle Count: {data['cattle_count']}\n")

print("=" * 70)
print("Tests Complete!")
print("=" * 70)
