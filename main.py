import cv2
import numpy as np
import time
from pose_detector import PoseDetector
from pose_analyzer import PoseAnalyzer

class YogaApp:
    def __init__(self):
        print("=== YOGA POSE CORRECTION SYSTEM ===")
        
        self.detector = PoseDetector()
        self.analyzer = PoseAnalyzer()
        
        # Yoga poses
        self.poses = {
            'T': {'id': 'tadasana', 'name': 'Tadasana'},
            'V': {'id': 'vriksasana', 'name': 'Vriksasana'},
            'P': {'id': 'padahastasana', 'name': 'Padahastasana'},
            'A': {'id': 'ardha_chakrasana', 'name': 'Ardha Chakrasana'},
            'R': {'id': 'trikonasana', 'name': 'Trikonasana'},
            'B': {'id': 'bhadrasana', 'name': 'Bhadrasana'},
            'J': {'id': 'vajrasana', 'name': 'Vajrasana'},
            'U': {'id': 'ustrasana', 'name': 'Ustrasana'},
            'S': {'id': 'sasakasana', 'name': 'Sasakasana'}  
            }
        
        self.current_pose = 'tadasana'
        self.current_pose_name = 'Mountain Pose'
        self.show_landmarks = True
        self.show_feedback = True
        
    def run(self):
        """Main application loop"""
        print("\nCONTROLS:")
        print("  Letter keys: Select yoga pose")
        print("  L: Toggle landmarks")
        print("  F: Toggle feedback")
        print("  Q: Quit application")
        print("\nAvailable Poses:")
        for key, pose in self.poses.items():
            print(f"  [{key}] {pose['name']}")
        print("="*50)
        
        # Open camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("ERROR: Cannot open camera!")
            return
        
        # Set camera resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        prev_time = 0
        frame_count = 0
        
        while True:
            # Read frame
            ret, frame = cap.read()
            if not ret:
                print("Failed to read frame")
                break
            
            # Flip for mirror view
            frame = cv2.flip(frame, 1)
            
            # Detect pose
            results = self.detector.detect(frame)
            
            feedback = ["Stand in frame..."]
            score = 0
            
            if results and results.pose_landmarks:
                # Get landmarks
                landmarks = self.detector.get_landmarks(results)
                self.analyzer.set_landmarks(landmarks)
                
                # Analyze pose
                feedback, score = self.analyzer.analyze_pose(self.current_pose)
                
                # Draw landmarks if enabled
                if self.show_landmarks:
                    frame = self.detector.draw(frame, results)
            
            # Calculate FPS
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time) if prev_time > 0 else 0
            prev_time = curr_time
            
            # Draw UI
            # FPS counter
            cv2.putText(frame, f"FPS: {int(fps)}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Current pose
            cv2.putText(frame, f"POSE: {self.current_pose_name}", 
                       (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            
            # Score
            cv2.putText(frame, f"Score: {score}%", (10, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 255), 2)
            
            # Controls
            cv2.putText(frame, "Letter keys: Pose | L: Landmarks | F: Feedback | Q: Quit", 
                       (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Draw feedback
            if self.show_feedback:
                y_pos = 180
                for i, fb in enumerate(feedback[:4]):  # Show first 4 feedback items
                    color = (0, 255, 0) if fb.startswith("✓") else (0, 165, 255)
                    cv2.putText(frame, fb, (20, y_pos + i*30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            # Show frame
            cv2.imshow('Yoga Pose Correction', frame)
            
            # Handle keys
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == 27:
                break
            elif key == ord('l'):
                self.show_landmarks = not self.show_landmarks
                status = "ON" if self.show_landmarks else "OFF"
                print(f"Landmarks: {status}")
            elif key == ord('f'):
                self.show_feedback = not self.show_feedback
                status = "ON" if self.show_feedback else "OFF"
                print(f"Feedback: {status}")
            elif chr(key).upper() in self.poses:
                pose_key = chr(key).upper()
                self.current_pose = self.poses[pose_key]['id']
                self.current_pose_name = self.poses[pose_key]['name']
                print(f"Changed to: {self.current_pose_name}")

            
            frame_count += 1
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        self.detector.close()
        print("\nThank you for practicing yoga!")

def main():
    app = YogaApp()
    app.run()

if __name__ == "__main__":
    main()