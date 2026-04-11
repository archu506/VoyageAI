"""
Service layer for business logic.
Keeps routes clean and logic testable/reusable.
"""

import requests
import logging
from typing import Optional, Dict, List, Tuple
from datetime import datetime
from flask import current_app
from sqlalchemy import func, desc
from app.extensions import db
from app.models import User, City, Attraction, Review


logger = logging.getLogger(__name__)


class WeatherService:
    """Service for weather API operations."""
    
    @staticmethod
    def get_weather(city_name: str) -> Optional[Dict]:
        """
        Fetch current weather for a city from OpenWeatherMap API.
        
        Args:
            city_name: Name of the city
            
        Returns:
            Dictionary with weather data or None if request fails
            {
                'temperature': float,
                'description': str,
                'humidity': int,
                'feels_like': float,
                'wind_speed': float
            }
        """
        try:
            api_key = current_app.config.get('WEATHER_API_KEY')
            if not api_key:
                logger.warning('WEATHER_API_KEY not configured')
                return None
            
            params = {
                'q': city_name,
                'appid': api_key,
                'units': 'metric'
            }
            
            response = requests.get(
                current_app.config.get('WEATHER_API_BASE_URL'),
                params=params,
                timeout=current_app.config.get('WEATHER_API_TIMEOUT', 10)
            )
            
            if response.status_code != 200:
                logger.warning(f'Weather API error: {response.status_code}')
                return None
            
            data = response.json()
            
            return {
                'temperature': round(data['main']['temp'], 1),
                'description': data['weather'][0]['description'].title(),
                'humidity': data['main']['humidity'],
                'feels_like': round(data['main']['feels_like'], 1),
                'wind_speed': round(data['wind'].get('speed', 0), 1),
            }
        
        except requests.RequestException as e:
            logger.error(f'Weather API connection error: {str(e)}')
            return None
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f'Weather API data parsing error: {str(e)}')
            return None


