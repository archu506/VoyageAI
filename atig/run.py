"""
ATIG Main Application Entry Point
"""

import os
import sys
from app import create_app

# Get configuration
config_name = os.getenv('FLASK_ENV', 'development')

# Create Flask app
app = create_app(config_name)

if __name__ == '__main__':
    # Default to development
    debug = config_name != 'production'
    port = int(os.getenv('PORT', 5000))
    
    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║  ATIG - Adaptive Tourism Intelligence Grid (MVP)            ║
    ║  Jaipur Smart Tourism System                                ║
    ║                                                              ║
    ║  🌍 Running on: http://localhost:{port}                     ║
    ║  📊 Dashboard: http://localhost:{port}/dashboard            ║
    ║  📍 API: http://localhost:{port}/api                        ║
    ║                                                              ║
    ║  Features: Crowd Prediction | Route Optimization |         ║
    ║            Sustainability Scoring | Heritage Protection    ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    app.run(debug=debug, host='0.0.0.0', port=port)
