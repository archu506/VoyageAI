"""
Application entry point.
Run this script to start the development server.
"""

import os
from dotenv import load_dotenv
from app import create_app, db
from app.models import User, City, Place, Review

# Load environment variables from .env file
load_dotenv()

# Create application
app = create_app(os.getenv('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    """Register models for Flask shell."""
    return {
        'db': db,
        'User': User,
        'City': City,
        'Place': Place,
        'Review': Review
    }


if __name__ == '__main__':
    # Create instance folder if it doesn't exist
    os.makedirs(os.path.join(os.path.dirname(__file__), 'instance'), exist_ok=True)
    
    # Run the application
    app.run(debug=True)
