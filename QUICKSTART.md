# 🚀 Quick Start Guide - CattleSure Dashboard

## Running the Complete System

### Step 1: Start the FastAPI Backend (if not already running)

```bash
py -3.13 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
🔄 Loading ResNet50 feature extractor...
✅ ResNet50 loaded successfully!
🚀 API is ready to accept requests!
```

### Step 2: Start the Streamlit Dashboard

Open a **NEW terminal** and run:

```bash
py -3.13 -m streamlit run dashboard.py
```

**Expected output:**
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

### Step 3: Open the Dashboard

The dashboard will automatically open in your browser at:
**http://localhost:8501**

If it doesn't open automatically, manually open the URL in your browser.

---

## 🎯 Using the Dashboard

### Page 1: Register New Cow

1. Click **"Register New Cow"** in the sidebar
2. Upload a muzzle photo from the `processed_results` folder
3. Click **"Register Cow"**
4. View the generated Cow ID and biometric signature

**Example images to try:**
- `processed_results/cattle_0100_DSCF3856_enhanced.jpg`
- `processed_results/cattle_0200_DSCF3868_enhanced.jpg`

### Page 2: Verify Claim (Fraud Detection)

1. Click **"Verify Claim"** in the sidebar
2. Upload **Original Policy Photo** (e.g., from cattle_0100)
3. Upload **Claim Photo**:
   - **Same cow** (another image from cattle_0100) → Should show ✅ MATCH
   - **Different cow** (image from cattle_0200) → Should show ⚠️ FRAUD
4. Click **"Verify Match"**
5. See the results with similarity score and recommendation

**Test Cases:**

**✅ Should MATCH (Same Cow):**
- Original: `cattle_0100_DSCF3856_enhanced.jpg`
- Claim: `cattle_0100_DSCF3858_enhanced.jpg`

**⚠️ Should DETECT FRAUD (Different Cow):**
- Original: `cattle_0100_DSCF3856_enhanced.jpg`
- Claim: `cattle_0200_DSCF3868_enhanced.jpg`

---

## 🛠️ Troubleshooting

### Dashboard shows "API Offline"
- Make sure the FastAPI backend is running on port 8000
- Check: http://localhost:8000/ in your browser

### "Connection Error"
- Ensure both services are running:
  - Backend: `http://localhost:8000`
  - Dashboard: `http://localhost:8501`

### Port already in use
```bash
# Kill process on port 8501 (Streamlit)
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Kill process on port 8000 (FastAPI)
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## 📊 System Architecture

```
┌─────────────────┐         ┌──────────────────┐
│   Streamlit     │  HTTP   │   FastAPI        │
│   Dashboard     │ ──────> │   Backend        │
│   (Port 8501)   │         │   (Port 8000)    │
└─────────────────┘         └──────────────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │   ResNet50       │
                            │   + CLAHE        │
                            │   Processing     │
                            └──────────────────┘
```

---

## 🎨 Dashboard Features

✅ **Two-page navigation**
- Register New Cow
- Verify Claim (Fraud Detection)

✅ **Visual feedback**
- Green success boxes for matches
- Red warning boxes for fraud
- Progress bars for similarity scores

✅ **Investor-ready UI**
- Professional styling
- Clear metrics and recommendations
- Real-time API status indicator

✅ **Fraud detection**
- Side-by-side photo comparison
- Biometric similarity analysis
- Automated claim recommendations

---

## 💡 Demo Tips for Investors

1. **Show the registration flow first**
   - Upload a clear muzzle photo
   - Highlight the unique biometric signature

2. **Demonstrate fraud detection**
   - First, verify with same cow (show ✅ MATCH)
   - Then, try different cow (show ⚠️ FRAUD DETECTED)
   - Emphasize the similarity score difference

3. **Key talking points:**
   - "Each cow has a unique muzzle pattern - like a fingerprint"
   - "AI-powered fraud detection in seconds"
   - "Prevents fraudulent insurance claims"
   - "Scalable to millions of cattle"

---

## 📝 Notes

- The dashboard requires the FastAPI backend to be running
- First API call may be slower (model initialization)
- Subsequent calls are fast (~100-200ms)
- All processing happens on the backend
- Dashboard is just a UI layer

---

**Built for CattleSure - AI-Powered Cattle Biometric Verification** 🐮
