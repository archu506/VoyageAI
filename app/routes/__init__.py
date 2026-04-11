"""
Main routes blueprint for home page and search functionality.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.forms import SearchForm
from app.services import CityService
from app.models import City

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page showing featured cities."""
    page = request.args.get('page', 1, type=int)
    
    # Get all cities with pagination
    cities_pagination = City.query.paginate(page=page, per_page=10)
    
    return render_template(
        'main/index.html',
        cities=cities_pagination
    )


@main_bp.route('/search', methods=['GET', 'POST'])
def search():
    """Search for cities."""
    form = SearchForm()
    results = None
    query = None
    
    if form.validate_on_submit():
        query = form.search_query.data.strip()
        
        if not query:
            flash('Please enter a search term.', 'warning')
        else:
            page = request.args.get('page', 1, type=int)
            results = CityService.search_cities(query, page=page, per_page=10)
            
            if not results.items:
                flash(f'No cities found matching "{query}".', 'info')
    
    return render_template(
        'main/search.html',
        form=form,
        results=results,
        query=query
    )


@main_bp.route('/about')
def about():
    """About page."""
    return render_template('main/about.html')


@main_bp.route('/featured')
def featured():
    """Featured destinations page."""
    # Get cities with most reviews for "featured" status
    cities = City.query.limit(6).all()
    return render_template('main/featured.html', cities=cities)


@main_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('errors/404.html'), 404


@main_bp.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return render_template('errors/500.html'), 500
