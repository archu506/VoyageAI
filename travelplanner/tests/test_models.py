"""
Tests for database models.
Tests model validation, relationships, and serialization.
"""

import pytest
from datetime import datetime
from app.models import User, City, Attraction, Review
from app.extensions import db


class TestUserModel:
    """Test User model."""
    
    def test_create_user(self, app_context):
        """Test creating a user."""
        user = User(
            username='newuser',
            email='new@example.com'
        )
        user.set_password('password123')
        
        assert user.username == 'newuser'
        assert user.email == 'new@example.com'
        assert user.check_password('password123')
    
    def test_password_hashing(self, app_context):
        """Test that passwords are hashed correctly."""
        user = User(username='test', email='test@example.com')
        password = 'testpassword123'
        user.set_password(password)
        
        # Password should not be stored as plain text
        assert user.password_hash != password
        
        # Should verify with correct password
        assert user.check_password(password)
        
        # Should fail with incorrect password
        assert not user.check_password('wrongpassword')
    
    def test_user_to_dict(self, app_context, test_user):
        """Test user serialization."""
        data = test_user.to_dict()
        
        assert data['id'] == test_user.id
        assert data['username'] == test_user.username
        assert data['email'] == test_user.email
        assert 'password_hash' not in data
        assert 'created_at' in data


class TestCityModel:
    """Test City model."""
    
    def test_create_city(self, app_context):
        """Test creating a city."""
        city = City(
            name='Paris',
            country='France',
            description='City of Light',
            latitude=48.8566,
            longitude=2.3522
        )
        
        assert city.name == 'Paris'
        assert city.country == 'France'
        assert city.latitude == 48.8566
    
    def test_city_to_dict(self, app_context, test_city):
        """Test city serialization."""
        data = test_city.to_dict()
        
        assert data['id'] == test_city.id
        assert data['name'] == test_city.name
        assert data['country'] == test_city.country
        assert data['latitude'] == test_city.latitude
        assert data['longitude'] == test_city.longitude
    
    def test_city_attraction_relationship(self, app_context, test_city, test_attraction):
        """Test relationship between cities and attractions."""
        db.session.refresh(test_city)
        
        assert test_attraction in test_city.attractions
        assert test_attraction.city_id == test_city.id


class TestAttractionModel:
    """Test Attraction model."""
    
    def test_create_attraction(self, app_context, test_city):
        """Test creating an attraction."""
        attraction = Attraction(
            city_id=test_city.id,
            name='Eiffel Tower',
            description='Iconic iron tower',
            category='heritage'
        )
        
        assert attraction.name == 'Eiffel Tower'
        assert attraction.category == 'heritage'
        assert attraction.city_id == test_city.id
    
    def test_attraction_to_dict(self, app_context, test_attraction):
        """Test attraction serialization."""
        data = test_attraction.to_dict()
        
        assert data['id'] == test_attraction.id
        assert data['name'] == test_attraction.name
        assert data['category'] == test_attraction.category
        assert 'average_rating' in data
        assert 'review_count' in data
    
    def test_get_average_rating(self, app_context, test_attraction, test_user, another_user):
        """Test calculating average rating."""
        # No reviews
        assert test_attraction.get_average_rating() == 0.0
        
        # Add first review
        review1 = Review(
            user_id=test_user.id,
            attraction_id=test_attraction.id,
            rating=4.0,
            title='Good',
            comment='Nice place'
        )
        db.session.add(review1)
        
        # Add second review
        review2 = Review(
            user_id=another_user.id,
            attraction_id=test_attraction.id,
            rating=5.0,
            title='Excellent',
            comment='Amazing place'
        )
        db.session.add(review2)
        db.session.commit()
        
        # Average should be 4.5
        db.session.refresh(test_attraction)
        assert test_attraction.get_average_rating() == 4.5
    
    def test_get_review_count(self, app_context, test_attraction, test_user, another_user):
        """Test getting review count."""
        assert test_attraction.get_review_count() == 0
        
        review1 = Review(
            user_id=test_user.id,
            attraction_id=test_attraction.id,
            rating=4.0,
            title='Good',
            comment='Nice place'
        )
        db.session.add(review1)
        
        review2 = Review(
            user_id=another_user.id,
            attraction_id=test_attraction.id,
            rating=5.0,
            title='Excellent',
            comment='Amazing place'
        )
        db.session.add(review2)
        db.session.commit()
        
        db.session.refresh(test_attraction)
        assert test_attraction.get_review_count() == 2


