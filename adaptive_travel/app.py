
"""
Real-Time Adaptive Travel Brain
A smart travel planner for Jaipur that adapts itineraries based on:
- Weather conditions
- Crowd levels
- Air Quality Index (AQI)
- User energy levels
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
import sqlite3
import hashlib
import time
from datetime import datetime
from dotenv import load_dotenv
from services.adaptation_engine import AdaptationEngine
from services.weather_service import fetch_weather

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class for Flask-Login
class User:
    def __init__(self, user_id, email, full_name=None):
        self.id = user_id
        self.email = email
        self.full_name = full_name
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

# Initialize database
DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')

def init_db():
    """Initialize the users database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            travel_style TEXT DEFAULT 'moderate',
            save_favorites BOOLEAN DEFAULT 1,
            notifications_enabled BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expiry INTEGER NOT NULL,
            used INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Local file-based itinerary storage (fallback when firebase-admin not available)
ITINERARY_STORAGE_DIR = 'itineraries'

def ensure_storage_dir():
    """Ensure storage directory exists."""
    if not os.path.exists(ITINERARY_STORAGE_DIR):
        os.makedirs(ITINERARY_STORAGE_DIR)

def get_itinerary_filepath(user_id):
    """Get the file path for a user's itinerary."""
    return os.path.join(ITINERARY_STORAGE_DIR, f'{user_id}_itinerary.json')

# Save itinerary to local storage
@app.route('/api/itinerary/save', methods=['POST'])
def save_itinerary():
    data = request.get_json()
    itinerary = data.get('itinerary')
    user_id = data.get('userId', 'guest')  # Default to guest if no user ID
    
    if not itinerary:
        return jsonify({'success': False, 'error': 'Missing itinerary'}), 400
    
    try:
        ensure_storage_dir()
        filepath = get_itinerary_filepath(user_id)
        
        # Save itinerary data
        with open(filepath, 'w') as f:
            json.dump({
                'user_id': user_id,
                'itinerary': itinerary,
                'saved_at': datetime.now().isoformat()
            }, f, indent=2)
        
        return jsonify({'success': True, 'message': 'Itinerary saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Retrieve itinerary from local storage
@app.route('/api/itinerary/get', methods=['GET'])
def get_itinerary():
    user_id = request.args.get('userId', 'guest')  # Default to guest
    
    try:
        ensure_storage_dir()
        filepath = get_itinerary_filepath(user_id)
        
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'No saved itinerary found'}), 404
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        return jsonify({'success': True, 'itinerary': data['itinerary']})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id, email, full_name FROM users WHERE id = ?', (int(user_id),))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(row[0], row[1], row[2])
        return None
    except:
        return None

# Load attractions data
ATTRACTIONS_PATH = os.path.join(os.path.dirname(__file__), 'attractions.json')

def load_attractions():
    """Load attractions from JSON file"""
    with open(ATTRACTIONS_PATH, 'r') as f:
        data = json.load(f)
    return data['attractions']

