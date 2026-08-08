🧘 YogaFlow — AI-Powered Yoga Pose Detection & Correction System

Real-time yoga pose detection and correction using computer vision and deep learning — helping users practice yoga safely and accurately.

<img width="1044" height="806" alt="image" src="https://github.com/user-attachments/assets/814bb8e2-42c9-496f-b319-effbc2f67fa2" />
<img width="751" height="866" alt="image" src="https://github.com/user-attachments/assets/84d9245b-aae3-4836-8a41-c1c79b3ddb66" />
<img width="773" height="841" alt="image" src="https://github.com/user-attachments/assets/0e1ce249-cc19-446f-a9a6-b7760b5b41c9" />

📖 Overview

YogaFlow is a real-time yoga pose detection and correction system that uses computer vision and deep learning to classify yoga poses and provide feedback to help users improve their form. The system was developed and deployed as part of a government health initiative, combining pose-estimation and object-detection models to deliver accurate, low-latency feedback directly from live video.

✨ Key Highlights
🎯 92% classification accuracy across 106 yoga pose categories
🧠 Deep learning pipeline combining MediaPipe keypoint extraction with YOLO object detection
📉 35% reduction in false positives through multi-model validation
⚡ 20% reduction in inference latency via optimized real-time video frame processing
🖼️ Trained on a preprocessed and augmented dataset of 10,000+ images
🏛️ Deployed for use in a government health initiative
🏗️ How It Works
                Live Camera Feed
                       │
                       ▼
        ┌──────────────────────────┐
        │   OpenCV Frame Capture   │
        │   & Preprocessing        │
        └───────────┬──────────────┘
                     ▼
        ┌──────────────────────────┐
        │  MediaPipe Pose          │
        │  Keypoint Extraction     │
        └───────────┬──────────────┘
                     ▼
        ┌──────────────────────────┐
        │  YOLO Object Detection   │
        │  (Multi-Model Validation)│
        └───────────┬──────────────┘
                     ▼
        ┌──────────────────────────┐
        │  Pose Classification     │
        │  (106 categories)        │
        └───────────┬──────────────┘
                     ▼
        ┌──────────────────────────┐
        │  Correction Feedback     │
        │  (Web UI - HTML/CSS/JS)  │
        └──────────────────────────┘
Capture — Live video frames are captured and preprocessed using OpenCV.
Keypoint Extraction — MediaPipe extracts body landmark keypoints (joints, limbs, posture angles).
Detection & Validation — YOLO-based object detection cross-validates pose regions, reducing false positives.
Classification — Keypoints and detection outputs are fed into the classification pipeline to identify the yoga pose from 106 categories.
Feedback — Real-time correction feedback is rendered on a web-based interface (HTML/CSS/JS) to guide the user toward proper form.
🛠️ Tech Stack
Layer	Tools
Computer Vision	OpenCV — real-time video frame processing
Pose Estimation	MediaPipe — body keypoint extraction
Object Detection	YOLO — multi-model validation, false positive reduction
Language	Python
Frontend	HTML, CSS, JavaScript
📊 Model Performance
Metric	Result
Classification Accuracy	92%
Pose Categories	106
False Positive Reduction	35% (via multi-model validation)
Inference Latency Reduction	20%
Training Dataset Size	10,000+ images (preprocessed & augmented)

Model performance was evaluated using accuracy, precision, recall, and F1-score.

🧪 Pipeline Details
Data Preparation — Collected and preprocessed 10,000+ yoga pose images; applied data augmentation (rotation, flipping, scaling, lighting variation) to improve model generalization.
Keypoint Extraction — Used MediaPipe to extract skeletal landmarks (joint angles, limb positions) as core features for pose classification.
Detection Layer — Integrated YOLO for object/person detection to validate pose regions and filter out noisy or false detections.
Multi-Model Validation — Combined outputs from MediaPipe and YOLO to cross-check predictions, cutting false positives by 35%.
Real-Time Optimization — Applied frame-processing optimizations in OpenCV to reduce inference latency by 20%, enabling smooth real-time feedback.
🚀 Getting Started
Prerequisites
Python 3.x
pip
Installation
bash
git clone https://github.com/<your-username>/yogaflow.git
cd yogaflow

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
Run
bash
python app.py

Then open the web interface (served via the local HTML/CSS/JS frontend) in your browser to start real-time pose detection.



🎯 Use Case & Impact

YogaFlow was built to make guided, accurate yoga practice more accessible — enabling users to receive real-time corrective feedback without needing an instructor physically present. The system was deployed as part of a government health initiative, supporting wider public wellness and preventive health goals.

🔮 Future Improvements
Expand pose library beyond 106 categories
Add voice-guided correction feedback
Mobile app deployment (iOS/Android)
Personalized difficulty progression and session tracking
Multi-person pose detection support
.

<p align="center">🧘 Built to bring accurate, real-time yoga guidance to everyone.</p>
