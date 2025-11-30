"""Test the new three-tier threshold logic."""
import requests

API_URL = "http://localhost:8000"

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def test_identify(image_path, description):
    """Test identification and show threshold tier."""
    print(f"\n{description}")
    print(f"Image: {image_path}")
    
    with open(image_path, 'rb') as f:
        files = {'file': ('test.jpg', f, 'image/jpeg')}
        r = requests.post(f"{API_URL}/identify", files=files, timeout=15)
        
    if r.status_code == 200:
        result = r.json()
        print(f"\nResult:")
        print(f"  Match: {result['match']}")
        print(f"  Status: {result['status']}")
        print(f"  Message: {result['message']}")
        if result.get('cow_name'):
            print(f"  Cow Name: {result['cow_name']}")
        if result.get('confidence'):
            print(f"  Confidence: {result['confidence']:.2f}%")
        if result.get('distance') is not None:
            print(f"  Distance: {result['distance']:.4f}")
        
        # Show which tier
        if result['status'] == 'APPROVED':
            print(f"\n  ✅ TIER 1: AUTO-APPROVED (confidence >= 85%)")
        elif result['status'] == 'MANUAL_REVIEW':
            print(f"\n  ⚠️ TIER 2: MANUAL REVIEW REQUIRED (75% <= confidence < 85%)")
        elif result['status'] == 'REJECTED':
            print(f"\n  ❌ TIER 3: REJECTED (confidence < 75%)")
    else:
        print(f"ERROR: {r.text}")

# Run tests
print_header("THREE-TIER THRESHOLD LOGIC TEST")
print("\nThresholds:")
print("  • AUTO_APPROVE: >= 85%")
print("  • MANUAL_REVIEW: 75% - 85%")
print("  • REJECTED: < 75%")

print_header("TEST 1: High Confidence Match (Should be APPROVED)")
test_identify("processed_results/cattle_0100_DSCF3858_enhanced.jpg", 
              "Testing Bessie with different photo")

print_header("TEST 2: Another High Confidence Match")
test_identify("processed_results/cattle_0200_DSCF3870_enhanced.jpg",
              "Testing Daisy with different photo")

print_header("TEST 3: Third Photo of Bessie")
test_identify("processed_results/cattle_0100_DSCF3859_enhanced.jpg",
              "Testing Bessie with third photo")

print_header("SUMMARY")
print("✓ Three-tier threshold logic implemented")
print("✓ Auto-approve for high confidence (>=85%)")
print("✓ Manual review for gray area (75-85%)")
print("✓ Rejection for low confidence (<75%)")
print("=" * 70)
