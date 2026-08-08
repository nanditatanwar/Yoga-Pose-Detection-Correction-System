// YogaFlow AI - Modern UI Version
let video;
let posesDropdown;
let selected_pose;
let poseLabel = "Detecting...";
let allYOLOPoses = [];
let sessionActive = false;

// Statistics
let stats = {
    totalDetections: 0,
    correctMatches: 0,
    avgConfidence: 0,
    sessionStart: null
};

function setup() {
    console.log("🎬 YogaFlow AI Initializing...");
    
    // Get camera container dimensions
    const cameraContainer = document.getElementById('cameraContainer');
    const containerWidth = cameraContainer.clientWidth;
    const containerHeight = cameraContainer.clientHeight;
    
    console.log(`📐 Container size: ${containerWidth}x${containerHeight}`);
    
    // Create canvas that FITS the container
    let cv = createCanvas(containerWidth, containerHeight);
    cv.parent("cameraContainer");
    cv.style('border-radius', '16px');
    cv.style('width', '100%');
    cv.style('height', '100%');
    
    // Get webcam with container dimensions
    video = createCapture(VIDEO);
    video.size(containerWidth, containerHeight);
    video.hide();
    
    // Get dropdown
    posesDropdown = document.getElementById("posesDropdown");

    initImageUpload();
    initDragAndDrop();
    
    console.log("✅ Setup complete. Loading poses...");
    
    // Load all poses from YOLO backend
    loadAllYOLOPoses();
    
    // Hide placeholder when video starts
    setTimeout(() => {
        if (video && video.elt) {
            document.getElementById("cameraPlaceholder").style.display = "none";
            console.log("📹 Camera feed active");
        }
    }, 1500);
    
    // Handle window resize
    window.addEventListener('resize', function() {
        const newWidth = cameraContainer.clientWidth;
        const newHeight = cameraContainer.clientHeight;
        
        resizeCanvas(newWidth, newHeight);
        video.size(newWidth, newHeight);
        
        console.log(`🔄 Resized to: ${newWidth}x${newHeight}`);
    });
}

// Load all poses from YOLO backend
async function loadAllYOLOPoses() {
    try {
        console.log("📡 Fetching pose names from AI model...");
        window.updateConnectionStatus("Loading poses...", true);
        
        const response = await fetch("http://localhost:5000/all-poses");
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        console.log(`✅ Loaded ${data.poses.length} poses`);
        allYOLOPoses = data.poses;
        
        // Clear dropdown
        posesDropdown.innerHTML = '<option value="none">Choose a yoga pose to practice...</option>';
        
        // Categorize poses
        const standingPoses = [];
        const seatedPoses = [];
        const balancingPoses = [];
        const backbendPoses = [];
        const otherPoses = [];
        
        // Categorize poses
        data.poses.forEach(pose => {
            const lowerPose = pose.toLowerCase();
            
            if (lowerPose.includes('tada') || lowerPose.includes('mountain') || 
                lowerPose.includes('triangle') || lowerPose.includes('warrior')) {
                standingPoses.push(pose);
            } else if (lowerPose.includes('padma') || lowerPose.includes('lotus') || 
                      lowerPose.includes('sukha') || lowerPose.includes('seated')) {
                seatedPoses.push(pose);
            } else if (lowerPose.includes('tree') || lowerPose.includes('vriksh') || 
                      lowerPose.includes('balance') || lowerPose.includes('eagle')) {
                balancingPoses.push(pose);
            } else if (lowerPose.includes('cobra') || lowerPose.includes('bhujang') || 
                      lowerPose.includes('wheel') || lowerPose.includes('bridge')) {
                backbendPoses.push(pose);
            } else {
                otherPoses.push(pose);
            }
        });
        
        // Add categorized options
        const categories = [
            { name: "🧍 Standing Poses", poses: standingPoses },
            { name: "🧘 Seated Poses", poses: seatedPoses },
            { name: "⚖️ Balancing Poses", poses: balancingPoses },
            { name: "🔙 Backbend Poses", poses: backbendPoses },
            { name: "📋 Other Poses", poses: otherPoses }
        ];
        
        categories.forEach(category => {
            if (category.poses.length > 0) {
                const optgroup = document.createElement("optgroup");
                optgroup.label = `${category.name} (${category.poses.length})`;
                
                // Sort poses alphabetically
                category.poses.sort().forEach(pose => {
                    const option = document.createElement("option");
                    option.value = pose;
                    option.text = pose;
                    optgroup.appendChild(option);
                });
                
                posesDropdown.appendChild(optgroup);
            }
        });
        
        console.log(`📋 Dropdown populated with ${data.poses.length} poses`);
        window.updateConnectionStatus(`Ready - ${data.poses.length} poses loaded`, true);
        
        // Add event listener for pose selection
        posesDropdown.addEventListener("change", function() {
            selected_pose = this.value;
            loadPoseImage();
            console.log(`🎯 Selected pose: ${selected_pose}`);
        });
        
    } catch (err) {
        console.error("❌ Failed to load poses:", err);
        window.updateConnectionStatus("Failed to load poses", false);
        window.showNotification("Cannot load poses from backend. Check if Python server is running.", "error");
        
        // Emergency fallback
        posesDropdown.innerHTML = `
            <option value="none">Connection Error - Using demo poses</option>
            <optgroup label="Demo Poses (8)">
                <option value="Tadasana">Tadasana (Mountain Pose)</option>
                <option value="Vrikshasana">Vrikshasana (Tree Pose)</option>
                <option value="Trikonasana">Trikonasana (Triangle Pose)</option>
                <option value="Adho Mukha Svanasana">Adho Mukha Svanasana (Downward Dog)</option>
                <option value="Bhujangasana">Bhujangasana (Cobra Pose)</option>
                <option value="Padmasana">Padmasana (Lotus Pose)</option>
                <option value="Virabhadrasana">Virabhadrasana (Warrior Pose)</option>
                <option value="Sukhasana">Sukhasana (Easy Pose)</option>
            </optgroup>
        `;
    }
}

