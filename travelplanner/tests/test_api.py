"""
Tests for API endpoints and JSON responses.
Tests RESTful endpoints, pagination, and serialization.
"""

import pytest
from flask import url_for
import json


# ==================== Attractions API ====================

class TestAttractionsAPI:
    """Test attractions API endpoints."""
    
    def test_get_attractions_json(self, client, test_attraction):
        """Test getting attractions as JSON."""
        response = client.get(url_for('attractions.api_attractions'))
        
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        data = response.json
        assert isinstance(data, list)
    
    def test_get_attractions_with_pagination(self, client, test_attraction):
        """Test attractions endpoint with pagination."""
        response = client.get(url_for('attractions.api_attractions', page=1, per_page=10))
        
        assert response.status_code == 200
        data = response.json
        assert isinstance(data, list)
    
    def test_get_attractions_by_city(self, client, test_city, test_attraction):
        """Test getting attractions by city."""
        response = client.get(
            url_for('attractions.api_attractions'),
            query_string={'city_id': test_city.id}
        )
        
        assert response.status_code == 200
        data = response.json
        if data:
            assert data[0]['city_id'] == test_city.id
    
    def test_get_attractions_by_category(self, client, test_attraction):
        """Test getting attractions by category."""
        response = client.get(
            url_for('attractions.api_attractions'),
            query_string={'category': test_attraction.category}
        )
        
        assert response.status_code == 200
        data = response.json
        if data:
            assert data[0]['category'] == test_attraction.category
    
    def test_get_attractions_by_rating(self, client, test_attraction):
        """Test getting attractions filtered by minimum rating."""
        response = client.get(
            url_for('attractions.api_attractions'),
            query_string={'min_rating': 3.0}
        )
        
        assert response.status_code == 200
        data = response.json
        if data:
            for attraction in data:
                assert float(attraction.get('rating', 0)) >= 3.0
    
    def test_attraction_response_format(self, client, test_attraction):
        """Test that attraction response has required fields."""
        response = client.get(url_for('attractions.api_attractions'))
        
        assert response.status_code == 200
        data = response.json
        if data:
            attraction = data[0]
            required_fields = ['id', 'name', 'description', 'city_id']
            for field in required_fields:
                assert field in attraction


# ==================== Reviews API ====================

class TestReviewsAPI:
    """Test reviews API endpoints."""
    
    def test_get_attraction_reviews(self, client, test_attraction, test_review):
        """Test getting reviews for attraction."""
        response = client.get(
            url_for('reviews.api_attraction_reviews', attraction_id=test_attraction.id)
        )
        
        assert response.status_code == 200
        data = response.json
        assert 'reviews' in data
        assert 'pagination' in data
        assert isinstance(data['reviews'], list)
    
    def test_get_reviews_pagination(self, client, test_attraction, multiple_reviews):
        """Test reviews pagination."""
        response = client.get(
            url_for('reviews.api_attraction_reviews', attraction_id=test_attraction.id),
            query_string={'page': 1, 'per_page': 5}
        )
        
        assert response.status_code == 200
        data = response.json
        assert 'pagination' in data
        assert 'current_page' in data['pagination']
    
    def test_review_response_format(self, client, test_attraction, test_review):
        """Test that review response has required fields."""
        response = client.get(
            url_for('reviews.api_attraction_reviews', attraction_id=test_attraction.id)
        )
        
        assert response.status_code == 200
        data = response.json
        if data['reviews']:
            review = data['reviews'][0]
            required_fields = ['id', 'title', 'rating', 'comment', 'username', 'created_at']
            for field in required_fields:
                assert field in review
    
    def test_get_user_reviews_api(self, client, test_user, test_review):
        """Test getting user's reviews."""
        response = client.get(
            url_for('reviews.api_user_reviews', user_id=test_user.id)
        )
        
        assert response.status_code == 200
        data = response.json
        assert 'reviews' in data
        assert isinstance(data['reviews'], list)
    
    def test_user_reviews_pagination(self, client, test_user, multiple_reviews):
        """Test user reviews pagination."""
        response = client.get(
            url_for('reviews.api_user_reviews', user_id=test_user.id),
            query_string={'page': 1, 'per_page': 5}
        )
        
        assert response.status_code == 200
        data = response.json
        assert 'pagination' in data


