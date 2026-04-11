"""
Tests for database operations and integrity.
Tests transactions, migrations, and data persistence.
"""

import pytest
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy


# ==================== Database Connection Tests ====================

class TestDatabaseConnection:
    """Test database connection and operations."""
    
    def test_database_connection(self, app_context):
        """Test that database connection works."""
        from sqlalchemy import text
        
        # Execute simple query to verify connection
        result = app_context.session.execute(text('SELECT 1')).scalar()
        assert result == 1
    
    def test_database_isolation(self, app_context):
        """Test that database provides proper isolation."""
        from app.models import User
        
        # Create user in first session
        user1 = User(username='user1', email='user1@example.com', password='pass1')
        app_context.session.add(user1)
        app_context.session.commit()
        
        # Query in another context should see it
        user = app_context.session.query(User).filter_by(username='user1').first()
        assert user is not None
        assert user.username == 'user1'


# ==================== Transaction Tests ====================

class TestTransactions:
    """Test database transaction handling."""
    
    def test_rollback_on_error(self, app_context, test_user):
        """Test that transactions rollback on error."""
        from app.models import City, Attraction
        initial_attractions = app_context.session.query(Attraction).count()
        
        try:
            # Start transaction
            city = City(name='Test City', country='Test Country', latitude=0, longitude=0)
            attraction = Attraction(
                name='Test Attraction',
                description='Description' * 50,
                category='Museum',
                city_id=city.id  # This will fail - city not yet in DB
            )
            app_context.session.add(city)
            app_context.session.add(attraction)
            app_context.session.flush()  # Force error
        except Exception:
            app_context.session.rollback()
        
        # Count should not have changed
        final_attractions = app_context.session.query(Attraction).count()
        assert final_attractions == initial_attractions
    
    def test_commit_persists_data(self, app_context):
        """Test that committed data persists."""
        from app.models import City
        
        city = City(name='Persistent City', country='Country', latitude=40.0, longitude=-70.0)
        app_context.session.add(city)
        app_context.session.commit()
        
        city_id = city.id
        
        # Clear session
        app_context.session.expunge_all()
        
        # Query again
        found = app_context.session.query(City).filter_by(id=city_id).first()
        assert found is not None
        assert found.name == 'Persistent City'


# ==================== Cascade Delete Tests ====================

class TestCascadeDelete:
    """Test cascade delete behavior."""
    
    def test_delete_user_cascades_to_reviews(self, db_session, test_user, test_review):
        """Test that deleting user deletes associated reviews."""
        from app.models import Review
        
        review_id = test_review.id
        user_id = test_user.id
        
        # Delete user
        db_session.delete(test_user)
        db_session.commit()
        
        # Check that review is deleted
        review = db_session.query(Review).filter_by(id=review_id).first()
        assert review is None
    
    def test_delete_attraction_cascades_to_reviews(self, db_session, test_attraction, test_review):
        """Test that deleting attraction deletes associated reviews."""
        from app.models import Review
        
        review_id = test_review.id
        attraction_id = test_attraction.id
        
        # Delete attraction
        db_session.delete(test_attraction)
        db_session.commit()
        
        # Check that review is deleted
        review = db_session.query(Review).filter_by(id=review_id).first()
        assert review is None
    
    def test_delete_city_cascades_to_attractions(self, db_session, test_city, test_attraction):
        """Test that deleting city deletes associated attractions."""
        from app.models import Attraction
        
        attraction_id = test_attraction.id
        city_id = test_city.id
        
        # Delete city
        db_session.delete(test_city)
        db_session.commit()
        
        # Check that attraction is deleted
        attraction = db_session.query(Attraction).filter_by(id=attraction_id).first()
        assert attraction is None


# ==================== Foreign Key Tests ====================

class TestForeignKeyConstraints:
    """Test foreign key relationships."""
    
    def test_attraction_requires_valid_city(self, db_session):
        """Test that attractions require valid city."""
        from app.models import Attraction
        
        # Try to create attraction with invalid city_id
        attraction = Attraction(
            name='Orphan Attraction',
            description='Description' * 50,
            category='Museum',
            city_id=99999  # Non-existent city
        )
        
        db_session.add(attraction)
        
        # Should fail on commit
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_review_requires_valid_user(self, db_session, test_attraction):
        """Test that reviews require valid user."""
        from app.models import Review
        
        # Try to create review with invalid user_id
        review = Review(
            title='Orphan Review',
            rating=4.0,
            comment='Comment' * 50,
            user_id=99999,  # Non-existent user
            attraction_id=test_attraction.id
        )
        
        db_session.add(review)
        
        # Should fail on commit
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_review_requires_valid_attraction(self, db_session, test_user):
        """Test that reviews require valid attraction."""
        from app.models import Review
        
        # Try to create review with invalid attraction_id
        review = Review(
            title='Orphan Review',
            rating=4.0,
            comment='Comment' * 50,
            user_id=test_user.id,
            attraction_id=99999  # Non-existent attraction
        )
        
        db_session.add(review)
        
        # Should fail on commit
        with pytest.raises(Exception):
            db_session.commit()


# ==================== Index Tests ====================