// Your existing draw() function - ADD THIS CODE:
function draw() {
    // Clear with dark background for camera feed
    background(25, 25, 35);
    
    // Draw video feed
    if (video) {
        // Center and fit video
        let aspectRatio = video.width / video.height;
        let canvasAspect = width / height;
        
        if (aspectRatio > canvasAspect) {
            // Video is wider
            let newWidth = width;
            let newHeight = width / aspectRatio;
            image(video, 0, (height - newHeight) / 2, newWidth, newHeight);
        } else {
            // Video is taller
            let newHeight = height;
            let newWidth = height * aspectRatio;
            image(video, (width - newWidth) / 2, 0, newWidth, newHeight);
        }
        
        // === ADD THIS SECTION ===
        // Draw pose landmarks OVER the video
        if (window.showLandmarks && window.currentKeypoints && window.currentKeypoints.length > 0) {
            if (window.simpleVisualizationMode) {
                // Use simple red dots and lines
                drawKeypoints();
                drawSkeleton();
            } else {
                // Use advanced colored visualization
                drawPoseLandmarks();
            }
        }
        // === END ADDED SECTION ===
    }
    
    // Add overlay for detected pose (your existing code continues...)
    if (poseLabel && poseLabel !== "Detecting..." && poseLabel !== "Error") {
        fill(255, 255, 255, 200);
        noStroke();
        rect(20, 20, 350, 80, 15);
        
        fill(79, 70, 229);
        textSize(24);
        textAlign(LEFT, CENTER);
        text("🤖 AI Detected:", 40, 45);
        
        fill(30, 30, 40);
        textSize(28);
        textFont('Arial');
        textStyle(BOLD);
        text(poseLabel, 40, 75);
    }
    
    // Draw keypoint legend in corner
    drawKeypointLegend();
}
// Draw a legend explaining keypoint colors
function drawKeypointLegend() {
    const legendX = width - 180;
    const legendY = 20;
    
    fill(0, 0, 0, 180);
    noStroke();
    rect(legendX, legendY, 160, 120, 10);
    
    fill(255, 255, 255);
    textSize(14);
    textAlign(LEFT);
    text("Pose Landmarks", legendX + 10, legendY + 25);
    
    textSize(10);
    
    // High confidence
    fill(0, 255, 0, 200);
    circle(legendX + 15, legendY + 45, 8);
    fill(255, 255, 255);
    text("High confidence", legendX + 30, legendY + 49);
    
    // Medium confidence
    fill(255, 165, 0, 200);
    circle(legendX + 15, legendY + 65, 8);
    fill(255, 255, 255);
    text("Medium confidence", legendX + 30, legendY + 69);
    
    // Low confidence
    fill(255, 0, 0, 150);
    circle(legendX + 15, legendY + 85, 8);
    fill(255, 255, 255);
    text("Low confidence", legendX + 30, legendY + 89);
    
    // Angles
    stroke(255, 0, 255, 180);
    strokeWeight(2);
    noFill();
    arc(legendX + 15, legendY + 105, 15, 15, 0, PI/2);
    fill(255, 255, 255);
    noStroke();
    text("Joint angles", legendX + 30, legendY + 109);
}
// Start yoga session - called from HTML
window.startYogaSession = function() {
    sessionActive = true;
    stats.sessionStart = Date.now();
    stats.totalDetections = 0;
    stats.correctMatches = 0;
    console.log("🎯 YOGA SESSION STARTED - AI detection active");
    
    // Start detection interval
    if (!window.detectionInterval) {
        window.detectionInterval = setInterval(() => {
            if (sessionActive && video && video.elt) {
                captureFrameFromVideo(video.elt);
            }
        }, 2000); // Detect every 2 seconds
    }
    
    // Force an immediate detection
    setTimeout(() => {
        if (video && video.elt && sessionActive) {
            console.log("📸 Taking first detection...");
            captureFrameFromVideo(video.elt);
        }
    }, 500);
};

