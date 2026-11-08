# Debug Steps - Counter Not Working

## What I Fixed

1. **Frontend JavaScript** - Updated to always show count/percentage when in training screen (removed the `data.calibrated` check)
2. **Backend Python** - Added extensive debug logging to trace the issue

## How to Debug

### Step 1: Restart Server
```bash
python app.py
```

### Step 2: Open Browser
```
http://localhost:5000
```

### Step 3: Follow Calibration Flow

Watch the **terminal output** closely at each step:

#### A. Enable Camera
- Terminal should show: `Client connected: <session_id>`

#### B. Calibrate MIN (Extend Arm - Down Position)
- Hold arm FULLY EXTENDED (straight down)
- Click "Calibrate MIN Angle"
- Hold for 7 seconds
- **Terminal should show:**
  ```
  MIN calibration sample collected: <angle>
  MIN calibration sample collected: <angle>
  ...
  MIN calibration complete: <XX>°
  ```
- **What angle do you see?** (should be something like 30-60°)

#### C. Calibrate MAX (Contract Arm - Bicep Curl Up)
- Hold arm in CONTRACTED position (bicep curled up)
- Click "Calibrate MAX Angle"
- Hold for 7 seconds
- **Terminal should show:**
  ```
  MAX calibration sample collected: <angle>
  MAX calibration sample collected: <angle>
  ...
  MAX angle calculated: <YY>°, MIN angle: <XX>
  ```

**CRITICAL CHECK:** Look at the next line:

**If you see:**
```
✓ MAX calibration complete: <YY>°
✓ Full calibration done: <XX>° - <YY>°
✓ Session calibrated flag set to: True
```
→ **Good! Calibration worked.**

**If you see:**
```
⚠ WARNING: Calibration not complete! max (<YY>) <= min (<XX>)
```
→ **Problem! MAX angle is not greater than MIN angle.**

This means either:
1. You calibrated in wrong order (extended first, contracted second)
2. The angle calculation is inverted
3. You're using the wrong arm

#### D. Start Training
- Click "Start Training"
- **Terminal should show:**
  ```
  Training mode - calibrated=True, min=<XX>, max=<YY>
  ```

#### E. Do a Bicep Curl

As you move your arm, **terminal should show:**

**If working correctly:**
```
TRAINING: angle=165, per=95%, min=45, max=165, count=0, dir=0
TRAINING: angle=160, per=90%, min=45, max=165, count=0, dir=0
...
TRAINING: angle=50, per=8%, min=45, max=165, count=0, dir=0
TRAINING: angle=45, per=3%, min=45, max=165, count=0, dir=0
✓ Rep counting DOWN: 0 -> 0.5 (per=3%)
TRAINING: angle=48, per=5%, min=45, max=165, count=0.5, dir=1
...
TRAINING: angle=162, per=97%, min=45, max=165, count=0.5, dir=1
✓ Rep counting UP: 0.5 -> 1.0 (per=97%)
```

**If NOT working:**
```
NOT TRAINING: calibration_mode=None, calibrated=False, min=45, max=165
```

→ This means the `calibrated` flag is still `False` even though you calibrated!

## Most Likely Issues

### Issue 1: MAX <= MIN
**Symptom:** Terminal shows `⚠ WARNING: Calibration not complete! max (XX) <= min (YY)`

**Cause:** You calibrated backwards - contracted arm first (larger angle), extended arm second (smaller angle)

**Fix:** The UI labels might be confusing. Let me check what angles you're actually getting.

**For bicep curls:**
- Contracted (bicep up) = SMALLER angle (30-60°)
- Extended (arm down) = LARGER angle (160-180°)

So:
- MIN calibration should show ~30-60° (contracted)
- MAX calibration should show ~160-180° (extended)

### Issue 2: Wrong Arm Selected
**Symptom:** No pose detected, or angles look wrong

**Fix:** Make sure you selected the correct arm (left/right) that you're exercising with

### Issue 3: Calibrated Flag Not Set
**Symptom:** Terminal shows `NOT TRAINING: calibration_mode=None, calibrated=False`

**Cause:** The MAX > MIN check failed on line 166 of app.py

**Fix:** See Issue 1

## Tell Me What You See

Run through the steps above and copy-paste the **exact terminal output** here so I can see what's happening!