@app.route('/')
def index():
    """Home page - display attractions selection"""
    attractions = load_attractions()
    return render_template('index.html', attractions=attractions)

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Handle user signup"""
    try:
        data = request.get_json()
        full_name = data.get('full_name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        confirm_password = data.get('confirm_password', '').strip()
        
        # Validation
        if not all([full_name, email, password, confirm_password]):
            return jsonify({'error': 'All fields are required'}), 400
        
        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Check if email already exists
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        password_hash = generate_password_hash(password)
        try:
            cursor.execute('''
                INSERT INTO users (email, full_name, password_hash)
                VALUES (?, ?, ?)
            ''', (email, full_name, password_hash))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            
            # Auto-login the user
            user = User(user_id, email, full_name)
            login_user(user)
            
            return jsonify({
                'success': True,
                'message': 'Account created successfully!',
                'user': {
                    'id': user_id,
                    'email': email,
                    'full_name': full_name
                }
            }), 201
        except Exception as e:
            conn.close()
            return jsonify({'error': f'Error creating account: {str(e)}'}), 500
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Handle user login"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Check user credentials
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id, password_hash, full_name FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        user_id, password_hash, full_name = row
        
        if not check_password_hash(password_hash, password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Login user
        user = User(user_id, email, full_name)
        login_user(user)
        
        return jsonify({
            'success': True,
            'message': 'Logged in successfully!',
            'user': {
                'id': user_id,
                'email': email,
                'full_name': full_name
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    return jsonify({'success': True, 'message': 'Logged out successfully!'}), 200

@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset link"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Find user by email
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id, full_name FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            # Don't reveal if email exists (security best practice)
            return jsonify({
                'success': True,
                'message': 'If this email exists, you will receive a password reset link shortly.'
            }), 200
        
        user_id, full_name = row
        
        # Generate reset token
        import hashlib
        import time
        timestamp = str(int(time.time()))
        message = f"{email}:{timestamp}:reset"
        token = hashlib.sha256(message.encode()).hexdigest()
        
        # Store token in database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        expiry = int(time.time()) + 3600  # 1 hour
        
        cursor.execute("""
            INSERT INTO password_reset_tokens (user_id, token, expiry)
            VALUES (?, ?, ?)
        """, (user_id, token, expiry))
        
        conn.commit()
        conn.close()
        
        # Return reset link
        reset_link = f"http://127.0.0.1:5000/reset-password/{token}"
        
        logger.info(f"Password reset requested for: {email}")
        return jsonify({
            'success': True,
            'message': 'Password reset link sent',
            'reset_link': reset_link  # For demo purposes
        }), 200
        
    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password_api():
    """Reset password using token"""
    try:
        data = request.get_json()
        token = data.get('token', '').strip()
        new_password = data.get('password', '').strip()
        confirm_password = data.get('confirm_password', '').strip()
        
        if not token or not new_password:
            return jsonify({'error': 'Token and password are required'}), 400
        
        if new_password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Verify token
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        current_time = int(time.time())
        
        cursor.execute("""
            SELECT user_id FROM password_reset_tokens 
            WHERE token = ? AND expiry > ? AND used = 0
        """, (token, current_time))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Invalid or expired reset link'}), 401
        
        user_id = row[0]
        password_hash = generate_password_hash(new_password)
        
        # Update password
        cursor.execute("""
            UPDATE users SET password_hash = ? WHERE id = ?
        """, (password_hash, user_id))
        
        # Mark token as used
        cursor.execute("""
            UPDATE password_reset_tokens SET used = 1 WHERE token = ?
        """, (token,))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Password reset successful for user_id: {user_id}")
        return jsonify({
            'success': True,
            'message': 'Password reset successful! Please login with your new password.'
        }), 200
        
    except Exception as e:
        logger.error(f"Reset password error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/auth/current-user', methods=['GET'])
def get_current_user():
    """Get current logged-in user"""
    if current_user.is_authenticated:
        return jsonify({
            'id': current_user.id,
            'email': current_user.email,
            'full_name': current_user.full_name
        }), 200
    return jsonify({'user': None}), 200

@app.route('/api/adapt', methods=['POST'])
def adapt_plan():
    """
    API endpoint to adapt travel plan based on conditions using scoring system.
    
    Accepts JSON with:
    - selected_attractions: list of attraction IDs
    - crowd_level: string (low/medium/high)
    - aqi_level: integer (0-500)
    
    Weather is fetched live from OpenWeatherMap API (or fallback if unavailable).
    
    Returns:
    - original_plan: user's initial selection
    - adapted_plan: reordered by scores
    - removed_attractions: removed due to low energy
    - energy_remaining: user's remaining energy
    - explanations: list of why changes were made
    - scoring_details: detailed breakdown of scores
    - timeline: time-slotted itinerary
    - weather: live weather data {temperature, condition, is_raining, humidity, source}
    """
    try:
        data = request.get_json()
        
        # Get selected attractions
        attractions = load_attractions()
        selected_ids = data.get('selected_attractions', [])
        selected_attractions = [
            attr for attr in attractions 
            if attr['id'] in selected_ids
        ]
        
        if not selected_attractions:
            return jsonify({
                "error": "Please select at least one attraction"
            }), 400
        
        # Get live weather data from API (with fallback)
        weather_data = fetch_weather()
        weather_raining = weather_data['is_raining']
        
        # Get other conditions
        crowd_level = data.get('crowd_level', 'medium')
        aqi_level = data.get('aqi_level', 150)
        
        # Create adaptation engine and generate plan
        engine = AdaptationEngine()
        engine.set_conditions(weather_raining, crowd_level, aqi_level)
        
        # Get adapted plan with scoring details
        result = engine.adapt_itinerary(selected_attractions)
        
        # Add weather data to result
        result['weather'] = weather_data
        
        # Generate timeline for adapted plan
        timeline = engine.generate_timeline(result['adapted_plan'])
        result['timeline'] = timeline
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500

@app.route('/api/attractions')
def get_attractions():
    """API endpoint to get all attractions"""
    attractions = load_attractions()
    return jsonify(attractions)

@app.route('/api/weather')
def get_weather():
    """API endpoint to fetch live weather for Jaipur"""
    try:
        weather_data = fetch_weather()
        return jsonify(weather_data)
    except Exception as e:
        return jsonify({
            "error": f"Failed to fetch weather: {str(e)}"
        }), 500

@app.template_filter('duration_to_time')
def duration_to_time(minutes):
    """Convert minutes to hours:minutes format"""
    hours = minutes // 60
    mins = minutes % 60
    if hours == 0:
        return f"{mins}m"
    elif mins == 0:
        return f"{hours}h"
    else:
        return f"{hours}h {mins}m"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
