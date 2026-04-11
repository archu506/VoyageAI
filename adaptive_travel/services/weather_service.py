"""
Weather Service for Real-Time Travel Planning

Fetches current weather data for Jaipur from OpenWeatherMap API.
Implements graceful fallback to mock data if API unavailable.

Usage:
    from services.weather_service import WeatherService
    
    service = WeatherService()
    weather = service.fetch_weather()
    
    # Returns:
    # {
    #     "temperature": 28.5,
    #     "condition": "Clear sky",
    #     "is_raining": False,
    #     "humidity": 60,
    #     "source": "openweathermap"  or "fallback"
    # }
"""

import os
import requests
from typing import Dict, Any
from datetime import datetime


class WeatherService:
    """
    Fetches real-time weather data for Jaipur using OpenWeatherMap API.
    
    Falls back to mock data if:
    - API key not provided
    - Network unavailable
    - API returns error
    """
    
    # OpenWeatherMap configuration
    API_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    CITY = "Jaipur"
    COUNTRY_CODE = "IN"
    TIMEOUT = 5  # seconds
    
    # Mock data fallback (used when API unavailable)
    DEFAULT_MOCK_WEATHER = {
        "temperature": 28.0,
        "condition": "Partly Cloudy",
        "is_raining": False,
        "humidity": 65,
        "source": "fallback"
    }
    
    def __init__(self):
        """Initialize weather service with API key from environment"""
        self.api_key = os.getenv('WEATHER_API_KEY')
        self.last_fetch = None
        self.cached_weather = None
    
    def fetch_weather(self) -> Dict[str, Any]:
        """
        Fetch current weather for Jaipur from OpenWeatherMap API.
        
        Returns:
            Dictionary containing:
            - temperature: float (Celsius)
            - condition: string (e.g., "Clear", "Rainy")
            - is_raining: boolean
            - humidity: int (0-100)
            - source: "openweathermap" or "fallback"
            
        Gracefully falls back to mock data if API fails.
        """
        # If no API key, use mock
        if not self.api_key:
            return self._get_mock_weather("No API key configured")
        
        try:
            # Fetch from OpenWeatherMap API
            weather_data = self._fetch_from_api()
            self.cached_weather = weather_data
            self.last_fetch = datetime.now()
            return weather_data
            
        except requests.exceptions.RequestException as e:
            return self._get_mock_weather(f"Network error: {str(e)}")
        except ValueError as e:
            return self._get_mock_weather(f"Invalid API response: {str(e)}")
        except Exception as e:
            return self._get_mock_weather(f"Unexpected error: {str(e)}")
    
    def _fetch_from_api(self) -> Dict[str, Any]:
        """
        Internal method to fetch from OpenWeatherMap API.
        
        Returns:
            Weather dictionary from API
            
        Raises:
            requests.exceptions.RequestException: Network error
            ValueError: Invalid API response
        """
        params = {
            'q': f"{self.CITY},{self.COUNTRY_CODE}",
            'appid': self.api_key,
            'units': 'metric'  # Celsius
        }
        
        # Make API request
        response = requests.get(
            self.API_BASE_URL,
            params=params,
            timeout=self.TIMEOUT
        )
        
        # Check for HTTP errors
        if response.status_code == 401:
            raise ValueError("Invalid API key")
        elif response.status_code == 404:
            raise ValueError("City not found")
        elif response.status_code != 200:
            raise ValueError(f"API returned status {response.status_code}")
        
        # Parse JSON response
        data = response.json()
        
        # Extract weather information
        if 'main' not in data or 'weather' not in data:
            raise ValueError("Missing required fields in API response")
        
        temperature = float(data['main'].get('temp', 25.0))
        humidity = int(data['main'].get('humidity', 50))
        
        # Parse weather condition
        weather_list = data.get('weather', [])
        if not weather_list:
            condition = "Unknown"
            is_raining = False
        else:
            main_condition = weather_list[0].get('main', 'Unknown').lower()
            description = weather_list[0].get('description', 'Unknown')
            condition = f"{main_condition.title()} - {description.title()}"
            
            # Determine if raining
            is_raining = main_condition in ['rain', 'drizzle', 'thunderstorm']
        
        return {
            "temperature": round(temperature, 1),
            "condition": condition,
            "is_raining": is_raining,
            "humidity": humidity,
            "source": "openweathermap"
        }
    
    def _get_mock_weather(self, reason: str = "") -> Dict[str, Any]:
        """
        Return mock weather data with fallback indicator.
        
        Args:
            reason: Reason for fallback (logged for debugging)
            
        Returns:
            Mock weather dictionary with source="fallback"
        """
        mock = self.DEFAULT_MOCK_WEATHER.copy()
        
        if reason:
            # Vary mock data slightly based on time for realism
            hour = datetime.now().hour
            if 6 <= hour < 12:
                mock["temperature"] = 32.0
                mock["condition"] = "Sunny"
                mock["humidity"] = 55
            elif 12 <= hour < 17:
                mock["temperature"] = 35.0
                mock["condition"] = "Hot & Humid"
                mock["humidity"] = 70
            elif 17 <= hour < 20:
                mock["temperature"] = 28.0
                mock["condition"] = "Partly Cloudy"
                mock["humidity"] = 65
            else:
                mock["temperature"] = 24.0
                mock["condition"] = "Cool Night"
                mock["humidity"] = 75
        
        return mock
    
    def get_cached_weather(self) -> Dict[str, Any]:
        """
        Return cached weather if available.
        
        Returns:
            Cached weather dictionary or mock if not cached
        """
        if self.cached_weather and self.last_fetch:
            # Return cached data (cache for 10 minutes)
            import time
            elapsed = (datetime.now() - self.last_fetch).total_seconds()
            if elapsed < 600:  # 10 minutes
                return self.cached_weather
        
        # Fetch fresh data
        return self.fetch_weather()


# Module-level function for convenient access
_weather_service = None


def get_weather_service() -> WeatherService:
    """
    Get or create the global weather service instance.
    
    Returns:
        WeatherService instance
    """
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService()
    return _weather_service


def fetch_weather() -> Dict[str, Any]:
    """
    Convenience function to fetch weather.
    
    Returns:
        Weather dictionary from OpenWeatherMap or fallback
    """
    return get_weather_service().fetch_weather()
