import hashlib
import time
import json
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models.trip import SavedTrip

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    expiry = db.Column(db.Integer, nullable=False)
    used = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(500), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    energy_level = db.Column(db.Integer, default=100)
    crowd_tolerance = db.Column(db.Integer, default=50)
    
    # Engine custom thresholds
    heat_tolerance = db.Column(db.Integer, default=38)
    rain_tolerance = db.Column(db.Float, default=0.6)
    aqi_tolerance = db.Column(db.Integer, default=150)

    # Relationships
    saved_trips = db.relationship('SavedTrip', backref='user', lazy=True, cascade='all, delete-orphan')
    password_reset_tokens = db.relationship('PasswordResetToken', backref='user', lazy=True, cascade='all, delete-orphan')

    def __init__(self, username, email, password=None):
        self.username = username
        self.email = email
        if password:
            self.password_hash = generate_password_hash(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def register_user(username, email, password):
        try:
            if User.query.filter((User.username == username) | (User.email == email)).first():
                return False, "User already exists"

            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            return True, "User registered successfully"
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def get_user(username):
        try:
            return User.query.filter_by(username=username).first()
        except:
            return None

    @staticmethod
    def get_user_by_email(email):
        try:
            return User.query.filter_by(email=email).first()
        except:
            return None

    def generate_reset_token(self):
        try:
            timestamp = str(int(time.time()))
            message = f"{self.email}:{timestamp}:{self.password_hash[:10]}"
            token = hashlib.sha256(message.encode()).hexdigest()
            expiry = int(time.time()) + 3600
            
            reset_token = PasswordResetToken(user_id=self.id, token=token, expiry=expiry)
            db.session.add(reset_token)
            db.session.commit()
            return token
        except Exception as e:
            db.session.rollback()
            print(f"Error generating reset token: {e}")
            return None

    @staticmethod
    def verify_reset_token(token):
        try:
            current_time = int(time.time())
            token_obj = PasswordResetToken.query.filter(
                PasswordResetToken.token == token,
                PasswordResetToken.expiry > current_time,
                PasswordResetToken.used == 0
            ).first()
            if not token_obj:
                return None
            return token_obj.user
        except Exception as e:
            print(f"Error verifying token: {e}")
            return None

    @staticmethod
    def reset_password(token, new_password):
        try:
            current_time = int(time.time())
            token_obj = PasswordResetToken.query.filter(
                PasswordResetToken.token == token,
                PasswordResetToken.expiry > current_time,
                PasswordResetToken.used == 0
            ).first()
            
            if not token_obj:
                return False, "Invalid or expired token"

            user = token_obj.user
            user.set_password(new_password)
            token_obj.used = 1
            
            db.session.commit()
            return True, "Password reset successful"
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    def save_preferences(self):
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error saving preferences: {e}")
            return False

    def save_trip(self, city, attractions, mood):
        try:
            new_trip = SavedTrip(
                user_id=self.id,
                city=city,
                attractions=json.dumps(attractions),
                mood=mood
            )
            db.session.add(new_trip)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error saving trip: {e}")
            return False

    def get_saved_trips(self):
        try:
            # Return ordered by created_at desc
            trips = SavedTrip.query.filter_by(user_id=self.id).order_by(SavedTrip.id.desc()).all()
            result = []
            for t in trips:
                result.append({
                    "id": t.id,
                    "city": t.city,
                    "attractions": json.loads(t.attractions) if t.attractions else [],
                    "mood": t.mood,
                    "created_at": t.created_at
                })
            return result
        except Exception as e:
            print(f"Error fetching trips: {e}")
            return []
