import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GLOG_minloglevel'] = '3'

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import cv2
import mediapipe as mp
import numpy as np
import base64
import math
import logging
from threading import Lock

logging.getLogger('absl').setLevel(logging.ERROR)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

class PoseDetector:
    def __init__(self, mode=True, smooth=False, detection_confidence=0.5, track_confidence=0.5):
        self.mode = mode
        self.smooth = smooth
        self.detection_confidence = detection_confidence
        self.track_confidence = track_confidence
        self.id_cx_cy = {}

        self.mpPose = mp.solutions.pose
        # static_image_mode=True processes each frame independently (no timestamp issues)
        self.pose = self.mpPose.Pose(
            static_image_mode=True,   # Treat each frame independently
            model_complexity=0,       # Use LITE model for maximum speed
            smooth_landmarks=False,   # No temporal smoothing
            enable_segmentation=False, # Disable segmentation for speed
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mpDraw = mp.solutions.drawing_utils

    def findPose(self, img, draw=False):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        if draw and self.results.pose_landmarks:
            self.mpDraw.draw_landmarks(img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)
        return img

    def findPosition(self, img, draw=False, landmark_id=None):
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.id_cx_cy[id] = (cx, cy)
                if draw and landmark_id is not None and id == landmark_id:
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
        return self.id_cx_cy

    def findAngle(self, img, p1, p2, p3, draw=True):
        if self.id_cx_cy and p1 in self.id_cx_cy and p2 in self.id_cx_cy and p3 in self.id_cx_cy:
            x1, y1 = self.id_cx_cy[p1]
            x2, y2 = self.id_cx_cy[p2]
            x3, y3 = self.id_cx_cy[p3]

            # Calculate angle using vectors for consistency across left/right arms
            # Vector from elbow to shoulder
            v1 = (x1 - x2, y1 - y2)
            # Vector from elbow to wrist
            v2 = (x3 - x2, y3 - y2)

            # Calculate angle using dot product (always gives interior angle 0-180)
            dot_product = v1[0] * v2[0] + v1[1] * v2[1]
            magnitude_v1 = math.sqrt(v1[0]**2 + v1[1]**2)
            magnitude_v2 = math.sqrt(v2[0]**2 + v2[1]**2)

            if magnitude_v1 == 0 or magnitude_v2 == 0:
                return None

            cos_angle = dot_product / (magnitude_v1 * magnitude_v2)
            # Clamp to avoid math domain errors
            cos_angle = max(-1, min(1, cos_angle))
            angle = math.degrees(math.acos(cos_angle))

            # Invert angle: 180° becomes 0°, 0° becomes 180°
            # This makes flexed arm (small interior angle ~30°) = large value (~150°)
            # and extended arm (large interior angle ~170°) = small value (~10°)
            # This matches the original behavior expected by rep counting logic
            angle = 180 - angle

            if draw:
                # Black lines (like original)
                cv2.line(img, (x1, y1), (x2, y2), (0, 0, 0), 2)
                cv2.line(img, (x2, y2), (x3, y3), (0, 0, 0), 2)
                # Red circles (like original)
                cv2.circle(img, (x1, y1), 8, (0, 0, 255), cv2.FILLED)
                cv2.circle(img, (x1, y1), 12, (0, 0, 255), 2)
                cv2.circle(img, (x2, y2), 8, (0, 0, 255), cv2.FILLED)
                cv2.circle(img, (x2, y2), 12, (0, 0, 255), 2)
                cv2.circle(img, (x3, y3), 8, (0, 0, 255), cv2.FILLED)
                cv2.circle(img, (x3, y3), 12, (0, 0, 255), 2)

            return angle
        return None

# Store session data for each user
user_sessions = {}
session_lock = Lock()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204  # No content response for favicon

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    with session_lock:
        user_sessions[request.sid] = {
            'detector': PoseDetector(),  # Reuse detector with static_image_mode=True
            'count': 0,
            'dir': 0,
            'min_angle': None,
            'max_angle': None,
            'calibrated': False,
            'arm_side': 'left',
            'calibration_samples_min': [],
            'calibration_samples_max': []
        }

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    with session_lock:
        if request.sid in user_sessions:
            del user_sessions[request.sid]

@socketio.on('set_arm_side')
def handle_set_arm_side(data):
    arm_side = data.get('arm_side', 'left')
    with session_lock:
        if request.sid in user_sessions:
            user_sessions[request.sid]['arm_side'] = arm_side
            user_sessions[request.sid]['count'] = 0
            user_sessions[request.sid]['dir'] = 0
            user_sessions[request.sid]['calibrated'] = False
            user_sessions[request.sid]['calibration_samples_min'] = []
            user_sessions[request.sid]['calibration_samples_max'] = []
    emit('arm_side_set', {'arm_side': arm_side})

@socketio.on('start_calibration_min')
def handle_start_calibration_min():
    with session_lock:
        if request.sid in user_sessions:
            user_sessions[request.sid]['calibration_samples_min'] = []
    emit('calibration_min_started')

@socketio.on('start_calibration_max')
def handle_start_calibration_max():
    with session_lock:
        if request.sid in user_sessions:
            user_sessions[request.sid]['calibration_samples_max'] = []
    emit('calibration_max_started')

@socketio.on('complete_calibration_min')
def handle_complete_calibration_min():
    with session_lock:
        if request.sid in user_sessions:
            session = user_sessions[request.sid]
            if len(session['calibration_samples_min']) > 0:
                min_angle = sum(session['calibration_samples_min']) / len(session['calibration_samples_min'])
                session['min_angle'] = min_angle
                emit('calibration_min_complete', {'min_angle': int(min_angle)})
                print(f"MIN calibration complete: {int(min_angle)}°")
            else:
                print("No MIN samples collected")

@socketio.on('complete_calibration_max')
def handle_complete_calibration_max():
    with session_lock:
        if request.sid in user_sessions:
            session = user_sessions[request.sid]
            if len(session['calibration_samples_max']) > 0:
                max_angle = sum(session['calibration_samples_max']) / len(session['calibration_samples_max'])
                session['max_angle'] = max_angle

                print(f"MAX angle calculated: {int(max_angle)}°, MIN angle: {session['min_angle']}")

                # Check if both min and max are set, then mark as calibrated
                if session['min_angle'] is not None and max_angle > session['min_angle']:
                    session['calibrated'] = True
                    emit('calibration_max_complete', {
                        'max_angle': int(max_angle),
                        'calibrated': True
                    })
                    print(f"✓ MAX calibration complete: {int(max_angle)}°")
                    print(f"✓ Full calibration done: {int(session['min_angle'])}° - {int(max_angle)}°")
                    print(f"✓ Session calibrated flag set to: {session['calibrated']}")
                else:
                    print(f"⚠ WARNING: Calibration not complete! max ({int(max_angle)}) <= min ({session['min_angle']})")
                    emit('calibration_max_complete', {'max_angle': int(max_angle)})
            else:
                print("No MAX samples collected")

@socketio.on('process_frame')
def handle_frame(data):
    try:
        # Get session reference
        if request.sid not in user_sessions:
            return

        session = user_sessions[request.sid]

        # Decode the base64 image
        img_data = data['image'].split(',')[1]
        img_bytes = base64.b64decode(img_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return

        # Get detector and session data (no lock needed for reading)
        detector = session['detector']
        arm_side = session['arm_side']
        calibrated = session['calibrated']
        min_angle = session['min_angle']
        max_angle = session['max_angle']

        # Get calibration mode
        calibration_mode = data.get('calibration_mode')

        # Determine landmarks based on arm side
        if arm_side == 'left':
            # Left arm: shoulder(11), elbow(13), wrist(15)
            landmarks = (11, 13, 15)
        else:
            # Right arm: shoulder(12), elbow(14), wrist(16)
            landmarks = (12, 14, 16)

        # Process pose
        img = detector.findPose(img, draw=False)
        id_cx_cy = detector.findPosition(img, draw=False)

        # Initialize response
        response_data = {
            'count': int(session['count']),
            'percentage': 0,
            'calibrated': calibrated,
            'angle': 0
        }

        if id_cx_cy:
            angle = detector.findAngle(img, *landmarks, draw=True)

            if angle is not None:
                response_data['angle'] = int(angle)

                # Handle calibration - collect samples
                # calibration_mode already defined above

                if calibration_mode == 'min':
                    with session_lock:
                        session['calibration_samples_min'].append(angle)

                elif calibration_mode == 'max':
                    with session_lock:
                        session['calibration_samples_max'].append(angle)

                # Count reps if calibrated
                elif calibrated and min_angle is not None and max_angle is not None:
                    per = np.interp(angle, (min_angle, max_angle), (0, 100))
                    per = max(0, min(100, per))  # Clamp between 0-100
                    response_data['percentage'] = int(per)

                    # Count logic - UPDATE SESSION WITH LOCK
                    with session_lock:
                        if per >= 95:
                            if session['dir'] == 0:
                                session['count'] += 0.5
                                session['dir'] = 1
                        elif per <= 5:
                            if session['dir'] == 1:
                                session['count'] += 0.5
                                session['dir'] = 0

                        response_data['count'] = int(session['count'])

        # Encode processed image with aggressive compression for speed
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 65,
                       int(cv2.IMWRITE_JPEG_OPTIMIZE), 1,
                       int(cv2.IMWRITE_JPEG_PROGRESSIVE), 0]
        _, buffer = cv2.imencode('.jpg', img, encode_param)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        response_data['processed_image'] = f"data:image/jpeg;base64,{img_base64}"

        emit('frame_processed', response_data)

    except Exception as e:
        print(f"Error processing frame: {str(e)}")
        import traceback
        traceback.print_exc()
        emit('error', {'message': str(e)})

@socketio.on('reset_counter')
def handle_reset():
    with session_lock:
        if request.sid in user_sessions:
            user_sessions[request.sid]['count'] = 0
            user_sessions[request.sid]['dir'] = 0
    emit('counter_reset', {'count': 0})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
