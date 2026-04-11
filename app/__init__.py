"""
Flask application factory.
Initializes and configures the Flask application.
"""

import os
import logging
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from config import config, Config
from app.models import db, User
from app.routes import main_bp
from app.routes.auth import auth_bp
from app.routes.itinerary import itinerary_bp
from app.routes.reviews import reviews_bp


def create_app(config_name=None):
    """
    Application factory function.
    
    Args:
        config_name (str): Configuration name ('development', 'testing', 'production')
                          Defaults to environment variable or 'development'
    
    Returns:
        Flask: Configured Flask application instance
    """
    # Use environment variable or default to development
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    app.config.from_object(config.get(config_name, Config))
    
    # Create instance folder if needed
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login."""
        return User.query.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(itinerary_bp)
    app.register_blueprint(reviews_bp)
    
    # Setup database
    with app.app_context():
        db.create_all()
        # Load initial data if needed
        _load_initial_data()
    
    # Setup logging
    if not app.debug:
        _setup_logging(app)
    
    # Register error handlers
    _register_error_handlers(app)
    
    return app


def _load_initial_data():
    """Load initial attractions data from JSON file."""
    import json
    from app.models import City, Place
    
    # Check if data already loaded
    if City.query.first():
        return
    
    attractions_file = os.path.join(
        os.path.dirname(__file__),
        '..',
        'data',
        'attractions.json'
    )
    
    # Try old location for backwards compatibility
    if not os.path.exists(attractions_file):
        attractions_file = os.path.join(
            os.path.dirname(__file__),
            '..',
            'attractions.json'
        )
    
    if not os.path.exists(attractions_file):
        return
    
    try:
        with open(attractions_file, 'r') as f:
            attractions_data = json.load(f)
        
        for city_name, places_data in attractions_data.items():
            # Create city
            city = City(name=city_name, country='India')  # Adjust as needed
            db.session.add(city)
            db.session.flush()  # Flush to get the city ID
            
            # Create places
            for place_data in places_data:
                place = Place(
                    name=place_data['name'],
                    city_id=city.id,
                    place_type=place_data.get('type', 'general')
                )
                db.session.add(place)
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f'Error loading initial data: {str(e)}')


def _setup_logging(app):
    """Setup application logging."""
    if not app.debug and not app.testing:
        # Setup file logging
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = logging.FileHandler('logs/smart_tourism.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Smart Tourism startup')


def _register_error_handlers(app):
    """Register error handlers."""
    
    @app.errorhandler(404)
    def not_found(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(error):
        from flask import render_template
        from app.models import db
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        from flask import render_template
        return render_template('errors/403.html'), 403
