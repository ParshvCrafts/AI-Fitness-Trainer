import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GLOG_minloglevel'] = '3'

import base64
import logging
import time

import cv2
import mediapipe as mp
import numpy as np
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

from trainer import ARM_LANDMARKS, RepCounter, elbow_flexion

logging.getLogger('absl').setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger('trainer')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production')
socketio = SocketIO(app, cors_allowed_origins='*', async_mode=os.environ.get('SOCKETIO_ASYNC_MODE', 'eventlet'))

# Per-connection state, keyed by Socket.IO session id.
sessions = {}


def new_pose():
    # static_image_mode: every frame is detected from scratch, so frames that
    # arrive out of order or after a gap never confuse a tracker.
    return mp.solutions.pose.Pose(
        static_image_mode=True,
        model_complexity=0,
        smooth_landmarks=False,
        enable_segmentation=False,
        min_detection_confidence=0.5,
    )


def decode_data_url(data_url):
    """'data:image/jpeg;base64,...' -> BGR image, or None if it is not a decodable image."""
    try:
        raw = base64.b64decode(data_url.split(',', 1)[1])
    except (AttributeError, IndexError, ValueError):
        return None
    return cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)


def arm_points(pose, img, arm_side):
    """Normalised (x, y) of shoulder, elbow, wrist for one arm, or None if no person."""
    result = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    if not result.pose_landmarks:
        return None
    lm = result.pose_landmarks.landmark
    h, w = img.shape[:2]
    # Angles use pixel units: normalised x and y have different scales on non-square frames.
    return [(lm[i].x, lm[i].y) for i in ARM_LANDMARKS[arm_side]], (w, h)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return '', 204


@socketio.on('connect')
def handle_connect():
    sessions[request.sid] = {
        'pose': new_pose(),
        'counter': RepCounter(),
        'arm_side': 'left',
        'samples': {'min': [], 'max': []},
        'held': {'min': None, 'max': None},
    }
    log.info('client connected %s', request.sid)


@socketio.on('disconnect')
def handle_disconnect():
    session = sessions.pop(request.sid, None)
    if session:
        session['pose'].close()
    log.info('client disconnected %s', request.sid)


def reset_calibration(session):
    session['counter'] = RepCounter()
    session['samples'] = {'min': [], 'max': []}
    session['held'] = {'min': None, 'max': None}


@socketio.on('set_arm_side')
def handle_set_arm_side(data):
    session = sessions.get(request.sid)
    arm_side = (data or {}).get('arm_side')
    if session is None or arm_side not in ARM_LANDMARKS:
        return
    session['arm_side'] = arm_side
    reset_calibration(session)
    emit('arm_side_set', {'arm_side': arm_side})


def start_step(step):
    session = sessions.get(request.sid)
    if session:
        session['samples'][step] = []
    emit(f'calibration_{step}_started')


def complete_step(step):
    """Average the angles collected while the pose was held; calibrate once both poses exist."""
    session = sessions.get(request.sid)
    if session is None:
        return
    samples = session['samples'][step]
    if not samples:
        emit('calibration_error', {'step': step, 'message': 'No arm detected. Step back so your whole arm is in frame.'})
        return
    held = sum(samples) / len(samples)
    session['held'][step] = held
    emit(f'calibration_{step}_complete', {f'{step}_angle': round(held)})

    if None in session['held'].values():
        return
    try:
        session['counter'].calibrate(session['held']['min'], session['held']['max'])
    except ValueError as exc:
        emit('calibration_error', {'step': step, 'message': str(exc)})
        return
    counter = session['counter']
    log.info('calibrated %s: %.0f-%.0f deg', request.sid, counter.low, counter.high)
    emit('calibration_done', {'low': round(counter.low), 'high': round(counter.high)})


@socketio.on('start_calibration_min')
def handle_start_calibration_min():
    start_step('min')


@socketio.on('start_calibration_max')
def handle_start_calibration_max():
    start_step('max')


@socketio.on('complete_calibration_min')
def handle_complete_calibration_min():
    complete_step('min')


@socketio.on('complete_calibration_max')
def handle_complete_calibration_max():
    complete_step('max')


@socketio.on('process_frame')
def handle_frame(data):
    session = sessions.get(request.sid)
    if session is None:
        return
    started = time.perf_counter()
    img = decode_data_url((data or {}).get('image'))
    if img is None:
        emit('error', {'message': 'Frame was not a decodable image.'})
        return

    counter = session['counter']
    response = {'count': counter.reps, 'percentage': 0, 'calibrated': counter.calibrated,
                'angle': None, 'points': None}

    detected = arm_points(session['pose'], img, session['arm_side'])
    if detected:
        points, (w, h) = detected
        angle = elbow_flexion(*[(x * w, y * h) for x, y in points])
        response['points'] = [[round(x, 4), round(y, 4)] for x, y in points]
        if angle is not None:
            response['angle'] = round(angle)
            step = data.get('calibration_mode')
            if step in ('min', 'max'):
                session['samples'][step].append(angle)
            elif counter.calibrated:
                response['percentage'] = round(counter.update(angle))
                response['count'] = counter.reps

    response['server_ms'] = round((time.perf_counter() - started) * 1000, 1)
    emit('frame_processed', response)


@socketio.on('reset_counter')
def handle_reset():
    session = sessions.get(request.sid)
    if session:
        session['counter'].reset()
    emit('counter_reset', {'count': 0})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
