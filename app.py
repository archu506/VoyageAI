import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_login import LoginManager, login_required, current_user, login_user, logout_user

from database import db, cache
from services.logger import logger
from models.user import User

# Blueprints
from routes.auth import auth as auth_bp
from routes.itineraries import itineraries_bp
from routes.planner import planner_bp

# =========================
# INITIAL SETUP
# =========================
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-key-change-in-production")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Cache config
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 600

db.init_app(app)
cache.init_app(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        logger.error(f"Error loading user: {e}")
        return None

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(itineraries_bp)
app.register_blueprint(planner_bp)

# Database init
with app.app_context():
    db.create_all()

logger.info("Application initialized - Adaptive Travel Planner ready")

# =========================
# HOME & STATIC ROUTES
# =========================
@app.route("/")
def home():
    if current_user.is_authenticated:
        logger.info(f"Authenticated user {current_user.username} accessing home")
    return render_template("index.html", current_user=current_user)

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

# =========================
# API ENDPOINTS FOR SIGNUP/LOGIN (JSON)
# =========================
@app.route('/api/auth/signup', methods=['POST'])
def api_signup():
    """API endpoint for user signup"""
    try:
        data = request.get_json()
        username = data.get('full_name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        confirm_password = data.get('confirm_password', '').strip()
        
        if not all([username, email, password, confirm_password]):
            return jsonify({'error': 'All fields are required'}), 400
        
        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        success, msg = User.register_user(username, email, password)
        if success:
            logger.info(f"New user registered: {username}")
            user = User.get_user(username)
            login_user(user)
            return jsonify({
                'success': True,
                'message': 'Account created successfully!',
                'user': {'username': username, 'email': email}
            }), 201
        else:
            return jsonify({'error': msg}), 400
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """API endpoint for user login"""
    try:
        data = request.get_json()
        username_or_email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not username_or_email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = User.get_user(username_or_email) or User.get_user_by_email(username_or_email)
        
        if user and user.check_password(password):
            login_user(user)
            logger.info(f"User logged in: {username_or_email}")
            return jsonify({
                'success': True,
                'message': 'Logged in successfully!',
                'user': {'username': user.username, 'email': user.email}
            }), 200
        else:
            logger.warning(f"Failed login attempt: {username_or_email}")
            return jsonify({'error': 'Invalid email or password'}), 401
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def api_logout():
    """API endpoint for user logout"""
    try:
        username = current_user.username
        logout_user()
        logger.info(f"User logged out: {username}")
        return jsonify({'success': True, 'message': 'Logged out successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/current-user', methods=['GET'])
def api_current_user():
    """Get current logged-in user"""
    if current_user.is_authenticated:
        return jsonify({'username': current_user.username, 'email': current_user.email}), 200
    return jsonify({'user': None}), 200

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    app.run(debug=True)