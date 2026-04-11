"""
Flask application factory.
Initializes the application with configurations, extensions, and blueprints.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_cors import CORS
from config import Config  # Import from root config.py
from app.extensions import db, migrate, login_manager, csrf, init_logging


def create_app(config_name: str = None) -> Flask:
    """
    Create and configure Flask application.
    
    Args:
        config_name: Configuration to use ('development', 'testing', 'production')
                    If None, reads from FLASK_ENV or defaults to 'development'
    
    Returns:
        Configured Flask app instance
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    config = Config.from_env(config_name)
    app.config.from_object(config)
    
    # Initialize logging
    init_logging(app)
    logger = logging.getLogger(__name__)
    logger.info(f'Creating Flask app with {config_name} configuration')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    CORS(app)
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register CLI commands
    register_cli_commands(app)
    
    # Register blueprints
    register_blueprints(app)
    
    logger.info('Flask app initialized successfully')
    
    return app


def register_error_handlers(app: Flask) -> None:
    """Register error handlers for common HTTP errors."""
    logger = logging.getLogger(__name__)
    
    @app.errorhandler(400)
    def bad_request(error):
        logger.warning(f'Bad request: {error}')
        return {'error': 'Bad request', 'status': 400}, 400
    
    @app.errorhandler(404)
    def not_found(error):
        logger.warning(f'Resource not found: {error}')
        return {'error': 'Resource not found', 'status': 404}, 404
    
    @app.errorhandler(403)
    def forbidden(error):
        logger.warning(f'Access forbidden: {error}')
        return {'error': 'Access forbidden', 'status': 403}, 403
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        logger.error(f'Internal server error: {error}', exc_info=True)
        return {'error': 'Internal server error', 'status': 500}, 500


def register_blueprints(app: Flask) -> None:
    """Register Flask blueprints with the app."""
    logger = logging.getLogger(__name__)
    
    # Import blueprints here to avoid circular imports
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.attractions import attractions_bp
    from app.routes.reviews import reviews_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(attractions_bp, url_prefix='/attractions')
    app.register_blueprint(reviews_bp, url_prefix='/reviews')
    
    logger.info('All blueprints registered')


def register_cli_commands(app: Flask) -> None:
    """Register Flask CLI commands for database operations."""
    import click
    from app.models import db as models_db, User, City, Attraction, Review
    
    @app.cli.command()
    def init_db():
        """Initialize database schema."""
        db.create_all()
        click.echo('Database initialized')
    
    @app.cli.command()
    def seed_db():
        """Populate database with sample data."""
        try:
            # Check if data already exists
            if User.query.first():
                click.echo('Database already contains data')
                return
            
            # Create sample cities
            cities = [
                City(
                    name='New York',
                    country='USA',
                    description='The city that never sleeps',
                    latitude=40.7128,
                    longitude=-74.0060,
                    image_url='https://via.placeholder.com/400x300?text=New+York'
                ),
                City(
                    name='Paris',
                    country='France',
                    description='City of light and romance',
                    latitude=48.8566,
                    longitude=2.3522,
                    image_url='https://via.placeholder.com/400x300?text=Paris'
                ),
                City(
                    name='Tokyo',
                    country='Japan',
                    description='Modern metropolis with ancient temples',
                    latitude=35.6762,
                    longitude=139.6503,
                    image_url='https://via.placeholder.com/400x300?text=Tokyo'
                ),
            ]
            db.session.add_all(cities)
            db.session.flush()  # Get IDs without committing
            
            # Create sample attractions
            attractions = [
                Attraction(
                    city_id=cities[0].id,
                    name='Statue of Liberty',
                    description='Iconic monument representing freedom',
                    category='heritage',
                    image_url='https://via.placeholder.com/400x300?text=Statue+of+Liberty'
                ),
                Attraction(
                    city_id=cities[0].id,
                    name='Central Park',
                    description='Large urban park with nature and activities',
                    category='adventure',
                    image_url='https://via.placeholder.com/400x300?text=Central+Park'
                ),
                Attraction(
                    city_id=cities[1].id,
                    name='Eiffel Tower',
                    description='Iconic iron lattice tower',
                    category='heritage',
                    image_url='https://via.placeholder.com/400x300?text=Eiffel+Tower'
                ),
                Attraction(
                    city_id=cities[2].id,
                    name='Senso-ji Temple',
                    description='Ancient Buddhist temple with cultural significance',
                    category='cultural',
                    image_url='https://via.placeholder.com/400x300?text=Senso-ji+Temple'
                ),
            ]
            db.session.add_all(attractions)
            
            # Create sample user
            user = User(username='demo', email='demo@example.com')
            user.set_password('demo1234')
            db.session.add(user)
            db.session.flush()
            
            # Create sample reviews
            reviews = [
                Review(
                    user_id=user.id,
                    attraction_id=attractions[0].id,
                    rating=4.5,
                    title='Amazing view',
                    comment='Great experience visiting this iconic monument'
                ),
                Review(
                    user_id=user.id,
                    attraction_id=attractions[1].id,
                    rating=5.0,
                    title='Perfect for relaxation',
                    comment='Beautiful park, perfect for walks and outdoor activities'
                ),
            ]
            db.session.add_all(reviews)
            
            db.session.commit()
            click.echo('Database seeded with sample data')
        
        except Exception as e:
            db.session.rollback()
            click.echo(f'Error seeding database: {str(e)}', err=True)
    
    @app.cli.command()
    def drop_db():
        """Drop all database tables."""
        if click.confirm('Are you sure you want to drop all tables?'):
            db.drop_all()
            click.echo('All tables dropped')
        else:
            click.echo('Cancelled')
