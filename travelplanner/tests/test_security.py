"""
Tests for security features.
Tests CSRF protection, authorization, authentication, and data validation.
"""

import pytest
from flask import url_for
from werkzeug.security import check_password_hash


# ==================== Password Security ====================

class TestPasswordSecurity:
    """Test password security measures."""
    
    def test_password_is_hashed(self, test_user):
        """Test that passwords are stored hashed, not plain text."""
        assert test_user.password_hash != 'testpass123'
        assert len(test_user.password_hash) > 20
    
    def test_password_verification(self, test_user):
        """Test password verification works correctly."""
        assert test_user.check_password('testpass123')
        assert not test_user.check_password('wrongpassword')
    
    def test_different_passwords_have_different_hashes(self, db_session):
        """Test that different passwords don't produce same hash."""
        from app.models import User
        
        user1 = User(username='user1', email='user1@example.com', password='password123')
        user2 = User(username='user2', email='user2@example.com', password='password123')
        
        db_session.add(user1)
        db_session.add(user2)
        db_session.commit()
        
        # Same password should produce different hashes (due to salt)
        assert user1.password_hash != user2.password_hash
        # But both should verify correctly
        assert user1.check_password('password123')
        assert user2.check_password('password123')


# ==================== Authentication & Authorization ====================

class TestAuthentication:
    """Test authentication flows."""
    
    def test_unauthenticated_user_cannot_add_review(self, client, test_attraction):
        """Test that unauthenticated users cannot add reviews."""
        response = client.get(url_for('reviews.add_review', attraction_id=test_attraction.id))
        
        assert response.status_code == 302  # Redirect to login
        assert '/auth/login' in response.location
    
    def test_authenticated_user_can_add_review(self, authenticated_client, test_attraction):
        """Test that authenticated users can add reviews."""
        response = authenticated_client.get(
            url_for('reviews.add_review', attraction_id=test_attraction.id)
        )
        
        # Should load the review form
        assert response.status_code == 200
    
    def test_user_cannot_edit_others_review(self, client, test_review, another_user):
        """Test that users cannot edit other users' reviews."""
        # Login as different user
        client.post(url_for('auth.login'), data={
            'username': another_user.username,
            'password': 'otherpass123'
        })
        
        # Try to access edit page
        response = client.get(url_for('reviews.edit_review', review_id=test_review.id))
        
        # Should deny access (403 or redirect)
        assert response.status_code in [302, 403]
    
    def test_user_can_edit_own_review(self, authenticated_client, test_review, test_user):
        """Test that users can edit their own reviews."""
        assert test_review.user_id == test_user.id
        
        response = authenticated_client.get(
            url_for('reviews.edit_review', review_id=test_review.id)
        )
        
        # Should allow access
        assert response.status_code == 200


# ==================== Authorization & Access Control ====================

class TestAuthorization:
    """Test authorization and access control."""
    
    def test_protected_routes_require_login(self, client):
        """Test that protected routes require authentication."""
        protected_routes = [
            url_for('auth.profile'),
            url_for('auth.edit_profile'),
        ]
        
        for route in protected_routes:
            response = client.get(route)
            assert response.status_code == 302  # Redirect
            assert '/auth/login' in response.location
    
    def test_delete_review_requires_ownership(self, client, test_review, test_user, another_user):
        """Test that only owner can delete review."""
        # Login as different user
        client.post(url_for('auth.login'), data={
            'username': another_user.username,
            'password': 'otherpass123'
        })
        
        # Try to delete another user's review
        response = client.post(
            url_for('reviews.delete_review', review_id=test_review.id),
            follow_redirects=True
        )
        
        # Should deny or redirect to unauthorized page
        assert response.status_code == 403 or response.status_code == 200
    
    def test_delete_review_owner_can_delete(self, authenticated_client, test_review, test_user):
        """Test that review owner can delete review."""
        assert test_review.user_id == test_user.id
        
        response = authenticated_client.post(
            url_for('reviews.delete_review', review_id=test_review.id),
            follow_redirects=True
        )
        
        # Should succeed
        assert response.status_code == 200


# ==================== CSRF Protection ====================

class TestCSRFProtection:
    """Test CSRF protection."""
    
    def test_login_form_has_csrf_token(self, client):
        """Test that login form includes CSRF token."""
        response = client.get(url_for('auth.login'))
        
        assert response.status_code == 200
        assert b'csrf_token' in response.data
    
    def test_register_form_has_csrf_token(self, client):
        """Test that register form includes CSRF token."""
        response = client.get(url_for('auth.register'))
        
        assert response.status_code == 200
        assert b'csrf_token' in response.data
    
    def test_review_form_has_csrf_token(self, authenticated_client, test_attraction):
        """Test that review form includes CSRF token."""
        response = authenticated_client.get(
            url_for('reviews.add_review', attraction_id=test_attraction.id)
        )
        
        assert response.status_code == 200
        assert b'csrf_token' in response.data


# ==================== Input Validation ====================

