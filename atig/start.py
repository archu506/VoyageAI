#!/usr/bin/env python
"""
ATIG Application - Simplified Standalone Launcher
This script starts the ATIG Flask app with minimal dependencies
"""

import os
import sys

# Add the ATIG directory to Python path
atig_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, atig_path)

# Import Flask and app factory
from flask import Flask

try:
    from app import create_app
except ImportError as e:
    print(f"Error importing app: {e}")
    print(f"ATIG Path: {atig_path}")
    print(f"Python Path: {sys.path}")
    sys.exit(1)

def main():
    # Create Flask app
    try:
        app = create_app('development')
    except Exception as e:
        print(f"Error creating app: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Print startup banner
    print("""
╔══════════════════════════════════════════════════════════════╗
║  ATIG - Adaptive Tourism Intelligence Grid (MVP)            ║
║  Jaipur Smart Tourism System                                ║
║                                                              ║
║  🌍 Open: http://localhost:5000                             ║
║  📊 Dashboard: http://localhost:5000/dashboard              ║
║  📍 Planner: http://localhost:5000/plan                     ║
║  📡 API: http://localhost:5000/api                          ║
║                                                              ║
║  Features: Crowd Prediction | Route Optimization |          ║
║            Sustainability Scoring | Heritage Protection    ║
║                                                              ║
║  Press Ctrl+C to stop                                       ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Run Flask dev server
    try:
        app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
    except Exception as e:
        print(f"Error running app: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
