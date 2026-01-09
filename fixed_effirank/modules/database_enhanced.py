# modules/database.py
"""
Database Module - Enhanced Version
Handles Supabase database operations with advanced features
Fully compatible with supabase_schema_modular.sql
"""

import streamlit as st
from supabase import create_client
from datetime import datetime
from config import logger

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
            logger.warning("No Supabase credentials provided")
            return None
        
        try:
            self.client = create_client(self.supabase_url, self.supabase_key)
            # Test connection
            test_result = self.client.table("history_snapshots").select("count", count="exact").limit(1).execute()
            logger.info("Supabase connection successful")
            return self.client
        except Exception as e:
            logger.error(f"Supabase connection failed: {e}")
            st.warning(f"Supabase connection failed: {e}. Using local storage only.")
            self.client = None
            return None
    
    def is_connected(self):
        """Check if database is connected"""
        return self.client is not None
    
    # =============================================================================
    # BASIC OPERATIONS (Original Methods - Fully Compatible)
    # =============================================================================
    
    def insert_history(self, history_data):
        """
        Insert history snapshot into database
        
        Args:
            history_data: Dictionary with snapshot data
                Required fields: timestamp, date, week_number, week_range,
                                rankings_json, analysis_json
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.warning("Cannot insert history: Database not connected")
            return False
        
        try:
            # Add created_by if not present
            if 'created_by' not in history_data:
                history_data['created_by'] = st.session_state.get('username', 'system')
            
            self.client.table("history_snapshots").insert(history_data).execute()
            logger.info(f"History snapshot inserted: {history_data.get('date')}")
            return True
        except Exception as e:
            logger.error(f"Error inserting history: {e}")
            st.error(f"Error inserting history: {e}")
            return False
    
    def get_all_history(self):
        """
        Get all history snapshots from database
        
        Returns:
            List of history snapshots ordered by ID descending
        """
        if not self.client:
            logger.warning("Cannot get history: Database not connected")
            return []
        
        try:
            response = self.client.table("history_snapshots").select("*").order("id", desc=True).execute()
            logger.info(f"Retrieved {len(response.data)} history records")
            return response.data or []
        except Exception as e:
            logger.error(f"Error fetching history: {e}")
            st.error(f"Error fetching history: {e}")
            return []
    
    def delete_all_history(self):
        """
        Delete all history snapshots from database
        
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.warning("Cannot delete history: Database not connected")
            return False
        
        try:
            self.client.table("history_snapshots").delete().neq("id", 0).execute()
            logger.warning("All history records deleted")
            return True
        except Exception as e:
            logger.error(f"Error deleting history: {e}")
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
        except Exception as e:
            logger.error(f"Error getting history count: {e}")
            return 0
    
    # =============================================================================
    # ENHANCED OPERATIONS (New Methods Using SQL Schema Features)
    # =============================================================================
    
    def get_recent_history(self, days=30):
        """
        Get recent history using the recent_history view
        
        Args:
            days: Number of days to retrieve (default: 30)
            
        Returns:
            List of recent history snapshots
        """
        if not self.client:
            return []
        
        try:
            # Use the view created in SQL schema
            response = self.client.table("recent_history").select("*").execute()
            logger.info(f"Retrieved {len(response.data)} recent history records")
            return response.data or []
        except Exception as e:
            logger.warning(f"Recent history view not available, using fallback: {e}")
            # Fallback to manual query
            try:
                from datetime import timedelta
                cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
                response = self.client.table("history_snapshots").select("*").gte("created_at", cutoff_date).order("created_at", desc=True).execute()
                return response.data or []
            except Exception as e2:
                logger.error(f"Error fetching recent history: {e2}")
                return []
    
    def get_history_stats(self):
        """
        Get history statistics using the history_stats view
        
        Returns:
            Dictionary with statistics or None
        """
        if not self.client:
            return None
        
        try:
            response = self.client.table("history_stats").select("*").execute()
            if response.data and len(response.data) > 0:
                stats = response.data[0]
                logger.info("Retrieved history statistics")
                return stats
            return None
        except Exception as e:
            logger.warning(f"History stats view not available: {e}")
            # Fallback to manual calculation
            try:
                count = self.get_history_count()
                return {
                    'total_records': count,
                    'last_7_days': 0,  # Would need to calculate
                    'last_30_days': 0,
                    'last_90_days': 0,
                }
            except:
                return None
    
    def get_history_paginated(self, page=1, page_size=10):
        """
        Get paginated history results
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of records per page
            
        Returns:
            Tuple of (records, total_count)
        """
        if not self.client:
            return [], 0
        
        try:
            # Try using the SQL function
            response = self.client.rpc('get_history_paginated', {
                'page_number': page,
                'page_size': page_size
            }).execute()
            
            if response.data:
                total = response.data[0].get('total_count', 0) if response.data else 0
                logger.info(f"Retrieved page {page} of history ({len(response.data)} records)")
                return response.data, total
            return [], 0
        except Exception as e:
            logger.warning(f"Pagination function not available, using fallback: {e}")
            # Fallback to manual pagination
            try:
                offset = (page - 1) * page_size
                response = self.client.table("history_snapshots").select("*").order("created_at", desc=True).range(offset, offset + page_size - 1).execute()
                total = self.get_history_count()
                return response.data or [], total
            except Exception as e2:
                logger.error(f"Error with paginated history: {e2}")
                return [], 0
    
    def cleanup_old_history(self, months=12):
        """
        Cleanup history older than specified months
        
        Args:
            months: Number of months to keep (default: 12)
            
        Returns:
            Number of deleted records or None
        """
        if not self.client:
            logger.warning("Cannot cleanup history: Database not connected")
            return None
        
        try:
            # Try using the SQL function
            response = self.client.rpc('manual_cleanup_history', {
                'months_to_keep': months
            }).execute()
            
            if response.data and len(response.data) > 0:
                deleted_count = response.data[0].get('deleted_count', 0)
                logger.info(f"Cleaned up {deleted_count} old history records")
                return deleted_count
            return 0
        except Exception as e:
            logger.warning(f"Cleanup function not available, using fallback: {e}")
            # Fallback to manual deletion
            try:
                from datetime import timedelta
                cutoff_date = (datetime.now() - timedelta(days=months*30)).isoformat()
                response = self.client.table("history_snapshots").delete().lt("created_at", cutoff_date).execute()
                logger.info("Manual cleanup completed")
                return None  # Can't get count with this method
            except Exception as e2:
                logger.error(f"Error during cleanup: {e2}")
                return None
    
    def archive_old_history(self):
        """
        Archive old history records using the SQL function
        
        Returns:
            Number of archived records or None
        """
        if not self.client:
            return None
        
        try:
            response = self.client.rpc('archive_old_history').execute()
            if response.data:
                archived_count = response.data
                logger.info(f"Archived {archived_count} old records")
                return archived_count
            return 0
        except Exception as e:
            logger.warning(f"Archive function not available: {e}")
            return None
    
    def get_history_by_date_range(self, start_date, end_date):
        """
        Get history within a date range
        
        Args:
            start_date: Start date (datetime or string)
            end_date: End date (datetime or string)
            
        Returns:
            List of history snapshots
        """
        if not self.client:
            return []
        
        try:
            if isinstance(start_date, datetime):
                start_date = start_date.date().isoformat()
            if isinstance(end_date, datetime):
                end_date = end_date.date().isoformat()
            
            response = self.client.table("history_snapshots").select("*").gte("date", start_date).lte("date", end_date).order("date", desc=True).execute()
            logger.info(f"Retrieved {len(response.data)} records for date range {start_date} to {end_date}")
            return response.data or []
        except Exception as e:
            logger.error(f"Error fetching history by date range: {e}")
            return []
    
    def get_history_by_week(self, week_number):
        """
        Get history for a specific week number
        
        Args:
            week_number: Week number to retrieve
            
        Returns:
            List of history snapshots
        """
        if not self.client:
            return []
        
        try:
            response = self.client.table("history_snapshots").select("*").eq("week_number", week_number).order("created_at", desc=True).execute()
            logger.info(f"Retrieved {len(response.data)} records for week {week_number}")
            return response.data or []
        except Exception as e:
            logger.error(f"Error fetching history for week {week_number}: {e}")
            return []
    
    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    def test_connection(self):
        """
        Test database connection
        
        Returns:
            True if connected and working, False otherwise
        """
        if not self.client:
            return False
        
        try:
            self.client.table("history_snapshots").select("count", count="exact").limit(1).execute()
            return True
        except:
            return False
    
    def get_table_info(self):
        """
        Get information about the history_snapshots table
        
        Returns:
            Dictionary with table info or None
        """
        if not self.client:
            return None
        
        try:
            # Get a sample record to show structure
            response = self.client.table("history_snapshots").select("*").limit(1).execute()
            if response.data and len(response.data) > 0:
                sample = response.data[0]
                return {
                    'total_records': self.get_history_count(),
                    'sample_keys': list(sample.keys()),
                    'connected': True
                }
            return {
                'total_records': 0,
                'sample_keys': [],
                'connected': True
            }
        except Exception as e:
            logger.error(f"Error getting table info: {e}")
            return None
