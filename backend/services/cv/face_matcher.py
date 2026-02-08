"""
Face matching service using DeepFace.
Compares selfie with CNIC photo to verify identity.
"""
from deepface import DeepFace
import cv2
import numpy as np
from typing import Tuple, Optional
import os


class FaceMatchService:
    """Service for matching faces using DeepFace."""
    
    def __init__(self, threshold: float = 0.6):
        """
        Initialize face matching service.
        
        Args:
            threshold: Similarity threshold (0-1, higher is more similar)
        """
        self.threshold = threshold
        self.model_name = 'VGG-Face'  # Options: VGG-Face, Facenet, OpenFace, DeepFace, ArcFace
        self.distance_metric = 'cosine'  # Options: cosine, euclidean, euclidean_l2
    
    def extract_face(self, image_path: str) -> Optional[np.ndarray]:
        """
        Extract face from image using DeepFace.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Face array if detected, None otherwise
        """
        try:
            # Use DeepFace to extract face
            face_objs = DeepFace.extract_faces(
                img_path=image_path,
                detector_backend='opencv',
                enforce_detection=True
            )
            
            if face_objs:
                # Get the first detected face
                return face_objs[0]['face']
            
            return None
        
        except Exception as e:
            print(f"Face extraction error: {e}")
            return None
    
    def match_faces(
        self,
        selfie_path: str,
        cnic_photo_path: str
    ) -> Tuple[bool, float, Optional[str]]:
        """
        Match selfie with CNIC photo.
        
        Args:
            selfie_path: Path to selfie image
            cnic_photo_path: Path to CNIC photo (extracted face)
            
        Returns:
            Tuple of (is_match, similarity_score, error_message)
        """
        try:
            # Verify both images exist
            if not os.path.exists(selfie_path):
                return False, 0.0, "Selfie image not found"
            
            if not os.path.exists(cnic_photo_path):
                return False, 0.0, "CNIC photo not found"
            
            # Perform face verification
            result = DeepFace.verify(
                img1_path=selfie_path,
                img2_path=cnic_photo_path,
                model_name=self.model_name,
                distance_metric=self.distance_metric,
                enforce_detection=True
            )
            
            # Extract results
            is_verified = result['verified']
            distance = result['distance']
            
            # Convert distance to similarity score (0-1)
            # For cosine distance: similarity = 1 - distance
            if self.distance_metric == 'cosine':
                similarity = 1 - distance
            else:
                # For euclidean: normalize to 0-1 range
                similarity = 1 / (1 + distance)
            
            # Check against threshold
            is_match = similarity >= self.threshold
            
            return is_match, similarity, None
        
        except ValueError as e:
            # No face detected
            return False, 0.0, f"Face detection failed: {str(e)}"
        
        except Exception as e:
            # Other errors
            return False, 0.0, f"Face matching error: {str(e)}"
    
    def extract_face_from_cnic(
        self,
        cnic_front_path: str,
        output_path: str
    ) -> bool:
        """
        Extract face region from CNIC front image and save it.
        
        Args:
            cnic_front_path: Path to CNIC front image
            output_path: Path to save extracted face
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read CNIC image
            img = cv2.imread(cnic_front_path)
            
            if img is None:
                return False
            
            # Use DeepFace to detect face
            face_objs = DeepFace.extract_faces(
                img_path=cnic_front_path,
                detector_backend='opencv',
                enforce_detection=True
            )
            
            if not face_objs:
                return False
            
            # Get facial area coordinates
            facial_area = face_objs[0]['facial_area']
            x, y, w, h = facial_area['x'], facial_area['y'], facial_area['w'], facial_area['h']
            
            # Crop face region
            face_img = img[y:y+h, x:x+w]
            
            # Save cropped face
            cv2.imwrite(output_path, face_img)
            
            return True
        
        except Exception as e:
            print(f"Face extraction from CNIC error: {e}")
            return False
    
    def validate_face_quality(self, image_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that image contains a clear, detectable face.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Try to detect face
            face_objs = DeepFace.extract_faces(
                img_path=image_path,
                detector_backend='opencv',
                enforce_detection=True
            )
            
            if not face_objs:
                return False, "No face detected"
            
            # Check confidence (if available)
            if len(face_objs) > 1:
                return False, "Multiple faces detected. Please ensure only one person in image."
            
            # Check image quality (size)
            face = face_objs[0]
            if face['facial_area']['w'] < 80 or face['facial_area']['h'] < 80:
                return False, "Face too small. Please move closer to camera."
            
            return True, None
        
        except Exception as e:
            return False, f"Face validation error: {str(e)}"


# Global face match service instance
face_match_service = FaceMatchService()
