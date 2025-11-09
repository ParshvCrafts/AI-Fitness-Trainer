import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Flask-SocketIO settings
    SOCKETIO_CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
    SOCKETIO_ASYNC_MODE = 'threading'

    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # MediaPipe settings
    DETECTION_CONFIDENCE = float(os.environ.get('DETECTION_CONFIDENCE', 0.5))
    TRACKING_CONFIDENCE = float(os.environ.get('TRACKING_CONFIDENCE', 0.5))

    # Video processing settings
    FRAME_PROCESSING_INTERVAL = int(os.environ.get('FRAME_INTERVAL', 100))  # milliseconds
    CALIBRATION_DURATION = int(os.environ.get('CALIBRATION_DURATION', 7))  # seconds

    # Image quality
    JPEG_QUALITY = int(os.environ.get('JPEG_QUALITY', 80))

    # Default angle ranges
    DEFAULT_MIN_ANGLE = 25
    DEFAULT_MAX_ANGLE = 150

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

    # Override CORS in production
    SOCKETIO_CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ORIGINS', 'https://yourdomain.com')

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
