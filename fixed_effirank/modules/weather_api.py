# modules/weather_api.py
"""
Weather API Module
Handles all OpenWeather API interactions
Enhanced with caching, rate limiting, and retry logic
"""

import requests
import time
from collections import deque
from datetime import datetime, timedelta
from config import API_TIMEOUT, API_MAX_RETRIES, RATE_LIMIT_CALLS, RATE_LIMIT_WINDOW, logger

class RateLimiter:
    """Simple rate limiter for API calls"""
    def __init__(self, max_calls, window_seconds):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.calls = deque()
    
    def can_proceed(self):
        """Check if we can make a call"""
        now = time.time()
        # Remove old calls outside window
        while self.calls and self.calls[0] < now - self.window_seconds:
            self.calls.popleft()
        
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False
    
    def wait_time(self):
        """Get wait time until next call is allowed"""
        if not self.calls:
            return 0
        oldest_call = self.calls[0]
        wait_until = oldest_call + self.window_seconds
        return max(0, wait_until - time.time())

class WeatherAPI:
    """Manage OpenWeather API calls"""
    
    def __init__(self, api_key=None):
        """
        Initialize Weather API manager
        
        Args:
            api_key: OpenWeather API key
        """
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.rate_limiter = RateLimiter(RATE_LIMIT_CALLS, RATE_LIMIT_WINDOW)
        self.cache = {}
        logger.info("Weather API initialized")
    
    def has_api_key(self):
        """Check if API key is configured"""
        return self.api_key is not None
    
    def _make_api_call(self, url, params):
        """
        Make API call with retry logic and rate limiting
        
        Args:
            url: API endpoint URL
            params: Request parameters
            
        Returns:
            Response JSON or None
        """
        # Rate limiting
        if not self.rate_limiter.can_proceed():
            wait_time = self.rate_limiter.wait_time()
            logger.warning(f"Rate limit reached, waiting {wait_time:.1f}s")
            time.sleep(wait_time)
        
        for attempt in range(API_MAX_RETRIES):
            try:
                response = requests.get(url, params=params, timeout=API_TIMEOUT)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout:
                logger.warning(f"API timeout on attempt {attempt + 1}")
                if attempt < API_MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed: {e}")
                if attempt < API_MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
                else:
                    return None
        return None
    
    def get_current_weather(self, lat, lon):
        """
        Fetch current weather data with caching
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Weather data dictionary or None
        """
        if not self.api_key:
            return None
        
        # Check cache
        cache_key = f"current_{lat}_{lon}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < timedelta(minutes=10):
                logger.debug(f"Using cached weather data for {lat}, {lon}")
                return cached_data
        
        url = f"{self.base_url}/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        data = self._make_api_call(url, params)
        if data:
            self.cache[cache_key] = (data, datetime.now())
        
        return data
    
    def get_forecast(self, lat, lon):
        """
        Fetch 5-day forecast with caching
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Forecast data dictionary or None
        """
        if not self.api_key:
            return None
        
        # Check cache
        cache_key = f"forecast_{lat}_{lon}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < timedelta(minutes=30):
                logger.debug(f"Using cached forecast data for {lat}, {lon}")
                return cached_data
        
        url = f"{self.base_url}/forecast"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        data = self._make_api_call(url, params)
        if data:
            self.cache[cache_key] = (data, datetime.now())
        
        return data
    
    def get_weather_for_location(self, location_name, weather_locations):
        """
        Get weather data for a specific location by name
        
        Args:
            location_name: Name of the location
            weather_locations: List of weather location dictionaries
            
        Returns:
            Weather data or None
        """
        if not weather_locations or not self.api_key:
            return None
        
        # Find matching weather location
        weather_loc = next(
            (loc for loc in weather_locations 
             if loc['name'].upper() in location_name.upper() 
             or location_name.upper() in loc['name'].upper()),
            None
        )
        
        if not weather_loc:
            return None
        
        return self.get_current_weather(weather_loc['latitude'], weather_loc['longitude'])
    
    @staticmethod
    def get_weather_icon(weather_desc):
        """
        Get emoji icon for weather description
        
        Args:
            weather_desc: Weather description string
            
        Returns:
            Emoji string
        """
        weather_desc = weather_desc.lower()
        
        if 'clear' in weather_desc:
            return "☀️"
        elif 'cloud' in weather_desc:
            return "☁️"
        elif 'rain' in weather_desc or 'drizzle' in weather_desc:
            return "🌧️"
        elif 'thunder' in weather_desc or 'storm' in weather_desc:
            return "⛈️"
        elif 'snow' in weather_desc:
            return "❄️"
        elif 'mist' in weather_desc or 'fog' in weather_desc:
            return "🌫️"
        else:
            return "🌤️"
