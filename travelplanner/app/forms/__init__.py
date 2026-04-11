"""
Flask-WTF forms with comprehensive validation.
Includes CSRF protection and server-side validation.
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, FloatField, TextAreaField,
    SubmitField, SelectField, IntegerField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, NumberRange,
    ValidationError, Regexp, Optional, URL
)
from app.models import User, Attraction


class RegistrationForm(FlaskForm):
    """User registration form."""
    
    username = StringField(
        'Username',
        validators=[
            DataRequired(message='Username is required'),
            Length(
                min=3,
                max=80,
                message='Username must be 3-80 characters'
            ),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message='Username can only contain letters, numbers, and underscores'
            )
        ]
    )
    
    email = StringField(
        'Email',
        validators=[
            DataRequired(message='Email is required'),
            Email(message='Invalid email address')
        ]
    )
    
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required'),
            Length(
                min=8,
                message='Password must be at least 8 characters'
            )
        ]
    )
    
    password_confirm = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message='Please confirm your password'),
            EqualTo('password', message='Passwords must match')
        ]
    )
    
    submit = SubmitField('Register')
    
    def validate_username(self, field):
        """Check if username already exists."""
        if User.query.filter_by(username=field.data.lower()).first():
            raise ValidationError('Username already taken. Please choose another.')
    
    def validate_email(self, field):
        """Check if email already registered."""
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered. Please use another.')


class LoginForm(FlaskForm):
    """User login form."""
    
    username = StringField(
        'Username',
        validators=[DataRequired(message='Username is required')]
    )
    
    password = PasswordField(
        'Password',
        validators=[DataRequired(message='Password is required')]
    )
    
    submit = SubmitField('Login')


class ReviewForm(FlaskForm):
    """Form for creating and editing reviews."""
    
    title = StringField(
        'Review Title',
        validators=[
            DataRequired(message='Please provide a title'),
            Length(
                min=5,
                max=200,
                message='Title must be 5-200 characters'
            )
        ]
    )
    
    rating = FloatField(
        'Rating (1-5)',
        validators=[
            DataRequired(message='Rating is required'),
            NumberRange(
                min=1.0,
                max=5.0,
                message='Rating must be between 1.0 and 5.0'
            )
        ]
    )
    
    comment = TextAreaField(
        'Your Review',
        validators=[
            DataRequired(message='Please write a review'),
            Length(
                min=20,
                max=2000,
                message='Review must be 20-2000 characters'
            )
        ]
    )
    
    submit = SubmitField('Submit Review')


class SearchForm(FlaskForm):
    """Form for searching cities."""
    
    query = StringField(
        'Search',
        validators=[
            DataRequired(message='Enter a search term'),
            Length(min=1, max=100, message='Search term too long')
        ]
    )
    
    submit = SubmitField('Search')


class CityFilterForm(FlaskForm):
    """Form for filtering cities."""
    
    country = StringField(
        'Country',
        validators=[Optional(), Length(max=100)]
    )
    
    sort = SelectField(
        'Sort By',
        choices=[
            ('name_asc', 'Name (A-Z)'),
            ('name_desc', 'Name (Z-A)'),
            ('rating', 'Highest Rated')
        ],
        default='name_asc'
    )
    
    submit = SubmitField('Filter')


class AttractionFilterForm(FlaskForm):
    """Form for filtering attractions."""
    
    category = SelectField(
        'Category',
        choices=[
            ('', 'All Categories'),
            ('heritage', 'Heritage'),
            ('adventure', 'Adventure'),
            ('cultural', 'Cultural'),
            ('natural', 'Natural'),
            ('religious', 'Religious'),
        ],
        validators=[Optional()]
    )
    
    min_rating = FloatField(
        'Minimum Rating',
        validators=[
            Optional(),
            NumberRange(min=1.0, max=5.0)
        ]
    )
    
    submit = SubmitField('Filter')


class EditProfileForm(FlaskForm):
    """Form for editing user profile."""
    
    email = StringField(
        'Email',
        validators=[
            DataRequired(message='Email is required'),
            Email(message='Invalid email address')
        ]
    )
    
    password = PasswordField(
        'New Password (leave blank to keep current)',
        validators=[
            Optional(),
            Length(
                min=8,
                message='Password must be at least 8 characters'
            )
        ]
    )
    
    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[
            Optional(),
            EqualTo('password', message='Passwords must match')
        ]
    )
    
    submit = SubmitField('Update Profile')
    
    def validate_email(self) -> None:
        """Check if email is already in use by another user."""
        from flask_login import current_user
        
        if self.email.data != current_user.email:
            user = User.query.filter_by(email=self.email.data).first()
            if user:
                raise ValidationError('This email is already registered')
