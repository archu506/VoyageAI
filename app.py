import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_login import LoginManager, login_required, current_user, login_user, logout_user

from database import db, cache
from services.logger import logger

# Blueprints
from routes.auth import auth as auth_bp
from routes.itineraries import itineraries_bp
from routes.planner import planner_bp

from flask_wtf.csrf import CSRFProtect

# =========================
# INITIAL SETUP
# =========================
load_dotenv()

app = Flask(__name__)

flask_env = os.getenv("FLASK_ENV", "development").lower()
secret_key = os.getenv("SECRET_KEY")

if flask_env == "production":
    if not secret_key or secret_key in ("voyage-ai-dev-secret-key-2024", "dev-secret-key-change-in-production"):
        raise ValueError("SECRET_KEY environment variable must be explicitly set in production!")
    app.secret_key = secret_key
else:
    app.secret_key = secret_key or "voyage-ai-dev-secret-key-2024"

database_url = os.getenv("TRAVEL_DATABASE_URL")

if database_url:
    database_url = database_url.replace(
        "postgres://",
        "postgresql://",
        1
    )
    if database_url.startswith("sqlite:///instance/"):
        base_dir = os.path.abspath(os.path.dirname(__file__))
        rel_db = database_url[len("sqlite:///instance/"):].lstrip('/\\')
        abs_db = os.path.join(base_dir, 'instance', rel_db).replace('\\', '/')
        database_url = f"sqlite:///{abs_db}"
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Local development fallback
    base_dir = os.path.abspath(os.path.dirname(__file__))
    instance_path = os.path.join(base_dir, 'instance')
    os.makedirs(instance_path, exist_ok=True)

    db_path = os.path.join(instance_path, 'travel.db').replace('\\', '/')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Cache config
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 600

db.init_app(app)
cache.init_app(app)

# CSRF Protection setup
csrf = CSRFProtect()
csrf.init_app(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith(('/api/', '/reviews/api/')) or request.is_json:
        return jsonify({'error': 'Unauthorized'}), 401
    flash("Please log in to access this page.", "info")
    return redirect(url_for('auth.login', next=request.url))

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    try:
        from models.user import User
        return db.session.get(User, int(user_id))
    except Exception as e:
        logger.error(f"Error loading user: {e}")
        return None

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(itineraries_bp)
app.register_blueprint(planner_bp)

# Exempt JSON API routes from CSRF form checks
csrf.exempt(itineraries_bp)

# Database init — import ALL models so SQLAlchemy registers every table
with app.app_context():
    from models.review import Review                      # noqa: F401
    from models.attraction import City, Attraction        # noqa: F401
    from models.trip import SavedTrip                     # noqa: F401
    from models.user import User, PasswordResetToken      # noqa: F401
    db.create_all()

logger.info("Application initialized - VoyageAI Smart Tourism ready")

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
# API AUTH ENDPOINTS
# =========================
@app.route('/api/auth/signup', methods=['POST'])
@csrf.exempt
def api_signup():
    """API endpoint for user signup"""
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({'error': 'Invalid or malformed JSON'}), 400

    username = data.get('full_name', '')
    email = data.get('email', '')
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')

    if not isinstance(username, str): username = ''
    if not isinstance(email, str): email = ''
    if not isinstance(password, str): password = ''
    if not isinstance(confirm_password, str): confirm_password = ''

    username = username.strip()
    email = email.strip()
    password = password.strip()
    confirm_password = confirm_password.strip()

    if not all([username, email, password, confirm_password]):
        return jsonify({'error': 'All fields are required'}), 400

    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    try:
        from models.user import User
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
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/api/auth/login', methods=['POST'])
@csrf.exempt
def api_login():
    """API endpoint for user login"""
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({'error': 'Invalid or malformed JSON'}), 400

    username_or_email = data.get('email', '')
    password = data.get('password', '')

    if not isinstance(username_or_email, str): username_or_email = ''
    if not isinstance(password, str): password = ''

    username_or_email = username_or_email.strip()
    password = password.strip()

    if not username_or_email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    try:
        from models.user import User
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
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/api/auth/logout', methods=['POST'])
@csrf.exempt
@login_required
def api_logout():
    """API endpoint for user logout"""
    try:
        username = current_user.username
        logout_user()
        logger.info(f"User logged out: {username}")
        return jsonify({'success': True, 'message': 'Logged out successfully!'}), 200
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/api/auth/current-user', methods=['GET'])
def api_current_user():
    """Get current logged-in user"""
    if current_user.is_authenticated:
        return jsonify({'username': current_user.username, 'email': current_user.email}), 200
    return jsonify({'user': None}), 200

# =========================
# API ERROR HANDLERS
# =========================
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
    if hasattr(error, 'get_response'):
        return error.get_response()
    return 'Not Found', 404

@app.errorhandler(405)
def method_not_allowed(error):
    if request.path.startswith(('/api/', '/reviews/api/')):
        return jsonify({'error': 'Method Not Allowed'}), 405
    if hasattr(error, 'get_response'):
        return error.get_response()
    return 'Method Not Allowed', 405

@app.errorhandler(500)
def server_error(error):
    try:
        db.session.rollback()
    except Exception:
        pass
    if request.path.startswith(('/api/', '/reviews/api/')):
        return jsonify({'error': 'Internal Server Error'}), 500
    if hasattr(error, 'get_response'):
        return error.get_response()
    return 'Internal Server Error', 500

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    app.run(debug=True)