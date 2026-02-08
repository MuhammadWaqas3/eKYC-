"""
Liveness detection service using MediaPipe for Pakistani eKYC.
Detects blinks and head movements to ensure the user is real.
"""
import cv2
import mediapipe as mp
import numpy as np
from typing import Tuple, Dict, List
import time

class LivenessDetectionService:
    """Service for detecting liveness in videos."""
    
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Eyes landmarks (MediaPipe)
        self.LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        self.RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        
        # EAR threshold (Eye Aspect Ratio)
        self.EYE_AR_THRESH = 0.2
        self.EYE_AR_CONSEC_FRAMES = 1
        
    def get_ear(self, landmarks, eye_indices):
        """Calculate Eye Aspect Ratio (EAR)."""
        # Vertical distances
        p1 = landmarks[eye_indices[12]] # Top
        p2 = landmarks[eye_indices[4]]  # Bottom
        p3 = landmarks[eye_indices[14]] # Top
        p4 = landmarks[eye_indices[2]]  # Bottom
        
        # Horizontal distance
        p5 = landmarks[eye_indices[8]]  # Inner
        p6 = landmarks[eye_indices[0]]  # Outer
        
        dist_v1 = np.linalg.norm(np.array(p1) - np.array(p2))
        dist_v2 = np.linalg.norm(np.array(p3) - np.array(p4))
        dist_h = np.linalg.norm(np.array(p5) - np.array(p6))
        
        ear = (dist_v1 + dist_v2) / (2.0 * dist_h)
        return ear

    def get_head_pose(self, landmarks, img_w, img_h):
        """Estimate head pose using face landmarks."""
        # 3D model points (arbitrary but representative)
        model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -330.0, -65.0),        # Chin
            (-225.0, 170.0, -135.0),     # Left eye left corner
            (225.0, 170.0, -135.0),      # Right eye right corner
            (-150.0, -150.0, -125.0),    # Left Mouth corner
            (150.0, -150.0, -125.0)      # Right mouth corner
        ])

        # 2D image points from MediaPipe
        # Nose: 1, Chin: 152, Left Eye Left: 33, Right Eye Right: 263, Left Mouth: 61, Right Mouth: 291
        image_points = np.array([
            (landmarks[1][0] * img_w, landmarks[1][1] * img_h),
            (landmarks[152][0] * img_w, landmarks[152][1] * img_h),
            (landmarks[33][0] * img_w, landmarks[33][1] * img_h),
            (landmarks[263][0] * img_w, landmarks[263][1] * img_h),
            (landmarks[61][0] * img_w, landmarks[61][1] * img_h),
            (landmarks[291][0] * img_w, landmarks[291][1] * img_h)
        ], dtype="double")

        camera_matrix = np.array([
            [img_w, 0, img_w / 2],
            [0, img_w, img_h / 2],
            [0, 0, 1]
        ], dtype="double")

        dist_coeffs = np.zeros((4, 1)) # Assuming no lens distortion
        (success, rotation_vector, translation_vector) = cv2.solvePnP(
            model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
        )
        
        return rotation_vector

    def check_liveness(self, video_path: str) -> Tuple[bool, float, Dict]:
        """
        Improved liveness check (blinks + head movement pose).
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return False, 0.0, {"error": "Could not open video file"}
            
        blink_count = 0
        eye_closed = False
        poses = []
        frames_processed = 0
        
        img_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        img_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            frames_processed += 1
            if frames_processed % 2 != 0: continue # Skip frames for speed
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                landmarks = [(lm.x, lm.y, lm.z) for lm in face_landmarks.landmark]
                
                # Head Pose
                rot_vec = self.get_head_pose(landmarks, img_w, img_h)
                poses.append(rot_vec.flatten())
                
                # Blinks
                ear = (self.get_ear(landmarks, self.LEFT_EYE) + self.get_ear(landmarks, self.RIGHT_EYE)) / 2.0
                if ear < self.EYE_AR_THRESH:
                    eye_closed = True
                else:
                    if eye_closed:
                        blink_count += 1
                        eye_closed = False
            
        cap.release()
        
        # Calculate movement variance in poses
        pose_variance = 0.0
        if len(poses) > 5:
            poses_np = np.array(poses)
            pose_variance = float(np.var(poses_np, axis=0).sum())

        # Robust Liveness logic: Require at least 1 blink OR significant head movement
        is_live = blink_count >= 1 or pose_variance > 0.005
        liveness_score = min(0.99, (blink_count * 0.3) + (pose_variance * 50))
        
        if not is_live: liveness_score = 0.1

        details = {
            "blinks": blink_count,
            "movement_variance": pose_variance,
            "frames": frames_processed
        }
        
        return is_live, liveness_score, details

# Global service instance
liveness_service = LivenessDetectionService()
