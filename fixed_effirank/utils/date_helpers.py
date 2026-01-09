# utils/date_helpers.py
"""
Date and Time Helper Functions
All date/week calculation and formatting utilities
"""

from datetime import datetime, timedelta

class DateHelpers:
    """Date and week calculation utilities"""
    
    @staticmethod
    def get_week_number(date):
        """
        Calculate week number from October 1st (crop year start)
        
        Args:
            date: Date object
            
        Returns:
            Week number (integer)
        """
        try:
            if date.month >= 10:
                crop_year_start = datetime(date.year, 10, 1).date()
            else:
                crop_year_start = datetime(date.year - 1, 10, 1).date()
            
            days_diff = (date - crop_year_start).days
            return max(1, (days_diff // 7) + 1)
        except Exception:
            return 1
    
    @staticmethod
    def get_week_range(date):
        """
        Get week start and end dates
        
        Args:
            date: Date object
            
        Returns:
            Tuple of (week_start, week_end)
        """
        try:
            week_num = DateHelpers.get_week_number(date)
            
            if date.month >= 10:
                crop_year_start = datetime(date.year, 10, 1).date()
            else:
                crop_year_start = datetime(date.year - 1, 10, 1).date()
            
            week_start = crop_year_start + timedelta(days=(week_num - 1) * 7)
            week_end = week_start + timedelta(days=6)
            
            return week_start, week_end
        except Exception:
            return date, date
    
    @staticmethod
    def format_date_display(date):
        """
        Format date for display
        
        Args:
            date: Date object
            
        Returns:
            Formatted date string
        """
        try:
            return date.strftime("%B %d, %Y (%A)")
        except Exception:
            return str(date)
    
    @staticmethod
    def format_week_display(week_start, week_end):
        """
        Format week range for display
        
        Args:
            week_start: Week start date
            week_end: Week end date
            
        Returns:
            Formatted week range string
        """
        try:
            return f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}"
        except Exception:
            return f"{week_start} - {week_end}"
    
    @staticmethod
    def get_current_week_info():
        """
        Get current week information
        
        Returns:
            Dictionary with week info
        """
        today = datetime.now().date()
        week_num = DateHelpers.get_week_number(today)
        week_start, week_end = DateHelpers.get_week_range(today)
        
        return {
            'date': today,
            'week_number': week_num,
            'week_start': week_start,
            'week_end': week_end,
            'week_range': DateHelpers.format_week_display(week_start, week_end)
        }
