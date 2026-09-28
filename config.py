"""
Configuration module for Smart Tourism application.
Supports environment-based configuration (development, testing, production).
"""

import os
from datetime import timedelta

# Ensure instance directory exists
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
os.makedirs(INSTANCE_DIR, exist_ok=True)

def _get_database_uri():
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        db_path = os.path.join(INSTANCE_DIR, 'smart_tourism.db').replace('\\', '/')
        return f"sqlite:///{db_path}"
    
    if db_url.startswith('sqlite:///'):
        rel_path = db_url[len('sqlite:///'):]
        if rel_path.startswith('instance/'):
            filename = rel_path[len('instance/'):]
            db_path = os.path.join(INSTANCE_DIR, filename).replace('\\', '/')
            return f"sqlite:///{db_path}"
        elif not os.path.isabs(rel_path):
            db_path = os.path.join(INSTANCE_DIR, rel_path).replace('\\', '/')
            return f"sqlite:///{db_path}"
            
    return db_url

class Config:
    """Base configuration with shared settings."""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = _get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Pagination
    REVIEWS_PER_PAGE = 5
    SEARCH_RESULTS_PER_PAGE = 10
    
    # Weather API
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')
    WEATHER_API_TIMEOUT = 10
    
    # File upload limits
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Form settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    
    # Ensure critical env vars are set in production
    @staticmethod
    def init_app(app):
        """Initialize production-specific settings."""
        if not os.getenv('SECRET_KEY'):
            raise ValueError('SECRET_KEY environment variable not set in production!')
        if not os.getenv('WEATHER_API_KEY'):
            raise ValueError('WEATHER_API_KEY environment variable not set!')


# Configuration dictionary for easy switching
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
