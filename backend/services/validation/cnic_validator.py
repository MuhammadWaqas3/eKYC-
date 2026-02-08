"""
CNIC data validator for Pakistani ID cards.
Validates format and cross-checks data.
"""
import re
from datetime import datetime
from typing import Tuple, List, Optional, Dict
from difflib import SequenceMatcher


class CNICValidator:
    """Validator for Pakistani CNIC data."""
    
    # CNIC format: XXXXX-XXXXXXX-X
    CNIC_PATTERN = re.compile(r'^\d{5}-\d{7}-\d$')
    
    # Minimum age for account opening
    MIN_AGE = 18
    
    def validate_cnic_format(self, cnic_number: str) -> Tuple[bool, Optional[str]]:
        """
        Validate CNIC number format.
        
        Args:
            cnic_number: CNIC number string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not cnic_number:
            return False, "CNIC number is required"
        
        # Remove spaces
        cnic_cleaned = cnic_number.strip().replace(' ', '')
        
        # Check format
        if not self.CNIC_PATTERN.match(cnic_cleaned):
            return False, "Invalid CNIC format. Should be XXXXX-XXXXXXX-X"
        
        return True, None
    
    def validate_date(self, date_str: str, date_type: str = "date") -> Tuple[bool, Optional[str], Optional[datetime]]:
        """
        Validate date string.
        
        Args:
            date_str: Date string (DD.MM.YYYY or DD/MM/YYYY)
            date_type: Type of date for error message
            
        Returns:
            Tuple of (is_valid, error_message, parsed_date)
        """
        if not date_str:
            return False, f"{date_type} is required", None
        
        # Try both formats
        for fmt in ['%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y']:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return True, None, parsed_date
            except ValueError:
                continue
        
        return False, f"Invalid {date_type} format", None
    
    def validate_age(self, dob_str: str) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Validate age based on date of birth.
        
        Args:
            dob_str: Date of birth string
            
        Returns:
            Tuple of (is_valid, error_message, age)
        """
        is_valid, error, dob = self.validate_date(dob_str, "date of birth")
        
        if not is_valid:
            return False, error, None
        
        # Calculate age
        today = datetime.now()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        
        # Check minimum age
        if age < self.MIN_AGE:
            return False, f"Must be at least {self.MIN_AGE} years old to open an account", age
        
        return True, None, age
    
    def validate_expiry(self, expiry_str: str) -> Tuple[bool, Optional[str]]:
        """
        Validate CNIC expiry date.
        
        Args:
            expiry_str: Expiry date string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        is_valid, error, expiry_date = self.validate_date(expiry_str, "expiry date")
        
        if not is_valid:
            return False, error
        
        # Check if expired
        if expiry_date < datetime.now():
            return False, "CNIC has expired. Please renew your CNIC."
        
        return True, None
    
    def fuzzy_match_name(self, name1: str, name2: str, threshold: float = 0.8) -> Tuple[bool, float]:
        """
        Fuzzy match two names using Levenshtein distance.
        
        Args:
            name1: First name
            name2: Second name
            threshold: Similarity threshold (0-1)
            
        Returns:
            Tuple of (is_match, similarity_score)
        """
        if not name1 or not name2:
            return False, 0.0
        
        # Normalize names
        name1_norm = name1.lower().strip()
        name2_norm = name2.lower().strip()
        
        # Calculate similarity
        similarity = SequenceMatcher(None, name1_norm, name2_norm).ratio()
        
        # Check threshold
        is_match = similarity >= threshold
        
        return is_match, similarity
    
    def cross_validate_data(
        self,
        ocr_data: Dict[str, str],
        user_data: Dict[str, str]
    ) -> Tuple[bool, List[str]]:
        """
        Cross-validate OCR extracted data with user-provided data.
        
        Args:
            ocr_data: Data extracted from CNIC via OCR
            user_data: Data provided by user during chat
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate name match
        if 'name' in ocr_data and 'name' in user_data:
            is_match, similarity = self.fuzzy_match_name(
                ocr_data['name'],
                user_data['name']
            )
            
            if not is_match:
                errors.append(
                    f"Name mismatch: CNIC shows '{ocr_data['name']}' "
                    f"but you provided '{user_data['name']}' (similarity: {similarity:.2f})"
                )
        
        # Note: Phone and email are not on CNIC, so we skip those validations
        
        # Overall validation
        is_valid = len(errors) == 0
        
        return is_valid, errors
    
    def validate_cnic_data(
        self,
        cnic_data: Dict[str, Optional[str]]
    ) -> Tuple[bool, List[str]]:
        """
        Comprehensive validation of all CNIC data.
        
        Args:
            cnic_data: Dictionary with CNIC data
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate CNIC number
        if 'cnic_number' in cnic_data:
            is_valid, error = self.validate_cnic_format(cnic_data['cnic_number'])
            if not is_valid:
                errors.append(error)
        else:
            errors.append("CNIC number not found")
        
        # Validate date of birth and age
        if 'dob' in cnic_data and cnic_data['dob']:
            is_valid, error, age = self.validate_age(cnic_data['dob'])
            if not is_valid:
                errors.append(error)
        else:
            errors.append("Date of birth not found")
        
        # Validate expiry date
        if 'expiry_date' in cnic_data and cnic_data['expiry_date']:
            is_valid, error = self.validate_expiry(cnic_data['expiry_date'])
            if not is_valid:
                errors.append(error)
        else:
            errors.append("CNIC expiry date not found")
        
        # Check required fields
        required_fields = ['name', 'cnic_number', 'dob']
        for field in required_fields:
            if field not in cnic_data or not cnic_data[field]:
                errors.append(f"Required field '{field}' is missing")
        
        # Overall validation
        is_valid = len(errors) == 0
        
        return is_valid, errors


# Global CNIC validator instance
cnic_validator = CNICValidator()
