"""
Service layer for business logic.
Separates complex business operations from route handlers.
"""

import requests
from datetime import datetime
from sqlalchemy import func, desc
from flask import current_app
from app.models import db, User, City, Place, Review


class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API."""
    
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
    
    @staticmethod
    def get_weather(city_name):
        """
        Fetch current weather for a city.
        
        Args:
            city_name (str): Name of the city
            
        Returns:
            dict: Weather data or None if API fails
                {
                    'temperature': float,
                    'description': str,
                    'humidity': int,
                    'feels_like': float
                }
        """
        try:
            api_key = current_app.config.get('WEATHER_API_KEY')
            if not api_key:
                return None
            
            params = {
                'q': city_name,
                'appid': api_key,
                'units': 'metric'
            }
            
            timeout = current_app.config.get('WEATHER_API_TIMEOUT', 10)
            response = requests.get(
                WeatherService.BASE_URL,
                params=params,
                timeout=timeout
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            return {
                'temperature': data['main']['temp'],
                'description': data['weather'][0]['description'].title(),
                'humidity': data['main']['humidity'],
                'feels_like': data['main']['feels_like']
            }
        
        except requests.RequestException as e:
            current_app.logger.error(f'Weather API error: {str(e)}')
            return None
        except (KeyError, IndexError) as e:
            current_app.logger.error(f'Invalid weather data format: {str(e)}')
            return None


class ItineraryService:
    """Service for generating travel itineraries."""
    
    @staticmethod
    def get_or_create_city(city_name):
        """
        Get existing city or create new one if not found.
        
        Args:
            city_name (str): Name of the city
            
        Returns:
            City: City object or None if neither exists nor can be created
        """
        city = City.query.filter_by(name=city_name).first()
        if city:
            return city
        
        # City doesn't exist in database - this is checked against attractions.json
        return None
    
    @staticmethod
    def generate_itinerary(city_name, num_days):
        """
        Generate travel itinerary for a city.
        
        Args:
            city_name (str): Name of the city
            num_days (int): Number of days
            
        Returns:
            dict: Itinerary organized by day with places
                {
                    'Day 1': [place_name1, place_name2],
                    'Day 2': [place_name3, place_name4]
                }
        """
        city = City.query.filter_by(name=city_name).first()
        if not city:
            return None
        
        places = Place.query.filter_by(city_id=city.id).all()
        if not places:
            return {'Day 1': []}
        
        # Distribute places across days
        itinerary = {}
        places_per_day = max(1, len(places) // num_days)
        
        place_index = 0
        for day in range(1, num_days + 1):
            day_label = f'Day {day}'
            itinerary[day_label] = []
            
            for _ in range(places_per_day):
                if place_index < len(places):
                    itinerary[day_label].append(places[place_index])
                    place_index += 1
        
        # Add remaining places to last day
        if place_index < len(places):
            last_day = f'Day {num_days}'
            while place_index < len(places):
                itinerary[last_day].append(places[place_index])
                place_index += 1
        
        return itinerary


class ReviewService:
    """Service for managing reviews and ratings."""
    
    @staticmethod
    def create_review(user_id, place_id, rating, comment):
        """
        Create a new review.
        
        Args:
            user_id (int): ID of the user
            place_id (int): ID of the place
            rating (float): Rating from 1.0 to 5.0
            comment (str): Review comment
            
        Returns:
            tuple: (Review object, error message or None)
        """
        # Check if place exists
        place = Place.query.get(place_id)
        if not place:
            return None, 'Place not found'
        
        # Check for duplicate review by same user
        existing_review = Review.query.filter_by(
            user_id=user_id,
            place_id=place_id
        ).first()
        
        if existing_review:
            return None, 'You have already reviewed this place. Update your existing review instead.'
        
        review = Review(
            user_id=user_id,
            place_id=place_id,
            rating=rating,
            comment=comment
        )
        
        db.session.add(review)
        db.session.commit()
        
        return review, None
    
    @staticmethod
    def update_review(review_id, user_id, rating, comment):
        """
        Update an existing review.
        
        Args:
            review_id (int): ID of the review
            user_id (int): ID of the user (for authorization)
            rating (float): New rating
            comment (str): New comment
            
        Returns:
            tuple: (Review object, error message or None)
        """
        review = Review.query.get(review_id)
        if not review:
            return None, 'Review not found'
        
        if review.user_id != user_id:
            return None, 'You can only edit your own reviews'
        
        review.rating = rating
        review.comment = comment
        review.updated_at = datetime.utcnow()
        
        db.session.commit()
        return review, None
    
    @staticmethod
    def delete_review(review_id, user_id):
        """
        Delete a review.
        
        Args:
            review_id (int): ID of the review
            user_id (int): ID of the user (for authorization)
            
        Returns:
            tuple: (success: bool, error message or None)
        """
        review = Review.query.get(review_id)
        if not review:
            return False, 'Review not found'
        
        if review.user_id != user_id:
            return False, 'You can only delete your own reviews'
        
        db.session.delete(review)
        db.session.commit()
        return True, None
    
    @staticmethod
    def get_reviews_by_place(place_id, page=1, per_page=5, min_rating=None, sort_by='recent'):
        """
        Get paginated reviews for a place with optional filtering.
        
        Args:
            place_id (int): ID of the place
            page (int): Page number for pagination
            per_page (int): Reviews per page
            min_rating (float): Minimum rating filter
            sort_by (str): Sort order ('recent', 'highest', 'lowest')
            
        Returns:
            Pagination object with reviews
        """
        query = Review.query.filter_by(place_id=place_id)
        
        # Apply rating filter
        if min_rating:
            query = query.filter(Review.rating >= min_rating)
        
        # Apply sorting
        if sort_by == 'highest':
            query = query.order_by(desc(Review.rating))
        elif sort_by == 'lowest':
            query = query.order_by(Review.rating)
        else:  # recent
            query = query.order_by(desc(Review.created_at))
        
        return query.paginate(page=page, per_page=per_page)
    
    @staticmethod
    def get_user_reviews(user_id, page=1, per_page=5):
        """Get all reviews by a specific user."""
        return Review.query.filter_by(user_id=user_id).order_by(
            desc(Review.created_at)
        ).paginate(page=page, per_page=per_page)


class CityService:
    """Service for managing cities and places."""
    
    @staticmethod
    def search_cities(query, page=1, per_page=10):
        """
        Search for cities by name.
        
        Args:
            query (str): Search query
            page (int): Page number
            per_page (int): Results per page
            
        Returns:
            Pagination object with cities
        """
        return City.query.filter(
            City.name.ilike(f'%{query}%')
        ).paginate(page=page, per_page=per_page)
    
    @staticmethod
    def get_city_with_places(city_name):
        """
        Get city with all its places and review statistics.
        
        Returns:
            dict: City data with enriched place information
        """
        city = City.query.filter_by(name=city_name).first()
        if not city:
            return None
        
        places_data = []
        for place in city.places:
            places_data.append({
                'id': place.id,
                'name': place.name,
                'type': place.place_type,
                'description': place.description,
                'average_rating': place.get_average_rating(),
                'review_count': place.get_review_count()
            })
        
        return {
            'id': city.id,
            'name': city.name,
            'description': city.description,
            'country': city.country,
            'places': places_data
        }
