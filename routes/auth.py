"""Authentication routes: register, login, logout, profile."""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from services.logger import logger

auth = Blueprint("auth", __name__, url_prefix="/auth")

@auth.route("/register", methods=["GET", "POST"])
def register():
    # If already logged in, redirect to home
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")
        
        # Validation
        if not all([username, email, password]):
            flash("All fields required", "error")
            return redirect(url_for("auth.register"))
        
        if password != confirm:
            flash("Passwords don't match", "error")
            return redirect(url_for("auth.register"))
        
        if len(password) < 6:
            flash("Password must be at least 6 characters", "error")
            return redirect(url_for("auth.register"))
        
        # Register
        success, msg = User.register_user(username, email, password)
        if success:
            logger.info(f"User registered: {username}")
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("auth.login"))
        else:
            logger.warning(f"Registration failed: {msg}")
            flash(f"Registration failed: {msg}", "error")
            return redirect(url_for("auth.register"))
    
    return render_template("auth/register.html")

@auth.route("/login", methods=["GET", "POST"])
def login():
    # If already logged in, redirect to home
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    
    if request.method == "POST":
        login_input = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        # Try to get user by username first, then by email
        user = User.get_user(login_input) or User.get_user_by_email(login_input)
        
        if user and user.check_password(password):
            login_user(user)
            logger.info(f"User logged in: {user.username}")
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("home"))
        else:
            if not login_input:
                flash("Please enter username or email", "error")
            elif not password:
                flash("Please enter your password", "error")
            else:
                logger.warning(f"Failed login attempt: {login_input}")
                flash("Invalid username/email or password", "error")
            return redirect(url_for("auth.login"))
    
    return render_template("auth/login.html")

@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        
        user = User.get_user_by_email(email)
        if user:
            token = user.generate_reset_token()
            if token:
                reset_link = url_for("auth.reset_password", token=token, _external=True)
                # In production, send this link via email
                logger.info(f"Password reset requested for: {email}")
                flash("If this email exists, you will receive a password reset link shortly.", "info")
                
                # For demo purposes, show the reset link
                flash(f"Reset link: {reset_link}", "warning")
            else:
                flash("Error generating reset token", "error")
        else:
            # Don't reveal if email exists (security best practice)
            logger.info(f"Password reset requested for non-existent email: {email}")
            flash("If this email exists, you will receive a password reset link shortly.", "info")
        
        return redirect(url_for("auth.login"))
    
    return render_template("auth/forgot_password.html")

@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = User.verify_reset_token(token)
    if not user:
        logger.warning(f"Invalid reset token attempted: {token}")
        flash("Invalid or expired reset link", "error")
        return redirect(url_for("auth.login"))
    
    if request.method == "POST":
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")
        
        if not password:
            flash("Password is required", "error")
            return render_template("auth/reset_password.html", token=token)
        
        if password != confirm:
            flash("Passwords don't match", "error")
            return render_template("auth/reset_password.html", token=token)
        
        if len(password) < 6:
            flash("Password must be at least 6 characters", "error")
            return render_template("auth/reset_password.html", token=token)
        
        success, msg = User.reset_password(token, password)
        if success:
            logger.info(f"Password reset successful for user: {user.username}")
            flash("Password reset successful! Please login with your new password.", "success")
            return redirect(url_for("auth.login"))
        else:
            logger.error(f"Password reset failed: {msg}")
            flash(f"Error: {msg}", "error")
            return render_template("auth/reset_password.html", token=token)
    
    return render_template("auth/reset_password.html", token=token)

@auth.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    username = current_user.username
    logout_user()
    logger.info(f"User logged out: {username}")
    flash("Logged out successfully", "success")
    return redirect(url_for("home"))

@auth.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        current_user.energy_level = int(request.form.get("energy_level", 100))
        current_user.crowd_tolerance = int(request.form.get("crowd_tolerance", 50))
        
        if current_user.save_preferences():
            logger.info(f"Preferences updated: {current_user.username}")
            flash("Preferences saved", "success")
        else:
            flash("Error saving preferences", "error")
        
        return redirect(url_for("auth.profile"))
    
    trips = current_user.get_saved_trips()
    return render_template("auth/profile.html", trips=trips)
