"""
OCR.space API service for enhanced CNIC text extraction.
Provides cloud-based OCR with high accuracy for Pakistani CNIC documents.
"""
import requests
import os
import re
from typing import Dict, Optional, List, Tuple
from config import settings


class OCRSpaceService:
    """Service for extracting CNIC data using OCR.space API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OCR.space service.
        
        Args:
            api_key: OCR.space API key (optional, uses env var if None)
        """
        self.api_key = api_key or os.getenv('OCRSPACE_API_KEY')
        self.api_url = os.getenv('OCRSPACE_API_BASE_URL', 'https://api.ocr.space/parse/image')
        self.enabled = os.getenv('OCRSPACE_ENABLED', 'true').lower() == 'true'
        
        # CNIC patterns (same as Tesseract)
        self.cnic_pattern = re.compile(r'\d{5}-\d{7}-\d')
        self.date_pattern = re.compile(r'\d{2}[./-]\d{2}[./-]\d{4}')
    
    def extract_text(self, image_path: str, language: str = 'eng') -> str:
        """
        Extract text from image using OCR.space API.
        
        Args:
            image_path: Path to image file
            language: OCR language (eng, ara for Urdu script)
            
        Returns:
            Extracted text as string
        """
        if not self.enabled or not self.api_key:
            print("OCR.space API is disabled or API key not configured")
            return ""
        
        try:
            with open(image_path, 'rb') as f:
                payload = {
                    'apikey': self.api_key,
                    'language': language,
                    'isOverlayRequired': False,
                    'detectOrientation': True,
                    'scale': True,
                    'OCREngine': 2  # Engine 2 for better accuracy
                }
                
                files = {'file': f}
                
                response = requests.post(
                    self.api_url,
                    files=files,
                    data=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get('IsErroredOnProcessing'):
                        error_msg = result.get('ErrorMessage', ['Unknown error'])[0]
                        print(f"OCR.space API error: {error_msg}")
                        return ""
                    
                    # Extract text from parsed results
                    parsed_results = result.get('ParsedResults', [])
                    if parsed_results:
                        text = parsed_results[0].get('ParsedText', '')
                        return text
                    
                    return ""
                else:
                    print(f"OCR.space API request failed with status {response.status_code}")
                    return ""
                    
        except Exception as e:
            print(f"Error calling OCR.space API: {e}")
            import traceback
            print(traceback.format_exc())
            return ""
    
    def extract_cnic_number(self, text: str) -> Optional[str]:
        """Extract CNIC number from text."""
        cleaned_text = text.replace(' ', '').replace('\n', ' ')
        match = self.cnic_pattern.search(cleaned_text)
        if match:
            return match.group()
        
        # Fix common OCR errors
        fixed_text = cleaned_text.replace('O', '0').replace('o', '0').replace('I', '1').replace('l', '1')
        match = self.cnic_pattern.search(fixed_text)
        if match:
            return match.group()
        
        return None
    
    def extract_dates(self, text: str) -> List[str]:
        """Extract all dates from text."""
        return self.date_pattern.findall(text)
    
    def extract_name(self, text: str) -> Optional[str]:
        """Extract name from text (heuristic-based)."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        name_keywords = ['name', 'نام']
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            if any(keyword in line_lower for keyword in name_keywords):
                for keyword in name_keywords:
                    if keyword in line_lower:
                        parts = line.split(keyword, 1)
                        if len(parts) > 1:
                            candidate = parts[1].strip(':').strip()
                            if len(candidate) > 2 and not candidate.isdigit():
                                return candidate
                
                if i + 1 < len(lines):
                    candidate = lines[i + 1].strip()
                    if len(candidate) > 2 and not candidate.isdigit():
                        return candidate
        
        # Fallback
        exclude_keywords = ['identity', 'card', 'pakistan', 'government', 'birth', 'date', 'issue', 'expiry']
        for line in lines:
            line_clean = line.strip()
            if (len(line_clean) > 5 and 
                not any(keyword in line_clean.lower() for keyword in exclude_keywords) and
                not self.cnic_pattern.search(line_clean) and
                not line_clean.replace('.', '').replace('/', '').replace('-', '').isdigit()):
                return line_clean
        
        return None
    
    def extract_father_name(self, text: str) -> Optional[str]:
        """Extract father's name from text."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        father_keywords = ['father', 'husband', 'والد', 'شوہر']
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            if any(keyword in line_lower for keyword in father_keywords):
                for keyword in father_keywords:
                    if keyword in line_lower:
                        parts = line.split(keyword, 1)
                        if len(parts) > 1:
                            candidate = parts[1].strip(':').strip()
                            if len(candidate) > 2:
                                return candidate
                
                if i + 1 < len(lines):
                    candidate = lines[i + 1].strip()
                    if len(candidate) > 2 and not candidate.isdigit():
                        return candidate
        
        return None
    
    def extract_gender(self, text: str) -> Optional[str]:
        """Extract gender from text."""
        text_lower = text.lower()
        
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
        """Extract data from CNIC front image."""
        try:
            text = self.extract_text(image_path)
            
            if not text:
                return {}
            
            cnic_number = self.extract_cnic_number(text)
            name = self.extract_name(text)
            dates = self.extract_dates(text)
            gender = self.extract_gender(text)
            
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
            print(f"Error processing front image with OCR.space: {e}")
            return {}
    
    def process_back_image(self, image_path: str) -> Dict[str, Optional[str]]:
        """Extract data from CNIC back image."""
        try:
            text = self.extract_text(image_path)
            
            if not text:
                return {}
            
            father_name = self.extract_father_name(text)
            dates = self.extract_dates(text)
            
            expiry_date = dates[0] if dates else None
            
            # Extract address
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            address = None
            max_len = 0
            
            exclude_keywords = ['father', 'husband', 'address', 'date', 'signature', 'والد', 'شوہر', 'پتہ']
            
            for line in lines:
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
            print(f"Error processing back image with OCR.space: {e}")
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
            if not os.path.exists(front_image_path):
                print(f"Error: Front image not found at {front_image_path}")
                return {}
            
            if not os.path.exists(back_image_path):
                print(f"Error: Back image not found at {back_image_path}")
                return {}
            
            print(f"Processing front image with OCR.space: {front_image_path}")
            front_data = self.process_front_image(front_image_path)
            
            print(f"Processing back image with OCR.space: {back_image_path}")
            back_data = self.process_back_image(back_image_path)
            
            cnic_data = {**front_data, **back_data}
            
            print(f"OCR.space extracted CNIC data: {cnic_data}")
            
            return cnic_data
            
        except Exception as e:
            print(f"CRITICAL ERROR in OCR.space extract_cnic_data: {e}")
            import traceback
            print(traceback.format_exc())
            return {}
    
    @staticmethod
    def merge_ocr_results(
        tesseract_data: Dict[str, Optional[str]],
        ocrspace_data: Dict[str, Optional[str]]
    ) -> Dict[str, Optional[str]]:
        """
        Merge results from Tesseract and OCR.space for best accuracy.
        Prioritizes non-null values and longer/more complete data.
        
        Args:
            tesseract_data: Data from Tesseract OCR
            ocrspace_data: Data from OCR.space API
            
        Returns:
            Merged dictionary with best available data
        """
        merged = {}
        
        # All possible fields
        all_fields = set(tesseract_data.keys()) | set(ocrspace_data.keys())
        
        for field in all_fields:
            tess_value = tesseract_data.get(field)
            ocr_value = ocrspace_data.get(field)
            
            # If only one has a value, use it
            if tess_value and not ocr_value:
                merged[field] = tess_value
            elif ocr_value and not tess_value:
                merged[field] = ocr_value
            # If both have values, prefer the longer/more complete one
            elif tess_value and ocr_value:
                # For CNIC number, prefer properly formatted one
                if field == 'cnic_number':
                    # Check if matches pattern
                    cnic_pattern = re.compile(r'\d{5}-\d{7}-\d')
                    if cnic_pattern.match(str(tess_value)):
                        merged[field] = tess_value
                    elif cnic_pattern.match(str(ocr_value)):
                        merged[field] = ocr_value
                    else:
                        merged[field] = tess_value  # Default to Tesseract
                # For names and text, prefer longer value
                else:
                    merged[field] = tess_value if len(str(tess_value)) >= len(str(ocr_value)) else ocr_value
            else:
                merged[field] = None
        
        return merged


# Global OCR.space service instance
ocrspace_service = OCRSpaceService()
