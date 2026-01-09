# modules/database.py
"""
Database Module
Handles Supabase database operations
"""

import streamlit as st
from supabase import create_client

class DatabaseManager:
    """Manage Supabase database connections and operations"""
    
    def __init__(self, supabase_url=None, supabase_key=None):
        """
        Initialize database manager
        
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase API key
        """
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.client = None
        
        if supabase_url and supabase_key:
            self.connect()
    
    def connect(self):
        """Connect to Supabase database"""
        if not self.supabase_url or not self.supabase_key:
            return None
        
        try:
            self.client = create_client(self.supabase_url, self.supabase_key)
            # Test connection
            test_result = self.client.table("history_snapshots").select("count", count="exact").limit(1).execute()
            return self.client
        except Exception as e:
            st.warning(f"Supabase connection failed: {e}. Using local storage only.")
            self.client = None
            return None
    
    def is_connected(self):
        """Check if database is connected"""
        return self.client is not None
    
    def insert_history(self, history_data):
        """
        Insert history snapshot into database
        
        Args:
            history_data: Dictionary with snapshot data
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False
        
        try:
            self.client.table("history_snapshots").insert(history_data).execute()
            return True
        except Exception as e:
            st.error(f"Error inserting history: {e}")
            return False
    
    def get_all_history(self):
        """
        Get all history snapshots from database
        
        Returns:
            List of history snapshots
        """
        if not self.client:
            return []
        
        try:
            response = self.client.table("history_snapshots").select("*").order("id", desc=True).execute()
            return response.data or []
        except Exception as e:
            st.error(f"Error fetching history: {e}")
            return []
    
    def delete_all_history(self):
        """
        Delete all history snapshots from database
        
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False
        
        try:
            self.client.table("history_snapshots").delete().neq("id", 0).execute()
            return True
        except Exception as e:
            st.error(f"Error deleting history: {e}")
            return False
    
    def get_history_count(self):
        """
        Get total count of history records
        
        Returns:
            Number of records
        """
        if not self.client:
            return 0
        
        try:
            response = self.client.table("history_snapshots").select("count", count="exact").execute()
            return response.count or 0
        except Exception:
            return 0
