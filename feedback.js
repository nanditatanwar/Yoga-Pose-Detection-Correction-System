// feedback.js - Flask backend yoga feedback system

class YogaFeedbackSystem {

    constructor() {
        console.log("🧘 Initializing Yoga Feedback System with Flask backend...");
        this.canvas = null;
        this.ctx = null;
        this.isRunning = false;
        this.lastFrameTime = 0;
        this.frameCount = 0;
        this.fps = 0;
        this.currentPose = 'tadasana';
        this.apiBaseUrl = 'http://localhost:5000/api';
        this.frameInterval = null;
        this.analysisInterval = null;
        this.isConnected = false;

        this.init();
    }

    async init() {
        // Set up canvas
        this.canvas = document.createElement('canvas');
        this.canvas.id = 'feedbackCanvas';
        this.ctx = this.canvas.getContext('2d');

        const cameraContainer = document.getElementById('cameraContainer');
        const existingCanvas = document.getElementById('feedbackCanvas');
        if (existingCanvas) existingCanvas.remove();

        cameraContainer.innerHTML = '';
        cameraContainer.appendChild(this.canvas);

        this.canvas.width = 640;
        this.canvas.height = 480;
        this.canvas.style.width = '100%';
        this.canvas.style.height = 'auto';
        this.canvas.style.objectFit = 'contain';
        this.canvas.style.backgroundColor = '#1A1200';
        this.canvas.style.borderRadius = '16px';

        this.showFallbackDisplay();

        // Connect to server and load poses
        await this.checkConnection();
        if (this.isConnected) {
            await this.loadPoses();
        }

        console.log("✅ Feedback system initialized");
    }

    async checkConnection() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            const data = await response.json();
            this.isConnected = true;
            console.log("✅ Connected to Flask server:", data);
        } catch (error) {
            console.error("❌ Cannot connect to Flask server:", error);
            this.isConnected = false;
            setTimeout(() => this.checkConnection(), 3000);
        }
    }

    async loadPoses() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/poses`);
            const data = await response.json();
            const dropdown = document.getElementById('posesDropdown');
            if (dropdown) {
                dropdown.innerHTML = '';
                Object.entries(data.poses).forEach(([id, name]) => {
                    const option = document.createElement('option');
                    option.value = id;
                    option.textContent = name;
                    if (id === this.currentPose) option.selected = true;
                    dropdown.appendChild(option);
                });
            }
        } catch (error) {
            console.error("❌ Error loading poses:", error);
        }
    }

    async startAnalysis() {
        if (this.isRunning) return;
        console.log("▶️ Starting pose analysis...");
        if (!this.isConnected) {
            this.showError("Cannot connect to server.");
            return;
        }

        try {
            const res = await fetch(`${this.apiBaseUrl}/start`, { method: 'POST' });
            const data = await res.json();
            console.log("✅ Server response:", data);

            this.isRunning = true;
            this.lastFrameTime = performance.now();
            this.frameCount = 0;

            this.startFrameStream();
            this.startAnalysisPolling();
        } catch (error) {
            console.error("❌ Error starting analysis:", error);
        }
    }

    startFrameStream() {
        if (this.frameInterval) clearInterval(this.frameInterval);

        this.frameInterval = setInterval(async () => {
            if (!this.isRunning) return;
            try {
                const res = await fetch(`${this.apiBaseUrl}/frame`);
                const data = await res.json();
                if (data.status === 'ok' && data.frame) this.displayFrame(data.frame);

                // FPS calculation
                const now = performance.now();
                const delta = now - this.lastFrameTime;
                this.frameCount++;
                if (delta >= 1000) {
                    this.fps = Math.round((this.frameCount * 1000) / delta);
                    this.lastFrameTime = now;
                    this.frameCount = 0;
                }
            } catch (err) {
                console.error("❌ Error fetching frame:", err);
                this.showFallbackDisplay();
            }
        }, 100);
    }

    displayFrame(frameData) {
        if (!this.canvas || !frameData) return;
        const img = new Image();
        img.onload = () => {
            this.canvas.width = img.width;
            this.canvas.height = img.height;
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
            this.ctx.drawImage(img, 0, 0);
        };
        img.src = frameData;
    }

    startAnalysisPolling() {
        if (this.analysisInterval) clearInterval(this.analysisInterval);

        this.analysisInterval = setInterval(async () => {
            if (!this.isRunning) return;
            try {
                const res = await fetch(`${this.apiBaseUrl}/analysis`);
                const analysis = await res.json();
                this.updateFeedbackUI(analysis);
            } catch (err) {
                console.error("❌ Error fetching analysis:", err);
            }
        }, 500);
    }

    updateAnalysisUI(analysis) {
    if (!analysis || !window.updateFeedbackUI) return;
    const uiData = {
        score: analysis.score || 0,
        feedback: analysis.feedback || ["No feedback available"],
        pose: analysis.pose || this.currentPose,
        pose_name: analysis.pose_name || "Unknown Pose"
    };
    window.updateFeedbackUI(uiData);
    if (window.updateDebugInfo) window.updateDebugInfo('pose', 'analyzing', `${analysis.pose_name || analysis.pose}: ${analysis.score}%`);
}


    updateFeedbackUI(data) {
        const container = document.getElementById('feedbackContainer');
        const scoreContainer = document.getElementById('scoreContainer');
        if (!container || !scoreContainer) return;

        // Clear previous feedback
        container.innerHTML = '';

        if (data.feedback && data.feedback.length > 0) {
            data.feedback.forEach(f => {
                const p = document.createElement('p');
                p.textContent = f;
                container.appendChild(p);
            });
        } else {
            container.textContent = "No feedback available";
        }

        scoreContainer.textContent = `Score: ${data.score || 0}`;
    }

    async stopAnalysis() {
        if (!this.isRunning) return;
        this.isRunning = false;
        clearInterval(this.frameInterval);
        clearInterval(this.analysisInterval);

        try {
            await fetch(`${this.apiBaseUrl}/stop`, { method: 'POST' });
        } catch (err) {
            console.error("❌ Error stopping server:", err);
        }
    }

    async changePose(poseId) {
        this.currentPose = poseId;
        try {
            await fetch(`${this.apiBaseUrl}/pose`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pose: poseId })
            });
        } catch (err) {
            console.error("❌ Error changing pose:", err);
        }
    }

    showFallbackDisplay() {
        if (!this.canvas) return;
        const ctx = this.canvas.getContext('2d');
        ctx.fillStyle = '#1A1200';
        ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        ctx.fillStyle = '#A69485';
        ctx.font = '20px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('Waiting for camera feed...', this.canvas.width / 2, this.canvas.height / 2);
    }

    showError(message) {
        console.error("❌ Error:", message);
    }
}

// Global functions
let feedbackSystem = null;
function setupFeedbackSystem() { feedbackSystem = new YogaFeedbackSystem(); }
function startFeedbackAnalysis() { feedbackSystem?.startAnalysis(); }
function stopFeedbackAnalysis() { feedbackSystem?.stopAnalysis(); }
function changePoseAnalysis(poseId) { feedbackSystem?.changePose(poseId); }

window.setupFeedbackSystem = setupFeedbackSystem;
window.startFeedbackAnalysis = startFeedbackAnalysis;
window.stopFeedbackAnalysis = stopFeedbackAnalysis;
window.changePoseAnalysis = changePoseAnalysis;

window.addEventListener('DOMContentLoaded', setupFeedbackSystem);