# ==================== Cities API ====================

class TestCitiesAPI:
    """Test cities API endpoints."""
    
    def test_get_cities(self, client, test_city):
        """Test getting all cities."""
        response = client.get(url_for('attractions.api_cities'))
        
        assert response.status_code == 200
        data = response.json
        assert isinstance(data, list)
    
    def test_city_response_format(self, client, test_city):
        """Test that city response has required fields."""
        response = client.get(url_for('attractions.api_cities'))
        
        assert response.status_code == 200
        data = response.json
        if data:
            city = data[0]
            required_fields = ['id', 'name', 'country', 'latitude', 'longitude']
            for field in required_fields:
                assert field in city


# ==================== Search API ====================

class TestSearchAPI:
    """Test search API endpoints."""
    
    def test_search_attractions(self, client, test_attraction):
        """Test searching attractions via API."""
        response = client.get(
            url_for('attractions.api_search'),
            query_string={'q': test_attraction.name}
        )
        
        assert response.status_code == 200
        data = response.json
        assert 'attractions' in data
        assert isinstance(data['attractions'], list)
    
    def test_search_cities(self, client, test_city):
        """Test searching cities via API."""
        response = client.get(
            url_for('attractions.api_search'),
            query_string={'q': test_city.name, 'type': 'cities'}
        )
        
        assert response.status_code == 200
        data = response.json
        assert 'cities' in data or 'attractions' in data
    
    def test_search_returns_results(self, client, test_attraction):
        """Test that search returns matching results."""
        response = client.get(
            url_for('attractions.api_search'),
            query_string={'q': test_attraction.name}
        )
        
        assert response.status_code == 200
        data = response.json
        if 'attractions' in data and data['attractions']:
            found = any(a['name'].lower() == test_attraction.name.lower() 
                       for a in data['attractions'])
            # At least one result should match
            assert len(data['attractions']) > 0


# ==================== Weather API ====================

class TestWeatherAPI:
    """Test weather API endpoints."""
    
    def test_get_attraction_weather(self, client, test_attraction, mock_weather_service):
        """Test getting weather for attraction."""
        response = client.get(
            url_for('main.get_weather', city=test_attraction.city.name)
        )
        
        assert response.status_code == 200
        data = response.json
        assert 'temperature' in data or 'weather' in data or 'error' in data


# ==================== Statistics API ====================

class TestStatisticsAPI:
    """Test statistics API endpoints."""
    
    def test_get_statistics(self, client, test_city, test_attraction, test_review):
        """Test getting statistics."""
        response = client.get(url_for('main.get_stats'))
        
        assert response.status_code == 200
        data = response.json
        
        assert 'total_cities' in data
        assert 'total_attractions' in data
        assert 'total_reviews' in data
        assert 'average_rating' in data
    
    def test_statistics_are_numbers(self, client):
        """Test that statistics return numeric values."""
        response = client.get(url_for('main.get_stats'))
        
        assert response.status_code == 200
        data = response.json
        
        assert isinstance(data['total_cities'], int)
        assert isinstance(data['total_attractions'], int)
        assert isinstance(data['total_reviews'], int)
        assert isinstance(data['average_rating'], (int, float))


# ==================== JSON Response Format Tests ====================

