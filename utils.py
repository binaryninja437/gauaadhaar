"""
Utility functions for cattle muzzle image processing.

This module contains helper functions for preprocessing muzzle images
and extracting features using deep learning models.
"""

import cv2
import numpy as np
from numpy.linalg import norm
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees) using Haversine formula.
    Returns distance in kilometers.
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input
from io import BytesIO
from PIL import Image


class ImageProcessor:
    """Handles image preprocessing for muzzle biometric identification."""
    
    # CLAHE parameters optimized for muzzle texture enhancement
    CLAHE_CLIP_LIMIT = 4.0
    CLAHE_TILE_GRID_SIZE = (8, 8)
    
    def __init__(self):
        """Initialize the image processor with CLAHE."""
        self.clahe = cv2.createCLAHE(
            clipLimit=self.CLAHE_CLIP_LIMIT,
            tileGridSize=self.CLAHE_TILE_GRID_SIZE
        )
    
    def process_image_bytes(self, image_bytes: bytes) -> np.ndarray:
        """
        Process image bytes: convert to grayscale, apply CLAHE, and prepare for ResNet50.
        
        Args:
            image_bytes: Raw image bytes from uploaded file
            
        Returns:
            Preprocessed image array ready for ResNet50 (224x224x3)
        """
        # Convert bytes to PIL Image
        pil_image = Image.open(BytesIO(image_bytes))
        
        # Convert PIL to numpy array
        img_array = np.array(pil_image)
        
        # Handle different image formats
        if len(img_array.shape) == 2:
            # Already grayscale
            gray = img_array
        elif len(img_array.shape) == 3:
            if img_array.shape[2] == 4:
                # RGBA - convert to RGB first
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
                gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            elif img_array.shape[2] == 3:
                # RGB - convert to BGR then grayscale
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            else:
                gray = img_array
        else:
            raise ValueError(f"Unexpected image shape: {img_array.shape}")
        
        # Apply CLAHE enhancement
        enhanced = self.clahe.apply(gray)
        
        # Convert back to 3-channel for ResNet50 (expects RGB)
        enhanced_rgb = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)
        
        # Resize to 224x224 for ResNet50
        resized = cv2.resize(enhanced_rgb, (224, 224))
        
        # Convert to array and add batch dimension
        img_array = np.expand_dims(resized, axis=0)
        
        # Preprocess for ResNet50
        preprocessed = preprocess_input(img_array)
        
        return preprocessed
    
    def process_image_file(self, file_path: str) -> np.ndarray:
        """
        Process image from file path.
        
        Args:
            file_path: Path to image file
            
        Returns:
            Preprocessed image array ready for ResNet50
        """
        with open(file_path, 'rb') as f:
            image_bytes = f.read()
        return self.process_image_bytes(image_bytes)
    
    def get_normalized_embedding(self, model, preprocessed_image: np.ndarray) -> np.ndarray:
        """
        Extract and normalize embedding vector from preprocessed image.
        
        Args:
            model: ResNet50 model
            preprocessed_image: Preprocessed image array
            
        Returns:
            L2-normalized feature vector
        """
        # Get raw embedding from model
        raw_vector = model.predict(preprocessed_image, verbose=0)
        raw_vector = raw_vector.flatten()
        
        # L2 normalize the vector (ensures all vectors are on same scale)
        normalized_vector = raw_vector / norm(raw_vector)
        
        return normalized_vector


def calculate_cosine_similarity(vector1: np.ndarray, vector2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two feature vectors.
    
    Args:
        vector1: First feature vector
        vector2: Second feature vector
        
    Returns:
        Cosine similarity score (0 to 1)
    """
    # Normalize vectors
    vec1_norm = vector1 / np.linalg.norm(vector1)
    vec2_norm = vector2 / np.linalg.norm(vector2)
    
    # Calculate cosine similarity
    similarity = np.dot(vec1_norm, vec2_norm)
    
    return float(similarity)
