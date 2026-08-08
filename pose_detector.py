import cv2
import mediapipe as mp
import numpy as np


class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=0,   # FAST
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils


    
    def detect(self, image):
        """Detect pose in image"""
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False
        results = self.pose.process(image_rgb)
        image_rgb.flags.writeable = True
        return results
    
    def get_landmarks(self, results):
        """Extract ALL available landmarks as dictionary"""
        if not results or not results.pose_landmarks:
            return {}
        
        landmarks = results.pose_landmarks.landmark
        landmark_dict = {}
        
        # All 33 MediaPipe landmarks
        indices = {
            'nose': 0,
            'left_eye_inner': 1, 'left_eye': 2, 'left_eye_outer': 3,
            'right_eye_inner': 4, 'right_eye': 5, 'right_eye_outer': 6,
            'left_ear': 7, 'right_ear': 8,
            'mouth_left': 9, 'mouth_right': 10,
            'left_shoulder': 11, 'right_shoulder': 12,
            'left_elbow': 13, 'right_elbow': 14,
            'left_wrist': 15, 'right_wrist': 16,
            'left_pinky': 17, 'right_pinky': 18,
            'left_index': 19, 'right_index': 20,
            'left_thumb': 21, 'right_thumb': 22,
            'left_hip': 23, 'right_hip': 24,
            'left_knee': 25, 'right_knee': 26,
            'left_ankle': 27, 'right_ankle': 28,
            'left_heel': 29, 'right_heel': 30,
            'left_foot_index': 31, 'right_foot_index': 32
        }
        
        for name, idx in indices.items():
            lm = landmarks[idx]
            if lm.visibility > 0.05:  # Only include visible landmarks
                landmark_dict[name] = [lm.x, lm.y, lm.z, lm.visibility]
        
        return landmark_dict
    
    def draw(self, image, results):
        """Draw landmarks on image"""
        if results and results.pose_landmarks:
            self.mp_draw.draw_landmarks(
                image,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                mp.solutions.drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp.solutions.drawing_utils.DrawingSpec(color=(255, 0, 0), thickness=2)
            )
        return image
    
    def close(self):
        """Close the pose detector"""
        self.pose.close()
