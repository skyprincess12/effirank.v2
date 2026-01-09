# utils/data_persistence.py
"""
Data Persistence Utilities
Handle local JSON file storage and retrieval
"""

import json
import pandas as pd
from datetime import datetime
from config import LOCATIONS_FILE, HISTORY_FILE, SETTINGS_FILE, DEFAULT_LOCATIONS

class DataPersistence:
    """Manage local data persistence"""
    
    @staticmethod
    def save_locations_data(locations_data):
        """
        Save locations data to JSON file
        
        Args:
            locations_data: Dictionary of location data
        """
        try:
            with open(LOCATIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(locations_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving locations data: {e}")
    
    @staticmethod
    def load_locations_data():
        """
        Load locations data from JSON file
        
        Returns:
            Dictionary of location data
        """
        try:
            with open(LOCATIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return DEFAULT_LOCATIONS.copy()
    
    @staticmethod
    def save_app_settings(settings):
        """
        Save app settings to JSON file
        
        Args:
            settings: Dictionary of settings
        """
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    @staticmethod
    def load_app_settings():
        """
        Load app settings from JSON file
        
        Returns:
            Dictionary of settings or None
        """
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # Convert date string back to date object
            if 'current_date' in settings:
                settings['current_date'] = datetime.fromisoformat(settings['current_date']).date()
            
            return settings
        except Exception:
            return None
    
    @staticmethod
    def save_history_snapshots(snapshots):
        """
        Save history snapshots to JSON file
        
        Args:
            snapshots: List of snapshot dictionaries
        """
        try:
            serializable_snapshots = []
            for snap in snapshots:
                serializable_snap = snap.copy()
                
                # Convert DataFrames to dict
                if 'rankings_df' in serializable_snap and isinstance(serializable_snap['rankings_df'], pd.DataFrame):
                    serializable_snap['rankings_df'] = serializable_snap['rankings_df'].to_dict('records')
                
                if 'analysis_df' in serializable_snap and isinstance(serializable_snap['analysis_df'], pd.DataFrame):
                    serializable_snap['analysis_df'] = serializable_snap['analysis_df'].to_dict('records')
                
                serializable_snapshots.append(serializable_snap)
            
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(serializable_snapshots, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    @staticmethod
    def load_history_snapshots():
        """
        Load history snapshots from JSON file
        
        Returns:
            List of snapshot dictionaries
        """
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                snapshots = json.load(f)
            
            # Convert lists back to DataFrames
            for snap in snapshots:
                if 'rankings_df' in snap and isinstance(snap['rankings_df'], list):
                    snap['rankings_df'] = pd.DataFrame(snap['rankings_df'])
                
                if 'analysis_df' in snap and isinstance(snap['analysis_df'], list):
                    snap['analysis_df'] = pd.DataFrame(snap['analysis_df'])
            
            return snapshots
        except Exception:
            return []
