# pages/weather_dashboard.py
import streamlit as st
from config import logger, CACHE_TTL

@st.cache_data(ttl=CACHE_TTL['weather_current'])
def get_cached_weather(weather_api, lat, lon):
    """Cached weather data"""
    return weather_api.get_current_weather(lat, lon)

def weather_dashboard_page(weather_api, weather_locations):
    """Weather dashboard page"""
    try:
        st.title("🌤️ Weather Dashboard")
        
        if not weather_api.has_api_key():
            st.warning("Weather API key not configured")
            return
        
        if not weather_locations:
            st.info("No weather locations configured")
            return
        
        for loc in weather_locations:
            weather = get_cached_weather(weather_api, loc['latitude'], loc['longitude'])
            if weather:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Location", loc['name'])
                with col2:
                    st.metric("Temperature", f"{weather.get('main', {}).get('temp', 'N/A')}°C")
                with col3:
                    st.metric("Humidity", f"{weather.get('main', {}).get('humidity', 'N/A')}%")
    
    except Exception as e:
        logger.error(f"Weather dashboard error: {e}")
        st.error("Error loading weather data")
