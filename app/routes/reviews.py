"""
Reviews management routes blueprint.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models import db, Place, Review
from app.forms import ReviewForm, UpdateReviewForm
from app.services import ReviewService

reviews_bp = Blueprint('reviews', __name__, url_prefix='/reviews')


@reviews_bp.route('/place/<int:place_id>')
def place_reviews(place_id):
    """View all reviews for a specific place."""
    place = Place.query.get_or_404(place_id)
    page = request.args.get('page', 1, type=int)
    min_rating = request.args.get('min_rating', None, type=float)
    sort_by = request.args.get('sort_by', 'recent')
    
    # Validate sort_by parameter
    if sort_by not in ['recent', 'highest', 'lowest']:
        sort_by = 'recent'
    
    reviews_pagination = ReviewService.get_reviews_by_place(
        place_id,
        page=page,
        per_page=5,
        min_rating=min_rating,
        sort_by=sort_by
    )
    
    user_review = None
    if current_user.is_authenticated:
        user_review = Review.query.filter_by(
            user_id=current_user.id,
            place_id=place_id
        ).first()
    
    return render_template(
        'reviews/place_reviews.html',
        place=place,
        reviews=reviews_pagination,
        user_review=user_review,
        min_rating=min_rating,
        sort_by=sort_by
    )


@reviews_bp.route('/place/<int:place_id>/add', methods=['GET', 'POST'])
@login_required
def add_review(place_id):
    """Add a new review for a place."""
    place = Place.query.get_or_404(place_id)
    
    # Check if user already reviewed
    existing_review = Review.query.filter_by(
        user_id=current_user.id,
        place_id=place_id
    ).first()
    
    if existing_review:
        flash('You have already reviewed this place. Edit your existing review instead.', 'info')
        return redirect(url_for('reviews.edit_review', review_id=existing_review.id))
    
    form = ReviewForm()
    if form.validate_on_submit():
        review, error = ReviewService.create_review(
            user_id=current_user.id,
            place_id=place_id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        
        if error:
            flash(error, 'danger')
        else:
            flash('Your review has been posted successfully!', 'success')
            return redirect(url_for('reviews.place_reviews', place_id=place_id))
    
    return render_template(
        'reviews/add_review.html',
        form=form,
        place=place
    )


@reviews_bp.route('/<int:review_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    """Edit an existing review."""
    review = Review.query.get_or_404(review_id)
    
    # Authorization check
    if review.user_id != current_user.id:
        flash('You can only edit your own reviews.', 'danger')
        return redirect(url_for('reviews.place_reviews', place_id=review.place_id))
    
    form = UpdateReviewForm()
    if form.validate_on_submit():
        updated_review, error = ReviewService.update_review(
            review_id=review_id,
            user_id=current_user.id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        
        if error:
            flash(error, 'danger')
        else:
            flash('Your review has been updated successfully!', 'success')
            return redirect(url_for('reviews.place_reviews', place_id=review.place_id))
    
    elif request.method == 'GET':
        form.rating.data = review.rating
        form.comment.data = review.comment
    
    return render_template(
        'reviews/edit_review.html',
        form=form,
        review=review
    )


@reviews_bp.route('/<int:review_id>/delete', methods=['POST'])
@login_required
def delete_review(review_id):
    """Delete a review."""
    review = Review.query.get_or_404(review_id)
    place_id = review.place_id
    
    success, error = ReviewService.delete_review(review_id, current_user.id)
    
    if not success:
        flash(error, 'danger')
    else:
        flash('Your review has been deleted.', 'success')
    
    return redirect(url_for('reviews.place_reviews', place_id=place_id))


@reviews_bp.route('/api/place/<int:place_id>/stats')
def place_stats(place_id):
    """Get review statistics for a place (API endpoint)."""
    place = Place.query.get_or_404(place_id)
    
    return jsonify({
        'place_id': place.id,
        'place_name': place.name,
        'average_rating': place.get_average_rating(),
        'review_count': place.get_review_count(),
        'city_name': place.city.name
    })
