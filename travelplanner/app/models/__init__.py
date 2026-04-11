"""
Database models for Travel Planner application.
Uses SQLAlchemy ORM with proper relationships and constraints.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db


class User(UserMixin, db.Model):
    """User model for authentication and review tracking."""
    
    __tablename__ = 'users'
    __table_args__ = (
        db.Index('idx_username', 'username'),
        db.Index('idx_email', 'email'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    reviews = db.relationship(
        'Review',
        backref=db.backref('author', lazy='joined'),
        cascade='all, delete-orphan',
        lazy='select'
    )
    
    def set_password(self, password: str) -> None:
        """Hash and set the user password."""
        self.password_hash = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=16
        )
    
    def check_password(self, password: str) -> bool:
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self) -> dict:
        """Convert user to dictionary for JSON responses."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
        }
    
    def __repr__(self) -> str:
        return f'<User {self.username}>'


class City(db.Model):
    """City model representing travel destinations."""
    
    __tablename__ = 'cities'
    __table_args__ = (
        db.Index('idx_city_name', 'name'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    country = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    attractions = db.relationship(
        'Attraction',
        backref=db.backref('city', lazy='joined'),
        cascade='all, delete-orphan',
        lazy='select'
    )
    
    def to_dict(self) -> dict:
        """Convert city to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'country': self.country,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'image_url': self.image_url,
            'attraction_count': len(self.attractions),
        }
    
    def __repr__(self) -> str:
        return f'<City {self.name}>'


class Attraction(db.Model):
    """Attraction model representing tourist attractions and places."""
    
    __tablename__ = 'attractions'
    __table_args__ = (
        db.Index('idx_attraction_city', 'city_id'),
        db.Index('idx_attraction_name', 'name'),
        db.Index('idx_attraction_type', 'category'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(
        db.Integer,
        db.ForeignKey('cities.id', ondelete='CASCADE'),
        nullable=False
    )
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # heritage, adventure, cultural, etc.
    address = db.Column(db.String(500))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    image_url = db.Column(db.String(500))
    website = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    reviews = db.relationship(
        'Review',
        backref=db.backref('attraction', lazy='joined'),
        cascade='all, delete-orphan',
        lazy='select'
    )
    
    def get_average_rating(self) -> float:
        """Calculate average rating from reviews."""
        if not self.reviews:
            return 0.0
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 2)
    
    def get_review_count(self) -> int:
        """Get total number of reviews."""
        return len(self.reviews)
    
    def to_dict(self) -> dict:
        """Convert attraction to dictionary."""
        return {
            'id': self.id,
            'city_id': self.city_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'image_url': self.image_url,
            'website': self.website,
            'average_rating': self.get_average_rating(),
            'review_count': self.get_review_count(),
        }
    
    def __repr__(self) -> str:
        return f'<Attraction {self.name}>'


class Review(db.Model):
    """Review model for user feedback on attractions."""
    
    __tablename__ = 'reviews'
    __table_args__ = (
        db.Index('idx_review_user', 'user_id'),
        db.Index('idx_review_attraction', 'attraction_id'),
        db.Index('idx_review_created', 'created_at'),
        db.UniqueConstraint(
            'user_id',
            'attraction_id',
            name='uq_user_attraction_review'
        ),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    attraction_id = db.Column(
        db.Integer,
        db.ForeignKey('attractions.id', ondelete='CASCADE'),
        nullable=False
    )
    rating = db.Column(db.Float, nullable=False)  # 1.0-5.0
    title = db.Column(db.String(200), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    def validate_rating(self) -> bool:
        """Validate rating is between 1.0 and 5.0."""
        return 1.0 <= self.rating <= 5.0
    
    def to_dict(self) -> dict:
        """Convert review to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.author.username,
            'attraction_id': self.attraction_id,
            'rating': self.rating,
            'title': self.title,
            'comment': self.comment,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
    
    def __repr__(self) -> str:
        return f'<Review user={self.user_id} attraction={self.attraction_id}>'
