"""
Tests for service layer.
Tests business logic and external service integrations.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services import (
    WeatherService, ReviewService, CityService, AttractionService
)
from app.models import Review


class TestWeatherService:
    """Test Weather API service."""
    
    def test_get_weather_success(self, mock_weather_service):
        """Test successful weather retrieval."""
        weather = WeatherService.get_weather('Tokyo')
        
        assert weather is not None
        assert weather['temperature'] == 22.5
        assert weather['description'] == 'Partly Cloudy'
        assert weather['humidity'] == 65
    
    def test_weather_data_structure(self, mock_weather_service):
        """Test weather response structure."""
        weather = WeatherService.get_weather('Paris')
        
        required_fields = ['temperature', 'description', 'humidity', 'feels_like', 'wind_speed']
        for field in required_fields:
            assert field in weather
    
    @patch('app.services.requests.get')
    def test_weather_api_timeout(self, mock_get, app_context):
        """Test handling of API timeout."""
        mock_get.side_effect = Exception('Connection timeout')
        
        result = WeatherService.get_weather('Tokyo')
        assert result is None
    
    @patch('app.services.requests.get')
    def test_weather_missing_api_key(self, mock_get, app_context):
        """Test handling when API key is missing."""
        result = WeatherService.get_weather('Tokyo')
        # When API key is None, should return None
        assert result is None


class TestReviewService:
    """Test Review service."""
    
    def test_create_review_success(self, app_context, test_user, test_attraction):
        """Test successful review creation."""
        review, error = ReviewService.create_review(
            user_id=test_user.id,
            attraction_id=test_attraction.id,
            rating=4.5,
            title='Excellent experience!',
            comment='This was an amazing place to visit.' * 5
        )
        
        assert error is None
        assert review is not None
        assert review.rating == 4.5
        assert review.title == 'Excellent experience!'
    
    def test_create_duplicate_review(self, app_context, test_review):
        """Test that duplicate reviews are prevented."""
        review, error = ReviewService.create_review(
            user_id=test_review.user_id,
            attraction_id=test_review.attraction_id,
            rating=3.0,
            title='Another review',
            comment='This is another review.' * 5
        )
        
        assert error is not None
        assert 'already reviewed' in error
        assert review is None
    
    def test_create_review_invalid_attraction(self, app_context, test_user):
        """Test creating review for non-existent attraction."""
        review, error = ReviewService.create_review(
            user_id=test_user.id,
            attraction_id=99999,  # Non-existent ID
            rating=4.0,
            title='Test',
            comment='Test comment' * 10
        )
        
        assert error is not None
        assert 'not found' in error
        assert review is None
    
    def test_create_review_invalid_rating(self, app_context, test_user, test_attraction):
        """Test review with invalid rating."""
        review, error = ReviewService.create_review(
            user_id=test_user.id,
            attraction_id=test_attraction.id,
            rating=6.0,  # Invalid, max is 5.0
            title='Test',
            comment='Test comment' * 10
        )
        
        assert error is not None
        assert review is None
    
    def test_update_review_success(self, app_context, test_review, test_user):
        """Test successful review update."""
        review, error = ReviewService.update_review(
            review_id=test_review.id,
            user_id=test_user.id,
            rating=5.0,
            title='Updated!',
            comment='This is an updated review.' * 5
        )
        
        assert error is None
        assert review is not None
        assert review.rating == 5.0
        assert review.title == 'Updated!'
    
    def test_update_review_unauthorized(self, app_context, test_review, another_user):
        """Test updating review by unauthorized user."""
        review, error = ReviewService.update_review(
            review_id=test_review.id,
            user_id=another_user.id,  # Different user
            rating=2.0,
            title='Hacked',
            comment='This should fail' * 10
        )
        
        assert error is not None
        assert 'Not authorized' in error
        assert review is None
    
    def test_delete_review_success(self, app_context, test_review, test_user):
        """Test successful review deletion."""
        success, error = ReviewService.delete_review(
            review_id=test_review.id,
            user_id=test_user.id
        )
        
        assert error is None
        assert success is True
        
        # Verify review is deleted
        deleted = Review.query.get(test_review.id)
        assert deleted is None
    
    def test_delete_review_unauthorized(self, app_context, test_review, another_user):
        """Test deleting review by unauthorized user."""
        success, error = ReviewService.delete_review(
            review_id=test_review.id,
            user_id=another_user.id  # Different user
        )
        
        assert success is False
        assert error is not None
    
    def test_get_reviews_by_attraction(self, app_context, test_attraction, multiple_reviews):
        """Test getting paginated reviews for attraction."""
        pagination = ReviewService.get_reviews_by_attraction(
            attraction_id=test_attraction.id,
            page=1,
            per_page=5
        )
        
        assert pagination is not None
        assert pagination.page == 1
        assert len(pagination.items) > 0
    
    def test_get_reviews_sorted_by_rating(self, app_context, test_attraction, multiple_reviews):
        """Test getting reviews sorted by rating."""
        pagination = ReviewService.get_reviews_by_attraction(
            attraction_id=test_attraction.id,
            sort_by='highest'
        )
        
        assert pagination is not None
        reviews = list(pagination.items)
        if len(reviews) > 1:
            # Verify sorted descending by rating
            for i in range(len(reviews) - 1):
                assert reviews[i].rating >= reviews[i + 1].rating


class TestCityService:
    """Test City service."""
    
    def test_search_cities(self, app_context, test_city, another_city):
        """Test city search."""
        results = CityService.search_cities('Tokyo')
        
        assert results is not None
        assert results.total >= 1
    
    def test_search_cities_no_results(self, app_context):
        """Test city search with no results."""
        results = CityService.search_cities('NonExistentCity123')
        
        assert results.total == 0
    
    def test_get_cities_with_rating(self, app_context, test_city, another_city, test_attraction, test_review):
        """Test getting cities with ratings."""
        cities = CityService.get_cities_with_rating(limit=10)
        
        assert cities is not None
        assert len(cities) > 0
        
        # Check structure
        for city in cities:
            assert 'id' in city
            assert 'name' in city
            assert 'average_rating' in city
    
    def test_get_cities_sorted_by_name(self, app_context, test_city, another_city):
        """Test getting cities sorted by name."""
        cities = CityService.get_cities_with_rating(sort_by='name')
        
        assert len(cities) >= 2
        names = [c['name'] for c in cities]
        assert names == sorted(names)
    
    def test_get_cities_sorted_by_rating(self, app_context, test_city, another_city, test_attraction, test_review):
        """Test getting cities sorted by rating."""
        cities = CityService.get_cities_with_rating(sort_by='rating')
        
        assert len(cities) >= 1
        ratings = [c['average_rating'] for c in cities]
        assert ratings == sorted(ratings, reverse=True)


class TestAttractionService:
    """Test Attraction service."""
    
    def test_get_attractions_by_city(self, app_context, test_city, test_attraction, another_attraction):
        """Test getting attractions for a city."""
        attractions = AttractionService.get_attractions_by_city(test_city.id)
        
        assert attractions is not None
        assert len(attractions) > 0
    
    def test_get_attractions_by_city_filtered(self, app_context, test_city, test_attraction, another_attraction):
        """Test filtering attractions by category."""
        attractions = AttractionService.get_attractions_by_city(
            city_id=test_city.id,
            category='cultural'
        )
        
        assert attractions is not None
        for attraction in attractions:
            assert attraction['category'] == 'cultural'
    
    def test_get_attractions_by_rating_filter(self, app_context, test_city, test_attraction, test_user, another_user):
        """Test filtering attractions by minimum rating."""
        # Create reviews with different ratings
        review1 = Review(
            user_id=test_user.id,
            attraction_id=test_attraction.id,
            rating=2.0,
            title='Okay',
            comment='It was okay.' * 10
        )
        from app.extensions import db
        db.session.add(review1)
        db.session.commit()
        
        # Get attractions with min rating 2.5 (should exclude this one)
        attractions = AttractionService.get_attractions_by_city(
            city_id=test_city.id,
            min_rating=2.5
        )
        
        # test_attraction should not be in results due to low rating
        attraction_ids = [a['id'] for a in attractions]
        assert test_attraction.id not in attraction_ids
    
    def test_get_attractions_empty_city(self, app_context, another_city):
        """Test getting attractions for city with none."""
        attractions = AttractionService.get_attractions_by_city(another_city.id)
        
        assert attractions == []
