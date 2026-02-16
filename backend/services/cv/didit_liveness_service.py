"""
DIDIT API service for face liveness detection.
Provides professional-grade liveness verification with anti-spoofing.
"""
import requests
import os
from typing import Tuple, Dict, Optional
import json


class DiditLivenessService:
    """Service for face liveness detection using DIDIT API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize DIDIT liveness service.
        
        Args:
            api_key: DIDIT API key (optional, uses env var if None)
        """
        self.api_key = api_key or os.getenv('DIDIT_API_KEY')
        self.api_base_url = os.getenv('DIDIT_API_BASE_URL', 'https://api.didit.me')
        self.enabled = os.getenv('DIDIT_ENABLED', 'true').lower() == 'true'
        
        # DIDIT API endpoints
        self.endpoints = {
            'liveness': f'{self.api_base_url}/v1/liveness',
            'verify': f'{self.api_base_url}/v1/liveness/verify'
        }
    
    def upload_video_to_didit(self, video_path: str) -> Optional[Dict]:
        """
        Upload video to DIDIT API for liveness check.
        
        Args:
            video_path: Path to liveness video file
            
        Returns:
            DIDIT API response dictionary or None on error
        """
        if not self.enabled or not self.api_key:
            print("DIDIT API is disabled or API key not configured")
            return None
        
        try:
            # Read video file
            with open(video_path, 'rb') as video_file:
                files = {
                    'video': (os.path.basename(video_path), video_file, 'video/webm')
                }
                
                headers = {
                    'Authorization': f'Bearer {self.api_key}'
                }
                
                # Upload to DIDIT
                response = requests.post(
                    self.endpoints['liveness'],
                    files=files,
                    headers=headers,
                    timeout=60  # Liveness check may take time
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"DIDIT API request failed with status {response.status_code}")
                    print(f"Response: {response.text}")
                    return None
                    
        except Exception as e:
            print(f"Error uploading video to DIDIT API: {e}")
            import traceback
            print(traceback.format_exc())
            return None
    
    def parse_didit_response(self, response: Dict) -> Tuple[bool, float, Dict]:
        """
        Parse DIDIT API response.
        
        Args:
            response: DIDIT API response dictionary
            
        Returns:
            Tuple of (is_live, confidence_score, details)
        """
        try:
            # DIDIT response structure (adjust based on actual API)
            # Example structure:
            # {
            #     "success": true,
            #     "liveness": {
            #         "is_live": true,
            #         "confidence": 0.95,
            #         "checks": {
            #             "blink_detected": true,
            #             "movement_detected": true,
            #             "face_quality": "high"
            #         }
            #     }
            # }
            
            is_success = response.get('success', False)
            
            if not is_success:
                error_msg = response.get('message', 'Unknown error')
                print(f"DIDIT liveness check failed: {error_msg}")
                return False, 0.0, {'error': error_msg}
            
            # Extract liveness data
            liveness_data = response.get('liveness', {})
            is_live = liveness_data.get('is_live', False)
            confidence = liveness_data.get('confidence', 0.0)
            checks = liveness_data.get('checks', {})
            
            details = {
                'blink_detected': checks.get('blink_detected', False),
                'movement_detected': checks.get('movement_detected', False),
                'face_quality': checks.get('face_quality', 'unknown'),
                'didit_used': True
            }
            
            return is_live, confidence, details
            
        except Exception as e:
            print(f"Error parsing DIDIT response: {e}")
            return False, 0.0, {'error': str(e)}
    
    def check_liveness(self, video_path: str) -> Tuple[bool, float, Dict]:
        """
        Check liveness using DIDIT API.
        Falls back to MediaPipe if DIDIT fails.
        
        Args:
            video_path: Path to liveness video file
            
        Returns:
            Tuple of (is_live, confidence_score, details)
        """
        try:
            if not self.enabled or not self.api_key:
                print("DIDIT API not available, falling back to MediaPipe")
                return self._fallback_to_mediapipe(video_path)
            
            # Upload and process with DIDIT
            print(f"Checking liveness with DIDIT API: {video_path}")
            response = self.upload_video_to_didit(video_path)
            
            if response is None:
                print("DIDIT API failed, falling back to MediaPipe")
                return self._fallback_to_mediapipe(video_path)
            
            # Parse DIDIT response
            is_live, confidence, details = self.parse_didit_response(response)
            
            print(f"DIDIT liveness result: is_live={is_live}, confidence={confidence}")
            return is_live, confidence, details
            
        except Exception as e:
            print(f"Error in DIDIT liveness check: {e}")
            import traceback
            print(traceback.format_exc())
            print("Falling back to MediaPipe")
            return self._fallback_to_mediapipe(video_path)
    
    def _fallback_to_mediapipe(self, video_path: str) -> Tuple[bool, float, Dict]:
        """
        Fallback to MediaPipe-based liveness detection.
        
        Args:
            video_path: Path to liveness video file
            
        Returns:
            Tuple of (is_live, confidence_score, details)
        """
        try:
            # Import MediaPipe service
            from services.cv.liveness_detection import liveness_service
            
            print("Using MediaPipe fallback for liveness detection")
            is_live, confidence, details = liveness_service.check_liveness(video_path)
            
            # Add fallback indicator
            details['didit_used'] = False
            details['fallback_method'] = 'MediaPipe'
            
            return is_live, confidence, details
            
        except Exception as e:
            print(f"MediaPipe fallback also failed: {e}")
            return False, 0.0, {'error': str(e), 'fallback_failed': True}


# Global DIDIT liveness service instance
didit_liveness_service = DiditLivenessService()
