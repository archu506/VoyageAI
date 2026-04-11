"""
Tests for form validation.
Tests WTForms validators and custom validation logic.
"""

import pytest
from app.forms import (
    RegistrationForm, LoginForm, ReviewForm, SearchForm,
    CityFilterForm, AttractionFilterForm, EditProfileForm
)
from app.models import User


class TestRegistrationForm:
    """Test registration form validation."""
    
    def test_valid_registration(self, app):
        """Test valid registration form."""
        with app.test_request_context():
            form = RegistrationForm(
                username='newuser',
                email='new@example.com',
                password='securepass123',
                confirm_password='securepass123'
            )
            assert form.validate()
    
    def test_missing_username(self, app):
        """Test validation when username is missing."""
        with app.test_request_context():
            form = RegistrationForm(
                username='',
                email='test@example.com',
                password='password123',
                confirm_password='password123'
            )
            assert not form.validate()
            assert 'username' in form.errors
    
    def test_invalid_username_format(self, app):
        """Test validation with invalid username format."""
        with app.test_request_context():
            form = RegistrationForm(
                username='user@name',  # @ not allowed
                email='test@example.com',
                password='password123',
                confirm_password='password123'
            )
            assert not form.validate()
            assert 'username' in form.errors
    
    def test_username_too_short(self, app):
        """Test validation when username is too short."""
        with app.test_request_context():
            form = RegistrationForm(
                username='ab',  # Only 2 chars, min is 3
                email='test@example.com',
                password='password123',
                confirm_password='password123'
            )
            assert not form.validate()
            assert 'username' in form.errors
    
    def test_invalid_email(self, app):
        """Test validation with invalid email."""
        with app.test_request_context():
            form = RegistrationForm(
                username='validuser',
                email='notanemail',
                password='password123',
                confirm_password='password123'
            )
            assert not form.validate()
            assert 'email' in form.errors
    
    def test_password_too_short(self, app):
        """Test validation when password is too short."""
        with app.test_request_context():
            form = RegistrationForm(
                username='newuser',
                email='new@example.com',
                password='pass',  # Only 4 chars, min is 8
                confirm_password='pass'
            )
            assert not form.validate()
            assert 'password' in form.errors
    
    def test_password_mismatch(self, app):
        """Test validation when passwords don't match."""
        with app.test_request_context():
            form = RegistrationForm(
                username='newuser',
                email='new@example.com',
                password='securepass123',
                confirm_password='differentpass'
            )
            assert not form.validate()
            assert 'confirm_password' in form.errors
    
    def test_duplicate_username(self, app, test_user):
        """Test validation when username already exists."""
        with app.test_request_context():
            form = RegistrationForm(
                username=test_user.username,  # Existing user
                email='different@example.com',
                password='password123',
                confirm_password='password123'
            )
            assert not form.validate()
            assert 'username' in form.errors
    
    def test_duplicate_email(self, app, test_user):
        """Test validation when email already exists."""
        with app.test_request_context():
            form = RegistrationForm(
                username='differentuser',
                email=test_user.email,  # Existing email
                password='password123',
                confirm_password='password123'
            )
            assert not form.validate()
            assert 'email' in form.errors


class TestLoginForm:
    """Test login form validation."""
    
    def test_valid_login(self, app):
        """Test valid login form."""
        with app.test_request_context():
            form = LoginForm(
                username='testuser',
                password='password123'
            )
            assert form.validate()
    
    def test_missing_username(self, app):
        """Test login without username."""
        with app.test_request_context():
            form = LoginForm(
                username='',
                password='password123'
            )
            assert not form.validate()
            assert 'username' in form.errors
    
    def test_missing_password(self, app):
        """Test login without password."""
        with app.test_request_context():
            form = LoginForm(
                username='testuser',
                password=''
            )
            assert not form.validate()
            assert 'password' in form.errors


