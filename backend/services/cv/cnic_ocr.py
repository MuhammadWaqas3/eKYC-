"""
CNIC OCR extraction service using EasyOCR.
Extracts text from Pakistani CNIC front and back images.
"""
import easyocr
import cv2
import re
import numpy as np
import os
import traceback
from typing import Dict, Optional, Tuple, List
from PIL import Image
from datetime import datetime

# Patch for Pillow 10+ compatibility (ANTIALIAS was removed)
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS


class CNICOCRService:
    """Service for extracting data from Pakistani CNIC using OCR."""
    
    def __init__(self):
        """Initialize EasyOCR reader."""
        # Initialize reader for English and Urdu
        self.reader = easyocr.Reader(['en', 'ur'], gpu=False)
        
        # CNIC number pattern (XXXXX-XXXXXXX-X)
        self.cnic_pattern = re.compile(r'\d{5}-\d{7}-\d')
        
        # Date pattern (DD.MM.YYYY or DD/MM/YYYY)
        self.date_pattern = re.compile(r'\d{2}[./]\d{2}[./]\d{4}')
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for better OCR results.
        Optimized for speed and accuracy.
        """
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            return np.zeros((100, 100, 3), dtype=np.uint8)

        # Resizing often helps OCR more than thresholding for EasyOCR
        height, width = img.shape[:2]
        if width < 1000:
            img = cv2.resize(img, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC)
        
        # Simple grayscale and mild sharpening
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Simple sharpening filter
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(gray, -1, kernel)
        
        return sharpened
    
    def extract_text(self, image_path: str) -> List[Tuple[str, float]]:
        """
        Extract all text from image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of (text, confidence) tuples
        """
        # Preprocess image
        processed_img = self.preprocess_image(image_path)
        
        # Perform OCR
        results = self.reader.readtext(processed_img)
        
        # Extract text and confidence
        text_results = [(text, conf) for (bbox, text, conf) in results]
        
        return text_results
    
    def extract_cnic_number(self, text_results: List[Tuple[str, float]]) -> Optional[str]:
        """
        Extract CNIC number from OCR results.
        
        Args:
            text_results: List of (text, confidence) tuples
            
        Returns:
            CNIC number if found, None otherwise
        """
        for text, conf in text_results:
            # Remove spaces and special characters
            cleaned = re.sub(r'[^\d-]', '', text)
            
            # Check if matches CNIC pattern
            match = self.cnic_pattern.search(cleaned)
            if match:
                return match.group()
        
        return None
    
    def extract_dates(self, text_results: List[Tuple[str, float]]) -> List[str]:
        """
        Extract all dates from OCR results.
        
        Args:
            text_results: List of (text, confidence) tuples
            
        Returns:
            List of dates found
        """
        dates = []
        for text, conf in text_results:
            matches = self.date_pattern.findall(text)
            dates.extend(matches)
        
        return dates
    
    def extract_name(self, text_results: List[Tuple[str, float]]) -> Optional[str]:
        """
        Extract name from OCR results (heuristic-based).
        """
        # Urdu keywords for Name: "نام"
        name_keywords = ['name', 'نام']
        
        for i, (text, conf) in enumerate(text_results):
            text_lower = text.lower().strip()
            if any(keyword in text_lower for keyword in name_keywords):
                # Try to get next few items if they look like a name
                for offset in range(1, 3):
                    if i + offset < len(text_results):
                        candidate = text_results[i + offset][0].strip()
                        # Name shouldn't be too short or just numbers
                        if len(candidate) > 2 and not candidate.isdigit():
                            return candidate
        
        # Fallback: return first reasonably long text that isn't a known label
        labels = ['identity', 'card', 'pakistan', 'government', 'birth', 'date', 'issue', 'expiry']
        for text, conf in text_results:
            text_clean = text.strip()
            if len(text_clean) > 5 and not any(l in text_clean.lower() for l in labels) and not self.cnic_pattern.search(text_clean):
                return text_clean
        
        return None

    def extract_father_name(self, text_results: List[Tuple[str, float]]) -> Optional[str]:
        """Extract father's name with Urdu support."""
        keywords = ['father', 'husband', 'والد', 'شوہر', 'نام']
        
        for i, (text, conf) in enumerate(text_results):
            text_lower = text.lower().strip()
            # Often labels like "Father Name" or "والد کا نام"
            if ('father' in text_lower or 'والد' in text_lower) and i + 1 < len(text_results):
                candidate = text_results[i + 1][0].strip()
                if len(candidate) > 2:
                    return candidate
        return None

    def process_front_image(self, image_path: str) -> Dict[str, Optional[str]]:
        """Extract data from CNIC front image."""
        try:
            text_results = self.extract_text(image_path)
            all_text = ' '.join([text for text, conf in text_results])
            
            return {
                'cnic_number': self.extract_cnic_number(text_results),
                'name': self.extract_name(text_results),
                'dob': (self.extract_dates(text_results) + [None])[0],
                'gender': 'M' if any(x in all_text.lower() for x in ['male', ' m ']) else 'F' if any(x in all_text.lower() for x in ['female', ' f ']) else None,
                'issue_date': (self.extract_dates(text_results) + [None, None])[1]
            }
        except Exception as e:
            print(f"Error processing front image: {e}")
            return {}

    def process_back_image(self, image_path: str) -> Dict[str, Optional[str]]:
        """Extract data from CNIC back image."""
        try:
            text_results = self.extract_text(image_path)
            
            # Father's name
            father_name = self.extract_father_name(text_results)
            
            # Expiry date
            dates = self.extract_dates(text_results)
            expiry_date = dates[0] if dates else None
            
            # Address (usually the largest text block on back)
            address = None
            max_len = 0
            for text, conf in text_results:
                if len(text) > max_len and conf > 0.4:
                    # Filter out short strings and common labels
                    if len(text) > 15:
                        address = text
                        max_len = len(text)

            return {
                'father_name': father_name,
                'address': address,
                'expiry_date': expiry_date
            }
        except Exception as e:
            print(f"Error processing back image: {e}")
            return {}

    def extract_cnic_data(
        self,
        front_image_path: str,
        back_image_path: str
    ) -> Dict[str, Optional[str]]:
        """Extract complete CNIC data from front and back images."""
        try:
            if not os.path.exists(front_image_path) or not os.path.exists(back_image_path):
                print(f"Image files not found: {front_image_path} or {back_image_path}")
                return {}

            # Process both images
            front_data = self.process_front_image(front_image_path)
            back_data = self.process_back_image(back_image_path)
            
            # Combine data
            cnic_data = {**front_data, **back_data}
            return cnic_data
        except Exception as e:
            import traceback
            print(f"CRITICAL ERROR in extract_cnic_data: {e}")
            print(traceback.format_exc())
            return {}

# Global OCR service instance
cnic_ocr_service = CNICOCRService()
