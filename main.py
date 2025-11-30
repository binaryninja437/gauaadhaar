"""
Cattle Muzzle Biometric Identification API
===========================================
FastAPI application for cattle identification using muzzle patterns.

This API provides endpoints for registering cattle muzzle images and
verifying identity through deep learning feature extraction.
"""

import os
import uuid
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from tensorflow.keras.applications import ResNet50
import uvicorn
from pinecone import Pinecone, ServerlessSpec

from utils import ImageProcessor, calculate_cosine_similarity, calculate_distance

# Initialize FastAPI app
app = FastAPI(
    title="Cattle Muzzle Biometric API",
    description="Biometric identification system for cattle using muzzle patterns",
    version="1.0.0"
)

# Global variables for model and processor (loaded once at startup)
model = None
processor = None
pc = None
index = None

# Configuration
SIMILARITY_THRESHOLD = 0.85  # Threshold for match/no-match decision (verify endpoint)
AUTO_APPROVE_THRESHOLD = 85.0  # High confidence threshold for auto-approval (percentage)
MANUAL_REVIEW_THRESHOLD = 75.0  # Minimum threshold for potential match requiring review (percentage)
MAX_DISTANCE_KM = 5.0          # Kilometers for Geo-Fencing


# Response models
class RegisterResponse(BaseModel):
    """Response model for registration endpoint."""
    status: str
    cow_id: str
    cow_name: str
    vector_dimensions: int


class VerifyResponse(BaseModel):
    """Response model for verification endpoint."""
    match: bool
    similarity_score: float
    threshold_used: float


class IdentifyResponse(BaseModel):
    """Response model for identification endpoint."""
    match: bool
    status: str  # APPROVED, MANUAL_REVIEW, REJECTED, LOCATION_MISMATCH
    cow_name: Optional[str] = None
    confidence: Optional[float] = None
    distance: Optional[float] = None
    distance_km: Optional[float] = None
    message: str


@app.on_event("startup")
async def load_model():
    """
    Load ResNet50 model, image processor, and Pinecone on application startup.
    This ensures the model is loaded only once, not on every request.
    """
    global model, processor, pc, index
    
    print("🔄 Loading ResNet50 feature extractor...")
    model = ResNet50(
        weights='imagenet',
        include_top=False,
        pooling='avg'
    )
    print("✅ ResNet50 loaded successfully!")
    
    print("🔄 Initializing image processor...")
    processor = ImageProcessor()
    print("✅ Image processor initialized!")
    
    print("🔄 Initializing Pinecone...")
    api_key = os.environ.get("PINECONE_API_KEY")
    if not api_key:
        print("⚠️ WARNING: PINECONE_API_KEY not found in environment variables!")
    
    pc = Pinecone(api_key=api_key)
    index_name = "cattle-faces"
    
    # Connect to existing index
    index = pc.Index(index_name)
    print(f"✅ Pinecone initialized! Connected to index '{index_name}'.")
    
    print("🚀 API is ready to accept requests!")


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "message": "🐄 Cattle Muzzle Biometric API",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "register": "POST /register - Register a new cattle muzzle",
            "verify": "POST /verify - Verify cattle identity",
            "identify": "POST /identify - Identify cattle from database"
        }
    }


@app.post("/register", response_model=RegisterResponse)
async def register_cattle(
    file: UploadFile = File(...),
    cow_name: str = Form(..., description="Name of the cow"),
    latitude: float = Form(..., description="GPS Latitude"),
    longitude: float = Form(..., description="GPS Longitude")
):
    """
    Register a new cattle muzzle image in the vector database.
    """
    try:
        # Read image bytes
        image_bytes = await file.read()
        
        # Validate file is not empty
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Validate cow_name is not empty
        if not cow_name or cow_name.strip() == "":
            raise HTTPException(status_code=400, detail="Cow name cannot be empty")
        
        # Process image (grayscale + CLAHE + preprocessing)
        processed_image = processor.process_image_bytes(image_bytes)
        
        # Extract and normalize feature vector using ResNet50
        feature_vector = processor.get_normalized_embedding(model, processed_image)
        
        # Generate unique cow ID
        cow_id = str(uuid.uuid4())
        
        print(f"DEBUG: cow_name={cow_name}, lat={latitude}, lon={longitude}")
        
        # Store in Pinecone with metadata
        index.upsert(
            vectors=[{
                "id": cow_id,
                "values": feature_vector.tolist(),
                "metadata": {
                    "name": cow_name.strip(),
                    "lat": float(latitude),
                    "lon": float(longitude)
                }
            }]
        )
        
        print(f"✅ Registered cow '{cow_name}' with ID: {cow_id} at ({latitude}, {longitude})")
        
        return RegisterResponse(
            status="saved",
            cow_id=cow_id,
            cow_name=cow_name.strip(),
            vector_dimensions=len(feature_vector)
        )
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )


