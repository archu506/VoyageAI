"""
Flask application factory.
Initializes and configures the Flask application.
"""

import patch_sqlalchemy
import os
import logging
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
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
    
    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path.startswith(('/api/', '/reviews/api/')) or request.is_json:
            return jsonify({'error': 'Unauthorized'}), 401
        flash(login_manager.login_message, login_manager.login_message_category)
        return redirect(url_for(login_manager.login_view, next=request.url))

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
        
        for city_name, city_info in attractions_data.items():
            # Create city
            city = City(name=city_name, country='India')  # Adjust as needed
            db.session.add(city)
            db.session.flush()  # Flush to get the city ID
            
            # Create places
            places_data = city_info.get("attractions", [])
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
    """Setup logging level for production/non-debug mode."""
    app.logger.setLevel(logging.INFO)
    app.logger.info("Smart Tourism startup")


def _register_error_handlers(app):
    """Register error handlers."""
    
    @app.errorhandler(400)
    def bad_request(error):
        if request.path.startswith(('/api/', '/reviews/api/')):
            return jsonify({'error': 'Bad Request'}), 400
        if hasattr(error, 'get_response'):
            return error.get_response()
        return 'Bad Request', 400

    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith(('/api/', '/reviews/api/')):
            return jsonify({'error': 'Not Found'}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        if request.path.startswith(('/api/', '/reviews/api/')):
            return jsonify({'error': 'Method Not Allowed'}), 405
        if hasattr(error, 'get_response'):
            return error.get_response()
        return 'Method Not Allowed', 405

    @app.errorhandler(500)
    def server_error(error):
        from app.models import db
        db.session.rollback()
        if request.path.startswith(('/api/', '/reviews/api/')):
            return jsonify({'error': 'Internal Server Error'}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        if request.path.startswith(('/api/', '/reviews/api/')):
            return jsonify({'error': 'Forbidden'}), 403
        return render_template('errors/403.html'), 403
