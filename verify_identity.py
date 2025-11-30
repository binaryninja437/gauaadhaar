"""
Cattle Muzzle Identity Verification Script
===========================================
This script tests the biometric identification system by comparing muzzle patterns
using deep learning feature extraction and cosine similarity.

Author: Senior Computer Vision Engineer
Purpose: Verify that the system can distinguish between individual cattle
"""

import os
import random
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input


class MuzzleIdentityVerifier:
    """Verifies cattle identity using deep learning feature extraction."""
    
    def __init__(self, processed_dir: str = "processed_results"):
        """
        Initialize the verifier with ResNet50 feature extractor.
        
        Args:
            processed_dir: Directory containing processed muzzle images
        """
        self.processed_dir = Path(processed_dir)
        
        # Load pre-trained ResNet50 without top layers (feature extractor)
        print("🔄 Loading ResNet50 feature extractor...")
        self.model = ResNet50(
            weights='imagenet',
            include_top=False,
            pooling='avg'
        )
        print("✅ ResNet50 loaded successfully!\n")
        
        # Group images by cattle ID
        self.cattle_groups = self._group_images_by_cattle()
        
    def _group_images_by_cattle(self):
        """
        Group images by cattle ID (extracted from filename).
        
        Returns:
            Dictionary mapping cattle_id to list of image paths
        """
        cattle_dict = {}
        
        for img_path in self.processed_dir.glob("*_enhanced.jpg"):
            # Extract cattle ID from filename (e.g., "cattle_0100" from "cattle_0100_DSCF3856_enhanced.jpg")
            filename = img_path.name
            parts = filename.split('_')
            
            if len(parts) >= 2:
                cattle_id = f"{parts[0]}_{parts[1]}"  # e.g., "cattle_0100"
                
                if cattle_id not in cattle_dict:
                    cattle_dict[cattle_id] = []
                cattle_dict[cattle_id].append(img_path)
        
        # Filter out cattle with less than 2 images
        cattle_dict = {k: v for k, v in cattle_dict.items() if len(v) >= 2}
        
        print(f"📊 Found {len(cattle_dict)} cattle with multiple images")
        return cattle_dict
    
    def _load_and_preprocess_image(self, img_path: Path):
        """
        Load and preprocess image for ResNet50.
        
        Args:
            img_path: Path to image file
            
        Returns:
            Preprocessed image array
        """
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        return img_array
    
    def _extract_features(self, img_path: Path):
        """
        Extract feature vector (embedding) from image using ResNet50.
        
        Args:
            img_path: Path to image file
            
        Returns:
            Feature vector (1D numpy array)
        """
        img_array = self._load_and_preprocess_image(img_path)
        features = self.model.predict(img_array, verbose=0)
        return features.flatten()
    
    def _calculate_cosine_similarity(self, vec1, vec2):
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First feature vector
            vec2: Second feature vector
            
        Returns:
            Cosine similarity score (0 to 1)
        """
        vec1 = vec1.reshape(1, -1)
        vec2 = vec2.reshape(1, -1)
        similarity = cosine_similarity(vec1, vec2)[0][0]
        return similarity
    
    def _display_results(self, img_paths, similarities, verdict):
        """
        Display the three images side-by-side with similarity scores.
        
        Args:
            img_paths: List of 3 image paths [cow_a_img1, cow_a_img2, cow_b_img1]
            similarities: Dictionary with similarity scores
            verdict: Boolean indicating if test passed
        """
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle('🐄 Cattle Muzzle Identity Verification Test', 
                     fontsize=16, fontweight='bold', y=1.02)
        
        labels = [
            f"Cow A - Image 1\n({img_paths[0].name})",
            f"Cow A - Image 2\n({img_paths[1].name})",
            f"Cow B - Image 1\n({img_paths[2].name})"
        ]
        
        for idx, (img_path, label) in enumerate(zip(img_paths, labels)):
            img = plt.imread(img_path)
            axes[idx].imshow(img)
            axes[idx].set_title(label, fontsize=10, pad=10)
            axes[idx].axis('off')
        
        # Add similarity scores as text annotations
        score1 = similarities['same_cow']
        score2 = similarities['different_cow']
        
        # Arrow and text between Cow A images
        fig.text(0.30, 0.15, f"Similarity: {score1:.4f}\n(Same Cow)", 
                ha='center', fontsize=12, fontweight='bold', 
                color='green' if score1 > 0.8 else 'orange',
                bbox=dict(boxstyle='round', facecolor='white', edgecolor='green' if score1 > 0.8 else 'orange', linewidth=2))
        
        # Arrow and text between Cow A and Cow B
        fig.text(0.70, 0.15, f"Similarity: {score2:.4f}\n(Different Cows)", 
                ha='center', fontsize=12, fontweight='bold',
                color='red' if score2 < 0.6 else 'orange',
                bbox=dict(boxstyle='round', facecolor='white', edgecolor='red' if score2 < 0.6 else 'orange', linewidth=2))
        
        # Add verdict
        verdict_text = "✅ SUCCESS: System can distinguish cows!" if verdict else "❌ FAILED: System cannot reliably distinguish cows"
        verdict_color = 'green' if verdict else 'red'
        
        fig.text(0.5, 0.05, verdict_text, 
                ha='center', fontsize=14, fontweight='bold',
                color=verdict_color,
                bbox=dict(boxstyle='round', facecolor='white', edgecolor=verdict_color, linewidth=3))
        
        plt.tight_layout()
        plt.savefig('verification_results.png', dpi=150, bbox_inches='tight')
        print(f"\n📊 Visualization saved to: verification_results.png")
        plt.show()
    
    def run_verification_test(self):
        """
        Run the identity verification test.
        
        Returns:
            Dictionary with test results
        """
        print("=" * 70)
        print("🔬 Running Cattle Identity Verification Test")
        print("=" * 70)
        
        # Check if we have enough cattle
        if len(self.cattle_groups) < 2:
            print("❌ Error: Need at least 2 different cattle with multiple images each")
            return None
        
        # Step 1: Select Cow A (with at least 2 images)
        cow_a_id = random.choice(list(self.cattle_groups.keys()))
        cow_a_images = self.cattle_groups[cow_a_id]
        
        # Pick 2 random images from Cow A
        cow_a_img1, cow_a_img2 = random.sample(cow_a_images, 2)
        
        # Step 2: Select Cow B (different from Cow A)
        available_cows = [k for k in self.cattle_groups.keys() if k != cow_a_id]
        cow_b_id = random.choice(available_cows)
        cow_b_images = self.cattle_groups[cow_b_id]
        
        # Pick 1 random image from Cow B
        cow_b_img1 = random.choice(cow_b_images)
        
        print(f"\n📸 Selected Images:")
        print(f"   Cow A ({cow_a_id}):")
        print(f"      - Image 1: {cow_a_img1.name}")
        print(f"      - Image 2: {cow_a_img2.name}")
        print(f"   Cow B ({cow_b_id}):")
        print(f"      - Image 1: {cow_b_img1.name}")
        
        # Step 3: Extract features
        print(f"\n🔄 Extracting features using ResNet50...")
        features_a1 = self._extract_features(cow_a_img1)
        features_a2 = self._extract_features(cow_a_img2)
        features_b1 = self._extract_features(cow_b_img1)
        print(f"✅ Feature extraction complete!")
        print(f"   Feature vector size: {features_a1.shape[0]} dimensions")
        
        # Step 4: Calculate cosine similarities
        print(f"\n📐 Calculating Cosine Similarities...")
        similarity_same_cow = self._calculate_cosine_similarity(features_a1, features_a2)
        similarity_diff_cow = self._calculate_cosine_similarity(features_a1, features_b1)
        
        # Step 5: Display results
        print("\n" + "=" * 70)
        print("📊 RESULTS:")
        print("=" * 70)
        print(f"   Score 1 (Cow A Img1 vs Cow A Img2): {similarity_same_cow:.4f}")
        print(f"   Score 2 (Cow A Img1 vs Cow B Img1): {similarity_diff_cow:.4f}")
        print("-" * 70)
        
        # Step 6: Verdict
        verdict = similarity_same_cow > similarity_diff_cow
        
        if verdict:
            print("   ✅ SUCCESS: System can distinguish cows!")
            print(f"      → Same cow similarity ({similarity_same_cow:.4f}) > Different cow similarity ({similarity_diff_cow:.4f})")
        else:
            print("   ❌ FAILED: System cannot reliably distinguish cows")
            print(f"      → Same cow similarity ({similarity_same_cow:.4f}) ≤ Different cow similarity ({similarity_diff_cow:.4f})")
        
        print("=" * 70)
        
        # Step 7: Visualize
        print(f"\n🎨 Generating visualization...")
        similarities = {
            'same_cow': similarity_same_cow,
            'different_cow': similarity_diff_cow
        }
        
        self._display_results(
            [cow_a_img1, cow_a_img2, cow_b_img1],
            similarities,
            verdict
        )
        
        return {
            'cow_a_id': cow_a_id,
            'cow_b_id': cow_b_id,
            'similarity_same_cow': similarity_same_cow,
            'similarity_diff_cow': similarity_diff_cow,
            'verdict': verdict
        }


def main():
    """Main entry point for the verification script."""
    # Create verifier
    verifier = MuzzleIdentityVerifier("processed_results")
    
    # Run verification test
    results = verifier.run_verification_test()
    
    if results:
        print(f"\n🎯 Test Complete!")
        print(f"   Verdict: {'PASS ✅' if results['verdict'] else 'FAIL ❌'}")


if __name__ == "__main__":
    main()
