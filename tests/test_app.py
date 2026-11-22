"""End-to-end through the real Socket.IO handlers and the real MediaPipe model.

Fixture frames are two stills from Mixkit clip 21272 (free Mixkit licence):
the person's left elbow measures ~9 deg in arm_down.jpg and ~134 deg in arm_curled.jpg.
"""
import base64
import os
from pathlib import Path

import pytest

os.environ['SOCKETIO_ASYNC_MODE'] = 'threading'  # the test client does not need eventlet
from app import app, socketio  # noqa: E402

FIXTURES = Path(__file__).parent / 'fixtures'


def frame(name):
    data = base64.b64encode((FIXTURES / name).read_bytes()).decode()
    return {'image': f'data:image/jpeg;base64,{data}'}


DOWN, CURLED = frame('arm_down.jpg'), frame('arm_curled.jpg')


@pytest.fixture
def client():
    c = socketio.test_client(app)
    c.emit('set_arm_side', {'arm_side': 'left'})
    c.get_received()
    yield c
    c.disconnect()


def send(client, image, mode=None):
    client.emit('process_frame', {**image, 'calibration_mode': mode})
    replies = [r for r in client.get_received() if r['name'] == 'frame_processed']
    assert len(replies) == 1
    return replies[0]['args'][0]


def events(client):
    return {r['name']: r['args'][0] if r['args'] else None for r in client.get_received()}


def calibrate(client, first_pose, second_pose):
    for step, image in (('min', first_pose), ('max', second_pose)):
        client.emit(f'start_calibration_{step}')
        for _ in range(3):
            send(client, image, step)
        client.emit(f'complete_calibration_{step}')
    return events(client)


def test_frame_returns_arm_points_and_angle(client):
    reply = send(client, CURLED)
    assert len(reply['points']) == 3
    assert all(0 <= v <= 1 for point in reply['points'] for v in point)
    assert 110 <= reply['angle'] <= 160
    assert 'processed_image' not in reply  # joints only, no JPEG round trip


def test_curl_up_first_still_calibrates_and_counts(client):
    # The old UI asked for this order (curl = MIN) and the server then never calibrated.
    got = calibrate(client, CURLED, DOWN)
    assert 'calibration_done' in got, got
    assert got['calibration_done']['low'] < 30 < 110 < got['calibration_done']['high']

    for image in [DOWN, CURLED, DOWN, CURLED, DOWN]:
        reply = send(client, image)
    assert reply['count'] == 2
    assert reply['percentage'] == 0


def test_same_pose_twice_reports_error(client):
    got = calibrate(client, DOWN, DOWN)
    assert 'calibration_done' not in got
    assert 'calibration_error' in got


def test_reset_counter(client):
    calibrate(client, DOWN, CURLED)
    for image in [CURLED, DOWN]:
        send(client, image)
    client.emit('reset_counter')
    assert events(client)['counter_reset'] == {'count': 0}
    assert send(client, DOWN)['count'] == 0


def test_garbage_frame_is_rejected_not_crashing(client):
    client.emit('process_frame', {'image': 'not-a-data-url'})
    assert 'error' in events(client)
    assert send(client, DOWN)['angle'] is not None  # session still works


def test_unknown_arm_side_is_ignored(client):
    client.emit('set_arm_side', {'arm_side': 'tail'})
    assert 'arm_side_set' not in events(client)
