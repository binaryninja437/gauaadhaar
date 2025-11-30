# 🌍 Geo-Fencing Testing Guide

Follow these steps to verify the location fraud prevention system.

## 1. Setup
Ensure the dashboard is running:
- URL: http://localhost:8501

## 2. Register a Cow (The "Truth")
1. Go to the **Register New Cow** page.
2. Enter Name: `Bessie`
3. Upload a clear muzzle photo.
4. **Location Data:** Keep the default values (Mumbai).
   - Latitude: `19.0760`
   - Longitude: `72.8777`
5. Click **Register Cow**.
   - ✅ Verify you see "Cow registered successfully!"

## 3. Test: Valid Location (Success)
1. Go to the **Identify Cow** page.
2. Upload the **same photo** (or a similar one of the same cow).
3. **Current Location:** Keep the default values (Same as registration).
   - Current Latitude: `19.0760`
   - Current Longitude: `72.8777`
4. Click **Identify Cow**.
   - ✅ **Result:** You should see a green **AUTO-APPROVED** box.
   - **Distance:** Should be `0.00 km` (or very close).

## 4. Test: Location Mismatch (Fraud Attempt)
1. Stay on the **Identify Cow** page.
2. Keep the same photo.
3. **Current Location:** Change the coordinates to simulate a different location (e.g., Pune).
   - Current Latitude: `18.5204` (Change `19` to `18`)
   - Current Longitude: `73.8567`
4. Click **Identify Cow**.
   - ❌ **Result:** You should see a red **LOCATION MISMATCH** box.
   - **Message:** "Face matches, but location is too far"
   - **Distance:** Should be > 100 km.

## 5. Test: Nearby Location (Boundary Check)
1. Change coordinates slightly (within 5km).
   - Current Latitude: `19.0800` (Small change)
   - Current Longitude: `72.8800`
2. Click **Identify Cow**.
   - ✅ **Result:** Should still be **APPROVED**.
   - **Distance:** Should be small (e.g., ~0.5 km).