// Stop yoga session - called from HTML
window.stopYogaSession = function() {
    sessionActive = false;
    console.log("⏸️ YOGA SESSION PAUSED - AI detection paused");
    
    // Clear the detection interval
    if (window.detectionInterval) {
        clearInterval(window.detectionInterval);
        window.detectionInterval = null;
    }
};

// YOLO Functions
async function sendFrameToYOLO(imageBlob) {
    if (!sessionActive) {
        console.log("⏸️ Session not active, skipping detection");
        return;
    }
    
    let formData = new FormData();
    formData.append("image", imageBlob, `frame_${Date.now()}.jpg`);

    try {
        console.log("📤 Sending frame to YOLO...");
        window.updateConnectionStatus("Detecting pose...", true);
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000);
        
        let response = await fetch("http://localhost:5000/predict", {
            method: "POST",
            body: formData,
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error("❌ HTTP Error:", errorText);
            throw new Error(`Server error: ${response.status} - ${errorText}`);
        }

        let data = await response.json();
        console.log("✅ AI detected:", data.pose, `(${(data.confidence * 100).toFixed(1)}%)`);
        
        // Store keypoints for drawing
        if (data.keypoints && data.keypoints.length > 0) {
            window.currentKeypoints = data.keypoints;
            console.log(`📊 Received ${data.keypoints.length} keypoints`);
        } else {
            window.currentKeypoints = null;
        }
        
        // Update pose label for drawing
        poseLabel = data.pose;
        
        // Update statistics
        stats.totalDetections++;
        if (data.confidence) {
            stats.avgConfidence = (stats.avgConfidence * (stats.totalDetections - 1) + data.confidence) / stats.totalDetections;
        }
        
        // Check if matches selected pose
        if (selected_pose !== "none" && selected_pose === data.pose) {
            stats.correctMatches++;
        }
        
        // Update UI via global function
        if (window.updateDetectionUI) {
            window.updateDetectionUI(data);
        }
        
        window.updateConnectionStatus("Ready - Detection complete", true);
        
    } catch (err) {
        console.error("❌ YOLO error:", err.name, "-", err.message);
        
        if (err.name === 'AbortError') {
            window.updateConnectionStatus("Timeout - Backend slow", false);
        } else if (err.message.includes('Failed to fetch')) {
            window.updateConnectionStatus("Backend disconnected", false);
        } else {
            window.updateConnectionStatus(`Error: ${err.message.substring(0, 30)}...`, false);
        }
        
        poseLabel = "Connection Error";
        window.currentKeypoints = null;
        
        if (window.updateDetectionUI) {
            window.updateDetectionUI({
                pose: "Connection Error",
                confidence: 0,
                error: err.message
            });
        }
    }
}

// Draw pose landmarks/keypoints on canvas
// Replace your existing drawPoseLandmarks() function with this enhanced version:
function drawPoseLandmarks() {
    if (!window.showLandmarks || !window.currentKeypoints || window.currentKeypoints.length === 0) {
        return;
    }
    
    // Use SIMPLE visualization (red dots and lines) if window.simpleVisualization is true
    if (window.simpleVisualization) {
        drawKeypointsSimple();
        drawSkeletonSimple();
    } else {
        // Use ADVANCED visualization (colored by confidence, with angles)
        drawPoseLandmarksAdvanced();
    }
}

// Simple keypoints drawing (red dots only)
// Updated simple keypoints drawing function
function drawKeypoints() {
    if (!window.currentKeypoints) return;
    
    for (let j = 0; j < window.currentKeypoints.length; j++) {
        // A keypoint is an object describing a body part
        let keypoint = window.currentKeypoints[j];
        // Only draw an ellipse if the confidence is bigger than 0.2
        if (keypoint.confidence > 0.2) {
            const x = mapKeypointToCanvas(keypoint.x, 'x');
            const y = mapKeypointToCanvas(keypoint.y, 'y');
            
            fill(255, 0, 0);
            noStroke();
            ellipse(x, y, 10, 10);
        }
    }
}

