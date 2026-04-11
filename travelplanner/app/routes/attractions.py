"""
Attractions blueprint for viewing and searching attractions.
"""

import logging
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models import City, Attraction, Review
from app.services import AttractionService, CityService, WeatherService


logger = logging.getLogger(__name__)
attractions_bp = Blueprint('attractions', __name__)


@attractions_bp.route('/')
def list_attractions():
    """
    List all attractions with filtering and pagination.
    
    Query parameters:
        - city_id: Filter by city
        - category: Filter by category (heritage, adventure, cultural)
        - sort: Sort order (recent, rating)
        - page: Page number
    """
    try:
        page = request.args.get('page', 1, type=int)
        city_id = request.args.get('city_id', type=int)
        category = request.args.get('category', type=str)
        sort = request.args.get('sort', 'rating', type=str)
        
        query = Attraction.query
        
        if city_id:
            query = query.filter_by(city_id=city_id)
        
        if category:
            query = query.filter_by(category=category)
        
        # Sort
        if sort == 'recent':
            query = query.order_by(Attraction.created_at.desc())
        else:  # rating
            # Sort by average rating (requires aggregation in post-processing)
            pass
        
        pagination = query.paginate(page=page, per_page=12, error_out=False)
        
        # Get unique categories for filter dropdown
        categories = db.session.query(Attraction.category).distinct().all()
        categories = [c[0] for c in categories if c[0]]
        
        # Get cities for filter dropdown
        cities = City.query.all()
        
        attractions_data = []
        for attr in pagination.items:
            data = attr.to_dict()
            attractions_data.append(data)
        
        return render_template(
            'attractions/list.html',
            attractions=attractions_data,
            pagination=pagination,
            cities=cities,
            categories=categories,
            selected_city=city_id,
            selected_category=category
        )
    
    except Exception as e:
        logger.error(f'Error listing attractions: {str(e)}')
        return render_template('error.html',
                             error='Failed to load attractions',
                             status_code=500), 500


@attractions_bp.route('/<int:attraction_id>')
def view_attraction(attraction_id: int):
    """
    View detailed information about an attraction.
    
    Args:
        attraction_id: ID of the attraction
    """
    try:
        attraction = Attraction.query.get(attraction_id)
        
        if not attraction:
            logger.warning(f'Attraction not found: {attraction_id}')
            return render_template('error.html',
                                 error='Attraction not found',
                                 status_code=404), 404
        
        # Get city details
        city = City.query.get(attraction.city_id)
        
        # Get weather for the city
        weather = WeatherService.get_weather(city.name) if city else None
        
        # Get paginated reviews
        page = request.args.get('page', 1, type=int)
        reviews_page = Review.query.filter_by(attraction_id=attraction_id).paginate(
            page=page,
            per_page=5,
            error_out=False
        )
        
        attraction_data = attraction.to_dict()
        
        return render_template(
            'attractions/detail.html',
            attraction=attraction_data,
            city=city,
            weather=weather,
            reviews=reviews_page.items,
            reviews_page=reviews_page,
            average_rating=attraction.get_average_rating(),
            review_count=attraction.get_review_count()
        )
    
    except Exception as e:
        logger.error(f'Error viewing attraction {attraction_id}: {str(e)}')
        return render_template('error.html',
                             error='Failed to load attraction',
                             status_code=500), 500


@attractions_bp.route('/search', methods=['GET'])
def search():
    """
    Search attractions by name or city.
    
    Query parameters:
        - q: Search query
        - type: Search type (attractions, cities)
    """
    try:
        query = request.args.get('q', '', type=str).strip()
        search_type = request.args.get('type', 'attractions', type=str)
        page = request.args.get('page', 1, type=int)
        
        if not query or len(query) < 2:
            return render_template('attractions/search.html',
                                 results=[],
                                 query=query,
                                 search_type=search_type)
        
        if search_type == 'cities':
            pagination = CityService.search_cities(query, page=page, per_page=12)
            results = [city.to_dict() for city in pagination.items]
        else:
            # Search attractions
            search_term = f'%{query}%'
            pagination = Attraction.query.filter(
                db.or_(
                    Attraction.name.ilike(search_term),
                    Attraction.description.ilike(search_term)
                )
            ).paginate(page=page, per_page=12, error_out=False)
            
            results = [attr.to_dict() for attr in pagination.items]
        
        return render_template(
            'attractions/search.html',
            results=results,
            pagination=pagination,
            query=query,
            search_type=search_type
        )
    
    except Exception as e:
        logger.error(f'Error searching: {str(e)}')
        return render_template('error.html',
                             error='Search failed',
                             status_code=500), 500


@attractions_bp.route('/city/<int:city_id>')
def city_attractions(city_id: int):
    """
    View all attractions in a specific city.
    
    Args:
        city_id: ID of the city
    """
    try:
        city = City.query.get(city_id)
        
        if not city:
            return render_template('error.html',
                                 error='City not found',
                                 status_code=404), 404
        
        # Get attractions with optional filtering
        category = request.args.get('category', type=str)
        min_rating = request.args.get('min_rating', type=float)
        
        attractions_data = AttractionService.get_attractions_by_city(
            city_id=city_id,
            category=category,
            min_rating=min_rating
        )
        
        # Get weather
        weather = WeatherService.get_weather(city.name)
        
        # Get unique categories for filter
        categories = db.session.query(Attraction.category).filter_by(
            city_id=city_id
        ).distinct().all()
        categories = [c[0] for c in categories if c[0]]
        
        city_data = city.to_dict()
        
        return render_template(
            'attractions/city.html',
            city=city_data,
            attractions=attractions_data,
            weather=weather,
            categories=categories,
            selected_category=category
        )
    
    except Exception as e:
        logger.error(f'Error viewing city {city_id}: {str(e)}')
        return render_template('error.html',
                             error='Failed to load city',
                             status_code=500), 500


@attractions_bp.route('/api/attractions')
def api_attractions():
    """
    API endpoint for getting attractions as JSON.
    
    Query parameters:
        - city_id: Filter by city
        - category: Filter by category
    """
    try:
        city_id = request.args.get('city_id', type=int)
        category = request.args.get('category', type=str)
        
        query = Attraction.query
        
        if city_id:
            query = query.filter_by(city_id=city_id)
        
        if category:
            query = query.filter_by(category=category)
        
        attractions = query.all()
        
        return jsonify([attr.to_dict() for attr in attractions]), 200
    
    except Exception as e:
        logger.error(f'API attractions error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500


# Fix missing import
from app.extensions import db
