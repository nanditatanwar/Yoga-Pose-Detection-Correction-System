from flask import Flask, jsonify, request
from flask_cors import CORS
import cv2
import base64
import logging
from datetime import datetime
import atexit  # For cleanup on server exit

from pose_detector import PoseDetector
from pose_analyzer import PoseAnalyzer

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# ---------------- GLOBALS ----------------
detector = PoseDetector()
analyzer = PoseAnalyzer()

cap = None
current_pose = "tadasana"

last_feedback = ["Stand in frame..."]
last_score = 0
last_results = None

frame_count = 0
is_camera_initialized = False
session_start_time = None


# ---------- HELPER FUNCTIONS ----------
def initialize_camera():
    """Initialize the camera with error handling"""
    global cap, is_camera_initialized
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            is_camera_initialized = True
            logger.info("Camera initialized successfully")
            return True
        else:
            logger.error("Failed to open camera")
            return False
    except Exception as e:
        logger.error(f"Error initializing camera: {str(e)}")
        return False


def release_camera():
    """Release camera resources"""
    global cap, is_camera_initialized
    if cap:
        cap.release()
        cap = None
    is_camera_initialized = False
    logger.info("Camera released")


# ---------- CLEANUP ON SERVER EXIT ----------
@atexit.register
def cleanup():
    release_camera()
    logger.info("Application shutting down, resources cleaned up")


# ---------- BASIC CHECK ----------
@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "yoga-pose-feedback",
        "version": "1.0.0"
    })


# ---------- TEST ENDPOINT ----------
@app.route("/api/test")
def test():
    return jsonify({
        "message": "Server is running",
        "current_pose": current_pose,
        "camera_status": "initialized" if is_camera_initialized else "not initialized",
        "timestamp": datetime.now().isoformat()
    })


# ---------- POSES ----------
@app.route("/api/poses")
def poses():
    return jsonify({
        "poses": {
            "tadasana": "Tadasana (Mountain Pose)",
            "vriksasana": "Vriksasana (Tree Pose)",
            "padahastasana": "Padahastasana (Hand to Foot)",
            "ardha_chakrasana": "Ardha Chakrasana (Half Wheel)",
            "trikonasana": "Trikonasana (Triangle Pose)",
            "bhadrasana": "Bhadrasana (Gracious Pose)",
            "vajrasana": "Vajrasana (Thunderbolt Pose)",
            "ustrasana": "Ustrasana (Camel Pose)",
            "sasakasana": "Sasakasana (Rabbit Pose)"
        },
        "current_pose": current_pose,
        "count": 9
    })


# ---------- START CAMERA ----------
@app.route("/api/start", methods=["POST"])
def start_camera():
    global cap, session_start_time, is_camera_initialized

    try:
        if cap is None or not is_camera_initialized:
            success = initialize_camera()
            if not success:
                return jsonify({
                    "status": "error",
                    "message": "Failed to initialize camera. Check if camera is connected."
                }), 500

        session_start_time = datetime.now()

        return jsonify({
            "status": "started",
            "message": "Camera started successfully",
            "timestamp": session_start_time.isoformat(),
            "camera_index": 0
        })
    except Exception as e:
        logger.error(f"Error starting camera: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Error starting camera: {str(e)}"
        }), 500


# ---------- STOP CAMERA ----------
@app.route("/api/stop", methods=["POST"])
def stop_camera():
    global cap, session_start_time, frame_count, last_results, last_feedback, last_score

    try:
        release_camera()

        # Reset session data
        session_duration = 0
        if session_start_time:
            session_duration = (datetime.now() - session_start_time).total_seconds()

        frame_count = 0
        last_results = None
        last_feedback = ["Session ended"]
        last_score = 0

        return jsonify({
            "status": "stopped",
            "message": "Camera stopped successfully",
            "session_duration_seconds": session_duration,
            "frames_processed": frame_count
        })
    except Exception as e:
        logger.error(f"Error stopping camera: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Error stopping camera: {str(e)}"
        }), 500


# ---------- CAMERA STATUS ----------
@app.route("/api/camera-status")
def camera_status():
    status = "unknown"
    if cap is not None and is_camera_initialized:
        if cap.isOpened():
            status = "running"
        else:
            status = "error"
    else:
        status = "stopped"

    return jsonify({
        "status": status,
        "is_initialized": is_camera_initialized,
        "current_pose": current_pose,
        "frame_count": frame_count
    })


