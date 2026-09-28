"""
Database models for Smart Tourism application.
Uses SQLAlchemy ORM for type-safe queries and relationships.
"""

import patch_sqlalchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model with authentication support."""
    
    __tablename__ = 'users'
    __table_args__ = (
        db.Index('idx_username', 'username'),
        db.Index('idx_email', 'email'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    reviews = db.relationship(
        'Review',
        backref=db.backref('author', lazy='joined'),
        cascade='all, delete-orphan',
        lazy=True
    )
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Verify that the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
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
    country = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    places = db.relationship(
        'Place',
        backref=db.backref('city', lazy='joined'),
        cascade='all, delete-orphan',
        lazy=True
    )
    
    def __repr__(self):
        return f'<City {self.name}>'


class Place(db.Model):
    """Place/Attraction model representing tourist attractions."""
    
    __tablename__ = 'places'
    __table_args__ = (
        db.Index('idx_place_name', 'name'),
        db.Index('idx_place_type', 'place_type'),
        db.Index('idx_city_id', 'city_id'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id', ondelete='CASCADE'), nullable=False)
    place_type = db.Column(db.String(50))  # heritage, adventure, cultural, etc.
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    reviews = db.relationship(
        'Review',
        backref=db.backref('place', lazy='joined'),
        cascade='all, delete-orphan',
        lazy=True
    )
    
    def get_average_rating(self):
        """Calculate average rating for this place."""
        if not self.reviews:
            return 0
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 1)
    
    def get_review_count(self):
        """Get the total number of reviews."""
        return len(self.reviews)
    
    def __repr__(self):
        return f'<Place {self.name}>'


class Review(db.Model):
    """Review model for user feedback on attractions."""
    
    __tablename__ = 'reviews'
    __table_args__ = (
        db.Index('idx_user_id', 'user_id'),
        db.Index('idx_place_id', 'place_id'),
        db.Index('idx_created_at', 'created_at'),
        db.UniqueConstraint('user_id', 'place_id', name='uq_user_place_review'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('places.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Float, nullable=False)  # 1.0 to 5.0
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    def __repr__(self):
        return f'<Review user={self.user_id} place={self.place_id} rating={self.rating}>'
