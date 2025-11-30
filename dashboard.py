"""
CattleSure: AI Biometric Verification Dashboard
================================================
Streamlit dashboard for cattle muzzle biometric identification system.
Designed for investor demonstrations and fraud detection in cattle insurance.
"""

import streamlit as st
import requests
from io import BytesIO

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="CattleSure - AI Biometric Verification",
    page_icon="🐮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #2E7D32;
        margin-bottom: 1rem;
    }
    .success-box {
        padding: 2rem;
        border-radius: 10px;
        background-color: #C8E6C9;
        border: 3px solid #4CAF50;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        color: #1B5E20;
    }
    .fraud-box {
        padding: 2rem;
        border-radius: 10px;
        background-color: #FFCDD2;
        border: 3px solid #F44336;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        color: #B71C1C;
    }
    .info-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #E3F2FD;
        border-left: 5px solid #2196F3;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🐮 CattleSure: AI Biometric Verification</div>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar navigation
st.sidebar.title("📋 Navigation")
page = st.sidebar.radio(
    "Select Page:",
    ["Register New Cow", "Identify Cow", "Verify Claim"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 System Info")
st.sidebar.info(f"**API Endpoint:** {API_BASE_URL}")

# Check API health
try:
    health_response = requests.get(f"{API_BASE_URL}/health", timeout=2)
    if health_response.status_code == 200:
        health_data = health_response.json()
        st.sidebar.success("✅ API Online")
        if 'cattle_count' in health_data:
            st.sidebar.info(f"🐮 Registered Cattle: {health_data['cattle_count']}")
    else:
        st.sidebar.error("⚠️ API Issues")
except:
    st.sidebar.error("❌ API Offline")

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 About")
st.sidebar.markdown("""
**CattleSure** uses AI-powered muzzle pattern recognition to prevent insurance fraud.

Each cow has a unique muzzle pattern - like a fingerprint!
""")


# ============================================================================
# PAGE 1: Register New Cow
# ============================================================================
if page == "Register New Cow":
    st.header("📝 Register New Cow")
    st.markdown("Upload a muzzle photo to register a new cow in the system.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="info-box">📸 <b>Upload Requirements:</b><br>• Clear muzzle photo<br>• Good lighting<br>• JPG or PNG format</div>', unsafe_allow_html=True)
        
        # Cow name input
        cow_name = st.text_input(
            "Cow Name",
            placeholder="Enter cow's name (e.g., Bessie)",
            help="Provide a unique name for this cow"
        )
        
        uploaded_file = st.file_uploader(
            "Upload Muzzle Photo",
            type=["jpg", "jpeg", "png"],
            help="Upload a clear photo of the cow's muzzle"
        )
        
        # GPS Coordinates
        st.markdown("#### 📍 Location Data")
        col_lat, col_lon = st.columns(2)
        with col_lat:
            latitude = st.number_input("Latitude", value=19.0760, format="%.4f")
        with col_lon:
            longitude = st.number_input("Longitude", value=72.8777, format="%.4f")
        
        if uploaded_file is not None:
            st.image(uploaded_file, caption="Uploaded Muzzle Photo", use_column_width=True)
        
        register_button = st.button("🔐 Register Cow", type="primary", use_container_width=True)
    
    with col2:
        if register_button and uploaded_file is not None and cow_name:
            with st.spinner("🔄 Processing muzzle pattern..."):
                try:
                    # Prepare the file and form data for upload
                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    data = {
                        'cow_name': cow_name,
                        'latitude': latitude,
                        'longitude': longitude
                    }
                    
                    # Send POST request to /register endpoint
                    response = requests.post(f"{API_BASE_URL}/register", files=files, data=data)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.success("✅ Cow registered successfully!")
                        
                        # Display Cow Name
                        st.markdown("### 🐮 Cow Name")
                        st.code(result['cow_name'], language=None)
                        
                        # Display Cow ID
                        st.markdown("### 🆔 Cow ID")
                        st.code(result['cow_id'], language=None)
                        
                        # Display vector dimensions
                        st.markdown("### 🧬 Biometric Signature")
                        st.write(f"Vector dimensions: **{result['vector_dimensions']}**")
                        st.caption("Stored in vector database for future identification")
                        
                        # Success metrics
                        st.markdown("---")
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Status", "Saved", delta="✓")
                        with col_b:
                            st.metric("Vector Size", f"{result['vector_dimensions']}D")
                        with col_c:
                            st.metric("Database", "ChromaDB", delta="✓")
                        
                    else:
                        st.error(f"❌ Error: {response.text}")
                        
                except Exception as e:
                    st.error(f"❌ Connection Error: {str(e)}")
                    st.warning("Make sure the API server is running at http://localhost:8000")
        
        elif register_button and uploaded_file is None:
            st.warning("⚠️ Please upload a muzzle photo first!")
        elif register_button and not cow_name:
            st.warning("⚠️ Please enter a cow name!")


# ============================================================================
# PAGE 2: Identify Cow
# ============================================================================
elif page == "Identify Cow":
    st.header("🔍 Identify Cow")
    st.markdown("Upload a muzzle photo to search the database and identify the cow.")
    
    st.markdown('<div class="info-box">🔎 <b>Database Search:</b> Our AI will search the vector database to find the matching cow based on muzzle patterns.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 📸 Upload Muzzle Photo")
        st.caption("Photo of the cow you want to identify")
        
        query_photo = st.file_uploader(
            "Upload Cow Photo",
            type=["jpg", "jpeg", "png"],
            key="identify",
            help="Upload a photo to search the database"
        )
        
        # Current GPS Coordinates
        st.markdown("#### 📍 Current Location")
        col_lat, col_lon = st.columns(2)
        with col_lat:
            current_lat = st.number_input("Current Latitude", value=19.0760, format="%.4f")
        with col_lon:
            current_lon = st.number_input("Current Longitude", value=72.8777, format="%.4f")
        
        if query_photo is not None:
            st.image(query_photo, caption="Query Photo", use_column_width=True)
        
        identify_button = st.button("🔐 Identify Cow", type="primary", use_container_width=True)
    
    with col2:
        if identify_button and query_photo is not None:
            with st.spinner("🔄 Searching database..."):
                try:
                    # Prepare file for upload
                    files = {'file': (query_photo.name, query_photo.getvalue(), query_photo.type)}
                    data = {
                        'current_lat': current_lat,
                        'current_lon': current_lon
                    }
                    
                    # Send POST request to /identify endpoint
                    response = requests.post(f"{API_BASE_URL}/identify", files=files, data=data)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.markdown("---")
                        st.markdown("### 📊 Identification Results")
                        
                        # Check status from three-tier threshold logic
                        status = result.get('status', 'REJECTED')
                        
                        if status == 'APPROVED':
                            # High confidence - Auto-approved
                            st.markdown(
                                '<div class="success-box">✅ AUTO-APPROVED</div>',
                                unsafe_allow_html=True
                            )
                            st.balloons()
                            
                            st.markdown("---")
                            
                            # Display cow name
                            st.markdown("### 🐮 Identified As:")
                            st.markdown(f"# **{result['cow_name']}**")
                            
                            # Confidence metrics
                            st.markdown("---")
                            st.markdown("#### 📈 Confidence Metrics")
                            
                            confidence_percentage = result['confidence']
                            st.progress(result['confidence'] / 100, text=f"**{confidence_percentage:.2f}%** Confidence")
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.metric(
                                    "Confidence Score",
                                    f"{confidence_percentage:.2f}%",
                                    delta="High"
                                )
                            with col_b:
                                st.metric(
                                    "Distance",
                                    f"{result['distance']:.4f}",
                                    delta="Low",
                                    delta_color="inverse"
                                )
                            
                            st.markdown("---")
                            st.success("""
                            **✅ AUTO-APPROVED - Strong Match**
                            
                            Confidence >= 85%. The uploaded photo strongly matches this registered cow.
                            No manual review required.
                            """)
                        
                        elif status == 'MANUAL_REVIEW':
                            # Medium confidence - Manual review needed
                            st.markdown(
                                '<div style="padding: 2rem; border-radius: 10px; background-color: #FFF3CD; border: 3px solid #FFC107; text-align: center; font-size: 2rem; font-weight: bold; color: #856404;">⚠️ MANUAL REVIEW REQUIRED</div>',
                                unsafe_allow_html=True
                            )
                            
                            st.markdown("---")
                            
                            # Display potential cow name
                            st.markdown("### 🐮 Potential Match:")
                            st.markdown(f"# **{result['cow_name']}**")
                            
                            # Confidence metrics
                            st.markdown("---")
                            st.markdown("#### 📈 Confidence Metrics")
                            
                            confidence_percentage = result['confidence']
                            st.progress(result['confidence'] / 100, text=f"**{confidence_percentage:.2f}%** Confidence")
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.metric(
                                    "Confidence Score",
                                    f"{confidence_percentage:.2f}%",
                                    delta="Medium"
                                )
                            with col_b:
                                st.metric(
                                    "Distance",
                                    f"{result['distance']:.4f}",
                                    delta="Medium",
                                    delta_color="inverse"
                                )
                            
                            st.markdown("---")
                            st.warning("""
                            **⚠️ MANUAL REVIEW REQUIRED**
                            
                            Confidence: 75-85%. This is a potential match but requires visual verification.
                            
                            **Action Required:**
                            - Compare the uploaded photo with registered images manually
                            - Verify muzzle patterns match visually
                            - Approve or reject based on visual inspection
                            """)
                        
                        elif status == 'LOCATION_MISMATCH':
                            # Face Match BUT Location Mismatch
                            st.markdown(
                                '<div class="fraud-box">❌ LOCATION MISMATCH</div>',
                                unsafe_allow_html=True
                            )
                            
                            st.markdown("---")
                            
                            # Display cow name
                            st.markdown("### 🐮 Identified As:")
                            st.markdown(f"# **{result['cow_name']}**")
                            
                            st.error(f"""
                            **❌ FRAUD ALERT: LOCATION MISMATCH**
                            
                            {result['message']}
                            
                            **Distance:** {result['distance_km']:.2f} km (Limit: 5.0 km)
                            """)
                            
                            # Metrics
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.metric("Confidence", f"{result['confidence']:.2f}%", delta="High")
                            with col_b:
                                st.metric("Distance", f"{result['distance_km']:.2f} km", delta="Too Far", delta_color="inverse")
                        
                        else:  # REJECTED
                            # Low confidence - Rejected
                            st.markdown(
                                '<div class="fraud-box">❌ REJECTED - No Match</div>',
                                unsafe_allow_html=True
                            )
                            
                            st.markdown("---")
                            st.error(f"""
                            **❌ NO MATCH FOUND**
                            
                            {result.get('message', 'This cow is not registered in the database.')}
                            
                            Confidence < 75%. This cow does not match any registered cattle.
                            
                            **Possible Reasons:**
                            - Cow has not been registered yet
                            - Photo quality is too poor
                            - This is a different cow (potential fraud)
                            """)
                            
                            if result.get('confidence'):
                                st.markdown("#### 📊 Closest Match Metrics")
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    st.metric("Confidence", f"{result['confidence']:.2f}%")
                                with col_b:
                                    st.metric("Distance", f"{result['distance']:.4f}")
                    
                    else:
                        st.error(f"❌ Error: {response.text}")
                
                except Exception as e:
                    st.error(f"❌ Connection Error: {str(e)}")
                    st.warning("Make sure the API server is running at http://localhost:8000")
        
        elif identify_button and query_photo is None:
            st.warning("⚠️ Please upload a photo first!")
# PAGE 3: Verify Claim (Fraud Detection)
# ============================================================================
elif page == "Verify Claim":
    st.header("🔍 Verify Claim (Fraud Detection)")
    st.markdown("Compare the original policy photo with the claim photo to detect fraud.")
    
    st.markdown('<div class="info-box">🛡️ <b>Fraud Detection:</b> Our AI compares muzzle patterns to verify if the claimed cow matches the insured cow.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📄 Original Policy Photo")
        st.caption("Photo taken when insurance was purchased")
        original_photo = st.file_uploader(
            "Upload Original Policy Photo",
            type=["jpg", "jpeg", "png"],
            key="original",
            help="The muzzle photo from the insurance policy"
        )
        
        if original_photo is not None:
            st.image(original_photo, caption="Policy Photo", use_column_width=True)
    
    with col2:
        st.markdown("#### 📸 Claim Photo")
        st.caption("Current photo submitted with the claim")
        claim_photo = st.file_uploader(
            "Upload Claim Photo",
            type=["jpg", "jpeg", "png"],
            key="claim",
            help="The current muzzle photo for verification"
        )
        
        if claim_photo is not None:
            st.image(claim_photo, caption="Claim Photo", use_column_width=True)
    
    st.markdown("---")
    
    # Verify button
    verify_button = st.button("🔐 Verify Match", type="primary", use_container_width=True)
    
    if verify_button:
        if original_photo is not None and claim_photo is not None:
            with st.spinner("🔄 Analyzing biometric patterns..."):
                try:
                    # Prepare files for upload
                    files = {
                        'image_a': (original_photo.name, original_photo.getvalue(), original_photo.type),
                        'image_b': (claim_photo.name, claim_photo.getvalue(), claim_photo.type)
                    }
                    
                    # Send POST request to /verify endpoint
                    response = requests.post(f"{API_BASE_URL}/verify", files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        match = data['match']
                        similarity_score = data['similarity_score']
                        threshold = data['threshold_used']
                        
                        st.markdown("---")
                        st.markdown("### 📊 Verification Results")
                        
                        # Display result with appropriate styling
                        if match:
                            st.markdown(
                                '<div class="success-box">✅ IDENTITY CONFIRMED</div>',
                                unsafe_allow_html=True
                            )
                            st.balloons()
                        else:
                            st.markdown(
                                '<div class="fraud-box">⚠️ FRAUD DETECTED</div>',
                                unsafe_allow_html=True
                            )
                        
                        st.markdown("---")
                        
                        # Similarity score as progress bar
                        st.markdown("#### 📈 Similarity Score")
                        similarity_percentage = similarity_score * 100
                        
                        # Color-coded progress bar
                        if similarity_score >= threshold:
                            st.progress(similarity_score, text=f"**{similarity_percentage:.2f}%** - Match Confirmed")
                        else:
                            st.progress(similarity_score, text=f"**{similarity_percentage:.2f}%** - Below Threshold")
                        
                        # Detailed metrics
                        st.markdown("---")
                        col_a, col_b, col_c = st.columns(3)
                        
                        with col_a:
                            st.metric(
                                "Similarity Score",
                                f"{similarity_percentage:.2f}%",
                                delta=f"{(similarity_score - threshold) * 100:.2f}% vs threshold"
                            )
                        
                        with col_b:
                            st.metric(
                                "Threshold",
                                f"{threshold * 100:.0f}%"
                            )
                        
                        with col_c:
                            verdict = "APPROVED" if match else "REJECTED"
                            delta_icon = "✓" if match else "✗"
                            st.metric(
                                "Claim Status",
                                verdict,
                                delta=delta_icon
                            )
                        
                        # Recommendation
                        st.markdown("---")
                        st.markdown("#### 💼 Recommendation")
                        if match:
                            st.success("""
                            **✅ APPROVE CLAIM**
                            
                            The biometric analysis confirms that the cow in the claim photo matches 
                            the cow in the original policy photo. The claim appears legitimate.
                            """)
                        else:
                            st.error("""
                            **⚠️ REJECT CLAIM - INVESTIGATE FRAUD**
                            
                            The biometric analysis indicates that the cow in the claim photo does NOT match 
                            the cow in the original policy photo. This suggests potential fraud.
                            
                            **Recommended Actions:**
                            - Flag for manual review
                            - Contact policy holder
                            - Investigate claim circumstances
                            """)
                    
                    else:
                        st.error(f"❌ Error: {response.text}")
                
                except Exception as e:
                    st.error(f"❌ Connection Error: {str(e)}")
                    st.warning("Make sure the API server is running at http://localhost:8000")
        
        else:
            st.warning("⚠️ Please upload both photos before verifying!")


# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p><b>CattleSure</b> - AI-Powered Cattle Biometric Verification System</p>
        <p>Powered by Deep Learning | ResNet50 + CLAHE Enhancement</p>
    </div>
    """,
    unsafe_allow_html=True
)
