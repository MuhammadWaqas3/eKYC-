"""
Tesseract OCR extraction service for Pakistani CNIC.
Extracts text from CNIC front and back images using Tesseract OCR.
"""
import pytesseract
import cv2
import re
import numpy as np
import os
from typing import Dict, Optional, List, Tuple
from PIL import Image


class TesseractOCRService:
    """Service for extracting data from Pakistani CNIC using Tesseract OCR."""
    
    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize Tesseract OCR service.
        
        Args:
            tesseract_cmd: Path to tesseract executable (optional, uses system default if None)
        """
        # Set Tesseract command path if provided (Windows typically: C:\\Program Files\\Tesseract-OCR\\tesseract.exe)
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        # CNIC number pattern (XXXXX-XXXXXXX-X)
        self.cnic_pattern = re.compile(r'\d{5}-\d{7}-\d')
        
        # Date pattern (DD.MM.YYYY or DD/MM/YYYY or DD-MM-YYYY)
        self.date_pattern = re.compile(r'\d{2}[./-]\d{2}[./-]\d{4}')
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for better OCR results.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Preprocessed image as numpy array
        """
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                print(f"Error: Could not read image from {image_path}")
                return np.zeros((100, 100), dtype=np.uint8)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Resize if image is too small (improves OCR accuracy)
            height, width = gray.shape
            if width < 1000:
                scale_factor = 1000 / width
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
            
            # Apply adaptive thresholding for better text extraction
            binary = cv2.adaptiveThreshold(
                denoised,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )
            
            # Apply morphological operations to clean up
            kernel = np.ones((1, 1), np.uint8)
            processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            return processed
            
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return np.zeros((100, 100), dtype=np.uint8)
    
    def extract_text(self, image_path: str, lang: str = 'eng+urd') -> str:
        """
        Extract all text from image using Tesseract.
        
        Args:
            image_path: Path to image file
            lang: Language(s) for OCR (default: 'eng+urd' for English and Urdu)
            
        Returns:
            Extracted text as string
        """
        try:
            # Preprocess image
            processed_img = self.preprocess_image(image_path)
            
            # Configure Tesseract
            custom_config = r'--oem 3 --psm 6'  # OEM 3 = LSTM, PSM 6 = Assume uniform block of text
            
            # Extract text
            text = pytesseract.image_to_string(
                processed_img,
                lang=lang,
                config=custom_config
            )
            
            return text
            
        except pytesseract.TesseractNotFoundError:
            print("ERROR: Tesseract is not installed or not in PATH")
            print("Please install Tesseract OCR from: https://github.com/tesseract-ocr/tesseract")
            return ""
        except Exception as e:
            print(f"Error extracting text: {e}")
            import traceback
            print(traceback.format_exc())
            return ""
    
    def extract_cnic_number(self, text: str) -> Optional[str]:
        """
        Extract CNIC number from text.
        
        Args:
            text: OCR extracted text
            
        Returns:
            CNIC number if found, None otherwise
        """
        # Remove spaces and extra characters
        cleaned_text = text.replace(' ', '').replace('\n', ' ')
        
        # Search for CNIC pattern
        match = self.cnic_pattern.search(cleaned_text)
        if match:
            return match.group()
        
        # Try to fix common OCR errors (O->0, I->1, etc.)
        fixed_text = cleaned_text.replace('O', '0').replace('o', '0').replace('I', '1').replace('l', '1')
        match = self.cnic_pattern.search(fixed_text)
        if match:
            return match.group()
        
        return None
    
    def extract_dates(self, text: str) -> List[str]:
        """
        Extract all dates from text.
        
        Args:
            text: OCR extracted text
            
        Returns:
            List of dates found
        """
        dates = self.date_pattern.findall(text)
        return dates
    
    def extract_name(self, text: str) -> Optional[str]:
        """
        Extract name from text (heuristic-based).
        
        Args:
            text: OCR extracted text
            
        Returns:
            Name if found, None otherwise
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Keywords that indicate the name field (English and Urdu)
        name_keywords = ['name', 'نام']
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check if line contains name keyword
            if any(keyword in line_lower for keyword in name_keywords):
                # Name might be on the same line or next line
                # Check same line first
                for keyword in name_keywords:
                    if keyword in line_lower:
                        # Extract text after the keyword
                        parts = line.split(keyword, 1)
                        if len(parts) > 1:
                            candidate = parts[1].strip(':').strip()
                            if len(candidate) > 2 and not candidate.isdigit():
                                return candidate
                
                # Check next line
                if i + 1 < len(lines):
                    candidate = lines[i + 1].strip()
                    if len(candidate) > 2 and not candidate.isdigit():
                        return candidate
        
        # Fallback: Find first reasonably long text that looks like a name
        # (Not a label, not a CNIC number, not too short)
        exclude_keywords = ['identity', 'card', 'pakistan', 'government', 'birth', 'date', 'issue', 'expiry', 'شناختی', 'کارڈ']
        for line in lines:
            line_clean = line.strip()
            if (len(line_clean) > 5 and 
                not any(keyword in line_clean.lower() for keyword in exclude_keywords) and
                not self.cnic_pattern.search(line_clean) and
                not line_clean.replace('.', '').replace('/', '').replace('-', '').isdigit()):
                return line_clean
        
        return None
    
    def extract_father_name(self, text: str) -> Optional[str]:
        """
        Extract father's name from text.
        
        Args:
            text: OCR extracted text
            
        Returns:
            Father's name if found, None otherwise
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Keywords for father/husband name (English and Urdu)
        father_keywords = ['father', 'husband', 'والد', 'شوہر']
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check if line contains father keyword
            if any(keyword in line_lower for keyword in father_keywords):
                # Extract from same line or next line
                for keyword in father_keywords:
                    if keyword in line_lower:
                        parts = line.split(keyword, 1)
                        if len(parts) > 1:
                            candidate = parts[1].strip(':').strip()
                            if len(candidate) > 2:
                                return candidate
                
                # Check next line
                if i + 1 < len(lines):
                    candidate = lines[i + 1].strip()
                    if len(candidate) > 2 and not candidate.isdigit():
                        return candidate
        
        return None
    
    def extract_gender(self, text: str) -> Optional[str]:
        """
        Extract gender from text.
        
        Args:
            text: OCR extracted text
            
        Returns:
            'M' or 'F' if found, None otherwise
        """
        text_lower = text.lower()
        
        # Check for gender indicators
        if 'male' in text_lower and 'female' not in text_lower:
            return 'M'
        elif 'female' in text_lower:
            return 'F'
        elif ' m ' in text_lower or '\nm\n' in text_lower:
            return 'M'
        elif ' f ' in text_lower or '\nf\n' in text_lower:
            return 'F'
        
        return None
    
    def process_front_image(self, image_path: str) -> Dict[str, Optional[str]]:
        """
        Extract data from CNIC front image.
        
        Args:
            image_path: Path to front image
            
        Returns:
            Dictionary with extracted data
        """
        try:
            # Extract text
            text = self.extract_text(image_path)
            
            if not text:
                print("Warning: No text extracted from front image")
                return {}
            
            # Extract individual fields
            cnic_number = self.extract_cnic_number(text)
            name = self.extract_name(text)
            dates = self.extract_dates(text)
            gender = self.extract_gender(text)
            
            # First date is usually DOB, second is issue date
            dob = dates[0] if len(dates) > 0 else None
            issue_date = dates[1] if len(dates) > 1 else None
            
            return {
                'cnic_number': cnic_number,
                'name': name,
                'dob': dob,
                'gender': gender,
                'issue_date': issue_date
            }
            
        except Exception as e:
            print(f"Error processing front image: {e}")
            import traceback
            print(traceback.format_exc())
            return {}
    
    def process_back_image(self, image_path: str) -> Dict[str, Optional[str]]:
        """
        Extract data from CNIC back image.
        
        Args:
            image_path: Path to back image
            
        Returns:
            Dictionary with extracted data
        """
        try:
            # Extract text
            text = self.extract_text(image_path)
            
            if not text:
                print("Warning: No text extracted from back image")
                return {}
            
            # Extract fields
            father_name = self.extract_father_name(text)
            dates = self.extract_dates(text)
            
            # Usually the first date on back is expiry date
            expiry_date = dates[0] if dates else None
            
            # Extract address (usually one of the longer text blocks)
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            address = None
            max_len = 0
            
            exclude_keywords = ['father', 'husband', 'address', 'date', 'signature', 'والد', 'شوہر', 'پتہ']
            
            for line in lines:
                # Look for longest line that's not a label
                if (len(line) > max_len and 
                    len(line) > 15 and 
                    not any(keyword in line.lower() for keyword in exclude_keywords)):
                    address = line
                    max_len = len(line)
            
            return {
                'father_name': father_name,
                'address': address,
                'expiry_date': expiry_date
            }
            
        except Exception as e:
            print(f"Error processing back image: {e}")
            import traceback
            print(traceback.format_exc())
            return {}
    
    def extract_cnic_data(
        self,
        front_image_path: str,
        back_image_path: str
    ) -> Dict[str, Optional[str]]:
        """
        Extract complete CNIC data from front and back images.
        
        Args:
            front_image_path: Path to front image
            back_image_path: Path to back image
            
        Returns:
            Dictionary with all extracted CNIC data
        """
        try:
            # Check if files exist
            if not os.path.exists(front_image_path):
                print(f"Error: Front image not found at {front_image_path}")
                return {}
            
            if not os.path.exists(back_image_path):
                print(f"Error: Back image not found at {back_image_path}")
                return {}
            
            # Process both images
            print(f"Processing front image: {front_image_path}")
            front_data = self.process_front_image(front_image_path)
            
            print(f"Processing back image: {back_image_path}")
            back_data = self.process_back_image(back_image_path)
            
            # Combine data from both images
            cnic_data = {**front_data, **back_data}
            
            # Log extracted data for debugging
            print(f"Extracted CNIC data: {cnic_data}")
            
            return cnic_data
            
        except Exception as e:
            print(f"CRITICAL ERROR in extract_cnic_data: {e}")
            import traceback
            print(traceback.format_exc())
            return {}


# Global Tesseract OCR service instance
# Note: If Tesseract is not in PATH, set the path explicitly:
# tesseract_ocr_service = TesseractOCRService(tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe')
tesseract_ocr_service = TesseractOCRService()
