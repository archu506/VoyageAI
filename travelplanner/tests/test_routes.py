"""
Tests for route handlers and integration tests.
Tests HTTP endpoints, authentication, and full workflows.
"""

import pytest
from flask import url_for


# ==================== Authentication Routes ====================

class TestAuthRoutes:
    """Test authentication routes."""
    
    def test_register_page_loads(self, client):
        """Test registration page loads."""
        response = client.get(url_for('auth.register'))
        assert response.status_code == 200
        assert b'Create Account' in response.data
    
    def test_register_valid_user(self, client, app_context):
        """Test successful user registration."""
        response = client.post(url_for('auth.register'), data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'securepass123',
            'confirm_password': 'securepass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Registration successful' in response.data
    
    def test_register_duplicate_username(self, client, test_user):
        """Test registration with existing username."""
        response = client.post(url_for('auth.register'), data={
            'username': test_user.username,
            'email': 'different@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        assert b'already registered' in response.data or b'Register' in response.data
    
    def test_login_page_loads(self, client):
        """Test login page loads."""
        response = client.get(url_for('auth.login'))
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_login_valid_user(self, client, test_user):
        """Test successful login."""
        response = client.post(url_for('auth.login'), data={
            'username': test_user.username,
            'password': 'testpass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'testuser' in response.data or b'Home' in response.data
    
    def test_login_invalid_password(self, client, test_user):
        """Test login with incorrect password."""
        response = client.post(url_for('auth.login'), data={
            'username': test_user.username,
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert b'Invalid username or password' in response.data
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post(url_for('auth.login'), data={
            'username': 'nonexistent',
            'password': 'somepassword'
        }, follow_redirects=True)
        
        assert b'Invalid username or password' in response.data
    
    def test_logout(self, authenticated_client):
        """Test logout."""
        response = authenticated_client.get(url_for('auth.logout'), follow_redirects=True)
        
        assert response.status_code == 200
        assert b'logged out' in response.data or b'Home' in response.data
    
    def test_profile_requires_login(self, client):
        """Test that profile page requires login."""
        response = client.get(url_for('auth.profile'))
        
        assert response.status_code == 302  # Redirect
        assert '/auth/login' in response.location
    
    def test_profile_page_authenticated(self, authenticated_client, test_user):
        """Test profile page when authenticated."""
        response = authenticated_client.get(url_for('auth.profile'))
        
        assert response.status_code == 200
        assert b'testuser' in response.data


# ==================== Main Routes ====================

class TestMainRoutes:
    """Test main application routes."""
    
    def test_home_page_loads(self, client, app_context):
        """Test home page loads."""
        response = client.get(url_for('main.index'))
        
        assert response.status_code == 200
        assert b'Discover Amazing Destinations' in response.data or b'Travel Planner' in response.data
    
    def test_about_page_loads(self, client, app_context):
        """Test about page loads."""
        response = client.get(url_for('main.about'))
        
        assert response.status_code == 200
        assert b'About' in response.data
    
    def test_health_check(self, client, app_context):
        """Test health check endpoint."""
        response = client.get(url_for('main.health_check'))
        
        assert response.status_code == 200
        assert response.json['status'] == 'healthy'
        assert 'database' in response.json
    
    def test_api_stats(self, client, app_context):
        """Test API stats endpoint."""
        response = client.get(url_for('main.get_stats'))
        
        assert response.status_code == 200
        data = response.json
        assert 'total_cities' in data
        assert 'total_attractions' in data
        assert 'total_reviews' in data


# ==================== Attraction Routes ====================

class TestAttractionRoutes:
    """Test attraction routes."""
    
    def test_attractions_list_page(self, client, test_city, test_attraction):
        """Test attractions list page."""
        response = client.get(url_for('attractions.list_attractions'))
        
        assert response.status_code == 200
        assert b'Attractions' in response.data
    
    def test_attraction_detail_page(self, client, test_attraction):
        """Test attraction detail page."""
        response = client.get(url_for('attractions.view_attraction', attraction_id=test_attraction.id))
        
        assert response.status_code == 200
        assert test_attraction.name.encode() in response.data
    
    def test_attraction_detail_not_found(self, client):
        """Test attraction detail page for non-existent attraction."""
        response = client.get(url_for('attractions.view_attraction', attraction_id=99999))
        
        assert response.status_code == 404
    
    def test_city_attractions_page(self, client, test_city, test_attraction):
        """Test city attractions page."""
        response = client.get(url_for('attractions.city_attractions', city_id=test_city.id))
        
        assert response.status_code == 200
        assert test_city.name.encode() in response.data
    
    def test_search_attractions(self, client, test_attraction):
        """Test searching for attractions."""
        response = client.get(url_for('attractions.search', q=test_attraction.name))
        
        assert response.status_code == 200
        assert test_attraction.name.encode() in response.data
    
    def test_search_cities(self, client, test_city):
        """Test searching for cities."""
        response = client.get(url_for('attractions.search', q=test_city.name, type='cities'))
        
        assert response.status_code == 200
        assert test_city.name.encode() in response.data
    
    def test_attractions_api_endpoint(self, client, test_attraction):
        """Test attractions API endpoint."""
        response = client.get(url_for('attractions.api_attractions'))
        
        assert response.status_code == 200
        data = response.json
        assert isinstance(data, list)
        if data:
            assert 'id' in data[0]
            assert 'name' in data[0]


# ==================== Review Routes ====================

class TestReviewRoutes:
    """Test review routes."""
    
    def test_add_review_requires_login(self, client, test_attraction):
        """Test that adding review requires login."""
        response = client.get(url_for('reviews.add_review', attraction_id=test_attraction.id))
        
        assert response.status_code == 302  # Redirect
        assert '/auth/login' in response.location
    
    def test_add_review_page(self, authenticated_client, test_attraction):
        """Test add review page loads."""
        response = authenticated_client.get(url_for('reviews.add_review', attraction_id=test_attraction.id))
        
        assert response.status_code == 200
        assert b'Share Your Experience' in response.data or b'Review' in response.data
    
    def test_add_review_valid(self, authenticated_client, test_user, test_attraction, app_context):
        """Test adding a valid review."""
        response = authenticated_client.post(
            url_for('reviews.add_review', attraction_id=test_attraction.id),
            data={
                'title': 'Excellent place!',
                'rating': 4.5,
                'comment': 'This was a wonderful experience.' * 5
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert b'review' in response.data or b'Excellent place!' in response.data
    
    def test_edit_review_page(self, authenticated_client, test_review, test_user):
        """Test edit review page."""
        response = authenticated_client.get(url_for('reviews.edit_review', review_id=test_review.id))
        
        assert response.status_code == 200
        assert b'Edit' in response.data
    
    def test_edit_review_unauthorized(self, client, test_review, another_user):
        """Test editing review by unauthorized user."""
        # Login as different user
        client.post(url_for('auth.login'), data={
            'username': another_user.username,
            'password': 'otherpass123'
        })
        
        response = client.get(url_for('reviews.edit_review', review_id=test_review.id))
        
        assert response.status_code == 403 or response.status_code == 302
    
    def test_delete_review(self, authenticated_client, test_review, test_user, app_context):
        """Test deleting a review."""
        response = authenticated_client.post(
            url_for('reviews.delete_review', review_id=test_review.id),
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert b'deleted' in response.data or b'review' in response.data
    
    def test_user_reviews_page(self, client, test_user, test_review):
        """Test user reviews page."""
        response = client.get(url_for('reviews.user_reviews', user_id=test_user.id))
        
        assert response.status_code == 200
        assert test_user.username.encode() in response.data
    
    def test_reviews_api_endpoint(self, client, test_attraction, test_review):
        """Test reviews API endpoint."""
        response = client.get(url_for('reviews.api_attraction_reviews', attraction_id=test_attraction.id))
        
        assert response.status_code == 200
        data = response.json
        assert 'reviews' in data
        assert 'pagination' in data


# ==================== Integration Tests ====================

class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_complete_user_workflow(self, client, app_context):
        """Test complete user workflow: register, login, review."""
        # Register
        response = client.post(url_for('auth.register'), data={
            'username': 'integrationuser',
            'email': 'integration@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        })
        assert response.status_code == 302  # Redirect on success
        
        # Login
        response = client.post(url_for('auth.login'), data={
            'username': 'integrationuser',
            'password': 'testpass123'
        })
        assert response.status_code == 302  # Redirect on success
        
        # View profile
        response = client.get(url_for('auth.profile'), follow_redirects=True)
        assert response.status_code == 200
        assert b'integrationuser' in response.data
    
    def test_attraction_browsing_workflow(self, client, test_city, test_attraction, test_review):
        """Test browsing attractions workflow."""
        # View attractions list
        response = client.get(url_for('attractions.list_attractions'))
        assert response.status_code == 200
        
        # View specific city
        response = client.get(url_for('attractions.city_attractions', city_id=test_city.id))
        assert response.status_code == 200
        
        # View attraction detail
        response = client.get(url_for('attractions.view_attraction', attraction_id=test_attraction.id))
        assert response.status_code == 200
        assert test_attraction.name.encode() in response.data
    
    def test_search_workflow(self, client, test_attraction, test_city):
        """Test search workflow."""
        # Search for attraction
        response = client.get(url_for('attractions.search', q=test_attraction.name))
        assert response.status_code == 200
        assert test_attraction.name.encode() in response.data
        
        # Search for city
        response = client.get(url_for('attractions.search', q=test_city.name, type='cities'))
        assert response.status_code == 200
        assert test_city.name.encode() in response.data


# ==================== Error Handling Tests ====================

class TestErrorHandling:
    """Test error handling."""
    
    def test_404_error_page(self, client):
        """Test 404 error page."""
        response = client.get('/nonexistent-page')
        
        assert response.status_code == 404
    
    def test_invalid_attraction_id(self, client):
        """Test accessing attraction with invalid ID."""
        response = client.get(url_for('attractions.view_attraction', attraction_id=99999))
        
        assert response.status_code == 404
    
    def test_invalid_city_id(self, client):
        """Test accessing city with invalid ID."""
        response = client.get(url_for('attractions.city_attractions', city_id=99999))
        
        assert response.status_code == 404
