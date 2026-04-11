"""
Configuration module for Travel Planner application.
Supports development, testing, and production environments.
"""

import os
from datetime import timedelta


class BaseConfig:
    """Base configuration with shared settings."""
    
    # Flask core
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Database - use SQLite if DATABASE_URL not set
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///travelplanner.db'  # Default to SQLite for local development
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # Changed to False for local development
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_NAME = 'travelplanner_session'
    
    # WTForms
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    WTF_CSRF_SSL_STRICT = False  # Changed to False for local development
    
    # Pagination
    ITEMS_PER_PAGE = 10
    REVIEWS_PER_PAGE = 5
    
    # File uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Weather API
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')
    WEATHER_API_TIMEOUT = 10
    WEATHER_API_BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/travelplanner.log')
    
    # Security
    BCRYPT_LOG_ROUNDS = 12
    PASSWORD_MIN_LENGTH = 8
    
    # API settings
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False


class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""
    
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_SSL_STRICT = False
    LOG_LEVEL = 'DEBUG'


class TestingConfig(BaseConfig):
    """Testing environment configuration."""
    
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    BCRYPT_LOG_ROUNDS = 4  # Faster for testing


class ProductionConfig(BaseConfig):
    """Production environment configuration."""
    
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    WTF_CSRF_SSL_STRICT = True
    
    @staticmethod
    def init_app(app):
        """Initialize production-specific configuration."""
        # Verify critical environment variables
        required_vars = ['SECRET_KEY', 'DATABASE_URL', 'WEATHER_API_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(
                f'Missing required environment variables: {", ".join(missing_vars)}'
            )


# Configuration factory
class Config:
    """Factory for getting configuration based on environment."""
    
    _configs = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig,
        'default': DevelopmentConfig
    }

    @staticmethod
    def from_env(env=None):
        """
        Get config class based on environment variable.
        
        Args:
            env: Environment name. If None, reads from FLASK_ENV or uses 'development'
        
        Returns:
            Configuration class instance
        """
        if env is None:
            env = os.getenv('FLASK_ENV', 'development')
        config_class = Config._configs.get(env, Config._configs['development'])
        return config_class()