// Updated simple skeleton drawing function
function drawSkeleton() {
    if (!window.currentKeypoints) return;
    
    // Define basic skeleton connections
    const skeleton = [
        ['left_shoulder', 'right_shoulder'],
        ['left_shoulder', 'left_elbow'],
        ['left_elbow', 'left_wrist'],
        ['right_shoulder', 'right_elbow'],
        ['right_elbow', 'right_wrist'],
        ['left_shoulder', 'left_hip'],
        ['right_shoulder', 'right_hip'],
        ['left_hip', 'right_hip'],
        ['left_hip', 'left_knee'],
        ['left_knee', 'left_ankle'],
        ['right_hip', 'right_knee'],
        ['right_knee', 'right_ankle']
    ];
    
    // Create a map of keypoints by name
    const keypointsMap = {};
    window.currentKeypoints.forEach(kp => {
        if (kp.name && kp.x && kp.y && kp.confidence > 0.2) {
            keypointsMap[kp.name] = kp;
        }
    });
    
    stroke(255, 0, 0);
    strokeWeight(3);
    
    for (let j = 0; j < skeleton.length; j++) {
        let partA = keypointsMap[skeleton[j][0]];
        let partB = keypointsMap[skeleton[j][1]];
        
        if (partA && partB) {
            const startX = mapKeypointToCanvas(partA.x, 'x');
            const startY = mapKeypointToCanvas(partA.y, 'y');
            const endX = mapKeypointToCanvas(partB.x, 'x');
            const endY = mapKeypointToCanvas(partB.y, 'y');
            
            line(startX, startY, endX, endY);
        }
    }
}

// Advanced visualization (your existing code renamed)
function drawPoseLandmarksAdvanced() {
    if (!window.currentKeypoints || window.currentKeypoints.length === 0) {
        return;
    }
    
    // Define connections between keypoints (skeleton)
    const connections = [
        // Face
        ['left_ear', 'left_eye'],
        ['right_ear', 'right_eye'],
        ['left_eye', 'right_eye'],
        ['left_eye', 'nose'],
        ['right_eye', 'nose'],
        
        // Torso
        ['left_shoulder', 'right_shoulder'],
        ['left_shoulder', 'left_hip'],
        ['right_shoulder', 'right_hip'],
        ['left_hip', 'right_hip'],
        
        // Left arm
        ['left_shoulder', 'left_elbow'],
        ['left_elbow', 'left_wrist'],
        
        // Right arm
        ['right_shoulder', 'right_elbow'],
        ['right_elbow', 'right_wrist'],
        
        // Left leg
        ['left_hip', 'left_knee'],
        ['left_knee', 'left_ankle'],
        
        // Right leg
        ['right_hip', 'right_knee'],
        ['right_knee', 'right_ankle']
    ];
    
    // Create a map of keypoints by name for easy lookup
    const keypointsMap = {};
    window.currentKeypoints.forEach(kp => {
        if (kp.name && kp.x && kp.y && kp.confidence > 0.3) {
            keypointsMap[kp.name] = kp;
        }
    });
    
    // Draw connections (skeleton lines)
    stroke(0, 255, 0, 200);
    strokeWeight(3);
    
    connections.forEach(connection => {
        const [startName, endName] = connection;
        const start = keypointsMap[startName];
        const end = keypointsMap[endName];
        
        if (start && end) {
            // Adjust coordinates to match video display
            const startX = mapKeypointToCanvas(start.x, 'x');
            const startY = mapKeypointToCanvas(start.y, 'y');
            const endX = mapKeypointToCanvas(end.x, 'x');
            const endY = mapKeypointToCanvas(end.y, 'y');
            
            line(startX, startY, endX, endY);
        }
    });
    
    // Draw keypoints (joints)
    noStroke();
    window.currentKeypoints.forEach(kp => {
        if (kp.x && kp.y && kp.confidence > 0.3) {
            const x = mapKeypointToCanvas(kp.x, 'x');
            const y = mapKeypointToCanvas(kp.y, 'y');
            
            // Color code by confidence
            if (kp.confidence > 0.7) {
                fill(0, 255, 0, 200); // Green - high confidence
            } else if (kp.confidence > 0.4) {
                fill(255, 165, 0, 200); // Orange - medium confidence
            } else {
                fill(255, 0, 0, 150); // Red - low confidence
            }
            
            // Draw circle for joint
            circle(x, y, 10);
            
            // Draw smaller inner circle
            fill(255, 255, 255, 200);
            circle(x, y, 4);
            
            // Optionally display joint name (for debugging)
            if (kp.name && kp.confidence > 0.7) {
                fill(255, 255, 255, 180);
                textSize(10);
                textAlign(CENTER);
                text(kp.name.replace('_', '\n'), x, y - 15);
            }
        }
    });
    
    // Draw angles at major joints if we have enough points
    drawJointAngles(keypointsMap);
}

