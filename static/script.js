// Initialize Socket.IO connection
const socket = io();

// DOM Elements
const landingScreen = document.getElementById('landing-screen');
const setupScreen = document.getElementById('setup-screen');
const calibrationScreen = document.getElementById('calibration-screen');
const trainingScreen = document.getElementById('training-screen');
const homeBtn = document.getElementById('home-btn');
const getStartedBtn = document.getElementById('get-started-btn');

const armButtons = document.querySelectorAll('.arm-btn');
const startCameraBtn = document.getElementById('start-camera-btn');

const calibrationVideo = document.getElementById('calibration-video');
const calibrationCanvas = document.getElementById('calibration-canvas');
const calibrationInstruction = document.getElementById('calibration-instruction');
const calibrationTimer = document.getElementById('calibration-timer');
const currentAngleDisplay = document.getElementById('current-angle-display');

const calibrateMinBtn = document.getElementById('calibrate-min-btn');
const calibrateMaxBtn = document.getElementById('calibrate-max-btn');
const completeCalibrationBtn = document.getElementById('complete-calibration-btn');
const minStatus = document.getElementById('min-status');
const maxStatus = document.getElementById('max-status');

const trainingVideo = document.getElementById('training-video');
const trainingCanvas = document.getElementById('training-canvas');
const repCount = document.getElementById('rep-count');
const progressFill = document.getElementById('progress-fill');
const progressPercentage = document.getElementById('progress-percentage');
const currentAngle = document.getElementById('current-angle');
const angleRange = document.getElementById('angle-range');
const trackingArm = document.getElementById('tracking-arm');
const resetBtn = document.getElementById('reset-btn');
const recalibrateBtn = document.getElementById('recalibrate-btn');

// State
let selectedArm = 'left';
let stream = null;
let processingInterval = null;
let calibrationMode = null;
let calibrationCountdown = null;
let minAngle = null;
let maxAngle = null;
let isCalibrated = false;

// Navigation Functions
function showScreen(screen) {
    // Hide all screens
    landingScreen.classList.remove('active');
    setupScreen.classList.remove('active');
    calibrationScreen.classList.remove('active');
    trainingScreen.classList.remove('active');

    // Show selected screen
    screen.classList.add('active');

    // Show/hide home button (hide on landing, show on others)
    if (screen === landingScreen) {
        homeBtn.style.display = 'none';
    } else {
        homeBtn.style.display = 'flex';
    }
}

function goHome() {
    // Stop any active processing
    stopProcessing();

    // Stop camera stream
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }

    // Reset state
    isCalibrated = false;
    minAngle = null;
    maxAngle = null;
    calibrateMaxBtn.disabled = true;
    completeCalibrationBtn.disabled = true;
    minStatus.textContent = '';
    maxStatus.textContent = '';
    minStatus.className = 'calibration-status';
    maxStatus.className = 'calibration-status';

    // Clear video sources
    if (calibrationVideo.srcObject) {
        calibrationVideo.srcObject = null;
    }
    if (trainingVideo.srcObject) {
        trainingVideo.srcObject = null;
    }

    // Show landing screen
    showScreen(landingScreen);
}

// Get Started Button
getStartedBtn.addEventListener('click', () => {
    showScreen(setupScreen);
});

// Home Button
homeBtn.addEventListener('click', () => {
    if (confirm('Return to home? This will stop your current session.')) {
        goHome();
    }
});

// Arm Selection
armButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        armButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        selectedArm = btn.dataset.arm;
        socket.emit('set_arm_side', { arm_side: selectedArm });
    });
});

// Camera Access
startCameraBtn.addEventListener('click', async () => {
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 640, max: 1280 },
                height: { ideal: 480, max: 720 },
                facingMode: 'user',
                frameRate: { ideal: 30, max: 30 }
            },
            audio: false
        });

        calibrationVideo.srcObject = stream;
        trainingVideo.srcObject = stream;

        // Wait for video to be ready before starting processing
        calibrationVideo.onloadedmetadata = () => {
            console.log('Video loaded, starting processing...');
            showScreen(calibrationScreen);
            startProcessing(calibrationVideo, calibrationCanvas);
        };
    } catch (error) {
        console.error('Error accessing camera:', error);
        alert('Unable to access camera. Please ensure camera permissions are granted.');
    }
});

// Calibration Min
calibrateMinBtn.addEventListener('click', () => {
    calibrationMode = 'min';
    socket.emit('start_calibration_min');

    calibrateMinBtn.disabled = true;
    calibrateMaxBtn.disabled = true;
    document.getElementById('step-min').classList.add('active');

    minStatus.textContent = 'Calibrating...';
    minStatus.className = 'calibration-status active';

    let countdown = 7;
    calibrationInstruction.textContent = 'ARM DOWN, FULLY STRAIGHT - HOLD';
    calibrationTimer.textContent = `${countdown}s`;

    calibrationCountdown = setInterval(() => {
        countdown--;
        calibrationTimer.textContent = `${countdown}s`;

        if (countdown <= 0) {
            clearInterval(calibrationCountdown);

            // Send complete signal to finalize MIN calibration
            socket.emit('complete_calibration_min');

            // Wait a bit for server response before clearing mode
            setTimeout(() => {
                calibrationMode = null;
                calibrateMinBtn.disabled = false;
                calibrateMaxBtn.disabled = false;
                document.getElementById('step-min').classList.remove('active');

                calibrationInstruction.textContent = '';
                calibrationTimer.textContent = '';

                // Enable next step
                document.getElementById('step-max').classList.add('active');
            }, 100);
        }
    }, 1000);
});

