"""
Development server runner.
Use this script to run the Flask development server locally.
"""

import os
from app import create_app, db
from app.models import User, City, Attraction, Review


def main():
    """Create and run the development server."""
    # Set development environment
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_APP', 'wsgi.py')
    
    # Create app
    app = create_app('development')
    
    # Register shell context
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'User': User,
            'City': City,
            'Attraction': Attraction,
            'Review': Review
        }
    
    # Run development server
    print('Starting development server...')
    print('Access the application at: http://localhost:5000')
    print('Press Ctrl+C to stop the server')
    
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=True
    )


if __name__ == '__main__':
    main()
