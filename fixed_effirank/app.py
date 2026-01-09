# app.py - Main Application Entry Point
"""
TLS Cost Input & Ranking System
Version 2.1.0 - Enhanced with Caching and Error Handling

Modular Architecture with Clean Imports
Each functionality is separated into its own module for easy troubleshooting.
"""

import streamlit as st
import sys
import traceback
from datetime import datetime

# Configuration and Constants
from config import PAGE_CONFIG, APP_CSS, APP_VERSION, logger

# Core Modules
from modules.secrets_loader import secrets_loader
from modules.auth import PersistentAuth
from modules.database import DatabaseManager
from modules.weather_api import WeatherAPI

# Utilities
from utils.session_manager import SessionManager
from utils.data_persistence import DataPersistence

# Pages
try:
    from pages.login import login_page
    from pages.cost_input import cost_input_page
    from pages.ranking import ranking_page
    from pages.cost_analysis import analysis_page
    from pages.weather_dashboard import weather_dashboard_page
    from pages.history import history_page
    from pages.account import account_page
except ImportError as e:
    logger.error(f"Failed to import pages: {e}")
    st.error(f"⚠️ Application Error: Missing page modules. Please contact support.")
    st.stop()

# =============================================================================
# INITIALIZE APP CONFIGURATION
# =============================================================================

try:
    # Configure Streamlit page
    st.set_page_config(**PAGE_CONFIG)
    
    # Apply custom CSS
    st.markdown(APP_CSS, unsafe_allow_html=True)
    
    logger.info(f"Application started - Version {APP_VERSION}")
    
except Exception as e:
    logger.error(f"Failed to configure app: {e}")
    st.error("Failed to initialize application. Please refresh the page.")
    st.stop()

# =============================================================================
# LOAD SECRETS AND INITIALIZE MANAGERS
# =============================================================================

@st.cache_resource
def initialize_managers():
    """
    Initialize all application managers with caching
    Auth manager now uses lazy initialization for CookieManager to avoid widget caching issues
    """
    try:
        # Get secrets
        users = secrets_loader.get_users()
        history_delete_passcode = secrets_loader.get_history_passcode()
        openweather_api_key = secrets_loader.get_openweather_api_key()
        weather_locations = secrets_loader.get_weather_locations()
        
        # Initialize auth manager (safe now with lazy cookie manager)
        auth_mgr = PersistentAuth()
        
        # Initialize database manager
        supabase_url, supabase_key = secrets_loader.get_supabase_credentials()
        db_mgr = DatabaseManager(supabase_url, supabase_key)
        
        # Initialize weather API
        weather_mgr = WeatherAPI(openweather_api_key)
        
        logger.info("All managers initialized successfully")
        
        return {
            'users': users,
            'history_passcode': history_delete_passcode,
            'openweather_key': openweather_api_key,
            'weather_locations': weather_locations,
            'auth_manager': auth_mgr,
            'db_manager': db_mgr,
            'weather_api': weather_mgr
        }
    
    except Exception as e:
        logger.error(f"Manager initialization failed: {e}\n{traceback.format_exc()}")
        st.error("⚠️ Failed to initialize application managers. Using fallback configuration.")
        
        # Return minimal fallback configuration
        return {
            'users': {'admin': {'password': 'admin', 'role': 'admin'}},
            'history_passcode': 'delete123',
            'openweather_key': None,
            'weather_locations': [],
            'auth_manager': PersistentAuth(),
            'db_manager': DatabaseManager(None, None),
            'weather_api': WeatherAPI(None)
        }

# Initialize managers (cached)
managers = initialize_managers()

USERS = managers['users']
HISTORY_DELETE_PASSCODE = managers['history_passcode']
OPENWEATHER_API_KEY = managers['openweather_key']
WEATHER_LOCATIONS = managers['weather_locations']
auth_manager = managers['auth_manager']
db_manager = managers['db_manager']
weather_api = managers['weather_api']

