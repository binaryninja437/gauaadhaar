import requests
import os

API_URL = "http://localhost:8000"
TEST_IMAGE = "uploaded_image_1764418557674.png"  # Using the uploaded image for testing

def log(msg):
    print(msg)
    with open("test_results.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def test_geo_fencing():
    # Clear previous results
    with open("test_results.txt", "w", encoding="utf-8") as f:
        f.write("🌍 TESTING GEO-FENCING LOGIC\n==================================================\n")

    log("\n1️⃣  Registering Cow 'GeoBessie' at Mumbai (19.0760, 72.8777)...")
    
    # ... (rest of the code using log instead of print)
    
    # Create dummy image if not exists
    if not os.path.exists("test_cow.jpg"):
        from PIL import Image
        img = Image.new('RGB', (100, 100), color = 'black')
        img.save('test_cow.jpg')
            
    files = {'file': open("test_cow.jpg", 'rb')}
    data = {
        'cow_name': 'GeoBessie',
        'latitude': 19.0760,
        'longitude': 72.8777
    }
    
    try:
        response = requests.post(f"{API_URL}/register", files=files, data=data)
        if response.status_code == 200:
            log("✅ Registration Successful!")
            log(str(response.json()))
        else:
            log(f"❌ Registration Failed: {response.text}")
            return
    except Exception as e:
        log(f"❌ Connection Error: {e}")
        return

    # 2. Identify from NEARBY location (Very Close - 19.0700, 72.8700)
    log("\n2️⃣  Identifying from NEARBY location (Very Close - 19.0700, 72.8700)...")
    files = {'file': open("test_cow.jpg", 'rb')}
    data = {
        'current_lat': 19.0700,
        'current_lon': 72.8700
    }
    
    response = requests.post(f"{API_URL}/identify", files=files, data=data)
    result = response.json()
    
    if result.get('status') == 'APPROVED' or result.get('status') == 'MANUAL_REVIEW':
        log(f"✅ SUCCESS: Match Found! Status: {result['status']}")
        log(f"   Distance: {result.get('distance_km', 0):.2f} km")
    else:
        log(f"❌ FAILED: Unexpected status {result.get('status')}")
        log(str(result))

    # 3. Identify from FAR location (Pune, ~150km away)
    log("\n3️⃣  Identifying from FAR location (Pune - 18.5204, 73.8567)...")
    files = {'file': open("test_cow.jpg", 'rb')}
    data = {
        'current_lat': 18.5204,
        'current_lon': 73.8567
    }
    
    response = requests.post(f"{API_URL}/identify", files=files, data=data)
    result = response.json()
    
    if result.get('status') == 'LOCATION_MISMATCH':
        log(f"✅ SUCCESS: Location Mismatch Detected!")
        log(f"   Message: {result['message']}")
        log(f"   Distance: {result.get('distance_km', 0):.2f} km")
    else:
        log(f"❌ FAILED: Expected LOCATION_MISMATCH, got {result.get('status')}")
        log(str(result))

if __name__ == "__main__":
    test_geo_fencing()
