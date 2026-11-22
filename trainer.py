"""Rep-counting logic, kept free of Flask and MediaPipe so it can be unit-tested.

Angles are elbow *flexion*: 0 deg = arm straight, ~150 deg = fully curled.
"""
import math

# MediaPipe Pose landmark ids (shoulder, elbow, wrist) for the person's own arm.
ARM_LANDMARKS = {
    'left': (11, 13, 15),
    'right': (12, 14, 16),
}

# A calibrated range narrower than this cannot tell "up" from landmark jitter.
MIN_RANGE_DEG = 30

# Hysteresis thresholds on the 0-100 progress scale.
TOP_PCT = 95
BOTTOM_PCT = 5


def elbow_flexion(shoulder, elbow, wrist):
    """Flexion angle in degrees at the elbow, or None if two points coincide.

    Uses the dot product, so the result is the same for left and right arms
    and for a mirrored image (an atan2 version gave different ranges per arm).
    """
    v1 = (shoulder[0] - elbow[0], shoulder[1] - elbow[1])
    v2 = (wrist[0] - elbow[0], wrist[1] - elbow[1])
    m1, m2 = math.hypot(*v1), math.hypot(*v2)
    if m1 == 0 or m2 == 0:
        return None
    cos_a = (v1[0] * v2[0] + v1[1] * v2[1]) / (m1 * m2)
    interior = math.degrees(math.acos(max(-1.0, min(1.0, cos_a))))
    return 180.0 - interior


class RepCounter:
    """Turns a stream of flexion angles into a progress % and a rep count.

    A rep is counted when the arm reaches the top of the calibrated range and
    then returns to the bottom, so half-reps and jitter in the middle do not count.
    """

    def __init__(self):
        self.low = None
        self.high = None
        self.reps = 0
        self._at_top = False

    @property
    def calibrated(self):
        return self.low is not None

    def calibrate(self, angle_a, angle_b):
        """Set the range from two held poses, in either order.

        Raises ValueError when the range is too small to count reliably.
        """
        low, high = sorted((angle_a, angle_b))
        if high - low < MIN_RANGE_DEG:
            raise ValueError(
                f'Range {low:.0f}-{high:.0f} deg is under {MIN_RANGE_DEG} deg: '
                'hold the arm fully straight for one step and fully curled for the other.'
            )
        self.low, self.high = low, high
        self.reset()

    def reset(self):
        self.reps = 0
        self._at_top = False

    def update(self, angle):
        """Feed one angle; returns progress 0-100 (0 = arm down, 100 = curled)."""
        if not self.calibrated:
            raise RuntimeError('calibrate() before update()')
        pct = (angle - self.low) / (self.high - self.low) * 100
        pct = max(0.0, min(100.0, pct))
        if pct >= TOP_PCT:
            self._at_top = True
        elif pct <= BOTTOM_PCT and self._at_top:
            self._at_top = False
            self.reps += 1
        return pct