# ---------- CHANGE POSE ----------
@app.route("/api/pose", methods=["POST"])
def change_pose():
    global current_pose

    try:
        data = request.json
        if not data or 'pose' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing 'pose' in request body"
            }), 400

        new_pose = data.get("pose", "tadasana")

        valid_poses = [
            "tadasana", "vriksasana", "padahastasana",
            "ardha_chakrasana", "trikonasana", "bhadrasana",
            "vajrasana", "ustrasana", "sasakasana"
        ]

        if new_pose not in valid_poses:
            return jsonify({
                "status": "error",
                "message": f"Invalid pose. Must be one of: {', '.join(valid_poses)}",
                "valid_poses": valid_poses
            }), 400

        current_pose = new_pose
        logger.info(f"Changed pose to: {current_pose}")

        return jsonify({
            "status": "success",
            "message": "Pose changed successfully",
            "pose": current_pose,
            "pose_name": current_pose.replace("_", " ").title(),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error changing pose: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Error changing pose: {str(e)}"
        }), 500


# ---------- GET CURRENT POSE ----------
@app.route("/api/current-pose")
def get_current_pose():
    return jsonify({
        "pose": current_pose,
        "pose_name": current_pose.replace("_", " ").title(),
        "description": "Select a pose and start camera for analysis"
    })


# ---------- SEND FRAME ----------
@app.route("/api/frame")
def get_frame():
    global cap, frame_count, last_results, last_feedback, last_score, is_camera_initialized

    if not is_camera_initialized or cap is None:
        return jsonify({
            "status": "error",
            "message": "Camera not started. Call /api/start first.",
            "code": "CAMERA_NOT_STARTED"
        }), 400

    try:
        ret, frame = cap.read()
        if not ret:
            logger.warning("Failed to read frame from camera")
            return jsonify({
                "status": "error",
                "message": "Failed to capture frame",
                "code": "FRAME_CAPTURE_ERROR"
            }), 500

        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (640, 480))

        frame_count += 1

        if frame_count % 3 == 0:
            try:
                last_results = detector.detect(frame)
                if last_results and last_results.pose_landmarks:
                    landmarks = detector.get_landmarks(last_results)
                    analyzer.set_landmarks(landmarks)
                    last_feedback, last_score = analyzer.analyze_pose(current_pose)
                    logger.debug(f"Pose analyzed: {current_pose}, Score: {last_score}")
                else:
                    last_feedback = ["No pose detected. Make sure you're visible in frame."]
                    last_score = 0
            except Exception as e:
                logger.error(f"Error in pose detection/analysis: {str(e)}")
                last_feedback = ["System error in pose analysis"]
                last_score = 0

        if last_results and last_results.pose_landmarks:
            frame = detector.draw(frame, last_results)

        _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        frame_base64 = base64.b64encode(buffer).decode("utf-8")

        return jsonify({
            "status": "ok",
            "frame": "data:image/jpeg;base64," + frame_base64,
            "frame_count": frame_count,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error getting frame: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Error processing frame: {str(e)}",
            "code": "FRAME_PROCESSING_ERROR"
        }), 500


# ---------- SEND ANALYSIS ----------
@app.route("/api/analysis", methods=["GET"])
def get_analysis():
    if not cap or not analyzer:
        return jsonify({"error": "Camera not started or analyzer missing"}), 400

    ret, frame = cap.read()
    if not ret:
        return jsonify({"error": "Failed to read frame"}), 500

    # Get landmarks from pose_detector
    results = detector.detect(frame)
    landmarks = detector.get_landmarks(results)
    print("Landmarks:", landmarks)
    analyzer.set_landmarks(landmarks)

    pose_name = current_pose  # set from /api/pose
    feedback, score = analyzer.analyze_pose(pose_name)

    logger.debug(f"Pose analyzed: {pose_name}, Score: {score}")

    # Return JSON with pose_name, score, and feedback
    return jsonify({
        "pose_name": pose_name,
        "score": round(score, 2),  # round for nicer display
        "feedback": feedback if feedback else ["No feedback available"]
    })



# ---------- SYSTEM STATUS ----------
@app.route("/api/status")
def system_status():
    return jsonify({
        "camera": {
            "status": "running" if is_camera_initialized and cap and cap.isOpened() else "stopped",
            "is_initialized": is_camera_initialized,
            "frame_count": frame_count
        },
        "pose": {
            "current": current_pose,
            "name": current_pose.replace("_", " ").title()
        },
        "analysis": {
            "last_score": last_score,
            "feedback_count": len(last_feedback) if last_feedback else 0
        },
        "server": {
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "uptime": "N/A"
        }
    })


# ---------- ERROR HANDLERS ----------
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "message": "Endpoint not found",
        "code": "NOT_FOUND"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        "status": "error",
        "message": "Internal server error",
        "code": "INTERNAL_ERROR"
    }), 500


if __name__ == "__main__":
    print("=" * 60)
    print("Yoga Pose Feedback System")
    print("Server starting on http://localhost:5000")
    print("=" * 60)
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        threaded=True
    )