# =============================================================================
# INITIALIZE SESSION STATE
# =============================================================================

try:
    SessionManager.initialize_session(auth_manager, USERS, db_manager)
except Exception as e:
    logger.error(f"Session initialization error: {e}\n{traceback.format_exc()}")
    st.warning("⚠️ Session initialization had issues. Some features may not work correctly.")

# =============================================================================
# ERROR BOUNDARY WRAPPER
# =============================================================================

def error_boundary(page_function, *args, **kwargs):
    """
    Wraps page functions with error handling
    Prevents entire app from crashing if a page has an error
    """
    try:
        return page_function(*args, **kwargs)
    except Exception as e:
        logger.error(f"Page error in {page_function.__name__}: {e}\n{traceback.format_exc()}")
        
        st.error("⚠️ An error occurred on this page")
        
        with st.expander("Error Details (for debugging)"):
            st.code(f"""
Error Type: {type(e).__name__}
Error Message: {str(e)}

Traceback:
{traceback.format_exc()}
            """)
        
        st.info("Please try refreshing the page or contact support if the issue persists.")
        
        # Show a "Go Back" button
        if st.button("🔄 Refresh Page"):
            st.rerun()

# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    """Main application logic with error handling"""
    
    try:
        # Check authentication
        if not st.session_state.get('authenticated', False):
            error_boundary(login_page, auth_manager, USERS)
            return
        
        # Sidebar navigation
        st.sidebar.title("🧭 Navigation")
        st.sidebar.markdown("---")
        
        page = st.sidebar.radio(
            "Go to",
            [
                "Cost Input",
                "Efficiency Ranking",
                "Cost Analysis",
                "Weather Dashboard",
                "History",
                "Account"
            ]
        )
        
        # System status
        st.sidebar.markdown("---")
        st.sidebar.markdown("**System Status:**")
        
        # Database status
        if db_manager.is_connected():
            st.sidebar.success("🟢 Database Connected")
        else:
            st.sidebar.warning("🟡 Local Storage Only")
        
        # Weather API status
        if weather_api.has_api_key():
            st.sidebar.success("🟢 Weather API Active")
        else:
            st.sidebar.warning("🟡 Weather API Inactive")
        
        # User info
        st.sidebar.markdown("---")
        user_info = SessionManager.get_current_user_info()
        st.sidebar.markdown(f"**User:** {user_info['username']}")
        st.sidebar.markdown(f"**Role:** {user_info['role'].title()}")
        
        # Version info
        st.sidebar.markdown("---")
        st.sidebar.markdown(f'<div class="version-info">Version: {APP_VERSION}</div>', unsafe_allow_html=True)
        
        # Route to pages with error boundary
        if page == "Cost Input":
            error_boundary(cost_input_page, weather_api, WEATHER_LOCATIONS)
        
        elif page == "Efficiency Ranking":
            error_boundary(ranking_page, weather_api, WEATHER_LOCATIONS, db_manager)
        
        elif page == "Cost Analysis":
            error_boundary(analysis_page)
        
        elif page == "Weather Dashboard":
            error_boundary(weather_dashboard_page, weather_api, WEATHER_LOCATIONS)
        
        elif page == "History":
            error_boundary(history_page, db_manager, HISTORY_DELETE_PASSCODE)
        
        elif page == "Account":
            error_boundary(account_page, auth_manager)
    
    except Exception as e:
        logger.error(f"Critical application error: {e}\n{traceback.format_exc()}")
        st.error("⚠️ Critical Application Error")
        st.error("The application encountered a critical error. Please refresh the page.")
        
        with st.expander("Error Details"):
            st.code(traceback.format_exc())
        
        if st.button("🔄 Restart Application"):
            st.rerun()

# =============================================================================
# RUN APPLICATION
# =============================================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        st.stop()
    except Exception as e:
        logger.critical(f"Application crashed: {e}\n{traceback.format_exc()}")
        st.error("⚠️ Application crashed. Please restart.")