// Calibration Max
calibrateMaxBtn.addEventListener('click', () => {
    calibrationMode = 'max';
    socket.emit('start_calibration_max');

    calibrateMinBtn.disabled = true;
    calibrateMaxBtn.disabled = true;

    maxStatus.textContent = 'Calibrating...';
    maxStatus.className = 'calibration-status active';

    let countdown = 7;
    calibrationInstruction.textContent = 'CURL UP FULLY - HOLD AT THE TOP';
    calibrationTimer.textContent = `${countdown}s`;

    calibrationCountdown = setInterval(() => {
        countdown--;
        calibrationTimer.textContent = `${countdown}s`;

        if (countdown <= 0) {
            clearInterval(calibrationCountdown);

            // Send complete signal to finalize MAX calibration
            socket.emit('complete_calibration_max');

            // Wait a bit for server response before clearing mode
            setTimeout(() => {
                calibrationMode = null;
                calibrateMinBtn.disabled = false;
                calibrateMaxBtn.disabled = false;
                document.getElementById('step-max').classList.remove('active');

                calibrationInstruction.textContent = '';
                calibrationTimer.textContent = '';
                // "Start Training" is enabled by the server's calibration_done event.
            }, 100);
        }
    }, 1000);
});

// Complete Calibration
completeCalibrationBtn.addEventListener('click', () => {
    if (!isCalibrated) {
        alert('Please complete both calibration steps first.');
        return;
    }

    stopProcessing();
    showScreen(trainingScreen);

    // Update tracking arm display
    trackingArm.textContent = selectedArm === 'left' ? 'Left Arm' : 'Right Arm';
    angleRange.textContent = `${minAngle}° - ${maxAngle}°`;

    startProcessing(trainingVideo, trainingCanvas);
});

// Reset Counter
resetBtn.addEventListener('click', () => {
    socket.emit('reset_counter');
});

// Recalibrate
recalibrateBtn.addEventListener('click', () => {
    if (confirm('This will reset your calibration. Continue?')) {
        stopProcessing();
        showScreen(calibrationScreen);

        // Reset calibration state
        isCalibrated = false;
        minAngle = null;
        maxAngle = null;
        calibrateMaxBtn.disabled = true;
        completeCalibrationBtn.disabled = true;
        minStatus.textContent = '';
        maxStatus.textContent = '';
        minStatus.className = 'calibration-status';
        maxStatus.className = 'calibration-status';
        document.getElementById('step-min').classList.remove('active');
        document.getElementById('step-max').classList.remove('active');

        socket.emit('set_arm_side', { arm_side: selectedArm });

        startProcessing(calibrationVideo, calibrationCanvas);
    }
});

// Processing Functions
// Two loops: the display loop paints the live camera every animation frame,
// while the process loop sends at most one frame per FRAME_INTERVAL_MS and
// waits for the reply before sending the next (no queue build-up on slow links).
// The server answers with three joint positions, which are drawn over the live
// video, so the preview never waits on the network.
const FRAME_INTERVAL_MS = 100;
const SEND_WIDTH = 480;
let isProcessing = false;
let animationFrameId = null;
let displayFrameId = null;
let armPoints = null; // [[x, y] x3] normalised, shoulder/elbow/wrist, from the server
const sendCanvas = document.createElement('canvas');

function drawArm(ctx, w, h) {
    if (!armPoints) return;
    // The preview is mirrored, the frames sent to the server are not.
    const pts = armPoints.map(([x, y]) => [(1 - x) * w, y * h]);
    ctx.lineWidth = 4;
    ctx.strokeStyle = '#00d4ff';
    ctx.beginPath();
    ctx.moveTo(...pts[0]);
    ctx.lineTo(...pts[1]);
    ctx.lineTo(...pts[2]);
    ctx.stroke();
    ctx.fillStyle = '#ff0080';
    for (const [x, y] of pts) {
        ctx.beginPath();
        ctx.arc(x, y, 8, 0, 2 * Math.PI);
        ctx.fill();
    }
}

