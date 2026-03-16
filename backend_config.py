import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload folder for detected images
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Detection settings
    MIN_CONTOUR_AREA = 700
    ASPECT_RATIO_MIN = 0.2
    ASPECT_RATIO_MAX = 8.0
    
    # HSV color range for fluorescent oil detection
    HSV_LOWER = [35, 120, 180]
    HSV_UPPER = [95, 255, 255]
    
    # Camera settings
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480
    FRAME_RATE = 20

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///oil_detection.db'
    )
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True

class ProductionConfig(Config):
    """Production configuration for Render"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///oil_detection.db'  # Use SQLite for free tier
    )
    TESTING = False

class FreeTierConfig(Config):
    """Optimized for Render free tier (512MB RAM limit)"""
    DEBUG = False
    TESTING = False
    
    # Reduce memory usage
    FRAME_WIDTH = 480      # Reduced from 640
    FRAME_HEIGHT = 360     # Reduced from 480
    FRAME_RATE = 10        # Reduced from 20
    
    # Less aggressive detection
    MIN_CONTOUR_AREA = 1000  # Higher threshold = faster processing
    
    # Use SQLite (ephemeral storage is fine)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///oil_detection.db'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'free_tier': FreeTierConfig,
    'default': DevelopmentConfig
}
