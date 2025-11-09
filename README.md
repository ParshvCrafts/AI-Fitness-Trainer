# AI Fitness Trainer - Bicep Curl Counter

A real-time AI-powered fitness application that uses computer vision to count bicep curls and provide form feedback.

![Python](https://img.shields.io/badge/python-v3.11-blue)
![Flask](https://img.shields.io/badge/flask-v3.0.0-green)
![MediaPipe](https://img.shields.io/badge/mediapipe-v0.10.8-orange)
![License](https://img.shields.io/badge/license-MIT-blue)

## Features

- **Real-time Pose Detection**: Uses MediaPipe for accurate body landmark tracking
- **Automatic Calibration**: Personalized angle calibration for accurate rep counting
- **Left/Right Arm Support**: Track either arm independently
- **Live Progress Visualization**: Real-time progress bar and rep counter
- **Mobile & Desktop Support**: Responsive design works on all devices
- **WebSocket Communication**: Low-latency real-time updates
- **Modern UI**: Sleek, animated interface with live stats

## Tech Stack

- **Backend**: Python, Flask, Flask-SocketIO
- **Computer Vision**: MediaPipe, OpenCV
- **Frontend**: HTML5, CSS3, JavaScript
- **Real-time Communication**: WebSockets (Socket.IO)
- **Deployment**: Render, Railway, or Fly.io

## How It Works

1. **Pose Estimation**: MediaPipe detects body landmarks from webcam feed
2. **Angle Calculation**: Measures elbow angle (shoulder-elbow-wrist)
3. **Calibration**: User sets minimum (contracted) and maximum (extended) positions
4. **Rep Counting**: Tracks movement through full range of motion
5. **Real-time Feedback**: Displays angle, progress, and rep count

## Local Installation

### Prerequisites

- Python 3.11+
- Webcam
- Modern web browser (Chrome, Firefox, Safari)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/ai-fitness-trainer.git
cd ai-fitness-trainer
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open browser and navigate to:
```
http://localhost:5000
```

## Usage Instructions

1. **Get Started**: Click "Get Started" on landing page
2. **Select Arm**: Choose which arm you'll be exercising
3. **Enable Camera**: Grant camera permissions when prompted
4. **Calibrate MIN**: Contract your arm (curl up) and click "Start MIN Calibration"
5. **Calibrate MAX**: Extend your arm (down) and click "Start MAX Calibration"
6. **Start Training**: Begin your workout - reps will be counted automatically!

## Deployment

See [DEPLOYMENT_COMPLETE_GUIDE.md](DEPLOYMENT_COMPLETE_GUIDE.md) for detailed deployment instructions.

### Quick Deploy to Render

1. Push code to GitHub
2. Create account on [Render](https://render.com)
3. Create new Web Service from your GitHub repo
4. Render will auto-detect Python and deploy
5. Your app will be live at `https://your-app-name.onrender.com`

## Project Structure

```
web_app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Procfile              # Deployment configuration
├── runtime.txt           # Python version specification
├── templates/
│   └── index.html        # Frontend HTML
├── static/
│   ├── style.css         # Styling
│   └── script.js         # Frontend JavaScript
└── README.md             # This file
```

## Key Components

### Backend (app.py)

- `PoseDetector` class: Handles MediaPipe pose detection
- `findPose()`: Processes video frames and detects pose landmarks
- `findAngle()`: Calculates joint angles using vector mathematics
- Socket.IO event handlers: Manage real-time communication

### Frontend

- WebSocket connection for real-time frame processing
- HTML5 Canvas for video capture
- Dynamic UI updates based on server responses
- Calibration and training modes

## Performance Optimizations

- Static image mode for frame-independent processing
- JPEG compression for reduced bandwidth
- Eventlet workers for async processing
- Session-based user data management
- Efficient angle calculation using vector dot product


## Browser Compatibility

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support (requires HTTPS for camera)
- Mobile browsers: Limited support (performance dependent)

## Troubleshooting

### Camera Not Working
- Ensure HTTPS connection (required by browsers)
- Check browser camera permissions
- Try different browser

### Slow Performance
- Close other applications
- Reduce browser window size
- Check internet connection (for deployed version)

### Calibration Issues
- Ensure full body is visible in frame
- Stand in good lighting
- Keep arm stable during calibration

## Future Enhancements

- [ ] Add more exercises (squats, pushups, shoulder press)
- [ ] Workout history and progress tracking
- [ ] User authentication
- [ ] Mobile app version
- [ ] Form feedback and corrections
- [ ] Multiple user support
- [ ] Exercise tutorials

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

**Parshv Patel**
- Data Science & Machine Learning Student
- University of California, Berkeley
- [LinkedIn](https://www.linkedin.com/in/parshv-patel-65a90326b/)

## Acknowledgments

- MediaPipe by Google for pose estimation
- Flask and Flask-SocketIO for web framework
- OpenCV for image processing

## Support

If you find this project helpful, please give it a star!

For questions or issues, please open an issue on GitHub.

---

Made with by Parshv Patel
