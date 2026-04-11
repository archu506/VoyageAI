"""
ATIG App Factory and Configuration
"""

from flask import Flask
import os
import json

def create_app(config_name="development"):
    """Create and configure Flask app."""
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(__file__), "templates"),
                static_folder=os.path.join(os.path.dirname(__file__), "static"))
    
    # Configuration
    app.config['SECRET_KEY'] = 'atig-hackathon-secret-2024'
    app.config['JSON_SORT_KEYS'] = False
    
    # Get base path
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app.config['DATA_PATH'] = os.path.join(base_path, 'data')
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.api import api_bp
    from app.routes.dashboard import dashboard_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found"}, 404
    
    @app.errorhandler(500)
    def server_error(error):
        return {"error": "Server error"}, 500
    
    return app
