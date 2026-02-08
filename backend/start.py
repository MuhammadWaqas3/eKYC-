# Backend Startup Helper
# This script helps you run the backend with optional CV dependencies

import subprocess
import sys

def check_cv_dependencies():
    """Check if CV libraries are installed."""
    missing = []
    try:
        import easyocr
    except ImportError:
        missing.append("easyocr")
    
    try:
        import cv2
    except ImportError:
        missing.append("opencv-python")
        
    try:
        import deepface
    except ImportError:
        missing.append("deepface")
    
    return missing

def main():
    print("=== eKYC Backend Startup Checker ===\n")
    
    missing = check_cv_dependencies()
    
    if missing:
        print("⚠️  WARNING: The following CV libraries are not installed:")
        for lib in missing:
            print(f"  - {lib}")
        print("\nThe backend will START, but CV endpoints won't work.")
        print("To install them later, run:")
        print("  pip install opencv-python deepface easyocr Pillow\n")
        
        response = input("Do you want to continue anyway? (y/n): ").lower()
        if response != 'y':
            print("Exiting...")
            sys.exit(0)
    else:
        print("✅ All CV dependencies found!\n")
    
    print("Starting FastAPI backend...\n")
    subprocess.run([sys.executable, "main.py"])

if __name__ == "__main__":
    main()
