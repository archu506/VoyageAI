"""
Reviews blueprint for review CRUD operations.
"""

import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Review, Attraction, User
from app.forms import ReviewForm
from app.services import ReviewService


logger = logging.getLogger(__name__)
reviews_bp = Blueprint('reviews', __name__)


@reviews_bp.route('/add/<int:attraction_id>', methods=['GET', 'POST'])
@login_required
def add_review(attraction_id: int):
    """
    Add a new review for an attraction.
    
    Args:
        attraction_id: ID of the attraction to review
    """
    try:
        # Verify attraction exists
        attraction = Attraction.query.get(attraction_id)
        if not attraction:
            flash('Attraction not found', 'danger')
            return redirect(url_for('main.index'))
        
        # Check if user already reviewed this attraction
        existing_review = Review.query.filter_by(
            user_id=current_user.id,
            attraction_id=attraction_id
        ).first()
        
        if existing_review:
            flash('You have already reviewed this attraction', 'warning')
            return redirect(url_for('attractions.view_attraction',
                                   attraction_id=attraction_id))
        
        form = ReviewForm()
        
        if form.validate_on_submit():
            review, error = ReviewService.create_review(
                user_id=current_user.id,
                attraction_id=attraction_id,
                rating=form.rating.data,
                title=form.title.data,
                comment=form.comment.data
            )
            
            if error:
                flash(error, 'danger')
            else:
                logger.info(f'Review created: {review.id}')
                flash('Your review has been posted!', 'success')
                return redirect(url_for('attractions.view_attraction',
                                       attraction_id=attraction_id))
        
        return render_template('reviews/add.html',
                             form=form,
                             attraction=attraction)
    
    except Exception as e:
        logger.error(f'Error adding review: {str(e)}')
        flash('An error occurred while adding your review', 'danger')
        return redirect(url_for('attractions.view_attraction',
                               attraction_id=attraction_id))


@reviews_bp.route('/<int:review_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_review(review_id: int):
    """
    Edit an existing review.
    
    Args:
        review_id: ID of the review to edit
    """
    try:
        review = Review.query.get(review_id)
        
        if not review:
            flash('Review not found', 'danger')
            return redirect(url_for('main.index'))
        
        # Check authorization
        if review.user_id != current_user.id:
            flash('You do not have permission to edit this review', 'danger')
            return redirect(url_for('attractions.view_attraction',
                                   attraction_id=review.attraction_id))
        
        form = ReviewForm()
        
        if form.validate_on_submit():
            updated_review, error = ReviewService.update_review(
                review_id=review_id,
                user_id=current_user.id,
                rating=form.rating.data,
                title=form.title.data,
                comment=form.comment.data
            )
            
            if error:
                flash(error, 'danger')
            else:
                logger.info(f'Review updated: {review_id}')
                flash('Your review has been updated!', 'success')
                return redirect(url_for('attractions.view_attraction',
                                       attraction_id=review.attraction_id))
        
        elif request.method == 'GET':
            form.title.data = review.title
            form.rating.data = review.rating
            form.comment.data = review.comment
        
        return render_template('reviews/edit.html',
                             form=form,
                             review=review)
    
    except Exception as e:
        logger.error(f'Error editing review {review_id}: {str(e)}')
        flash('An error occurred while editing your review', 'danger')
        return redirect(url_for('main.index'))


@reviews_bp.route('/<int:review_id>/delete', methods=['POST'])
@login_required
def delete_review(review_id: int):
    """
    Delete a review.
    
    Args:
        review_id: ID of the review to delete
    """
    try:
        review = Review.query.get(review_id)
        
        if not review:
            return jsonify({'error': 'Review not found'}), 404
        
        # Check authorization
        if review.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        attraction_id = review.attraction_id
        
        success, error = ReviewService.delete_review(review_id, current_user.id)
        
        if error:
            return jsonify({'error': error}), 400
        
        logger.info(f'Review deleted: {review_id}')
        
        # Return based on request type
        if request.is_json:
            return jsonify({'success': True}), 200
        
        flash('Review deleted successfully', 'success')
        return redirect(url_for('attractions.view_attraction',
                               attraction_id=attraction_id))
    
    except Exception as e:
        logger.error(f'Error deleting review {review_id}: {str(e)}')
        
        if request.is_json:
            return jsonify({'error': 'Internal server error'}), 500
        
        flash('An error occurred while deleting your review', 'danger')
        return redirect(url_for('main.index'))


@reviews_bp.route('/user/<int:user_id>')
def user_reviews(user_id: int):
    """
    View all reviews by a specific user.
    
    Args:
        user_id: ID of the user
    """
    try:
        user = User.query.get(user_id)
        
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('main.index'))
        
        page = request.args.get('page', 1, type=int)
        
        reviews_page = Review.query.filter_by(user_id=user_id).order_by(
            Review.created_at.desc()
        ).paginate(page=page, per_page=10, error_out=False)
        
        reviews_data = []
        for review in reviews_page.items:
            data = review.to_dict()
            # Add attraction info
            attraction = Attraction.query.get(review.attraction_id)
            if attraction:
                data['attraction'] = attraction.to_dict()
            reviews_data.append(data)
        
        return render_template('reviews/user_reviews.html',
                             user=user,
                             reviews=reviews_data,
                             pagination=reviews_page)
    
    except Exception as e:
        logger.error(f'Error viewing user reviews: {str(e)}')
        flash('Failed to load reviews', 'danger')
        return redirect(url_for('main.index'))


@reviews_bp.route('/api/attraction/<int:attraction_id>')
def api_attraction_reviews(attraction_id: int):
    """
    API endpoint for getting reviews for an attraction.
    
    Query parameters:
        - page: Page number
        - per_page: Items per page
        - sort_by: Sort order (recent, highest, lowest)
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)
        sort_by = request.args.get('sort_by', 'recent', type=str)
        
        reviews_page = ReviewService.get_reviews_by_attraction(
            attraction_id=attraction_id,
            page=page,
            per_page=per_page,
            sort_by=sort_by
        )
        
        reviews_data = [review.to_dict() for review in reviews_page.items]
        
        return jsonify({
            'reviews': reviews_data,
            'pagination': {
                'page': reviews_page.page,
                'per_page': reviews_page.per_page,
                'total': reviews_page.total,
                'pages': reviews_page.pages
            }
        }), 200
    
    except Exception as e:
        logger.error(f'API reviews error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500
