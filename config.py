"""
Configuration file for Text Summarization Application
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # API Configuration
    API_HOST = os.environ.get('API_HOST') or '0.0.0.0'
    API_PORT = int(os.environ.get('API_PORT') or 5000)
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS') or '*'
    
    # Summarization Model Configuration
    DEFAULT_MODEL = 'facebook/bart-large-cnn'
    MAX_SUMMARY_LENGTH = 500
    MIN_SUMMARY_LENGTH = 30
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = False
    RATE_LIMIT_REQUESTS = 100  # requests per hour
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = 'app.log'
    
    # Cache Configuration
    CACHE_ENABLED = False
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    RATE_LIMIT_ENABLED = True
    CACHE_ENABLED = True
    
    # Override with environment variables in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in production")


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    RATE_LIMIT_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """Get configuration based on environment"""
    if env is None:
        env = os.environ.get('FLASK_ENV') or 'development'
    return config.get(env, config['default'])