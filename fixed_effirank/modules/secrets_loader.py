
# modules/secrets_loader.py
"""
Secrets and Credentials Loader
Handles loading all secrets from Streamlit secrets.toml
"""

import streamlit as st

class SecretsLoader:
    """Load and manage application secrets"""
    
    def __init__(self):
        self.users = None
        self.history_delete_passcode = None
        self.supabase_url = None
        self.supabase_key = None
        self.openweather_api_key = None
        self.weather_locations = None
        
        self.load_all_secrets()
    
    def load_all_secrets(self):
        """Load all secrets from Streamlit secrets"""
        try:
            # Load user accounts
            self.users = st.secrets.get("users", {})
            if not self.users:
                # Fallback to single user format
                username = st.secrets.get("USERNAME", "admin")
                password = st.secrets.get("PASSWORD", "admin")
                self.users = {
                    username: {
                        "password": password,
                        "role": "admin"
                    }
                }
            
            # Load system settings
            self.history_delete_passcode = st.secrets.get("HISTORY_DELETE_PASSCODE", "delete123")
            
            # Load Supabase credentials
            self.supabase_url = st.secrets.get("SUPABASE_URL")
            self.supabase_key = st.secrets.get("SUPABASE_KEY")
            
            # Load OpenWeather API
            self.openweather_api_key = st.secrets.get("openweather", {}).get("api_key")
            
            # Load weather locations
            self.weather_locations = st.secrets.get("weather_locations", [])
            
        except Exception as e:
            st.error(f"Error loading secrets: {e}")
            st.info("Using default credentials. Please configure .streamlit/secrets.toml")
            self._load_defaults()
    
    def _load_defaults(self):
        """Load default values if secrets loading fails"""
        self.users = {
            "admin": {"password": "admin", "role": "admin"},
            "user": {"password": "user", "role": "user"}
        }
        self.history_delete_passcode = "delete123"
        self.supabase_url = None
        self.supabase_key = None
        self.openweather_api_key = None
        self.weather_locations = []
    
    def get_users(self):
        """Get user accounts dictionary"""
        return self.users
    
    def get_history_passcode(self):
        """Get history delete passcode"""
        return self.history_delete_passcode
    
    def get_supabase_credentials(self):
        """Get Supabase URL and Key"""
        return self.supabase_url, self.supabase_key
    
    def get_openweather_api_key(self):
        """Get OpenWeather API key"""
        return self.openweather_api_key
    
    def get_weather_locations(self):
        """Get weather locations list"""
        return self.weather_locations
    
    def has_supabase(self):
        """Check if Supabase credentials are available"""
        return self.supabase_url is not None and self.supabase_key is not None
    
    def has_openweather(self):
        """Check if OpenWeather API key is available"""
        return self.openweather_api_key is not None

# Create global instance
secrets_loader = SecretsLoader()
