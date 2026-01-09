# utils/session_manager.py
"""
Session State Manager
Initialize and manage Streamlit session state
"""

import streamlit as st
from datetime import datetime
from utils.data_persistence import DataPersistence
from modules.database import DatabaseManager
from config import DEFAULT_COST_WEIGHT, DEFAULT_LKG_WEIGHT

class SessionManager:
    """Manage Streamlit session state"""
    
    @staticmethod
    def initialize_session(auth_manager, users, db_manager):
        """
        Initialize all session state variables
        
        Args:
            auth_manager: PersistentAuth instance
            users: Dictionary of valid users
            db_manager: DatabaseManager instance
        """
        # Initialize locations data
        if 'locations_data' not in st.session_state:
            st.session_state.locations_data = DataPersistence.load_locations_data()
        
        # Initialize history snapshots
        if 'history_snapshots' not in st.session_state:
            if db_manager and db_manager.is_connected():
                # Load from database
                db_history = db_manager.get_all_history()
                st.session_state.history_snapshots = SessionManager._process_db_history(db_history)
            else:
                # Load from local
                st.session_state.history_snapshots = DataPersistence.load_history_snapshots()
        
        # Initialize authentication
        if 'authenticated' not in st.session_state:
            is_authenticated, username = auth_manager.check_authentication(users)
            st.session_state.authenticated = is_authenticated
            if is_authenticated:
                st.session_state.username = username
                st.session_state.user_role = users[username].get('role', 'user')
        
        # Load app settings
        saved_settings = DataPersistence.load_app_settings()
        
        if saved_settings:
            if 'current_date' not in st.session_state:
                st.session_state.current_date = saved_settings.get('current_date', datetime.now().date())
            if 'current_week' not in st.session_state:
                st.session_state.current_week = saved_settings.get('current_week', 1)
            if 'cost_weight' not in st.session_state:
                st.session_state.cost_weight = saved_settings.get('cost_weight', DEFAULT_COST_WEIGHT)
            if 'lkg_weight' not in st.session_state:
                st.session_state.lkg_weight = saved_settings.get('lkg_weight', DEFAULT_LKG_WEIGHT)
        else:
            # Set defaults if no saved settings
            if 'current_date' not in st.session_state:
                st.session_state.current_date = datetime.now().date()
            
            if 'current_week' not in st.session_state:
                current_date = datetime.now()
                if current_date.month >= 10:
                    crop_year_start = datetime(current_date.year, 10, 1)
                else:
                    crop_year_start = datetime(current_date.year - 1, 10, 1)
                days_diff = (current_date - crop_year_start).days
                st.session_state.current_week = max(1, (days_diff // 7) + 1)
            
            if 'cost_weight' not in st.session_state:
                st.session_state.cost_weight = DEFAULT_COST_WEIGHT
            
            if 'lkg_weight' not in st.session_state:
                st.session_state.lkg_weight = DEFAULT_LKG_WEIGHT
    
    @staticmethod
    def _process_db_history(db_history):
        """
        Process database history into session format
        
        Args:
            db_history: List of history records from database
            
        Returns:
            List of processed history snapshots
        """
        import pandas as pd
        
        processed = []
        for record in db_history:
            try:
                snap = {
                    'timestamp': record.get('timestamp'),
                    'date': record.get('date'),
                    'week_number': record.get('week_number'),
                    'week_range': record.get('week_range'),
                    'rankings_df': pd.DataFrame(record.get('rankings_json', [])),
                    'analysis_df': pd.DataFrame(record.get('analysis_json', []))
                }
                processed.append(snap)
            except Exception:
                continue
        
        return processed
    
    @staticmethod
    def save_current_settings():
        """Save current session settings to file"""
        settings = {
            'current_date': st.session_state.current_date.isoformat(),
            'current_week': st.session_state.current_week,
            'cost_weight': st.session_state.get('cost_weight', DEFAULT_COST_WEIGHT),
            'lkg_weight': st.session_state.get('lkg_weight', DEFAULT_LKG_WEIGHT)
        }
        DataPersistence.save_app_settings(settings)
    
    @staticmethod
    def get_current_user_info():
        """
        Get current user information
        
        Returns:
            Dictionary with user info
        """
        return {
            'username': st.session_state.get('username', 'Unknown'),
            'role': st.session_state.get('user_role', 'user'),
            'authenticated': st.session_state.get('authenticated', False)
        }
