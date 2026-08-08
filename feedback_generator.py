import cv2
import numpy as np
from typing import List, Tuple, Dict
from utils.visualization import draw_angle, draw_feedback_panel, draw_progress_bar, draw_pose_instructions
from utils.constants import COLORS, YOGA_POSES

class FeedbackGenerator:
    def __init__(self):
        self.pose_instructions = {
            'tadasana': [
                "Stand with feet together",
                "Distribute weight evenly",
                "Lengthen your spine upward",
                "Relax shoulders down",
                "Arms by your sides"
            ],
            'vriksasana': [
                "Shift weight to left leg",
                "Place right foot on inner left thigh",
                "Bring palms together at chest",
                "Fix gaze on a steady point",
                "Hold for 5 breaths"
            ],
            'padahastasana': [
                "Stand with feet hip-width apart",
                "Exhale and bend forward from hips",
                "Keep legs straight",
                "Place palms under feet",
                "Hold for 5 breaths"
            ]
            # Add instructions for other poses
        }
    
    def generate_visual_feedback(self, image: np.ndarray, landmarks_dict: Dict, 
                                pose_name: str, feedback: List[str], score: float) -> np.ndarray:
        """
        Generate visual feedback on the image
        
        Args:
            image: Input image
            landmarks_dict: Dictionary of landmarks
            pose_name: Current pose name
            feedback: List of feedback messages
            score: Pose accuracy score
            
        Returns:
            Image with visual feedback
        """
        h, w = image.shape[:2]
        
        # Convert normalized coordinates to pixel coordinates
        def to_pixel(landmark):
            return (int(landmark[0] * w), int(landmark[1] * h))
        
        # Draw progress bar
        image = draw_progress_bar(image, score)
        
        # Draw feedback panel
        image = draw_feedback_panel(image, feedback)
        
        # Draw pose instructions
        if pose_name in self.pose_instructions:
            image = draw_pose_instructions(image, 
                                          YOGA_POSES[pose_name]['english'],
                                          self.pose_instructions[pose_name])
        
        # Draw specific visual cues based on pose
        if pose_name == 'tadasana':
            image = self._draw_tadasana_cues(image, landmarks_dict)
        elif pose_name == 'vriksasana':
            image = self._draw_vriksasana_cues(image, landmarks_dict)
        elif pose_name == 'padahastasana':
            image = self._draw_padahastasana_cues(image, landmarks_dict)
        
        # Draw pose name
        cv2.putText(image, f"POSE: {YOGA_POSES[pose_name]['english']}", 
                   (w//2 - 150, 40), cv2.FONT_HERSHEY_SIMPLEX, 
                   1, (255, 255, 0), 2)
        
        return image
    
    def _draw_tadasana_cues(self, image: np.ndarray, landmarks_dict: Dict) -> np.ndarray:
        """Draw visual cues for Tadasana"""
        h, w = image.shape[:2]
        
        # Draw alignment lines
        if 'left_shoulder' in landmarks_dict and 'right_shoulder' in landmarks_dict:
            left_shoulder = (int(landmarks_dict['left_shoulder'][0] * w),
                           int(landmarks_dict['left_shoulder'][1] * h))
            right_shoulder = (int(landmarks_dict['right_shoulder'][0] * w),
                            int(landmarks_dict['right_shoulder'][1] * h))
            
            # Draw shoulder alignment line
            cv2.line(image, left_shoulder, right_shoulder, COLORS['warning'], 2)
            
            # Draw ideal horizontal line
            y_avg = (left_shoulder[1] + right_shoulder[1]) // 2
            cv2.line(image, (0, y_avg), (w, y_avg), COLORS['good'], 1, cv2.LINE_AA)
        
        return image
    
    def _draw_vriksasana_cues(self, image: np.ndarray, landmarks_dict: Dict) -> np.ndarray:
        """Draw visual cues for Vriksasana"""
        h, w = image.shape[:2]
        
        # Draw balance line (from nose to standing ankle)
        if 'nose' in landmarks_dict and 'left_ankle' in landmarks_dict:
            nose = (int(landmarks_dict['nose'][0] * w),
                   int(landmarks_dict['nose'][1] * h))
            ankle = (int(landmarks_dict['left_ankle'][0] * w),
                    int(landmarks_dict['left_ankle'][1] * h))
            
            # Draw vertical line for balance reference
            cv2.line(image, (ankle[0], 0), (ankle[0], h), COLORS['good'], 1, cv2.LINE_AA)
            
            # Draw line from nose to ankle
            cv2.line(image, nose, ankle, COLORS['warning'], 2)
        
        return image
    
    def _draw_padahastasana_cues(self, image: np.ndarray, landmarks_dict: Dict) -> np.ndarray:
        """Draw visual cues for Padahastasana"""
        h, w = image.shape[:2]
        
        # Draw forward bend angle
        if all(k in landmarks_dict for k in ['left_shoulder', 'left_hip', 'left_knee']):
            shoulder = (int(landmarks_dict['left_shoulder'][0] * w),
                       int(landmarks_dict['left_shoulder'][1] * h))
            hip = (int(landmarks_dict['left_hip'][0] * w),
                  int(landmarks_dict['left_hip'][1] * h))
            knee = (int(landmarks_dict['left_knee'][0] * w),
                   int(landmarks_dict['left_knee'][1] * h))
            
            # Calculate and draw angle
            angle = self._calculate_angle_degrees(shoulder, hip, knee)
            image = draw_angle(image, shoulder, hip, knee, angle)
        
        return image
    
    def _calculate_angle_degrees(self, a: Tuple[int, int], b: Tuple[int, int], c: Tuple[int, int]) -> float:
        """Calculate angle between three points"""
        import math
        
        # Calculate vectors
        ba = (a[0] - b[0], a[1] - b[1])
        bc = (c[0] - b[0], c[1] - b[1])
        
        # Calculate dot product and magnitudes
        dot_product = ba[0] * bc[0] + ba[1] * bc[1]
        mag_ba = math.sqrt(ba[0]**2 + ba[1]**2)
        mag_bc = math.sqrt(bc[0]**2 + bc[1]**2)
        
        # Calculate angle
        if mag_ba == 0 or mag_bc == 0:
            return 0
        
        cos_angle = dot_product / (mag_ba * mag_bc)
        cos_angle = max(-1, min(1, cos_angle))  # Clamp
        angle_rad = math.acos(cos_angle)
        angle_deg = math.degrees(angle_rad)
        
        return angle_deg
    
    def generate_verbal_feedback(self, feedback: List[str]) -> str:
        """
        Generate concise verbal feedback summary
        """
        if not feedback:
            return "Perfect pose! Maintain this position."
        
        # Categorize feedback
        critical = [f for f in feedback if not f.startswith("✓")]
        positive = [f for f in feedback if f.startswith("✓")]
        
        if critical:
            return f"Focus on: {critical[0]}"
        elif positive:
            return positive[0]
        
        return "Good effort! Keep practicing."