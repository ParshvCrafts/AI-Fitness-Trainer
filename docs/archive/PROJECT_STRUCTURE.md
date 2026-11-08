# AI Fitness Trainer - Project Structure

Complete overview of the web application architecture and files.

## Directory Structure

```
web_app/
│
├── app.py                      # Main Flask application & backend logic
├── config.py                   # Configuration settings for different environments
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker container configuration
├── docker-compose.yml          # Docker Compose orchestration
├── .dockerignore              # Files to exclude from Docker build
├── .gitignore                 # Files to exclude from Git
├── .env.example               # Environment variables template
│
├── run.sh                     # Linux/Mac startup script
├── run.bat                    # Windows startup script
│
├── README.md                  # Main documentation
├── DEPLOYMENT_GUIDE.md        # Comprehensive deployment instructions
├── QUICK_START.md             # Quick start guide for users
├── PROJECT_STRUCTURE.md       # This file
│
├── templates/                 # HTML templates
│   └── index.html             # Main application interface
│
├── static/                    # Static files (CSS, JS, images)
│   ├── style.css              # Application styles & animations
│   └── script.js              # Frontend logic & WebSocket client
│
└── logs/                      # Application logs (created at runtime)
```

---

## Core Files Explained

### Backend

#### [app.py](app.py)
**Purpose**: Main Flask application with WebSocket support

**Key Components**:
- `PoseDetector` class: Handles MediaPipe pose detection
- Flask routes: Serves web interface
- SocketIO handlers: Real-time communication
- Session management: Tracks user state per connection

**Main Functions**:
```python
handle_connect()           # Client connects
handle_disconnect()        # Client disconnects
handle_set_arm_side()     # User selects arm
handle_start_calibration_min()  # Start MIN calibration
handle_start_calibration_max()  # Start MAX calibration
handle_frame()            # Process video frame
handle_reset()            # Reset rep counter
```

**Data Flow**:
1. Client sends video frame (base64)
2. Server decodes and processes with MediaPipe
3. Calculates angles and counts reps
4. Returns processed frame + stats

#### [config.py](config.py)
**Purpose**: Centralized configuration management

**Environments**:
- Development: Debug mode, relaxed CORS
- Production: Secure settings, strict CORS
- Testing: Test-specific settings

**Key Settings**:
- MediaPipe confidence thresholds
- Frame processing intervals
- Calibration durations
- Security keys

---

### Frontend

#### [templates/index.html](templates/index.html)
**Purpose**: Main user interface structure

**Screens**:
1. **Setup Screen**: Arm selection + camera access
2. **Calibration Screen**: MIN/MAX angle calibration
3. **Training Screen**: Live rep counting

**Key Features**:
- Responsive grid layouts
- SVG icons for visual appeal
- Semantic HTML5 structure
- Accessibility considerations

#### [static/style.css](static/style.css)
**Purpose**: Complete styling and animations

**Highlights**:
- CSS Variables for theming
- Gradient backgrounds
- Smooth animations
- Mobile-responsive design
- Modern glassmorphism effects

**Animations**:
- Fade in/out transitions
- Scale effects on updates
- Pulse animations
- Shimmer effects on progress bar

**Responsive Breakpoints**:
- Desktop: > 1200px
- Tablet: 768px - 1200px
- Mobile: < 768px
- Small mobile: < 480px

#### [static/script.js](static/script.js)
**Purpose**: Client-side logic and WebSocket communication

**Key Features**:
- Camera access via WebRTC
- Frame capture and encoding
- Socket.IO real-time updates
- State management
- UI updates

**Main Functions**:
```javascript
startProcessing()         # Begin frame processing
stopProcessing()          # Stop frame processing
handle_frame()            # Send frame to server

// Socket event handlers
socket.on('connect')
socket.on('frame_processed')
socket.on('counter_reset')
```

**Data Flow**:
1. Capture video frame from webcam
2. Convert to base64 image
3. Send via WebSocket
4. Receive processed frame + stats
5. Update UI

---

### Configuration Files

#### [requirements.txt](requirements.txt)
Python package dependencies:
```
Flask==3.0.0              # Web framework
flask-socketio==5.3.5     # WebSocket support
opencv-python==4.8.1.78   # Computer vision
mediapipe==0.10.8         # Pose estimation
numpy==1.24.3             # Numerical operations
```

#### [Dockerfile](Dockerfile)
Container configuration:
- Base: Python 3.10 slim
- System deps: OpenCV requirements
- Python deps: From requirements.txt
- Exposes port 5000
- Health check included

#### [docker-compose.yml](docker-compose.yml)
Service orchestration:
- Single service: ai-trainer
- Port mapping: 5000:5000
- Volume mounting for logs
- Environment variables
- Restart policy

---

## Data Flow Architecture

```
User Browser
    ↓
  Camera
    ↓
  JavaScript (script.js)
    ↓
  Base64 Encode
    ↓
WebSocket (Socket.IO)
    ↓
Flask Server (app.py)
    ↓
Decode Image
    ↓
MediaPipe Processing
    ↓
Angle Calculation
    ↓
Rep Counting Logic
    ↓
Encode Processed Image
    ↓
WebSocket Response
    ↓
JavaScript Updates UI
    ↓
User Sees Results
```

---

## State Management

