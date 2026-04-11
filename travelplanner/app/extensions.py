"""
Flask extensions initialization module.
All extensions are created here and initialized with the app in app/__init__.py
This allows for circular import prevention and better organization.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import logging
from logging.handlers import RotatingFileHandler
import os

# Database
db = SQLAlchemy()

# Database migrations
migrate = Migrate()

# Login management
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# CSRF protection
csrf = CSRFProtect()


def init_logging(app):
    """Initialize application logging."""
    if app.debug or app.testing:
        return
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(app.config['LOG_FILE'])
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        app.config['LOG_FILE'],
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    file_handler.setFormatter(formatter)
    
    # Set log level
    log_level = getattr(logging, app.config['LOG_LEVEL'], logging.INFO)
    file_handler.setLevel(log_level)
    app.logger.addHandler(file_handler)
    
    app.logger.setLevel(log_level)
    app.logger.info('Application startup')
