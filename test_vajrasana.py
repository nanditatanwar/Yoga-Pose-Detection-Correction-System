import cv2
import mediapipe as mp
import time

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

cap = cv2.VideoCapture(0)

print("Testing Vajrasana detection...")
print("Sit in Vajrasana position (sitting on heels)")
print("Press 'q' to quit")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)
    
    visible_landmarks = []
    if results.pose_landmarks:
        for idx, lm in enumerate(results.pose_landmarks.landmark):
            if lm.visibility > 0.3:
                visible_landmarks.append(idx)
        
        print(f"\rVisible landmarks: {len(visible_landmarks)}/33 - Indices: {visible_landmarks[:10]}...", end="")
        
        # Draw landmarks
        mp.solutions.drawing_utils.draw_landmarks(
            frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
        )
    
    cv2.imshow('Vajrasana Test', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pose.close()
print("\nTest complete!")