@app.post("/verify", response_model=VerifyResponse)
async def verify_cattle(
    image_a: UploadFile = File(..., description="First image for comparison"),
    image_b: UploadFile = File(..., description="Second image for comparison")
):
    """
    Verify cattle identity by comparing two muzzle images.
    """
    try:
        # Read both image files
        image_a_bytes = await image_a.read()
        image_b_bytes = await image_b.read()
        
        # Validate files are not empty
        if len(image_a_bytes) == 0 or len(image_b_bytes) == 0:
            raise HTTPException(status_code=400, detail="One or both files are empty")
        
        # Process both images
        processed_a = processor.process_image_bytes(image_a_bytes)
        processed_b = processor.process_image_bytes(image_b_bytes)
        
        # Extract feature vectors
        vector_a = model.predict(processed_a, verbose=0).flatten()
        vector_b = model.predict(processed_b, verbose=0).flatten()
        
        # Calculate cosine similarity
        similarity_score = calculate_cosine_similarity(vector_a, vector_b)
        
        # Determine match based on threshold
        is_match = similarity_score >= SIMILARITY_THRESHOLD
        
        return VerifyResponse(
            match=is_match,
            similarity_score=float(similarity_score),
            threshold_used=SIMILARITY_THRESHOLD
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during verification: {str(e)}"
        )


@app.post("/identify", response_model=IdentifyResponse)
async def identify_cattle(
    file: UploadFile = File(...),
    current_lat: float = Form(..., description="Current GPS Latitude"),
    current_lon: float = Form(..., description="Current GPS Longitude")
):
    """
    Identify a cattle by searching the vector database with Geo-Fencing.
    """
    try:
        # Read image bytes
        image_bytes = await file.read()
        
        # Validate file is not empty
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Process image (grayscale + CLAHE + preprocessing)
        processed_image = processor.process_image_bytes(image_bytes)
        
        # Extract and normalize feature vector using ResNet50
        feature_vector = processor.get_normalized_embedding(model, processed_image)
        
        # Query Pinecone for nearest neighbor
        results = index.query(
            vector=feature_vector.tolist(),
            top_k=1,
            include_metadata=True
        )
        
        # Extract results
        if results['matches'] and len(results['matches']) > 0:
            match = results['matches'][0]
            score = match['score']  # Pinecone returns cosine similarity directly (0 to 1)
            metadata = match['metadata']
            cow_name = metadata.get('name', 'Unknown')
            
            # Retrieve registered location
            reg_lat = metadata.get('lat')
            reg_lon = metadata.get('lon')
            
            # Calculate physical distance if coordinates exist
            geo_distance_km = None
            location_match = True
            
            if reg_lat is not None and reg_lon is not None:
                geo_distance_km = calculate_distance(current_lat, current_lon, reg_lat, reg_lon)
                if geo_distance_km > MAX_DISTANCE_KM:
                    location_match = False
            
            # Convert score to confidence percentage
            confidence = score * 100.0
            
            # Logic Flow
            if confidence >= MANUAL_REVIEW_THRESHOLD:
                # Face matches (either Auto-Approve or Manual Review)
                
                if not location_match:
                    # Case: Face Match BUT Location Mismatch
                    print(f"❌ LOCATION MISMATCH: {cow_name} is {geo_distance_km:.2f}km away (Limit: {MAX_DISTANCE_KM}km)")
                    return IdentifyResponse(
                        match=False,
                        status="LOCATION_MISMATCH",
                        cow_name=cow_name,
                        confidence=float(confidence),
                        distance=float(1.0 - score), # Return distance as 1-score for compatibility
                        distance_km=float(geo_distance_km),
                        message=f"❌ Face matches, but location is too far ({geo_distance_km:.1f}km)"
                    )
                
                # Location is OK (or unknown), proceed with normal thresholds
                if confidence >= AUTO_APPROVE_THRESHOLD:
                    print(f"✅ APPROVED: {cow_name} (conf: {confidence:.2f}%)")
                    return IdentifyResponse(
                        match=True,
                        status="APPROVED",
                        cow_name=cow_name,
                        confidence=float(confidence),
                        distance=float(1.0 - score),
                        distance_km=float(geo_distance_km) if geo_distance_km else None,
                        message="✅ Strong Match"
                    )
                else:
                    print(f"⚠️ MANUAL_REVIEW: {cow_name} (conf: {confidence:.2f}%)")
                    return IdentifyResponse(
                        match=True,
                        status="MANUAL_REVIEW",
                        cow_name=cow_name,
                        confidence=float(confidence),
                        distance=float(1.0 - score),
                        distance_km=float(geo_distance_km) if geo_distance_km else None,
                        message="⚠️ Potential Match (Verify Visually)"
                    )
            
            else:
                # Case: Low Confidence - Reject
                print(f"❌ REJECTED: Closest was {cow_name} (conf: {confidence:.2f}%)")
                return IdentifyResponse(
                    match=False,
                    status="REJECTED",
                    cow_name=None,
                    confidence=float(confidence),
                    distance=float(1.0 - score),
                    message="❌ No Match Found"
                )
        else:
            return IdentifyResponse(
                match=False,
                status="REJECTED",
                message="No results from database"
            )
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error during identification: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "processor_loaded": processor is not None,
        "pinecone_connected": index is not None
    }


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
