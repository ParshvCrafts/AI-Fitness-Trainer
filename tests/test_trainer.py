import pytest

from trainer import MIN_RANGE_DEG, RepCounter, elbow_flexion

# Left-elbow flexion measured by the app's pose model on Mixkit clip 21272
# (front view, EZ-bar curls), sampled every 5th frame at 29.97 fps.
# Watching the clip: 5 full curls, the last one back down at ~9.3 s.
CLIP_21272_ANGLES = [
    7, 21, 121, 150, 152, 144, 79, 22, 10, 6, 6, 13, 32, 142, 152, 152, 140, 170,
    26, 7, 4, 4, 9, 30, 131, 154, 153, 155, 148, 130, 43, 16, 7, 4, 6, 17, 21, 142,
    154, 152, 151, 148, 133, 53, 23, 9, 2, 3, 9, 4, 126, 147, 149, 146, 143, 130,
    15, 16, 9, 7, 7, 18, 45,
]


def test_straight_arm_is_zero_flexion():
    assert elbow_flexion((0, 0), (0, 10), (0, 20)) == pytest.approx(0)


def test_right_angle_is_ninety():
    assert elbow_flexion((0, 0), (0, 10), (10, 10)) == pytest.approx(90)


def test_same_angle_for_mirrored_arm():
    # Left and right arms (and a mirrored camera) must produce the same number.
    arm = [(3, 1), (5, 9), (12, 4)]
    mirrored = [(-x, y) for x, y in arm]
    assert elbow_flexion(*arm) == pytest.approx(elbow_flexion(*mirrored))


def test_coincident_points_return_none():
    assert elbow_flexion((1, 1), (1, 1), (5, 5)) is None


def test_calibration_is_order_independent():
    # Regression: the UI used to ask for "curl up" as the MIN pose, which gives the
    # larger flexion angle, so the server's max > min check failed and no rep was ever counted.
    curled_first = RepCounter()
    curled_first.calibrate(140, 10)
    down_first = RepCounter()
    down_first.calibrate(10, 140)
    assert (curled_first.low, curled_first.high) == (10, 140) == (down_first.low, down_first.high)


def test_narrow_range_is_rejected():
    with pytest.raises(ValueError):
        RepCounter().calibrate(50, 50 + MIN_RANGE_DEG - 1)


def test_update_before_calibration_fails_loudly():
    with pytest.raises(RuntimeError):
        RepCounter().update(90)


def test_progress_is_clamped():
    c = RepCounter()
    c.calibrate(20, 120)
    assert c.update(0) == 0
    assert c.update(70) == pytest.approx(50)
    assert c.update(170) == 100


def test_rep_needs_top_then_bottom():
    c = RepCounter()
    c.calibrate(10, 140)
    for angle in [10, 80, 140]:
        c.update(angle)
    assert c.reps == 0  # at the top, not yet back down
    c.update(10)
    assert c.reps == 1


def test_partial_reps_and_jitter_do_not_count():
    c = RepCounter()
    c.calibrate(10, 140)
    for angle in [10, 60, 100, 60, 10, 100, 130, 15, 10]:  # never reaches 95%
        c.update(angle)
    assert c.reps == 0


def test_staying_at_top_counts_once():
    c = RepCounter()
    c.calibrate(10, 140)
    for angle in [140, 120, 140, 125, 140, 10, 10]:
        c.update(angle)
    assert c.reps == 1


def test_reset_clears_reps_and_half_rep():
    c = RepCounter()
    c.calibrate(10, 140)
    c.update(140)
    c.reset()
    c.update(10)
    assert c.reps == 0


def test_real_clip_counts_five_curls():
    c = RepCounter()
    # Calibration poses held in the clip: arm down ~6 deg, top of the curl ~152 deg.
    c.calibrate(152, 6)
    for angle in CLIP_21272_ANGLES:
        c.update(angle)
    assert c.reps == 5
