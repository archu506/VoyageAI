"""
Pytest configuration and fixtures for the test suite.
Sets up test database, app context, and reusable fixtures.
"""

import os
import pytest
from unittest.mock import patch

from app import create_app, db
from app.models import User, City, Attraction, Review


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Test client for making requests."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """CLI runner for testing CLI commands."""
    return app.test_cli_runner()


@pytest.fixture(autouse=True)
def clear_db(app):
    """Clear database before each test."""
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
        yield
        db.session.remove()


@pytest.fixture
def app_context(app):
    """Application context for tests."""
    with app.app_context():
        yield app


@pytest.fixture
def mock_weather_service():
    """Mock the weather service to avoid external API calls."""
    with patch('app.services.WeatherService.get_weather') as mock:
        mock.return_value = {
            'temperature': 22.5,
            'description': 'Partly Cloudy',
            'humidity': 65,
            'feels_like': 21.0,
            'wind_speed': 3.2
        }
        yield mock


# ==================== User Fixtures ====================

@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(username='testuser', email='test@test.com')
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    
    # Return fresh object in new context
    with app.app_context():
        user = db.session.query(User).filter_by(id=user_id).first()
        db.session.expunge(user)
        return user


@pytest.fixture
def demo_user(app):
    """Create demo user for login testing."""
    with app.app_context():
        user = User(username='demo', email='demo@test.com')
        user.set_password('demo1234')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    
    with app.app_context():
        user = db.session.query(User).filter_by(id=user_id).first()
        db.session.expunge(user)
        return user


@pytest.fixture
def another_user(app):
    """Create another user for authorization tests."""
    with app.app_context():
        user = User(username='otheruser', email='other@test.com')
        user.set_password('otherpass123')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    
    with app.app_context():
        user = db.session.query(User).filter_by(id=user_id).first()
        db.session.expunge(user)
        return user


# ==================== Location Fixtures ====================

@pytest.fixture
def test_city(app):
    """Create a test city."""
    with app.app_context():
        city = City(name='Tokyo', country='Japan', latitude=35.6762, longitude=139.6503)
        db.session.add(city)
        db.session.commit()
        city_id = city.id
    
    with app.app_context():
        city = db.session.query(City).filter_by(id=city_id).first()
        db.session.expunge(city)
        return city


@pytest.fixture
def another_city(app):
    """Create another test city."""
    with app.app_context():
        city = City(name='Paris', country='France', latitude=48.8566, longitude=2.3522)
        db.session.add(city)
        db.session.commit()
        city_id = city.id
    
    with app.app_context():
        city = db.session.query(City).filter_by(id=city_id).first()
        db.session.expunge(city)
        return city


@pytest.fixture
def test_attraction(app, test_city):
    """Create a test attraction."""
    with app.app_context():
        attraction = Attraction(
            name='Senso-ji Temple',
            description='Ancient Buddhist temple',
            category='Temple',
            city_id=test_city.id
        )
        db.session.add(attraction)
        db.session.commit()
        attr_id = attraction.id
    
    with app.app_context():
        attraction = db.session.query(Attraction).filter_by(id=attr_id).first()
        db.session.expunge(attraction)
        return attraction


@pytest.fixture
def another_attraction(app, test_city):
    """Create another test attraction."""
    with app.app_context():
        attraction = Attraction(
            name='Mount Fuji',
            description='Iconic mountain',
            category='Mountain',
            city_id=test_city.id
        )
        db.session.add(attraction)
        db.session.commit()
        attr_id = attraction.id
    
    with app.app_context():
        attraction = db.session.query(Attraction).filter_by(id=attr_id).first()
        db.session.expunge(attraction)
        return attraction


# ==================== Review Fixtures ====================

@pytest.fixture
def test_review(app, test_user, test_attraction):
    """Create a test review."""
    with app.app_context():
        review = Review(
            user_id=test_user.id,
            attraction_id=test_attraction.id,
            rating=4.5,
            title='Amazing place!',
            comment='This is a wonderful attraction with great views.'
        )
        db.session.add(review)
        db.session.commit()
        review_id = review.id
    
    with app.app_context():
        review = db.session.query(Review).filter_by(id=review_id).first()
        db.session.expunge(review)
        return review


@pytest.fixture
def multiple_reviews(app, test_user, test_attraction):
    """Create multiple reviews for pagination testing."""
    review_ids = []
    with app.app_context():
        for i in range(3):
            review = Review(
                user_id=test_user.id,
                attraction_id=test_attraction.id,
                rating=float(i + 3),
                title=f'Review {i+1}',
                comment=f'Comment {i+1}.' * 20
            )
            db.session.add(review)
        db.session.commit()
        review_ids = [r.id for r in db.session.query(Review).all()]
    
    with app.app_context():
        reviews = db.session.query(Review).filter(Review.id.in_(review_ids)).all()
        for r in reviews:
            db.session.expunge(r)
        return reviews


# ==================== Authenticated Client Fixtures ====================

@pytest.fixture
def authenticated_client(client, test_user):
    """Client with authenticated test user."""
    client.post('/auth/login', data={
        'username': test_user.username,
        'password': 'testpass123'
    }, follow_redirects=True)
    return client


@pytest.fixture
def demo_authenticated_client(client, demo_user):
    """Client authenticated as demo user."""
    client.post('/auth/login', data={
        'username': 'demo',
        'password': 'demo1234'
    }, follow_redirects=True)
    return client
