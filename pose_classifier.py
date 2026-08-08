import numpy as np
from typing import Dict, List

class PoseClassifier:
    def __init__(self):
        # This is a simple classifier - you can expand this with ML later
        self.pose_features = {
            'tadasana': {'legs_straight': True, 'arms_down': True},
            'vriksasana': {'one_leg_bent': True, 'balance': True},
            'padahastasana': {'forward_bend': True, 'legs_straight': True},
        }
    
    def classify_pose(self, landmarks_dict: Dict) -> str:
        """
        Simple rule-based pose classifier
        """
        if not landmarks_dict:
            return 'unknown'
        
        # Check for Tree Pose
        if self._is_tree_pose(landmarks_dict):
            return 'vriksasana'
        
        # Check for Forward Bend
        if self._is_forward_bend(landmarks_dict):
            return 'padahastasana'
        
        # Default to Mountain Pose
        return 'tadasana'
    
    def _is_tree_pose(self, landmarks_dict: Dict) -> bool:
        """Check if pose is Tree Pose"""
        if 'left_ankle' in landmarks_dict and 'right_ankle' in landmarks_dict:
            # Check if feet are at different heights
            ankle_height_diff = abs(landmarks_dict['left_ankle'][1] - landmarks_dict['right_ankle'][1])
            return ankle_height_diff > 0.1
        return False
    
    def _is_forward_bend(self, landmarks_dict: Dict) -> bool:
        """Check if pose is Forward Bend"""
        if 'left_shoulder' in landmarks_dict and 'left_hip' in landmarks_dict:
            # Check if shoulders are below hips
            return landmarks_dict['left_shoulder'][1] > landmarks_dict['left_hip'][1] + 0.1
        return False
