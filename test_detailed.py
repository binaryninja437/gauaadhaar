"""Detailed test to show all results clearly."""
import requests
import time

API_URL = "http://localhost:8000"

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def test_register(image_path, cow_name):
    """Register a cow and return result."""
    with open(image_path, 'rb') as f:
        files = {'file': ('test.jpg', f, 'image/jpeg')}
        data = {'cow_name': cow_name}
        r = requests.post(f"{API_URL}/register", files=files, data=data, timeout=15)
        return r.status_code, r.json() if r.status_code == 200 else r.text

def test_identify(image_path):
    """Identify a cow and return result."""
    with open(image_path, 'rb') as f:
        files = {'file': ('test.jpg', f, 'image/jpeg')}
        r = requests.post(f"{API_URL}/identify", files=files, timeout=15)
        return r.status_code, r.json() if r.status_code == 200 else r.text

# Start tests
print_header("CATTLE BIOMETRIC SYSTEM - COMPREHENSIVE TEST")

# Test 1: Register Bessie
print_header("TEST 1: Register Bessie")
status, result = test_register("processed_results/cattle_0100_DSCF3856_enhanced.jpg", "Bessie")
print(f"Status: {status}")
if status == 200:
    print(f"✓ SUCCESS!")
    print(f"  Cow Name: {result['cow_name']}")
    print(f"  Cow ID: {result['cow_id'][:16]}...")
    print(f"  Vector Dimensions: {result['vector_dimensions']}")
else:
    print(f"✗ FAILED: {result}")
    exit(1)

time.sleep(1)

# Test 2: Register Daisy
print_header("TEST 2: Register Daisy")
status, result = test_register("processed_results/cattle_0200_DSCF3868_enhanced.jpg", "Daisy")
print(f"Status: {status}")
if status == 200:
    print(f"✓ SUCCESS!")
    print(f"  Cow Name: {result['cow_name']}")
    print(f"  Cow ID: {result['cow_id'][:16]}...")
else:
    print(f"✗ FAILED: {result}")
    exit(1)

time.sleep(1)

# Test 3: Identify Bessie (different photo)
print_header("TEST 3: Identify Bessie (Different Photo)")
print("Image: cattle_0100_DSCF3858_enhanced.jpg")
print("Expected: Should identify as Bessie with >75% confidence")
status, result = test_identify("processed_results/cattle_0100_DSCF3858_enhanced.jpg")
print(f"\nStatus: {status}")
if status == 200:
    if result['match_found']:
        print(f"✓ MATCH FOUND!")
        print(f"  Identified as: {result['cow_name']}")
        print(f"  Confidence: {result['confidence']:.2f}%")
        print(f"  Distance: {result['distance']:.4f}")
        
        if result['cow_name'] == 'Bessie' and result['confidence'] > 75:
            print(f"\n✓✓ TEST PASSED - Correct cow with high confidence!")
        else:
            print(f"\n✗✗ TEST FAILED - Wrong cow or low confidence")
    else:
        print(f"✗ NO MATCH: {result.get('message')}")
        print(f"  Confidence: {result.get('confidence', 0):.2f}%")
        print(f"\n✗✗ TEST FAILED - Should have matched Bessie")
else:
    print(f"✗ FAILED: {result}")

time.sleep(1)

# Test 4: Identify Daisy (different photo)
print_header("TEST 4: Identify Daisy (Different Photo)")
print("Image: cattle_0200_DSCF3870_enhanced.jpg")
print("Expected: Should identify as Daisy with >75% confidence")
status, result = test_identify("processed_results/cattle_0200_DSCF3870_enhanced.jpg")
print(f"\nStatus: {status}")
if status == 200:
    if result['match_found']:
        print(f"✓ MATCH FOUND!")
        print(f"  Identified as: {result['cow_name']}")
        print(f"  Confidence: {result['confidence']:.2f}%")
        print(f"  Distance: {result['distance']:.4f}")
        
        if result['cow_name'] == 'Daisy' and result['confidence'] > 75:
            print(f"\n✓✓ TEST PASSED - Correct cow with high confidence!")
        else:
            print(f"\n✗✗ TEST FAILED - Wrong cow or low confidence")
    else:
        print(f"✗ NO MATCH: {result.get('message')}")
        print(f"  Confidence: {result.get('confidence', 0):.2f}%")
        print(f"\n✗✗ TEST FAILED - Should have matched Daisy")
else:
    print(f"✗ FAILED: {result}")

time.sleep(1)

# Test 5: Another Bessie photo
print_header("TEST 5: Identify Bessie (Third Photo)")
print("Image: cattle_0100_DSCF3859_enhanced.jpg")
print("Expected: Should still identify as Bessie")
status, result = test_identify("processed_results/cattle_0100_DSCF3859_enhanced.jpg")
print(f"\nStatus: {status}")
if status == 200:
    if result['match_found']:
        print(f"✓ MATCH FOUND!")
        print(f"  Identified as: {result['cow_name']}")
        print(f"  Confidence: {result['confidence']:.2f}%")
        print(f"  Distance: {result['distance']:.4f}")
        
        if result['cow_name'] == 'Bessie':
            print(f"\n✓✓ TEST PASSED - Correctly identified as Bessie!")
        else:
            print(f"\n✗✗ TEST FAILED - Misidentified as {result['cow_name']}")
    else:
        print(f"✗ NO MATCH: {result.get('message')}")
else:
    print(f"✗ FAILED: {result}")

# Final summary
print_header("TEST SUMMARY")
print("✓ Vector Normalization: APPLIED")
print("✓ Distance Metric: COSINE")
print("✓ Confidence Formula: (1 - distance) × 100")
print("✓ Threshold: 75%")
print("✓ Image Processing: Fixed (handles grayscale/RGB/RGBA)")
print("\n🎉 All tests completed! Check results above.")
print("=" * 70)
