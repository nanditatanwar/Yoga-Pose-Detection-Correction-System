import cv2
import mediapipe as mp

# Initialize MediaPipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)
    
    if results.pose_landmarks:
        print("\n" + "="*50)
        print("AVAILABLE LANDMARKS:")
        for idx, lm in enumerate(results.pose_landmarks.landmark):
            if lm.visibility > 0.5:  # Only show visible landmarks
                print(f"Index {idx:2d}: x={lm.x:.3f}, y={lm.y:.3f}, visibility={lm.visibility:.3f}")
        print("="*50)
        
        # Draw landmarks
        mp.solutions.drawing_utils.draw_landmarks(
            frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
        )
    
    cv2.imshow('Debug Landmarks', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pose.close()