class TestReviewModel:
    """Test Review model."""
    
    def test_create_review(self, app_context, test_user, test_attraction):
        """Test creating a review."""
        review = Review(
            user_id=test_user.id,
            attraction_id=test_attraction.id,
            rating=4.5,
            title='Great!',
            comment='This is a wonderful place to visit.'
        )
        
        assert review.rating == 4.5
        assert review.title == 'Great!'
    
    def test_review_to_dict(self, app_context, test_review):
        """Test review serialization."""
        data = test_review.to_dict()
        
        assert data['id'] == test_review.id
        assert data['rating'] == test_review.rating
        assert data['title'] == test_review.title
        assert 'created_at' in data
        assert 'updated_at' in data
    
    def test_validate_rating(self, app_context, test_user, test_attraction):
        """Test rating validation."""
        # Valid rating
        review = Review(
            user_id=test_user.id,
            attraction_id=test_attraction.id,
            rating=3.5,
            title='Test',
            comment='Test comment' * 10
        )
        assert review.validate_rating()
        
        # Invalid rating - too low
        review_low = Review(
            user_id=test_user.id,
            attraction_id=test_attraction.id,
            rating=0.5,
            title='Test',
            comment='Test comment' * 10
        )
        assert not review_low.validate_rating()
        
        # Invalid rating - too high
        review_high = Review(
            user_id=test_user.id,
            attraction_id=test_attraction.id,
            rating=5.5,
            title='Test',
            comment='Test comment' * 10
        )
        assert not review_high.validate_rating()
    
    def test_unique_constraint(self, app_context, test_user, test_attraction):
        """Test that one user cannot review same attraction twice."""
        # First review
        review1 = Review(
            user_id=test_user.id,
            attraction_id=test_attraction.id,
            rating=4.0,
            title='Good',
            comment='Nice place' * 10
        )
        db.session.add(review1)
        db.session.commit()
        
        # Try to create duplicate review
        review2 = Review(
            user_id=test_user.id,
            attraction_id=test_attraction.id,
            rating=5.0,
            title='Excellent',
            comment='Amazing place' * 10
        )
        db.session.add(review2)
        
        # Should raise IntegrityError due to unique constraint
        with pytest.raises(Exception):  # SQLAlchemy raises IntegrityError
            db.session.commit()
    
    def test_review_timestamps(self, app_context, test_review):
        """Test that timestamps are set correctly."""
        assert test_review.created_at is not None
        assert isinstance(test_review.created_at, datetime)
        assert test_review.updated_at is not None
        assert isinstance(test_review.updated_at, datetime)
        
        # created_at and updated_at should be equal initially
        assert test_review.created_at == test_review.updated_at
    
    def test_review_cascade_delete(self, app_context, test_user, test_attraction):
        """Test that deleting an attraction cascades to reviews."""
        review = Review(
            user_id=test_user.id,
            attraction_id=test_attraction.id,
            rating=4.0,
            title='Good',
            comment='Nice place' * 10
        )
        db.session.add(review)
        db.session.commit()
        
        review_id = review.id
        attraction_id = test_attraction.id
        
        # Delete attraction
        db.session.delete(test_attraction)
        db.session.commit()
        
        # Review should also be deleted
        deleted_review = Review.query.get(review_id)
        assert deleted_review is None


class TestModelRelationships:
    """Test model relationships and cascading."""
    
    def test_user_reviews_relationship(self, app_context, test_user, test_review):
        """Test user-reviews relationship."""
        db.session.refresh(test_user)
        
        assert test_review in test_user.reviews
        assert test_review.user_id == test_user.id
    
    def test_attraction_reviews_relationship(self, app_context, test_attraction, test_review):
        """Test attraction-reviews relationship."""
        db.session.refresh(test_attraction)
        
        assert test_review in test_attraction.reviews
        assert test_review.attraction_id == test_attraction.id