class ReviewService:
    """Service for review management."""
    
    @staticmethod
    def create_review(
        user_id: int,
        attraction_id: int,
        rating: float,
        title: str,
        comment: str
    ) -> Tuple[Optional[Review], Optional[str]]:
        """
        Create a new review.
        
        Args:
            user_id: ID of reviewing user
            attraction_id: ID of attraction
            rating: Rating 1.0-5.0
            title: Review title
            comment: Review text
            
        Returns:
            Tuple of (Review object, error message or None)
        """
        try:
            # Check attraction exists
            attraction = Attraction.query.get(attraction_id)
            if not attraction:
                return None, 'Attraction not found'
            
            # Check for duplicate review
            existing = Review.query.filter_by(
                user_id=user_id,
                attraction_id=attraction_id
            ).first()
            
            if existing:
                return None, 'You have already reviewed this attraction'
            
            # Validate rating
            if not (1.0 <= rating <= 5.0):
                return None, 'Rating must be between 1.0 and 5.0'
            
            review = Review(
                user_id=user_id,
                attraction_id=attraction_id,
                rating=rating,
                title=title,
                comment=comment
            )
            
            if not review.validate_rating():
                return None, 'Invalid rating'
            
            db.session.add(review)
            db.session.commit()
            logger.info(f'Review created: {review.id}')
            
            return review, None
        
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error creating review: {str(e)}')
            return None, 'Failed to create review'
    
    @staticmethod
    def update_review(
        review_id: int,
        user_id: int,
        rating: float,
        title: str,
        comment: str
    ) -> Tuple[Optional[Review], Optional[str]]:
        """
        Update an existing review.
        
        Args:
            review_id: ID of review to update
            user_id: ID of user (for authorization)
            rating: New rating
            title: New title
            comment: New comment
            
        Returns:
            Tuple of (updated Review, error message or None)
        """
        try:
            review = Review.query.get(review_id)
            if not review:
                return None, 'Review not found'
            
            if review.user_id != user_id:
                return None, 'Not authorized to update this review'
            
            if not (1.0 <= rating <= 5.0):
                return None, 'Rating must be between 1.0 and 5.0'
            
            review.rating = rating
            review.title = title
            review.comment = comment
            review.updated_at = datetime.utcnow()
            
            db.session.commit()
            logger.info(f'Review updated: {review_id}')
            
            return review, None
        
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error updating review: {str(e)}')
            return None, 'Failed to update review'
    
    @staticmethod
    def delete_review(review_id: int, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Delete a review.
        
        Args:
            review_id: ID of review
            user_id: ID of user (for authorization)
            
        Returns:
            Tuple of (success bool, error message or None)
        """
        try:
            review = Review.query.get(review_id)
            if not review:
                return False, 'Review not found'
            
            if review.user_id != user_id:
                return False, 'Not authorized to delete this review'
            
            db.session.delete(review)
            db.session.commit()
            logger.info(f'Review deleted: {review_id}')
            
            return True, None
        
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error deleting review: {str(e)}')
            return False, 'Failed to delete review'
    
    @staticmethod
    def get_reviews_by_attraction(
        attraction_id: int,
        page: int = 1,
        per_page: int = 5,
        sort_by: str = 'recent'
    ):
        """
        Get paginated reviews for an attraction.
        
        Args:
            attraction_id: ID of attraction
            page: Page number
            per_page: Items per page
            sort_by: Sort order ('recent', 'highest', 'lowest')
            
        Returns:
            Pagination object with reviews
        """
        query = Review.query.filter_by(attraction_id=attraction_id)
        
        if sort_by == 'highest':
            query = query.order_by(desc(Review.rating))
        elif sort_by == 'lowest':
            query = query.order_by(Review.rating)
        else:  # recent
            query = query.order_by(desc(Review.created_at))
        
        return query.paginate(page=page, per_page=per_page, error_out=False)


class CityService:
    """Service for city operations."""
    
    @staticmethod
    def search_cities(
        query: str,
        page: int = 1,
        per_page: int = 10
    ):
        """
        Search cities by name or description.
        
        Args:
            query: Search term
            page: Page number
            per_page: Results per page
            
        Returns:
            Pagination object with cities
        """
        search_filter = db.or_(
            City.name.ilike(f'%{query}%'),
            City.description.ilike(f'%{query}%'),
            City.country.ilike(f'%{query}%')
        )
        
        return City.query.filter(search_filter).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    
    @staticmethod
    def get_cities_with_rating(
        limit: int = 10,
        sort_by: str = 'name'
    ) -> List[Dict]:
        """
        Get cities with average attraction ratings.
        
        Args:
            limit: Maximum cities to return
            sort_by: Sort order ('name' or 'rating')
            
        Returns:
            List of city dictionaries with rating info
        """
        cities = City.query.limit(limit).all()
        
        cities_data = []
        for city in cities:
            data = city.to_dict()
            if city.attractions:
                ratings = [attr.get_average_rating() for attr in city.attractions]
                data['average_rating'] = round(sum(ratings) / len(ratings), 2)
            else:
                data['average_rating'] = 0.0
            cities_data.append(data)
        
        if sort_by == 'rating':
            cities_data.sort(key=lambda x: x['average_rating'], reverse=True)
        else:
            cities_data.sort(key=lambda x: x['name'])
        
        return cities_data


class AttractionService:
    """Service for attraction operations."""
    
    @staticmethod
    def get_attractions_by_city(
        city_id: int,
        category: Optional[str] = None,
        min_rating: Optional[float] = None
    ) -> List[Dict]:
        """
        Get attractions for a city with optional filtering.
        
        Args:
            city_id: ID of city
            category: Optional category filter
            min_rating: Optional minimum rating filter
            
        Returns:
            List of attraction dictionaries
        """
        query = Attraction.query.filter_by(city_id=city_id)
        
        if category:
            query = query.filter_by(category=category)
        
        attractions = query.all()
        
        attractions_data = [attr.to_dict() for attr in attractions]
        
        if min_rating:
            attractions_data = [
                a for a in attractions_data
                if a['average_rating'] >= min_rating
            ]
        
        return sorted(attractions_data, key=lambda x: x['average_rating'], reverse=True)