class TestReviewForm:
    """Test review form validation."""
    
    def test_valid_review(self, app):
        """Test valid review form."""
        with app.test_request_context():
            form = ReviewForm(
                title='Great place!',
                rating=4.5,
                comment='This is a wonderful place to visit.' * 5
            )
            assert form.validate()
    
    def test_missing_title(self, app):
        """Test review without title."""
        with app.test_request_context():
            form = ReviewForm(
                title='',
                rating=4.0,
                comment='Nice place' * 5
            )
            assert not form.validate()
            assert 'title' in form.errors
    
    def test_title_too_short(self, app):
        """Test review with title too short."""
        with app.test_request_context():
            form = ReviewForm(
                title='Good',  # Only 4 chars, min is 5
                rating=4.0,
                comment='Nice place' * 5
            )
            assert not form.validate()
            assert 'title' in form.errors
    
    def test_title_too_long(self, app):
        """Test review with title too long."""
        with app.test_request_context():
            form = ReviewForm(
                title='a' * 201,  # 201 chars, max is 200
                rating=4.0,
                comment='Nice place' * 5
            )
            assert not form.validate()
            assert 'title' in form.errors
    
    def test_invalid_rating(self, app):
        """Test review with invalid rating."""
        with app.test_request_context():
            form = ReviewForm(
                title='Great!',
                rating=6.0,  # Max is 5.0
                comment='Nice place' * 5
            )
            assert not form.validate()
            assert 'rating' in form.errors
    
    def test_missing_comment(self, app):
        """Test review without comment."""
        with app.test_request_context():
            form = ReviewForm(
                title='Great!',
                rating=4.0,
                comment=''
            )
            assert not form.validate()
            assert 'comment' in form.errors
    
    def test_comment_too_short(self, app):
        """Test review with comment too short."""
        with app.test_request_context():
            form = ReviewForm(
                title='Good!',
                rating=4.0,
                comment='Short'  # Less than 20 chars
            )
            assert not form.validate()
            assert 'comment' in form.errors
    
    def test_comment_too_long(self, app):
        """Test review with comment too long."""
        with app.test_request_context():
            form = ReviewForm(
                title='Good!',
                rating=4.0,
                comment='a' * 2001  # More than 2000 chars
            )
            assert not form.validate()
            assert 'comment' in form.errors


class TestSearchForm:
    """Test search form validation."""
    
    def test_valid_search(self, app):
        """Test valid search form."""
        with app.test_request_context():
            form = SearchForm(query='Paris')
            assert form.validate()
    
    def test_empty_search(self, app):
        """Test search with empty query."""
        with app.test_request_context():
            form = SearchForm(query='')
            assert not form.validate()


class TestEditProfileForm:
    """Test profile editing form."""
    
    def test_valid_profile_edit(self, app, test_user):
        """Test valid profile edit without password change."""
        with app.test_request_context():
            form = EditProfileForm(
                email='newemail@example.com',
                password='',
                confirm_password=''
            )
            assert form.validate()
    
    def test_valid_profile_with_password(self, app):
        """Test valid profile edit with password change."""
        with app.test_request_context():
            form = EditProfileForm(
                email='new@example.com',
                password='newpass123',
                confirm_password='newpass123'
            )
            assert form.validate()
    
    def test_password_mismatch_on_edit(self, app):
        """Test profile edit with mismatched passwords."""
        with app.test_request_context():
            form = EditProfileForm(
                email='new@example.com',
                password='newpass123',
                confirm_password='differentpass'
            )
            assert not form.validate()
            assert 'confirm_password' in form.errors
    
    def test_invalid_email_on_edit(self, app):
        """Test profile edit with invalid email."""
        with app.test_request_context():
            form = EditProfileForm(
                email='notanemail',
                password='',
                confirm_password=''
            )
            assert not form.validate()
            assert 'email' in form.errors


class TestFilterForms:
    """Test filtering forms."""
    
    def test_city_filter_form(self, app):
        """Test city filter form."""
        with app.test_request_context():
            form = CityFilterForm(
                search='Paris'
            )
            assert form.validate()
    
    def test_attraction_filter_form(self, app):
        """Test attraction filter form."""
        with app.test_request_context():
            form = AttractionFilterForm(
                category='heritage',
                min_rating=3.0
            )
            assert form.validate()
