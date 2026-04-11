"""
WTForms for Smart Tourism application.
Handles validation and CSRF protection for all forms.
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, IntegerField, FloatField,
    TextAreaField, SubmitField, SelectField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, NumberRange, Regexp,
    ValidationError, Optional
)
from app.models import User, Place


class RegistrationForm(FlaskForm):
    """Form for user registration."""
    
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Length(min=3, max=80, message='Username must be between 3 and 80 characters'),
            Regexp('^[a-zA-Z0-9_]*$', message='Username can only contain letters, numbers, and underscores')
        ]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(message='Invalid email address')
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=8, message='Password must be at least 8 characters long')
        ]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match')
        ]
    )
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """Check if username is already taken."""
        user = User.query.filter_by(username=username.data.lower()).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        """Check if email is already registered."""
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')


class LoginForm(FlaskForm):
    """Form for user login."""
    
    username = StringField(
        'Username',
        validators=[DataRequired()]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )
    submit = SubmitField('Login')


class ItineraryForm(FlaskForm):
    """Form for planning travel itinerary."""
    
    city = StringField(
        'City',
        validators=[
            DataRequired(message='City name is required'),
            Length(min=2, max=100, message='City name must be between 2 and 100 characters')
        ]
    )
    days = IntegerField(
        'Number of Days',
        validators=[
            DataRequired(),
            NumberRange(min=1, max=30, message='Number of days must be between 1 and 30')
        ]
    )
    submit = SubmitField('Generate Plan')
    # crowd_level removed: now predicted automatically


class ReviewForm(FlaskForm):
    """Form for submitting reviews."""
    
    rating = FloatField(
        'Rating',
        validators=[
            DataRequired(),
            NumberRange(min=1.0, max=5.0, message='Rating must be between 1.0 and 5.0')
        ]
    )
    comment = TextAreaField(
        'Your Review',
        validators=[
            DataRequired(message='Please write a review'),
            Length(min=10, max=1000, message='Review must be between 10 and 1000 characters')
        ]
    )
    submit = SubmitField('Submit Review')


class UpdateReviewForm(FlaskForm):
    """Form for updating existing reviews."""
    
    rating = FloatField(
        'Rating',
        validators=[
            DataRequired(),
            NumberRange(min=1.0, max=5.0, message='Rating must be between 1.0 and 5.0')
        ]
    )
    comment = TextAreaField(
        'Your Review',
        validators=[
            DataRequired(message='Please write a review'),
            Length(min=10, max=1000, message='Review must be between 10 and 1000 characters')
        ]
    )
    submit = SubmitField('Update Review')


class SearchForm(FlaskForm):
    """Form for searching cities."""
    
    search_query = StringField(
        'Search',
        validators=[
            DataRequired(),
            Length(min=1, max=100)
        ]
    )
    submit = SubmitField('Search')


class FilterReviewsForm(FlaskForm):
    """Form for filtering reviews."""
    
    min_rating = FloatField(
        'Minimum Rating',
        validators=[
            Optional(),
            NumberRange(min=1.0, max=5.0)
        ]
    )
    sort_by = SelectField(
        'Sort By',
        choices=[
            ('recent', 'Most Recent'),
            ('highest', 'Highest Rated'),
            ('lowest', 'Lowest Rated')
        ],
        default='recent'
    )
    submit = SubmitField('Filter')