### Server-Side (Python)
Each user session stores:
```python
{
    'detector': PoseDetector(),      # MediaPipe instance
    'count': 0,                      # Rep counter
    'dir': 0,                        # Direction (up/down)
    'min_angle': None,               # Calibrated min
    'max_angle': None,               # Calibrated max
    'calibrated': False,             # Calibration status
    'arm_side': 'left',              # Selected arm
    'calibration_samples_min': [],   # MIN samples
    'calibration_samples_max': []    # MAX samples
}
```

### Client-Side (JavaScript)
```javascript
{
    selectedArm: 'left',             // User selection
    stream: MediaStream,             // Camera stream
    processingInterval: Number,      // Timer ID
    calibrationMode: String,         // Current mode
    minAngle: Number,                // Calibrated min
    maxAngle: Number,                // Calibrated max
    isCalibrated: Boolean            // Status
}
```

---

## MediaPipe Landmarks

The application uses these body landmarks:

**Left Arm**:
- 11: Left Shoulder
- 13: Left Elbow
- 15: Left Wrist

**Right Arm**:
- 12: Right Shoulder
- 14: Right Elbow
- 16: Right Wrist

**Angle Calculation**:
```python
angle = atan2(y3-y2, x3-x2) - atan2(y2-y1, x2-x1)
```

---

## API Endpoints (WebSocket Events)

### Client → Server

| Event | Payload | Description |
|-------|---------|-------------|
| `connect` | - | Client connection |
| `disconnect` | - | Client disconnection |
| `set_arm_side` | `{arm_side: 'left'/'right'}` | Select arm |
| `start_calibration_min` | - | Begin MIN calibration |
| `start_calibration_max` | - | Begin MAX calibration |
| `process_frame` | `{image: base64, calibration_mode: string}` | Process video frame |
| `reset_counter` | - | Reset rep count |

### Server → Client

| Event | Payload | Description |
|-------|---------|-------------|
| `arm_side_set` | `{arm_side: string}` | Confirm arm selection |
| `calibration_min_started` | - | MIN calibration started |
| `calibration_max_started` | - | MAX calibration started |
| `frame_processed` | `{processed_image, count, percentage, angle, calibrated}` | Processed frame data |
| `counter_reset` | `{count: 0}` | Counter reset confirmed |
| `error` | `{message: string}` | Error occurred |

---

## Performance Considerations

### Frame Processing Rate
- **Default**: 10 FPS (~100ms interval)
- **Trade-off**: Higher FPS = smoother but more CPU
- **Adjustable**: Modify in script.js

### Image Quality
- **Format**: JPEG
- **Quality**: 80% (configurable)
- **Trade-off**: Quality vs bandwidth

### Calibration Duration
- **Default**: 7 seconds
- **Samples**: ~70 angle measurements
- **Purpose**: Average for accuracy

---

## Security Features

### Input Validation
- Base64 image validation
- Session verification
- Arm selection validation

### CORS Protection
- Configurable allowed origins
- Production mode restrictions

### Session Management
- Per-connection isolation
- Automatic cleanup on disconnect

### Environment Variables
- Secret key externalized
- No hardcoded credentials

---

## Extensibility

### Adding New Exercises

1. **Define Landmarks**:
```python
# In app.py
if exercise == 'squat':
    landmarks = (23, 25, 27)  # hip, knee, ankle
```

2. **Add UI Selection**:
```html
<!-- In index.html -->
<button data-exercise="squat">Squats</button>
```

3. **Update Logic**:
```javascript
// In script.js
socket.emit('set_exercise', { exercise: 'squat' });
```

### Adding User Accounts
1. Add database (PostgreSQL/MongoDB)
2. Implement authentication (Flask-Login)
3. Store user sessions and history
4. Add profile pages

### Adding Analytics
1. Track workout sessions
2. Store rep history
3. Calculate statistics
4. Generate progress charts

---

## Testing

### Manual Testing Checklist
- [ ] Camera access on different devices
- [ ] Calibration accuracy
- [ ] Rep counting precision
- [ ] UI responsiveness
- [ ] WebSocket stability
- [ ] Error handling

### Automated Testing (Future)
```python
# Example unit test
def test_angle_calculation():
    detector = PoseDetector()
    angle = detector.findAngle(img, 11, 13, 15)
    assert 0 <= angle <= 360
```

---

## Maintenance

### Regular Tasks
- Update dependencies monthly
- Review logs for errors
- Monitor performance metrics
- Test on new browsers/devices

### Dependency Updates
```bash
pip list --outdated
pip install --upgrade package-name
pip freeze > requirements.txt
```

---

## Resources

### MediaPipe Documentation
- [Pose Estimation Guide](https://google.github.io/mediapipe/solutions/pose)
- [Landmark Index](https://google.github.io/mediapipe/solutions/pose.html#pose-landmark-model)

### Flask-SocketIO
- [Documentation](https://flask-socketio.readthedocs.io/)
- [Examples](https://github.com/miguelgrinberg/Flask-SocketIO)

### Docker
- [Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Compose Documentation](https://docs.docker.com/compose/)

---

## Future Enhancements

### Potential Features
- [ ] Multiple exercise types
- [ ] Workout programs
- [ ] User accounts and profiles
- [ ] Progress tracking
- [ ] Social sharing
- [ ] Voice coaching
- [ ] Form correction feedback
- [ ] Mobile app version
- [ ] Multiplayer challenges
- [ ] AI personal trainer

### Technical Improvements
- [ ] Redis for session storage
- [ ] PostgreSQL for user data
- [ ] Celery for background tasks
- [ ] ML model for form analysis
- [ ] PWA capabilities
- [ ] Offline mode

---

**This document is your complete guide to understanding and extending the AI Fitness Trainer!**
