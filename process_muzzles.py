"""
Cattle Muzzle Image Preprocessing Script
==========================================
This script processes cattle muzzle images to enhance biometric features
(ridges and beads) using CLAHE (Contrast Limited Adaptive Histogram Equalization).

Author: Senior Computer Vision Engineer
Purpose: Muzzle Fingerprint Biometric Identification System
"""

import os
import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, List


class MuzzleProcessor:
    """Handles preprocessing of cattle muzzle images for biometric identification."""
    
    # Supported image extensions
    VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
    
    # CLAHE parameters optimized for muzzle texture enhancement
    CLAHE_CLIP_LIMIT = 4.0
    CLAHE_TILE_GRID_SIZE = (8, 8)
    
    def __init__(self, input_dir: str, output_dir: str = "processed_results"):
        """
        Initialize the MuzzleProcessor.
        
        Args:
            input_dir: Path to directory containing muzzle images
            output_dir: Path to directory for saving processed images
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.processed_count = 0
        self.error_count = 0
        self.error_files = []
        
        # Create CLAHE object
        self.clahe = cv2.createCLAHE(
            clipLimit=self.CLAHE_CLIP_LIMIT,
            tileGridSize=self.CLAHE_TILE_GRID_SIZE
        )
        
    def _validate_input_dir(self) -> bool:
        """Validate that input directory exists."""
        if not self.input_dir.exists():
            print(f"❌ Error: Input directory '{self.input_dir}' does not exist.")
            return False
        if not self.input_dir.is_dir():
            print(f"❌ Error: '{self.input_dir}' is not a directory.")
            return False
        return True
    
    def _create_output_dir(self) -> None:
        """Create output directory if it doesn't exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Output directory: {self.output_dir.absolute()}")
    
    def _find_images(self) -> List[Path]:
        """
        Recursively find all valid image files in input directory.
        
        Returns:
            List of Path objects for valid image files
        """
        image_files = []
        for ext in self.VALID_EXTENSIONS:
            # Case-insensitive search
            image_files.extend(self.input_dir.rglob(f"*{ext}"))
            image_files.extend(self.input_dir.rglob(f"*{ext.upper()}"))
        
        return sorted(set(image_files))  # Remove duplicates and sort
    
    def _apply_clahe(self, gray_image: np.ndarray) -> np.ndarray:
        """
        Apply CLAHE to enhance muzzle texture features.
        
        Args:
            gray_image: Grayscale input image
            
        Returns:
            Enhanced image with CLAHE applied
        """
        return self.clahe.apply(gray_image)
    
    def _create_comparison_image(
        self, 
        original_gray: np.ndarray, 
        enhanced: np.ndarray
    ) -> np.ndarray:
        """
        Create side-by-side comparison image with labels.
        
        Args:
            original_gray: Original grayscale image
            enhanced: CLAHE-enhanced image
            
        Returns:
            Combined comparison image
        """
        # Ensure both images have the same height
        height, width = original_gray.shape
        
        # Create copies to avoid modifying originals
        left_img = original_gray.copy()
        right_img = enhanced.copy()
        
        # Add text labels
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.8
        font_thickness = 2
        text_color = 255  # White text
        
        # Calculate text position (top-left with padding)
        padding = 20
        
        # Add "Original" label
        cv2.putText(
            left_img,
            "Original",
            (padding, padding + 25),
            font,
            font_scale,
            text_color,
            font_thickness,
            cv2.LINE_AA
        )
        
        # Add "Enhanced" label
        cv2.putText(
            right_img,
            "Enhanced",
            (padding, padding + 25),
            font,
            font_scale,
            text_color,
            font_thickness,
            cv2.LINE_AA
        )
        
        # Combine side-by-side
        comparison = np.hstack([left_img, right_img])
        
        return comparison
    
    def _process_single_image(self, image_path: Path) -> bool:
        """
        Process a single muzzle image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Step A: Load and convert to grayscale
            image = cv2.imread(str(image_path))
            
            if image is None:
                raise ValueError(f"Failed to load image (possibly corrupted)")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Step B: Apply CLAHE enhancement
            enhanced = self._apply_clahe(gray)
            
            # Step C: Create side-by-side comparison
            comparison = self._create_comparison_image(gray, enhanced)
            
            # Generate output filename
            output_filename = image_path.stem + "_enhanced" + image_path.suffix
            output_path = self.output_dir / output_filename
            
            # Save the comparison image
            cv2.imwrite(str(output_path), comparison)
            
            self.processed_count += 1
            return True
            
        except Exception as e:
            self.error_count += 1
            self.error_files.append((image_path.name, str(e)))
            print(f"⚠ Error processing '{image_path.name}': {e}")
            return False
    
    def process_all(self) -> None:
        """Process all images in the input directory."""
        print("=" * 70)
        print("🐄 Cattle Muzzle Image Preprocessing")
        print("=" * 70)
        
        # Validate input directory
        if not self._validate_input_dir():
            return
        
        # Create output directory
        self._create_output_dir()
        
        # Find all images
        print(f"\n🔍 Scanning for images in: {self.input_dir.absolute()}")
        image_files = self._find_images()
        
        if not image_files:
            print(f"❌ No valid image files found in '{self.input_dir}'")
            print(f"   Supported formats: {', '.join(self.VALID_EXTENSIONS)}")
            return
        
        print(f"✓ Found {len(image_files)} image(s)")
        
        # Process each image
        print(f"\n🔄 Processing images...")
        print("-" * 70)
        
        for idx, image_path in enumerate(image_files, 1):
            print(f"[{idx}/{len(image_files)}] Processing: {image_path.name}...", end=" ")
            
            if self._process_single_image(image_path):
                print("✓")
            else:
                print("✗")
        
        # Print summary
        print("-" * 70)
        print(f"\n📊 Summary:")
        print(f"   Processed: {self.processed_count} images")
        print(f"   Errors: {self.error_count}")
        
        if self.error_files:
            print(f"\n⚠ Failed files:")
            for filename, error in self.error_files:
                print(f"   - {filename}: {error}")
        
        if self.processed_count > 0:
            print(f"\n✅ Results saved to: {self.output_dir.absolute()}")
        
        print("=" * 70)


def main():
    """Main entry point for the script."""
    # Configuration
    INPUT_DIR = "archive (7)"
    OUTPUT_DIR = "processed_results"
    
    # Create processor and run
    processor = MuzzleProcessor(INPUT_DIR, OUTPUT_DIR)
    processor.process_all()


if __name__ == "__main__":
    main()
