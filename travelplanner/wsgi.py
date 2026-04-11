"""
WSGI entry point for production deployment.
Used by Gunicorn and other WSGI servers.
"""

import os
from app import create_app, db
from app.models import User, City, Attraction, Review


# Create application
app = create_app(os.getenv('FLASK_ENV', 'production'))


@app.shell_context_processor
def make_shell_context():
    """Register models for flask shell commands."""
    return {
        'db': db,
        'User': User,
        'City': City,
        'Attraction': Attraction,
        'Review': Review
    }


if __name__ == '__main__':
    app.run()
