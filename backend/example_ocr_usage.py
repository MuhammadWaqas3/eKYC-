"""
Quick reference example for using Tesseract OCR service.
"""

# Example 1: Direct OCR Service Usage
from services.ocr_service import tesseract_ocr_service

# Extract CNIC data
data = tesseract_ocr_service.extract_cnic_data(
    "uploads/session123_cnic_front.jpg",
    "uploads/session123_cnic_back.jpg"
)

print("Extracted Data:")
print(f"  CNIC Number: {data.get('cnic_number')}")
print(f"  Name: {data.get('name')}")
print(f"  Father's Name: {data.get('father_name')}")
print(f"  Date of Birth: {data.get('dob')}")
print(f"  Gender: {data.get('gender')}")
print(f"  Address: {data.get('address')}")
print(f"  Issue Date: {data.get('issue_date')}")
print(f"  Expiry Date: {data.get('expiry_date')}")


# Example 2: With Validation
from services.validation.cnic_validator import cnic_validator

data = tesseract_ocr_service.extract_cnic_data(
    "uploads/cnic_front.jpg",
    "uploads/cnic_back.jpg"
)

is_valid, errors = cnic_validator.validate_cnic_data(data)

if is_valid:
    print("✓ All data valid!")
else:
    print("✗ Validation errors:")
    for error in errors:
        print(f"  - {error}")


# Example 3: Extract Text Only (Low-level)
text = tesseract_ocr_service.extract_text("uploads/cnic_front.jpg")
print(f"Raw OCR Text:\n{text}")

# Extract specific fields
cnic_number = tesseract_ocr_service.extract_cnic_number(text)
dates = tesseract_ocr_service.extract_dates(text)
name = tesseract_ocr_service.extract_name(text)

print(f"CNIC: {cnic_number}")
print(f"Dates: {dates}")
print(f"Name: {name}")