function startProcessing(video, canvas) {
    const ctx = canvas.getContext('2d');
    let lastSent = 0;
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    sendCanvas.width = SEND_WIDTH;
    sendCanvas.height = Math.round(SEND_WIDTH * canvas.height / canvas.width);
    const sendCtx = sendCanvas.getContext('2d');

    function displayLoop() {
        if (video.readyState === video.HAVE_ENOUGH_DATA) {
            ctx.save();
            ctx.scale(-1, 1);
            ctx.drawImage(video, -canvas.width, 0, canvas.width, canvas.height);
            ctx.restore();
            drawArm(ctx, canvas.width, canvas.height);
        }
        displayFrameId = requestAnimationFrame(displayLoop);
    }

    function processLoop(now) {
        if (now - lastSent >= FRAME_INTERVAL_MS && !isProcessing &&
            video.readyState === video.HAVE_ENOUGH_DATA) {
            isProcessing = true;
            lastSent = now;
            sendCtx.drawImage(video, 0, 0, sendCanvas.width, sendCanvas.height);
            socket.emit('process_frame', {
                image: sendCanvas.toDataURL('image/jpeg', 0.8),
                calibration_mode: calibrationMode
            });
        }
        animationFrameId = requestAnimationFrame(processLoop);
    }

    displayFrameId = requestAnimationFrame(displayLoop);
    animationFrameId = requestAnimationFrame(processLoop);
}

function stopProcessing() {
    cancelAnimationFrame(animationFrameId);
    cancelAnimationFrame(displayFrameId);
    animationFrameId = null;
    displayFrameId = null;
    isProcessing = false;
    armPoints = null;
}

// Socket Event Handlers
socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
});

socket.on('arm_side_set', (data) => {
    console.log('Arm side set to:', data.arm_side);
});

socket.on('calibration_min_complete', (data) => {
    if (data.min_angle !== undefined) {
        minAngle = data.min_angle;
        minStatus.textContent = `✓ Arm down: ${minAngle}°`;
        minStatus.className = 'calibration-status success';
        console.log('MIN calibration complete:', minAngle);
    }
});

socket.on('calibration_max_complete', (data) => {
    if (data.max_angle !== undefined) {
        maxAngle = data.max_angle;
        maxStatus.textContent = `✓ Curled up: ${maxAngle}°`;
        maxStatus.className = 'calibration-status success';
    }
});

// Sent once both poses are held; the server sorts them, so step order cannot break counting.
socket.on('calibration_done', (data) => {
    isCalibrated = true;
    minAngle = data.low;
    maxAngle = data.high;
    completeCalibrationBtn.disabled = false;
});

socket.on('calibration_error', (data) => {
    isCalibrated = false;
    completeCalibrationBtn.disabled = true;
    const status = data.step === 'min' ? minStatus : maxStatus;
    status.textContent = data.message;
    status.className = 'calibration-status error';
});

socket.on('frame_processed', (data) => {
    isProcessing = false;
    armPoints = data.points;

    const currentScreen = document.querySelector('.screen.active');
    if (data.angle !== null) {
        if (currentScreen === calibrationScreen) {
            currentAngleDisplay.textContent = `${data.angle}°`;
        } else if (currentScreen === trainingScreen) {
            currentAngle.textContent = `${data.angle}°`;
        }
    }

    if (currentScreen === trainingScreen) {
        if (data.count !== undefined && repCount.textContent !== String(data.count)) {
            repCount.textContent = data.count;
            // Restart the pop animation (forcing a reflow between the two assignments).
            repCount.style.animation = 'none';
            void repCount.offsetWidth;
            repCount.style.animation = 'scaleIn 0.3s ease';
        }

        if (data.percentage !== undefined) {
            progressFill.style.width = `${data.percentage}%`;
            progressPercentage.textContent = `${data.percentage}%`;

            // Color based on progress
            if (data.percentage >= 95) {
                progressFill.style.background = 'linear-gradient(135deg, #00ff88 0%, #00cc66 100%)';
            } else if (data.percentage <= 5) {
                progressFill.style.background = 'linear-gradient(135deg, #ff00ff 0%, #ff0080 100%)';
            } else {
                progressFill.style.background = 'linear-gradient(135deg, #00d4ff 0%, #0099ff 100%)';
            }
        }
    }
});

socket.on('counter_reset', (data) => {
    repCount.textContent = data.count;
    progressFill.style.width = '0%';
    progressPercentage.textContent = '0%';
});

socket.on('error', (data) => {
    isProcessing = false; // the frame failed; let the next one go
    console.error('Server error:', data.message);
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    stopProcessing();
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
});

// Prevent screen timeout on mobile
let wakeLock = null;

async function requestWakeLock() {
    try {
        if ('wakeLock' in navigator) {
            wakeLock = await navigator.wakeLock.request('screen');
            console.log('Wake Lock activated');
        }
    } catch (err) {
        console.error('Wake Lock error:', err);
    }
}

// Request wake lock when camera starts
startCameraBtn.addEventListener('click', () => {
    requestWakeLock();
});

// Re-acquire wake lock if page becomes visible again
document.addEventListener('visibilitychange', async () => {
    if (wakeLock !== null && document.visibilityState === 'visible') {
        await requestWakeLock();
    }
});