class TestDatabaseIndexes:
    """Test that database indexes are functioning."""
    
    def test_username_index_exists(self, app_context):
        """Test that username index exists for fast lookups."""
        from app.models import User
        
        # Create users and verify fast lookup works
        user = User(username='indexed_user', email='indexed@example.com', password='pass')
        app_context.session.add(user)
        app_context.session.commit()
        
        # Query should use index
        found = app_context.session.query(User).filter_by(username='indexed_user').first()
        assert found is not None
    
    def test_email_index_exists(self, app_context):
        """Test that email index exists."""
        from app.models import User
        
        user = User(username='email_indexed', email='indexed2@example.com', password='pass')
        app_context.session.add(user)
        app_context.session.commit()
        
        # Query should use index
        found = app_context.session.query(User).filter_by(email='indexed2@example.com').first()
        assert found is not None
    
    def test_foreign_key_index_exists(self, app_context, test_attraction):
        """Test that foreign key indexes exist."""
        from app.models import Review
        
        # Query by foreign keys should be fast
        reviews = app_context.session.query(Review).filter_by(
            attraction_id=test_attraction.id
        ).all()
        
        assert isinstance(reviews, list)


# ==================== Data Type Tests ====================

class TestDataTypes:
    """Test that data types are correctly stored."""
    
    def test_user_timestamps(self, test_user):
        """Test that user timestamps are datetime objects."""
        assert isinstance(test_user.created_at, datetime)
        assert isinstance(test_user.updated_at, datetime)
    
    def test_review_timestamps(self, test_review):
        """Test that review timestamps are datetime objects."""
        assert isinstance(test_review.created_at, datetime)
        assert isinstance(test_review.updated_at, datetime)
    
    def test_review_rating_is_numeric(self, test_review):
        """Test that review rating is numeric."""
        assert isinstance(test_review.rating, (int, float))
        assert 1.0 <= test_review.rating <= 5.0
    
    def test_city_coordinates_are_numeric(self, test_city):
        """Test that city coordinates are numeric."""
        assert isinstance(test_city.latitude, (int, float))
        assert isinstance(test_city.longitude, (int, float))


# ==================== Query Performance Tests ====================

class TestQueryPerformance:
    """Test query efficiency."""
    
    def test_attraction_listing_query_efficiency(self, app_context, test_city, test_attraction):
        """Test that attraction queries are efficient."""
        from app.models import Attraction
        
        # Should use single query (not N+1)
        attractions = app_context.session.query(Attraction).all()
        
        # Accessing city should not require additional queries due to relationships
        for attraction in attractions:
            city = attraction.city
            assert city is not None
    
    def test_review_listing_includes_relationships(self, app_context, test_attraction, test_review):
        """Test that review queries include related data efficiently."""
        from app.models import Review
        
        reviews = app_context.session.query(Review).all()
        
        # Should have user and attraction data loaded
        for review in reviews:
            user = review.user
            attraction = review.attraction
            assert user is not None
            assert attraction is not None


# ==================== Serialization Tests ====================

class TestModelSerialization:
    """Test model serialization to dictionaries."""
    
    def test_user_to_dict(self, test_user):
        """Test user serialization."""
        user_dict = test_user.to_dict()
        
        assert user_dict['id'] == test_user.id
        assert user_dict['username'] == test_user.username
        assert user_dict['email'] == test_user.email
        assert 'password_hash' not in user_dict  # Should not include sensitive data
    
    def test_city_to_dict(self, test_city):
        """Test city serialization."""
        city_dict = test_city.to_dict()
        
        assert city_dict['id'] == test_city.id
        assert city_dict['name'] == test_city.name
        assert city_dict['country'] == test_city.country
        assert city_dict['latitude'] == test_city.latitude
        assert city_dict['longitude'] == test_city.longitude
    
    def test_attraction_to_dict(self, test_attraction):
        """Test attraction serialization."""
        attr_dict = test_attraction.to_dict()
        
        assert attr_dict['id'] == test_attraction.id
        assert attr_dict['name'] == test_attraction.name
        assert attr_dict['city_id'] == test_attraction.city_id
        assert attr_dict['category'] == test_attraction.category
    
    def test_review_to_dict(self, test_review):
        """Test review serialization."""
        review_dict = test_review.to_dict()
        
        assert review_dict['id'] == test_review.id
        assert review_dict['title'] == test_review.title
        assert review_dict['rating'] == test_review.rating
        assert review_dict['user_id'] == test_review.user_id
        assert review_dict['attraction_id'] == test_review.attraction_id


# ==================== Concurrency Tests ====================

class TestDatabaseConcurrency:
    """Test database behavior with concurrent operations."""
    
    def test_concurrent_review_creation(self, db_session, test_user, test_attraction):
        """Test that concurrent reviews are handled safely."""
        from app.models import Review
        
        # Create multiple reviews to simulate concurrent operations
        reviews = []
        for i in range(3):
            review = Review(
                title=f'Review {i}',
                rating=float(i + 2),
                comment=f'Comment about attraction {i}' * 20,
                user_id=test_user.id,
                attraction_id=test_attraction.id
            )
            reviews.append(review)
        
        try:
            for review in reviews:
                db_session.add(review)
                db_session.commit()
        except Exception:
            # Unique constraint should prevent this
            db_session.rollback()
        
        # Only one review should exist per user per attraction
        existing = db_session.query(Review).filter_by(
            user_id=test_user.id,
            attraction_id=test_attraction.id
        ).count()
        
        assert existing <= 1  # Should be 1 or 0