// Helper function to map keypoint coordinates to canvas coordinates
function mapKeypointToCanvas(value, axis) {
    const video = window.video; // Access the global video object
    
    if (!video || !video.width || !video.height) {
        return value;
    }
    
    const canvasWidth = width;
    const canvasHeight = height;
    const videoWidth = video.width;
    const videoHeight = video.height;
    
    // Calculate the displayed video area (centered)
    let displayX, displayY, displayWidth, displayHeight;
    
    const videoAspect = videoWidth / videoHeight;
    const canvasAspect = canvasWidth / canvasHeight;
    
    if (videoAspect > canvasAspect) {
        // Video is wider than canvas
        displayWidth = canvasWidth;
        displayHeight = canvasWidth / videoAspect;
        displayX = 0;
        displayY = (canvasHeight - displayHeight) / 2;
    } else {
        // Video is taller than canvas
        displayHeight = canvasHeight;
        displayWidth = canvasHeight * videoAspect;
        displayX = (canvasWidth - displayWidth) / 2;
        displayY = 0;
    }
    
    if (axis === 'x') {
        // Map from original video coordinates to displayed coordinates
        const scale = displayWidth / videoWidth;
        return displayX + (value * scale);
    } else { // 'y'
        const scale = displayHeight / videoHeight;
        return displayY + (value * scale);
    }
}

// Draw angles at joints (elbows, knees, shoulders, hips)
function drawJointAngles(keypointsMap) {
    const anglesToDraw = [
        {
            name: 'Left Elbow',
            points: ['left_shoulder', 'left_elbow', 'left_wrist'],
            color: [255, 0, 255]
        },
        {
            name: 'Right Elbow',
            points: ['right_shoulder', 'right_elbow', 'right_wrist'],
            color: [255, 0, 255]
        },
        {
            name: 'Left Knee',
            points: ['left_hip', 'left_knee', 'left_ankle'],
            color: [0, 255, 255]
        },
        {
            name: 'Right Knee',
            points: ['right_hip', 'right_knee', 'right_ankle'],
            color: [0, 255, 255]
        },
        {
            name: 'Left Shoulder',
            points: ['left_hip', 'left_shoulder', 'left_elbow'],
            color: [255, 255, 0]
        },
        {
            name: 'Right Shoulder',
            points: ['right_hip', 'right_shoulder', 'right_elbow'],
            color: [255, 255, 0]
        }
    ];
    
    anglesToDraw.forEach(angleConfig => {
        const [aName, bName, cName] = angleConfig.points;
        const pointA = keypointsMap[aName];
        const pointB = keypointsMap[bName];
        const pointC = keypointsMap[cName];
        
        if (pointA && pointB && pointC) {
            const ax = mapKeypointToCanvas(pointA.x, 'x');
            const ay = mapKeypointToCanvas(pointA.y, 'y');
            const bx = mapKeypointToCanvas(pointB.x, 'x');
            const by = mapKeypointToCanvas(pointB.y, 'y');
            const cx = mapKeypointToCanvas(pointC.x, 'x');
            const cy = mapKeypointToCanvas(pointC.y, 'y');
            
            // Calculate angle using law of cosines
            const angle = calculateAngle(ax, ay, bx, by, cx, cy);
            
            // Draw angle arc
            stroke(angleConfig.color[0], angleConfig.color[1], angleConfig.color[2], 180);
            strokeWeight(2);
            noFill();
            
            // Draw arc at the joint (point B)
            const radius = 20;
            const startAngle = atan2(ay - by, ax - bx);
            const endAngle = atan2(cy - by, cx - bx);
            
            arc(bx, by, radius * 2, radius * 2, startAngle, endAngle);
            
            // Display angle value
            fill(255, 255, 255, 220);
            noStroke();
            textSize(12);
            textAlign(CENTER);
            text(`${Math.round(angle)}°`, bx, by - radius - 5);
        }
    });
}

// Calculate angle between three points (B is the vertex)
function calculateAngle(ax, ay, bx, by, cx, cy) {
    const ab = {x: ax - bx, y: ay - by};
    const cb = {x: cx - bx, y: cy - by};
    
    const dot = (ab.x * cb.x + ab.y * cb.y);
    const magAB = Math.sqrt(ab.x * ab.x + ab.y * ab.y);
    const magCB = Math.sqrt(cb.x * cb.x + cb.y * cb.y);
    
    const cosTheta = dot / (magAB * magCB);
    const theta = Math.acos(Math.min(Math.max(cosTheta, -1), 1));
    
    return theta * (180 / Math.PI); // Convert to degrees
}