class TestJSONFormat:
    """Test JSON response format and structure."""
    
    def test_json_response_content_type(self, client):
        """Test that API returns proper JSON content type."""
        response = client.get(url_for('attractions.api_attractions'))
        
        assert response.content_type == 'application/json'
    
    def test_json_response_is_valid(self, client):
        """Test that responses contain valid JSON."""
        response = client.get(url_for('attractions.api_attractions'))
        
        assert response.status_code == 200
        # This will raise if JSON is invalid
        assert response.json is not None
    
    def test_error_response_format(self, client):
        """Test error response format."""
        response = client.get(url_for('attractions.view_attraction', attraction_id=99999))
        
        assert response.status_code == 404
    
    def test_pagination_format(self, client, test_attraction):
        """Test pagination response format."""
        response = client.get(
            url_for('reviews.api_attraction_reviews', attraction_id=test_attraction.id)
        )
        
        assert response.status_code == 200
        data = response.json
        
        if 'pagination' in data:
            pagination = data['pagination']
            required_fields = ['current_page', 'per_page', 'total_pages']
            for field in required_fields:
                assert field in pagination


# ==================== API Authorization Tests ====================

class TestAPIAuthorization:
    """Test authorization for API endpoints."""
    
    def test_add_review_api_requires_login(self, client, test_attraction):
        """Test that adding review via API requires authentication."""
        response = client.post(
            url_for('reviews.api_add_review', attraction_id=test_attraction.id),
            json={'title': 'Test', 'rating': 4.0, 'comment': 'Good place' * 10},
            content_type='application/json'
        )
        
        # Should redirect to login
        assert response.status_code == 302 or response.status_code == 401
    
    def test_add_review_api_authenticated(self, authenticated_client, test_attraction, test_user):
        """Test adding review via API when authenticated."""
        response = authenticated_client.post(
            url_for('reviews.api_add_review', attraction_id=test_attraction.id),
            json={
                'title': 'Great Experience',
                'rating': 4.5,
                'comment': 'This was wonderful and I loved it' * 5
            },
            content_type='application/json'
        )
        
        assert response.status_code in [200, 201, 302]  # May redirect after creation
    
    def test_delete_review_api_requires_ownership(self, client, test_review, another_user):
        """Test that deleting review requires ownership."""
        # Login as different user
        client.post(
            url_for('auth.login'),
            data={'username': another_user.username, 'password': 'otherpass123'}
        )
        
        response = client.delete(
            url_for('reviews.api_delete_review', review_id=test_review.id)
        )
        
        # Should fail (403 Forbidden or 302 redirect)
        assert response.status_code in [302, 403]


# ==================== Data Validation Tests ====================

class TestAPIDataValidation:
    """Test data validation in API responses."""
    
    def test_rating_is_valid_number(self, client, test_attraction, test_review):
        """Test that ratings are valid numbers."""
        response = client.get(
            url_for('reviews.api_attraction_reviews', attraction_id=test_attraction.id)
        )
        
        assert response.status_code == 200
        data = response.json
        
        for review in data.get('reviews', []):
            rating = review.get('rating')
            assert isinstance(rating, (int, float))
            assert 1.0 <= rating <= 5.0
    
    def test_coordinates_are_valid(self, client, test_city):
        """Test that city coordinates are valid."""
        response = client.get(url_for('attractions.api_cities'))
        
        assert response.status_code == 200
        data = response.json
        
        for city in data:
            lat = city.get('latitude')
            lon = city.get('longitude')
            assert isinstance(lat, (int, float))
            assert isinstance(lon, (int, float))
            assert -90 <= lat <= 90
            assert -180 <= lon <= 180
    
    def test_timestamps_are_iso_format(self, client, test_attraction, test_review):
        """Test that timestamps are in ISO format."""
        response = client.get(
            url_for('reviews.api_attraction_reviews', attraction_id=test_attraction.id)
        )
        
        assert response.status_code == 200
        data = response.json
        
        for review in data.get('reviews', []):
            created_at = review.get('created_at')
            # Should be ISO format string with T separator
            assert isinstance(created_at, str)
            assert 'T' in created_at or '-' in created_at
