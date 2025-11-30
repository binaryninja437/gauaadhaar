"""
Test script for ChromaDB-integrated API endpoints.
Tests /register and /identify endpoints with actual cattle images.
"""

import requests
from pathlib import Path

API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint to verify ChromaDB is loaded."""
    print("=" * 70)
    print("TEST 1: Health Check")
    print("=" * 70)
    
    response = requests.get(f"{API_URL}/health")
    data = response.json()
    
    print(f"Status: {data['status']}")
    print(f"Model Loaded: {data['model_loaded']}")
    print(f"Collection Loaded: {data['collection_loaded']}")
    print(f"Cattle Count: {data['cattle_count']}")
    print()
    
    return data['collection_loaded']


def test_register(image_path, cow_name):
    """Test registration endpoint."""
    print("=" * 70)
    print(f"TEST 2: Register Cow - {cow_name}")
    print("=" * 70)
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        data = {'cow_name': cow_name}
        response = requests.post(f"{API_URL}/register", files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Status: {result['status']}")
        print(f"   Cow ID: {result['cow_id']}")
        print(f"   Cow Name: {result['cow_name']}")
        print(f"   Vector Dimensions: {result['vector_dimensions']}")
        print()
        return result
    else:
        print(f"❌ Error: {response.text}")
        print()
        return None


def test_identify(image_path, expected_name=None):
    """Test identification endpoint."""
    print("=" * 70)
    print(f"TEST 3: Identify Cow")
    print("=" * 70)
    print(f"Image: {Path(image_path).name}")
    if expected_name:
        print(f"Expected: {expected_name}")
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{API_URL}/identify", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nMatch Found: {result['match_found']}")
        
        if result['match_found']:
            print(f"✅ Identified as: {result['cow_name']}")
            print(f"   Confidence: {result['confidence']:.4f}")
            print(f"   Distance: {result['distance']:.4f}")
            
            if expected_name and result['cow_name'] == expected_name:
                print(f"   ✅ CORRECT! Matched expected cow.")
            elif expected_name:
                print(f"   ❌ WRONG! Expected {expected_name}")
        else:
            print(f"❌ {result.get('message', 'Unknown Cow')}")
            if 'distance' in result:
                print(f"   Closest distance: {result['distance']:.4f}")
                print(f"   Confidence: {result['confidence']:.4f}")
        
        print()
        return result
    else:
        print(f"❌ Error: {response.text}")
        print()
        return None


def main():
    """Run all tests."""
    print("\n")
    print("=" * 70)
    print("   ChromaDB Vector Database - API Tests")
    print("=" * 70)
    print()
    
    # Test 1: Health check
    if not test_health():
        print("❌ ChromaDB not loaded! Exiting...")
        return
    
    # Test 2: Register first cow (Bessie)
    bessie_img1 = "processed_results/cattle_0100_DSCF3856_enhanced.jpg"
    test_register(bessie_img1, "Bessie")
    
    # Test 3: Register second cow (Daisy)
    daisy_img1 = "processed_results/cattle_0200_DSCF3868_enhanced.jpg"
    test_register(daisy_img1, "Daisy")
    
    # Test 4: Identify Bessie with different photo (should match)
    bessie_img2 = "processed_results/cattle_0100_DSCF3858_enhanced.jpg"
    test_identify(bessie_img2, expected_name="Bessie")
    
    # Test 5: Identify Daisy with different photo (should match)
    daisy_img2 = "processed_results/cattle_0200_DSCF3870_enhanced.jpg"
    test_identify(daisy_img2, expected_name="Daisy")
    
    # Test 6: Try to identify unknown cow (should not match)
    print("=" * 70)
    print("TEST 4: Identify Unknown Cow")
    print("=" * 70)
    unknown_img = "processed_results/cattle_0300_DSCF3880_enhanced.jpg"
    
    if Path(unknown_img).exists():
        test_identify(unknown_img, expected_name=None)
    else:
        print(f"⚠️ Unknown cow image not found, skipping test")
        print()
    
    # Final health check
    print("=" * 70)
    print("FINAL: Health Check")
    print("=" * 70)
    test_health()
    
    print("=" * 70)
    print("   All Tests Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