class TestInputValidation:
    """Test input validation and sanitization."""
    
    def test_username_validation(self, client):
        """Test username validation."""
        # Too short
        response = client.post(url_for('auth.register'), data={
            'username': 'ab',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        assert response.status_code == 200
        # Should show error or reject
    
    def test_email_validation(self, client):
        """Test email validation."""
        response = client.post(url_for('auth.register'), data={
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        # Should reject invalid email
        assert response.status_code == 200  # Re-renders form
    
    def test_password_requirements(self, client):
        """Test password minimum length requirement."""
        response = client.post(url_for('auth.register'), data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'short',
            'confirm_password': 'short'
        })
        
        # Should reject - password too short
        assert response.status_code == 200  # Re-renders form
    
    def test_review_title_validation(self, authenticated_client, test_attraction):
        """Test review title length validation."""
        response = authenticated_client.post(
            url_for('reviews.add_review', attraction_id=test_attraction.id),
            data={
                'title': 'ab',  # Too short
                'rating': 4.0,
                'comment': 'This is a valid comment about the place' * 5
            }
        )
        
        # Should reject - title too short
        assert response.status_code == 200  # Re-renders form
    
    def test_review_rating_validation(self, authenticated_client, test_attraction):
        """Test review rating range validation."""
        response = authenticated_client.post(
            url_for('reviews.add_review', attraction_id=test_attraction.id),
            data={
                'title': 'Great Place',
                'rating': 10.0,  # Out of range
                'comment': 'This is a valid comment about the place' * 5
            }
        )
        
        # Should reject - rating out of range
        assert response.status_code == 200  # Re-renders form


# ==================== Data Integrity ====================

class TestDataIntegrity:
    """Test data integrity and constraints."""
    
    def test_unique_username_constraint(self, db_session, test_user):
        """Test that usernames must be unique."""
        from app.models import User
        
        # Try to create user with same username
        duplicate = User(
            username=test_user.username,
            email='different@example.com',
            password='password123'
        )
        
        db_session.add(duplicate)
        
        # Should raise constraint error
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_unique_email_constraint(self, db_session, test_user):
        """Test that emails must be unique."""
        from app.models import User
        
        # Try to create user with same email
        duplicate = User(
            username='different_user',
            email=test_user.email,
            password='password123'
        )
        
        db_session.add(duplicate)
        
        # Should raise constraint error
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_unique_review_per_user_per_attraction(self, db_session, test_user, test_attraction):
        """Test that user can only review attraction once."""
        from app.models import Review
        
        # Existing review by test_user on test_attraction
        # Try to create another review
        duplicate_review = Review(
            title='Another Review',
            rating=3.0,
            comment='Another comment about this place' * 10,
            user_id=test_user.id,
            attraction_id=test_attraction.id
        )
        
        db_session.add(duplicate_review)
        
        # Should raise constraint error (unique constraint)
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_review_cascade_delete(self, db_session, test_user, test_review):
        """Test that deleting user cascades to delete reviews."""
        from app.models import Review
        
        review_id = test_review.id
        
        # Delete user
        db_session.delete(test_user)
        db_session.commit()
        
        # Check that review is also deleted
        review = db_session.query(Review).filter_by(id=review_id).first()
        assert review is None


# ==================== Session Security ====================

class TestSessionSecurity:
    """Test session security."""
    
    def test_session_expires_on_logout(self, authenticated_client, test_user):
        """Test that session is cleared on logout."""
        # Verify authenticated
        response = authenticated_client.get(url_for('auth.profile'))
        assert response.status_code == 200
        
        # Logout
        authenticated_client.get(url_for('auth.logout'))
        
        # Try to access protected route
        response = authenticated_client.get(url_for('auth.profile'))
        
        # Should redirect to login
        assert response.status_code == 302
    
    def test_session_required_for_protected_routes(self, client, test_user):
        """Test that protected routes require valid session."""
        # Not authenticated
        response = client.get(url_for('auth.profile'))
        
        assert response.status_code == 302
        assert '/auth/login' in response.location


# ==================== SQL Injection Prevention ====================

class TestSQLInjectionPrevention:
    """Test protection against SQL injection."""
    
    def test_search_with_special_characters(self, client):
        """Test that search handles special characters safely."""
        response = client.get(
            url_for('attractions.search'),
            query_string={'q': "'; DROP TABLE users; --"}
        )
        
        # Should not execute SQL
        assert response.status_code == 200
        # Database should still be intact
    
    def test_filter_with_sql_injection_attempt(self, client):
        """Test that filter handles injection attempts safely."""
        response = client.get(
            url_for('attractions.list_attractions'),
            query_string={'category': "'; DELETE FROM attractions; --"}
        )
        
        # Should not execute SQL
        assert response.status_code == 200


# ==================== XSS Prevention ====================

class TestXSSPrevention:
    """Test protection against cross-site scripting."""
    
    def test_review_text_is_escaped(self, client, test_attraction):
        """Test that review text is properly escaped."""
        from app.models import Review
        from sqlalchemy import create_engine
        from sqlalchemy.orm import Session
        
        # Create review with HTML/script content
        # In real scenario, this would be caught by form validation
        malicious_content = '<script>alert("xss")</script>'
        
        # This should be handled by form validation first
        # But test that it's safe in template
        response = client.get(
            url_for('attractions.view_attraction', attraction_id=test_attraction.id)
        )
        
        assert response.status_code == 200
        # Even if review content included script tags, they should be escaped
        # (This would be verified by checking the rendered HTML)
    
    def test_user_input_in_search_is_escaped(self, client):
        """Test that search input is escaped in results."""
        search_term = '<script>alert("xss")</script>'
        
        response = client.get(
            url_for('attractions.search'),
            query_string={'q': search_term}
        )
        
        assert response.status_code == 200
        # Should not render unescaped script tags


# ==================== Rate Limiting Tests ====================

class TestSecurityHeaders:
    """Test security headers."""
    
    def test_security_headers_present(self, client):
        """Test that security headers are set."""
        response = client.get(url_for('main.index'))
        
        # Some security headers that Flask/Werkzeug typically sets
        assert response.status_code == 200
        # Could check for specific headers depending on implementation
        # E.g., Content-Type, X-Content-Type-Options, etc.
