"""
Test script for the Cattle Muzzle Biometric API.

This script demonstrates how to use the API endpoints.
"""

import requests
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test the health check endpoint."""
    print("🔍 Testing health check endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")


def test_register(image_path: str):
    """
    Test the register endpoint.
    
    Args:
        image_path: Path to image file
    """
    print(f"📝 Testing registration with: {image_path}")
    
    with open(image_path, 'rb') as f:
        files = {'file': ('image.jpg', f, 'image/jpeg')}
        response = requests.post(f"{BASE_URL}/register", files=files)
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Cow ID: {data['cow_id']}")
        print(f"   Vector size: {len(data['vector'])} dimensions")
        print(f"   First 5 values: {data['vector'][:5]}\n")
        return data
    else:
        print(f"   Error: {response.text}\n")
        return None


def test_verify(image_a_path: str, image_b_path: str):
    """
    Test the verify endpoint.
    
    Args:
        image_a_path: Path to first image
        image_b_path: Path to second image
    """
    print(f"🔐 Testing verification:")
    print(f"   Image A: {image_a_path}")
    print(f"   Image B: {image_b_path}")
    
    with open(image_a_path, 'rb') as f1, open(image_b_path, 'rb') as f2:
        files = {
            'image_a': ('image_a.jpg', f1, 'image/jpeg'),
            'image_b': ('image_b.jpg', f2, 'image/jpeg')
        }
        response = requests.post(f"{BASE_URL}/verify", files=files)
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Match: {data['match']}")
        print(f"   Similarity Score: {data['similarity_score']:.4f}")
        print(f"   Threshold: {data['threshold_used']}")
        print(f"   Result: {'✅ MATCH' if data['match'] else '❌ NO MATCH'}\n")
        return data
    else:
        print(f"   Error: {response.text}\n")
        return None


def main():
    """Run API tests."""
    print("=" * 70)
    print("🐄 Cattle Muzzle Biometric API - Test Suite")
    print("=" * 70)
    print()
    
    # Test health check
    test_health_check()
    
    # Find some test images
    processed_dir = Path("processed_results")
    
    # Get images from cattle_0100 (same cow)
    cattle_0100_images = list(processed_dir.glob("cattle_0100_*.jpg"))[:2]
    
    # Get image from cattle_0200 (different cow)
    cattle_0200_images = list(processed_dir.glob("cattle_0200_*.jpg"))[:1]
    
    if len(cattle_0100_images) >= 2 and len(cattle_0200_images) >= 1:
        # Test 1: Register an image
        print("TEST 1: Register a cattle muzzle")
        print("-" * 70)
        test_register(str(cattle_0100_images[0]))
        
        # Test 2: Verify same cow (should match)
        print("TEST 2: Verify same cow (should match)")
        print("-" * 70)
        test_verify(str(cattle_0100_images[0]), str(cattle_0100_images[1]))
        
        # Test 3: Verify different cow (should not match)
        print("TEST 3: Verify different cow (should NOT match)")
        print("-" * 70)
        test_verify(str(cattle_0100_images[0]), str(cattle_0200_images[0]))
        
        print("=" * 70)
        print("✅ All tests completed!")
        print("=" * 70)
    else:
        print("❌ Error: Not enough test images found in processed_results folder")


if __name__ == "__main__":
    main()