function captureFrameFromVideo(video) {
    if (!sessionActive) {
        console.log("⏸️ Session paused, skipping frame");
        return;
    }
    
    if (!video.videoWidth || !video.videoHeight) {
        console.log("📹 Video not ready yet");
        return;
    }
    
    console.log("📸 Capturing frame for AI analysis...");
    
    const canvas = document.createElement("canvas");
    canvas.width = 640;
    canvas.height = 480;
    
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, video.videoWidth, video.videoHeight, 0, 0, 640, 480);
    
    canvas.toBlob((blob) => {
        if (blob && blob.size > 10240) {
            console.log(`📦 Frame size: ${(blob.size / 1024).toFixed(1)} KB`);
            sendFrameToYOLO(blob);
        } else {
            console.log("📦 Frame too small, skipping");
        }
    }, "image/jpeg", 0.8);
}

// Load pose image when selected
function loadPoseImage() {
    let selected = posesDropdown.value;
    const poseImage = document.getElementById("poseImage");
    const poseName = document.getElementById("poseName");
    
    if (selected && selected !== "none") {
        // For demo - in real app, you'd have images for all poses
        const demoImages = {
            "Tadasana": "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&h=400&fit=crop",
            "Vrikshasana": "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?w=400&h=400&fit=crop",
            "Trikonasana": "https://images.unsplash.com/photo-1594736797933-d0401ba94693?w=400&h=400&fit=crop",
            "Adho Mukha Svanasana": "https://images.unsplash.com/photo-1594730005115-6dac5c55e3c9?w=400&h=400&fit=crop",
            "Bhujangasana": "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?w=400&h=400&fit=crop"
        };
        
        if (selected in demoImages) {
            poseImage.src = demoImages[selected];
            poseImage.style.display = "block";
            poseName.textContent = selected;
        } else {
            // Show placeholder for poses without images
            poseImage.style.display = "none";
            poseName.textContent = `${selected} (No reference image available)`;
        }
    } else {
        poseImage.style.display = "none";
        poseName.textContent = "Select a pose to see reference";
    }
}

// Make functions globally available
window.setup = setup;
window.loadPoseImage = loadPoseImage;
// ===== IMAGE UPLOAD FUNCTIONALITY =====

// Global variable for uploaded image
let uploadedImageBlob = null;
let uploadedImageUrl = null;

// Initialize upload functionality
function initImageUpload() {
    const uploadInput = document.getElementById('imageUpload');
    const uploadPreview = document.getElementById('uploadPreview');
    const uploadedImage = document.getElementById('uploadedImage');
    const uploadHelp = document.getElementById('uploadHelp');
    
    uploadInput.addEventListener('change', function(event) {
        const file = event.target.files[0];
        
        if (!file) return;
        
        // Check file type
        if (!file.type.match('image.*')) {
            window.showNotification("Please select an image file", "error");
            return;
        }
        
        // Check file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            window.showNotification("Image is too large (max 5MB)", "error");
            return;
        }
        
        // Create blob URL for preview
        uploadedImageBlob = file;
        uploadedImageUrl = URL.createObjectURL(file);
        
        // Show preview
        uploadedImage.src = uploadedImageUrl;
        uploadPreview.style.display = 'block';
        uploadHelp.style.display = 'none';
        
        // Show file info
        const fileSizeKB = (file.size / 1024).toFixed(1);
        console.log(`📁 Image uploaded: ${file.name} (${fileSizeKB} KB)`);
        
        // Show upload results card
        document.getElementById('uploadResultsCard').style.display = 'block';
        document.getElementById('uploadedPoseResult').textContent = 'Ready to analyze';
        
        window.showNotification(`Image uploaded: ${file.name}`, "success");
    });
}

