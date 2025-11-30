"""
Test script to verify vector normalization and cosine distance fixes.
Tests registration and identification with the new normalized embeddings.
"""

import requests
from pathlib import Path

API_URL = "http://localhost:8000"

print("\n" + "=" * 70)
print("Testing Vector Normalization & Cosine Distance Fixes")
print("=" * 70 + "\n")

# Test 1: Health check
print("1. Health Check...")
response = requests.get(f"{API_URL}/health")
data = response.json()
print(f"   Status: {data['status']}")
print(f"   Collection Loaded: {data['collection_loaded']}")
print(f"   Cattle Count: {data['cattle_count']}\n")

# Test 2: Register Bessie
print("2. Registering Bessie (cattle_0100)...")
with open("processed_results/cattle_0100_DSCF3856_enhanced.jpg", 'rb') as f:
    files = {'file': f}
    form_data = {'cow_name': 'Bessie'}
    response = requests.post(f"{API_URL}/register", files=files, data=form_data)
    
if response.status_code == 200:
    result = response.json()
    print(f"   SUCCESS! Cow ID: {result['cow_id'][:8]}...")
    print(f"   Name: {result['cow_name']}")
    print(f"   Vector Dimensions: {result['vector_dimensions']}\n")
else:
    print(f"   ERROR: {response.text}\n")
    exit(1)

# Test 3: Register Daisy
print("3. Registering Daisy (cattle_0200)...")
with open("processed_results/cattle_0200_DSCF3868_enhanced.jpg", 'rb') as f:
    files = {'file': f}
    form_data = {'cow_name': 'Daisy'}
    response = requests.post(f"{API_URL}/register", files=files, data=form_data)
    
if response.status_code == 200:
    result = response.json()
    print(f"   SUCCESS! Cow ID: {result['cow_id'][:8]}...")
    print(f"   Name: {result['cow_name']}\n")
else:
    print(f"   ERROR: {response.text}\n")
    exit(1)

# Test 4: Identify Bessie (different photo - should MATCH)
print("4. Identifying Bessie with different photo...")
print("   Image: cattle_0100_DSCF3858_enhanced.jpg")
with open("processed_results/cattle_0100_DSCF3858_enhanced.jpg", 'rb') as f:
    files = {'file': f}
    response = requests.post(f"{API_URL}/identify", files=files)
    
if response.status_code == 200:
    result = response.json()
    if result['match_found']:
        print(f"   ✓ MATCH! Identified as: {result['cow_name']}")
        print(f"   Confidence: {result['confidence']:.2f}%")
        print(f"   Distance: {result['distance']:.4f}")
        
        if result['cow_name'] == 'Bessie' and result['confidence'] > 75:
            print(f"   ✓ TEST PASSED - Correct identification with high confidence!\n")
        else:
            print(f"   X TEST FAILED - Wrong cow or low confidence\n")
    else:
        print(f"   X NO MATCH: {result.get('message', 'Unknown')}")
        print(f"   Confidence: {result.get('confidence', 0):.2f}%")
        print(f"   X TEST FAILED - Should have matched Bessie\n")
else:
    print(f"   ERROR: {response.text}\n")

# Test 5: Identify Daisy (different photo - should MATCH)
print("5. Identifying Daisy with different photo...")
print("   Image: cattle_0200_DSCF3870_enhanced.jpg")
with open("processed_results/cattle_0200_DSCF3870_enhanced.jpg", 'rb') as f:
    files = {'file': f}
    response = requests.post(f"{API_URL}/identify", files=files)
    
if response.status_code == 200:
    result = response.json()
    if result['match_found']:
        print(f"   ✓ MATCH! Identified as: {result['cow_name']}")
        print(f"   Confidence: {result['confidence']:.2f}%")
        print(f"   Distance: {result['distance']:.4f}")
        
        if result['cow_name'] == 'Daisy' and result['confidence'] > 75:
            print(f"   ✓ TEST PASSED - Correct identification with high confidence!\n")
        else:
            print(f"   X TEST FAILED - Wrong cow or low confidence\n")
    else:
        print(f"   X NO MATCH: {result.get('message', 'Unknown')}")
        print(f"   Confidence: {result.get('confidence', 0):.2f}%")
        print(f"   X TEST FAILED - Should have matched Daisy\n")
else:
    print(f"   ERROR: {response.text}\n")

# Test 6: Cross-identification (Bessie image, should NOT match Daisy)
print("6. Testing cross-identification (Bessie photo vs Daisy in DB)...")
print("   Expected: Should identify as Bessie, NOT Daisy")
with open("processed_results/cattle_0100_DSCF3859_enhanced.jpg", 'rb') as f:
    files = {'file': f}
    response = requests.post(f"{API_URL}/identify", files=files)
    
if response.status_code == 200:
    result = response.json()
    if result['match_found']:
        print(f"   Identified as: {result['cow_name']}")
        print(f"   Confidence: {result['confidence']:.2f}%")
        
        if result['cow_name'] == 'Bessie':
            print(f"   ✓ TEST PASSED - Correctly identified as Bessie!\n")
        else:
            print(f"   X TEST FAILED - Misidentified as {result['cow_name']}\n")
    else:
        print(f"   NO MATCH: {result.get('message', 'Unknown')}")
        print(f"   Confidence: {result.get('confidence', 0):.2f}%\n")
else:
    print(f"   ERROR: {response.text}\n")

# Final health check
print("7. Final Health Check...")
response = requests.get(f"{API_URL}/health")
data = response.json()
print(f"   Cattle Count: {data['cattle_count']}\n")

print("=" * 70)
print("Testing Complete!")
print("=" * 70)
print("\nSummary:")
print("- Vector normalization: APPLIED")
print("- Distance metric: COSINE")
print("- Confidence formula: (1 - distance) × 100")
print("- Threshold: 75%")
print("\nIf all tests passed, the 'Unknown Cow' issue is RESOLVED! ✓")
print("=" * 70)
