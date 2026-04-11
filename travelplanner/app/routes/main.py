"""
Main blueprint for core application routes.
Includes home page and health check endpoints.
"""

import logging
from flask import Blueprint, render_template, jsonify
from app.models import City, Attraction, Review
from app.services import CityService, WeatherService


logger = logging.getLogger(__name__)
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page with featured cities and attractions."""
    try:
        # Get featured cities with ratings
        cities = CityService.get_cities_with_rating(limit=6)
        
        return render_template('index.html', cities=cities)
    
    except Exception as e:
        logger.error(f'Error rendering home page: {str(e)}')
        return render_template('error.html', 
                             error='Failed to load home page',
                             status_code=500), 500


@main_bp.route('/about')
def about():
    """About page with application information."""
    try:
        # Get statistics
        city_count = City.query.count()
        attraction_count = Attraction.query.count()
        review_count = Review.query.count()
        
        stats = {
            'cities': city_count,
            'attractions': attraction_count,
            'reviews': review_count
        }
        
        return render_template('about.html', stats=stats)
    
    except Exception as e:
        logger.error(f'Error rendering about page: {str(e)}')
        return render_template('error.html',
                             error='Failed to load about page',
                             status_code=500), 500


@main_bp.route('/health')
def health_check():
    """
    Health check endpoint for monitoring.
    Returns application status and dependency health.
    
    Returns:
        JSON with status and component health
    """
    try:
        # Check database connectivity
        City.query.first()
        
        return jsonify({
            'status': 'healthy',
            'service': 'travel-planner',
            'database': 'connected'
        }), 200
    
    except Exception as e:
        logger.error(f'Health check failed: {str(e)}')
        return jsonify({
            'status': 'unhealthy',
            'service': 'travel-planner',
            'database': 'disconnected',
            'error': str(e)
        }), 503


@main_bp.route('/api/cities/<int:city_id>/weather')
def get_city_weather(city_id: int):
    """
    Get current weather for a city.
    
    Args:
        city_id: ID of the city
        
    Returns:
        JSON with weather data
    """
    try:
        city = City.query.get(city_id)
        if not city:
            return jsonify({'error': 'City not found'}), 404
        
        weather = WeatherService.get_weather(city.name)
        
        if weather is None:
            return jsonify({'error': 'Could not fetch weather'}), 503
        
        return jsonify({
            'city': city.name,
            'weather': weather
        }), 200
    
    except Exception as e:
        logger.error(f'Error fetching weather: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500


@main_bp.route('/api/stats')
def get_stats():
    """
    Get system statistics.
    
    Returns:
        JSON with application statistics
    """
    try:
        stats = {
            'total_cities': City.query.count(),
            'total_attractions': Attraction.query.count(),
            'total_reviews': Review.query.count(),
        }
        
        return jsonify(stats), 200
    
    except Exception as e:
        logger.error(f'Error fetching stats: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500
