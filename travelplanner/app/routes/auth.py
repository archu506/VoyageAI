"""
Authentication blueprint for user registration, login, and profile management.
"""

import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import User
from app.forms import RegistrationForm, LoginForm


logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration page and handler.
    
    GET: Display registration form
    POST: Process registration
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                email=form.email.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f'New user registered: {user.username}')
            flash('Registration successful! You can now login.', 'success')
            
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            db.session.rollback()
            logger.error(f'Registration error: {str(e)}')
            flash('An error occurred during registration', 'danger')
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login page and handler.
    
    GET: Display login form
    POST: Process login
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            logger.warning(f'Failed login attempt for username: {form.username.data}')
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        logger.info(f'User logged in: {user.username}')
        
        next_page = request.args.get('next')
        if not next_page or url_has_allowed_host_and_scheme(next_page):
            next_page = url_for('main.index')
        
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Log out the current user."""
    username = current_user.username
    logout_user()
    logger.info(f'User logged out: {username}')
    flash('You have been logged out.', 'info')
    
    return redirect(url_for('main.index'))


@auth_bp.route('/profile')
@login_required
def profile():
    """
    User profile page showing reviews and account info.
    """
    try:
        # Get user's reviews
        reviews = current_user.reviews
        
        return render_template('auth/profile.html', reviews=reviews)
    
    except Exception as e:
        logger.error(f'Error loading profile: {str(e)}')
        flash('Failed to load profile', 'danger')
        return redirect(url_for('main.index'))


@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    Edit user profile.
    
    GET: Display edit form
    POST: Process profile update
    """
    from app.forms import EditProfileForm
    
    form = EditProfileForm()
    
    if form.validate_on_submit():
        try:
            current_user.email = form.email.data
            
            if form.password.data:
                current_user.set_password(form.password.data)
            
            db.session.commit()
            logger.info(f'Profile updated for user: {current_user.username}')
            flash('Your profile has been updated.', 'success')
            
            return redirect(url_for('auth.profile'))
        
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error updating profile: {str(e)}')
            flash('An error occurred while updating profile', 'danger')
    
    elif request.method == 'GET':
        form.email.data = current_user.email
    
    return render_template('auth/edit_profile.html', form=form)


def url_has_allowed_host_and_scheme(url: str, allowed_hosts=None) -> bool:
    """
    Check if URL has allowed host and scheme for redirect.
    Prevents open redirect vulnerabilities.
    
    Args:
        url: URL to check
        allowed_hosts: List of allowed hostnames
        
    Returns:
        True if URL is safe to redirect to
    """
    if allowed_hosts is None:
        allowed_hosts = ['localhost', '127.0.0.1']
    
    from urllib.parse import urlparse
    
    if not url:
        return False
    
    parsed = urlparse(url)
    
    # Allow relative URLs
    if not parsed.netloc:
        return True
    
    # Check if domain is in allowed list
    return parsed.netloc.lower() in allowed_hosts
