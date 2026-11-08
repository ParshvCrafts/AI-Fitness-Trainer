# Quick Start Guide - AI Fitness Trainer

Get your AI Fitness Trainer running in under 5 minutes!

## Option 1: Docker (Easiest - Recommended)

### Prerequisites
- Docker and Docker Compose installed
- Camera/webcam connected

### Steps

1. **Open terminal in the `web_app` folder**

2. **Run one command**:
```bash
docker-compose up
```

3. **Open your browser**:
   - Go to: `http://localhost:5000`

4. **That's it!** Start training!

To stop: Press `Ctrl+C`

---

## Option 2: Python (5 minutes)

### Prerequisites
- Python 3.8+ installed
- Camera/webcam connected

### Windows

1. **Double-click `run.bat`**

   OR open Command Prompt in `web_app` folder and run:
```cmd
run.bat
```

2. **Open browser**: `http://localhost:5000`

### Mac/Linux

1. **Open terminal in `web_app` folder**

2. **Make script executable and run**:
```bash
chmod +x run.sh
./run.sh
```

3. **Open browser**: `http://localhost:5000`

---

## Using the Application

### Step 1: Setup (30 seconds)
1. Choose your arm (Left or Right)
2. Click "Enable Camera"
3. Allow camera access when prompted

### Step 2: Calibration (30 seconds)
1. **MIN Calibration**:
   - Click "Start MIN Calibration"
   - Curl your arm UP (contracted position)
   - Hold steady for 7 seconds

2. **MAX Calibration**:
   - Click "Start MAX Calibration"
   - Extend your arm DOWN fully
   - Hold steady for 7 seconds

3. Click "Start Training"

### Step 3: Train! (∞)
- Perform bicep curls
- Watch your reps count automatically
- See real-time progress
- Get stronger!

---

## Tips for Best Results

### Camera Setup
- Position camera at chest height
- Stand 3-6 feet from camera
- Ensure good lighting
- Keep upper body in frame

### During Exercise
- Keep elbow stable and visible
- Full range of motion
- Controlled movements
- Stay in frame

### Troubleshooting Quick Fixes

#### Camera not working?
- Check browser permissions
- Make sure no other app is using camera
- Try refreshing the page

#### Reps not counting?
- Recalibrate
- Ensure full range of motion
- Stay in frame
- Check lighting

#### Page not loading?
- Check if app is running (`http://localhost:5000`)
- Try different browser
- Clear browser cache

---

## What's Next?

### Training Tips
- Start with 3 sets of 10 reps
- Rest 60 seconds between sets
- Focus on form over speed
- Track your progress

### Customize
- Change calibration duration
- Adjust processing speed
- Modify UI colors
- Add more exercises (see main README)

### Share
- Deploy to the cloud (see DEPLOYMENT_GUIDE.md)
- Share with friends
- Track multiple users

---

## Need Help?

1. Check full README.md
2. See DEPLOYMENT_GUIDE.md for advanced setup
3. Open an issue on GitHub
4. Check browser console for errors

---

## Quick Command Reference

### Start Application
```bash
# Docker
docker-compose up

# Python (Windows)
run.bat

# Python (Mac/Linux)
./run.sh
```

### Stop Application
```bash
# Docker
docker-compose down

# Python
Ctrl+C in terminal
```

### Update Application
```bash
# Pull latest changes
git pull

# Rebuild Docker
docker-compose up --build

# Or reinstall Python packages
pip install -r requirements.txt --upgrade
```

---

**Ready to train? Let's go! 💪**

Open `http://localhost:5000` and start your fitness journey!