// Analyze the uploaded image
async function analyzeUploadedImage() {
    if (!uploadedImageBlob) {
        window.showNotification("Please upload an image first", "error");
        return;
    }
    
    console.log("🔍 Analyzing uploaded image...");
    const startTime = Date.now();
    
    // Show analyzing state
    document.getElementById('uploadedPoseResult').textContent = 'Analyzing...';
    document.getElementById('uploadConfidenceValue').textContent = 'Processing';
    document.getElementById('uploadConfidenceFill').style.width = '0%';
    document.getElementById('uploadMatchFeedback').style.display = 'none';
    
    try {
        // Send to YOLO backend
        let formData = new FormData();
        formData.append("image", uploadedImageBlob, `upload_${Date.now()}.jpg`);
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000);
        
        let response = await fetch("http://localhost:5000/predict", {
            method: "POST",
            body: formData,
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        let data = await response.json();
        const endTime = Date.now();
        const analysisTime = ((endTime - startTime) / 1000).toFixed(2);
        
        console.log("✅ Image analysis result:", data.pose, `(${(data.confidence * 100).toFixed(1)}%)`);
        
        // Store keypoints for uploaded image
        if (data.keypoints && data.keypoints.length > 0) {
            console.log(`📊 Received ${data.keypoints.length} keypoints for uploaded image`);
        }
        
        // Update UI with results
        updateUploadResultsUI(data, analysisTime);
        
        // Update stats
        window.detectionCount = (window.detectionCount || 0) + 1;
        window.updateStats();
        
        window.showNotification(`Analysis complete: ${data.pose} (${Math.round(data.confidence * 100)}% confidence)`, "success");
        
    } catch (error) {
        console.error("❌ Image analysis failed:", error);
        
        document.getElementById('uploadedPoseResult').textContent = 'Analysis Failed';
        document.getElementById('uploadConfidenceValue').textContent = 'Error';
        document.getElementById('uploadConfidenceFill').style.width = '0%';
        
        document.getElementById('uploadMatchFeedback').className = "match-feedback match-incorrect";
        document.getElementById('uploadMatchFeedback').innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${error.message}`;
        document.getElementById('uploadMatchFeedback').style.display = 'block';
        
        window.showNotification("Failed to analyze image", "error");
    }
}
// Update UI with uploaded image analysis results
function updateUploadResultsUI(data, analysisTime) {
    const pose = data.pose || "Unknown Pose";
    const confidence = data.confidence || 0;
    const percent = Math.round(confidence * 100);
    
    // Update pose result
    document.getElementById('uploadedPoseResult').textContent = pose;
    document.getElementById('uploadConfidencePercent').textContent = `${percent}%`;
    document.getElementById('uploadConfidenceValue').textContent = `${percent}%`;
    
    // Animate confidence bar
    setTimeout(() => {
        document.getElementById('uploadConfidenceFill').style.width = `${percent}%`;
        
        // Color coding
        if (percent >= 80) {
            document.getElementById('uploadConfidenceFill').style.background = "linear-gradient(to right, #10b981, #22c55e)";
            document.getElementById('uploadedPoseResult').style.color = "#10b981";
        } else if (percent >= 60) {
            document.getElementById('uploadConfidenceFill').style.background = "linear-gradient(to right, #f59e0b, #fbbf24)";
            document.getElementById('uploadedPoseResult').style.color = "#f59e0b";
        } else {
            document.getElementById('uploadConfidenceFill').style.background = "linear-gradient(to right, #ef4444, #f87171)";
            document.getElementById('uploadedPoseResult').style.color = "#ef4444";
        }
    }, 100);
    
    // Update analysis time
    document.getElementById('uploadAnalysisTime').textContent = `${analysisTime}s`;
    
    // Update file size
    const fileSizeKB = (uploadedImageBlob.size / 1024).toFixed(1);
    document.getElementById('uploadFileSize').textContent = `${fileSizeKB} KB`;
    
    // Check match with selected pose
    const selectedPose = document.getElementById('posesDropdown').value;
    const feedbackDiv = document.getElementById('uploadMatchFeedback');
    
    if (selectedPose !== "none" && pose === selectedPose) {
        feedbackDiv.className = "match-feedback match-correct";
        feedbackDiv.innerHTML = '<i class="fas fa-check-circle"></i> Perfect Match!';
        feedbackDiv.style.display = "block";
    } else if (selectedPose !== "none") {
        feedbackDiv.className = "match-feedback match-incorrect";
        feedbackDiv.innerHTML = `<i class="fas fa-times-circle"></i> Expected: ${selectedPose}`;
        feedbackDiv.style.display = "block";
    } else {
        feedbackDiv.style.display = "none";
    }
    
    // Also update main detection UI if available
    if (window.updateDetectionUI) {
        window.updateDetectionUI(data);
    }
}

// Clear uploaded image
function clearUploadedImage() {
    // Clean up blob URL
    if (uploadedImageUrl) {
        URL.revokeObjectURL(uploadedImageUrl);
    }
    
    // Reset variables
    uploadedImageBlob = null;
    uploadedImageUrl = null;
    
    // Reset UI
    document.getElementById('imageUpload').value = '';
    document.getElementById('uploadPreview').style.display = 'none';
    document.getElementById('uploadHelp').style.display = 'block';
    document.getElementById('uploadedImage').src = '';
    
    // Hide results card
    document.getElementById('uploadResultsCard').style.display = 'none';
    
    console.log("🗑️ Cleared uploaded image");
    window.showNotification("Upload cleared", "info");
}

// Make functions globally available
window.analyzeUploadedImage = analyzeUploadedImage;
window.clearUploadedImage = clearUploadedImage;

// Drag and drop functionality
function initDragAndDrop() {
    const uploadContainer = document.getElementById('uploadContainer');
    const uploadInput = document.getElementById('imageUpload');
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadContainer.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    // Highlight drop zone when dragging over
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadContainer.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadContainer.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight(e) {
        uploadContainer.style.backgroundColor = '#f0f9ff';
        uploadContainer.style.border = '2px dashed #3b82f6';
    }
    
    function unhighlight(e) {
        uploadContainer.style.backgroundColor = '';
        uploadContainer.style.border = '';
    }
    
    // Handle dropped files
    uploadContainer.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            uploadInput.files = files;
            
            // Trigger change event
            const event = new Event('change', { bubbles: true });
            uploadInput.dispatchEvent(event);
        }
    }
}


// Global variable to track landmarks visibility
window.showLandmarks = true;

// Simple keypoints drawing (red dots) - Modern version compatible with your data structure
function drawKeypoints() {
  if (!window.currentKeypoints) return;
  
  for (let j = 0; j < window.currentKeypoints.length; j++) {
    // A keypoint is an object describing a body part (like right_shoulder or left_elbow)
    let keypoint = window.currentKeypoints[j];
    // Only draw an ellipse if the pose probability is bigger than 0.2
    if (keypoint.confidence > 0.2) {
      const x = mapKeypointToCanvas(keypoint.x, 'x');
      const y = mapKeypointToCanvas(keypoint.y, 'y');
      
      fill(255, 0, 0);
      noStroke();
      ellipse(x, y, 10, 10);
    }
  }
}

// Simple skeleton drawing (red lines) - Modern version compatible with your data structure
function drawSkeleton() {
  if (!window.currentKeypoints) return;
  
  // Define skeleton connections
  const skeletonConnections = [
    ['left_shoulder', 'right_shoulder'],
    ['left_shoulder', 'left_elbow'],
    ['left_elbow', 'left_wrist'],
    ['right_shoulder', 'right_elbow'],
    ['right_elbow', 'right_wrist'],
    ['left_shoulder', 'left_hip'],
    ['right_shoulder', 'right_hip'],
    ['left_hip', 'right_hip'],
    ['left_hip', 'left_knee'],
    ['left_knee', 'left_ankle'],
    ['right_hip', 'right_knee'],
    ['right_knee', 'right_ankle']
  ];
  
  // Create a map of keypoints by name
  const keypointsMap = {};
  window.currentKeypoints.forEach(kp => {
    if (kp.name && kp.confidence > 0.2) {
      keypointsMap[kp.name] = kp;
    }
  });
  
  stroke(255, 0, 0);
  strokeWeight(3);
  
  for (let j = 0; j < skeletonConnections.length; j++) {
    let partA = keypointsMap[skeletonConnections[j][0]];
    let partB = keypointsMap[skeletonConnections[j][1]];
    
    if (partA && partB) {
      const startX = mapKeypointToCanvas(partA.x, 'x');
      const startY = mapKeypointToCanvas(partA.y, 'y');
      const endX = mapKeypointToCanvas(partB.x, 'x');
      const endY = mapKeypointToCanvas(partB.y, 'y');
      
      line(startX, startY, endX, endY);
    }
  }
}
// Toggle between simple and advanced visualization modes
function toggleVisualizationMode() {
    window.simpleVisualizationMode = !window.simpleVisualizationMode;
    const button = document.getElementById('visualizationToggle');
    
    if (window.simpleVisualizationMode) {
        button.innerHTML = '<i class="fas fa-projector"></i> Switch to Advanced View';
        button.classList.remove('secondary-btn');
        button.classList.add('accent-btn');
        window.showNotification("Simple visualization mode (red dots & lines)", "info");
    } else {
        button.innerHTML = '<i class="fas fa-projector"></i> Switch to Simple View';
        button.classList.remove('accent-btn');
        button.classList.add('secondary-btn');
        window.showNotification("Advanced visualization mode (colored by confidence)", "info");
    }
}

// Initialize the visualization mode variable
window.simpleVisualizationMode = false;
// Toggle landmarks display
function toggleLandmarks() {
    window.showLandmarks = !window.showLandmarks;
    const button = document.getElementById('landmarksBtn');
    
    if (window.showLandmarks) {
        button.innerHTML = '<i class="fas fa-circle-dot"></i> Hide Landmarks';
        button.classList.remove('secondary-btn');
        button.classList.add('primary-btn');
        window.showNotification("Landmarks displayed", "info");
    } else {
        button.innerHTML = '<i class="fas fa-circle-dot"></i> Show Landmarks';
        button.classList.remove('primary-btn');
        button.classList.add('secondary-btn');
        window.showNotification("Landmarks hidden", "info");
    }
}