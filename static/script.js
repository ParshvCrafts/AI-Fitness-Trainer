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
const calibrationProcessed = document.getElementById('calibration-processed');
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
const trainingProcessed = document.getElementById('training-processed');
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
                width: { ideal: 480, max: 640 },
                height: { ideal: 360, max: 480 },
                facingMode: 'user',
                frameRate: { ideal: 30, max: 30 }
            },
            audio: false
        });

        calibrationVideo.srcObject = stream;
        trainingVideo.srcObject = stream;

        showScreen(calibrationScreen);

        startProcessing(calibrationVideo, calibrationCanvas, calibrationProcessed);
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
    calibrationInstruction.textContent = 'CONTRACT YOUR ARM (Bicep Curl Up)';
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
    calibrationInstruction.textContent = 'EXTEND YOUR ARM FULLY (Down Position)';
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

                // Enable complete button
                completeCalibrationBtn.disabled = false;
            }, 100);
        }
    }, 1000);
});

// Complete Calibration
completeCalibrationBtn.addEventListener('click', () => {
    // Check if both angles are set (more reliable than isCalibrated flag)
    if (!minAngle || !maxAngle || minAngle === null || maxAngle === null) {
        alert('Please complete both MIN and MAX calibration first.');
        return;
    }

    stopProcessing();
    showScreen(trainingScreen);

    // Update tracking arm display
    trackingArm.textContent = selectedArm === 'left' ? 'Left Arm' : 'Right Arm';
    angleRange.textContent = `${minAngle}° - ${maxAngle}°`;

    startProcessing(trainingVideo, trainingCanvas, trainingProcessed);
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

        startProcessing(calibrationVideo, calibrationCanvas, calibrationProcessed);
    }
});

// Processing Functions
let isProcessing = false;
let animationFrameId = null;
let displayFrameId = null;

function startProcessing(video, canvas, processedImg) {
    const ctx = canvas.getContext('2d');
    let lastFrameTime = 0;
    const frameInterval = 40; // Process every 40ms (~25 FPS) for optimal balance

    // Separate display loop for smooth 60fps video preview
    function displayLoop() {
        if (video.readyState === video.HAVE_ENOUGH_DATA) {
            // Show raw video feed at 60fps for smoothness
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        }
        displayFrameId = requestAnimationFrame(displayLoop);
    }

    function processFrame(currentTime) {
        if (currentTime - lastFrameTime >= frameInterval) {
            if (video.readyState === video.HAVE_ENOUGH_DATA && !isProcessing) {
                isProcessing = true;
                lastFrameTime = currentTime;

                // Capture frame for processing
                const imageData = canvas.toDataURL('image/jpeg', 0.65);

                socket.emit('process_frame', {
                    image: imageData,
                    calibration_mode: calibrationMode
                });
            }
        }

        animationFrameId = requestAnimationFrame(processFrame);
    }

    displayFrameId = requestAnimationFrame(displayLoop);
    animationFrameId = requestAnimationFrame(processFrame);
}

function stopProcessing() {
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
        animationFrameId = null;
    }
    if (displayFrameId) {
        cancelAnimationFrame(displayFrameId);
        displayFrameId = null;
    }
    isProcessing = false;
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
        minStatus.textContent = `✓ MIN Angle Calibrated: ${minAngle}°`;
        minStatus.className = 'calibration-status success';
        console.log('MIN calibration complete:', minAngle);
    }
});

socket.on('calibration_max_complete', (data) => {
    if (data.max_angle !== undefined) {
        maxAngle = data.max_angle;
        maxStatus.textContent = `✓ MAX Angle Calibrated: ${maxAngle}°`;
        maxStatus.className = 'calibration-status success';
        console.log('MAX calibration complete:', maxAngle);

        if (data.calibrated) {
            isCalibrated = true;
            console.log('Full calibration complete!', minAngle, '-', maxAngle);
        }
    }
});

socket.on('frame_processed', (data) => {
    // Allow next frame to be processed
    isProcessing = false;

    // Update processed image
    const currentScreen = document.querySelector('.screen.active');
    if (currentScreen === calibrationScreen) {
        calibrationProcessed.src = data.processed_image;
    } else if (currentScreen === trainingScreen) {
        trainingProcessed.src = data.processed_image;
    }

    // Update angle display
    if (data.angle) {
        if (currentScreen === calibrationScreen) {
            currentAngleDisplay.textContent = `${data.angle}°`;
        } else if (currentScreen === trainingScreen) {
            currentAngle.textContent = `${data.angle}°`;
        }
    }

    // Update calibration data
    if (data.calibrated !== undefined && data.calibrated) {
        isCalibrated = true;
        if (data.min_angle !== undefined) {
            minAngle = data.min_angle;
        }
        if (data.max_angle !== undefined) {
            maxAngle = data.max_angle;
        }
    }

    // Update training data - ALWAYS update when in training screen
    if (currentScreen === trainingScreen) {
        // Update count and percentage regardless of calibrated flag
        if (data.count !== undefined) {
            repCount.textContent = data.count;
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

        // Animate rep count on change
        if (data.count !== undefined && parseInt(repCount.textContent) !== data.count) {
            repCount.style.animation = 'none';
            setTimeout(() => {
                repCount.style.animation = 'scaleIn 0.3s ease';
            }, 10);
        }
    }
});

socket.on('counter_reset', (data) => {
    repCount.textContent = data.count;
    progressFill.style.width = '0%';
    progressPercentage.textContent = '0%';
});

socket.on('error', (data) => {
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
