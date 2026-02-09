"""
Test script to verify Tesseract OCR integration.
Tests CNIC extraction from sample images.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ocr_service import tesseract_ocr_service


def test_tesseract_installation():
    """Test if Tesseract is properly installed."""
    print("=" * 60)
    print("Testing Tesseract Installation")
    print("=" * 60)
    
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✓ Tesseract version: {version}")
        
        # Check available languages
        try:
            import subprocess
            result = subprocess.run(['tesseract', '--list-langs'], capture_output=True, text=True)
            langs = result.stdout
            print(f"\n✓ Available languages:\n{langs}")
            
            if 'eng' in langs:
                print("✓ English language pack found")
            else:
                print("✗ WARNING: English language pack not found!")
            
            if 'urd' in langs:
                print("✓ Urdu language pack found")
            else:
                print("✗ WARNING: Urdu language pack not found!")
                print("  Install from: https://github.com/tesseract-ocr/tessdata")
        except Exception as e:
            print(f"Could not list languages: {e}")
        
        return True
    except Exception as e:
        print(f"✗ ERROR: Tesseract not found or not properly installed")
        print(f"  Error: {e}")
        print("\nInstallation instructions:")
        print("  1. Download Tesseract from: https://github.com/tesseract-ocr/tesseract")
        print("  2. Install and add to PATH")
        print("  3. Install Urdu language pack if needed")
        return False


def test_ocr_service():
    """Test OCR service initialization."""
    print("\n" + "=" * 60)
    print("Testing OCR Service Initialization")
    print("=" * 60)
    
    try:
        # Test service initialization
        print(f"✓ OCR service initialized: {tesseract_ocr_service}")
        print(f"✓ CNIC pattern: {tesseract_ocr_service.cnic_pattern.pattern}")
        print(f"✓ Date pattern: {tesseract_ocr_service.date_pattern.pattern}")
        return True
    except Exception as e:
        print(f"✗ ERROR: Could not initialize OCR service")
        print(f"  Error: {e}")
        return False


def test_cnic_extraction(front_image_path: str = None, back_image_path: str = None):
    """
    Test CNIC data extraction from images.
    
    Args:
        front_image_path: Path to front CNIC image (optional)
        back_image_path: Path to back CNIC image (optional)
    """
    print("\n" + "=" * 60)
    print("Testing CNIC Data Extraction")
    print("=" * 60)
    
    # Use provided paths or default test paths
    if not front_image_path:
        front_image_path = "uploads/test_cnic_front.jpg"
    if not back_image_path:
        back_image_path = "uploads/test_cnic_back.jpg"
    
    # Check if images exist
    if not os.path.exists(front_image_path):
        print(f"⚠ WARNING: Front image not found at: {front_image_path}")
        print("  Please provide actual CNIC images to test extraction")
        return False
    
    if not os.path.exists(back_image_path):
        print(f"⚠ WARNING: Back image not found at: {back_image_path}")
        print("  Please provide actual CNIC images to test extraction")
        return False
    
    print(f"Front image: {front_image_path}")
    print(f"Back image: {back_image_path}")
    print("\nExtracting data...")
    
    try:
        # Extract CNIC data
        extracted_data = tesseract_ocr_service.extract_cnic_data(
            front_image_path,
            back_image_path
        )
        
        # Display results
        print("\n" + "-" * 60)
        print("Extracted Data:")
        print("-" * 60)
        
        if not extracted_data:
            print("✗ No data extracted (check image quality and OCR configuration)")
            return False
        
        for key, value in extracted_data.items():
            status = "✓" if value else "✗"
            print(f"{status} {key}: {value}")
        
        # Validate required fields
        print("\n" + "-" * 60)
        print("Validation:")
        print("-" * 60)
        
        required_fields = ['cnic_number', 'name', 'dob']
        all_present = True
        
        for field in required_fields:
            if field in extracted_data and extracted_data[field]:
                print(f"✓ Required field '{field}' extracted")
            else:
                print(f"✗ Required field '{field}' MISSING")
                all_present = False
        
        if all_present:
            print("\n✓ All required fields extracted successfully!")
            return True
        else:
            print("\n✗ Some required fields are missing")
            print("  Tips:")
            print("  - Ensure image quality is good (clear, well-lit)")
            print("  - Check if Urdu language pack is installed for bilingual CNICs")
            print("  - Try different preprocessing settings")
            return False
        
    except Exception as e:
        print(f"\n✗ ERROR during extraction: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def test_pattern_matching():
    """Test pattern matching functions."""
    print("\n" + "=" * 60)
    print("Testing Pattern Matching")
    print("=" * 60)
    
    # Test CNIC pattern
    test_cnic = "12345-1234567-1"
    result = tesseract_ocr_service.extract_cnic_number(test_cnic)
    if result == test_cnic:
        print(f"✓ CNIC pattern matching works: {test_cnic}")
    else:
        print(f"✗ CNIC pattern matching failed")
        return False
    
    # Test date pattern
    test_dates = ["01.02.2000", "15/06/1990", "25-12-2025"]
    extracted_dates = tesseract_ocr_service.extract_dates(" ".join(test_dates))
    if len(extracted_dates) == 3:
        print(f"✓ Date pattern matching works: {extracted_dates}")
    else:
        print(f"✗ Date pattern matching failed: {extracted_dates}")
        return False
    
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("TESSERACT OCR SERVICE TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Test Tesseract installation
    results.append(("Tesseract Installation", test_tesseract_installation()))
    
    # Test OCR service
    results.append(("OCR Service Init", test_ocr_service()))
    
    # Test pattern matching
    results.append(("Pattern Matching", test_pattern_matching()))
    
    # Test CNIC extraction (if images available)
    # You can pass custom image paths here
    results.append(("CNIC Extraction", test_cnic_extraction()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, result in results if result)
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n✓ All tests passed! OCR service is ready to use.")
    else:
        print("\n✗ Some tests failed. Please review the errors above.")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
