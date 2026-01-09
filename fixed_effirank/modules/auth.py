# modules/auth.py
"""
Authentication Module
Handles user authentication with persistent login via cookies
"""

import streamlit as st
import extra_streamlit_components as stx
import hashlib
import secrets
import json
from datetime import datetime, timedelta

class PersistentAuth:
    """Handle persistent authentication with encrypted cookies"""
    
    def __init__(self, cookie_name="tls_auth_v2", cookie_expiry_days=30):
        """
        Initialize authentication manager
        
        Args:
            cookie_name: Name of the authentication cookie
            cookie_expiry_days: Number of days before cookie expires
        """
        self.cookie_name = cookie_name
        self.cookie_expiry_days = cookie_expiry_days
        self._cookie_manager = None  # Lazy initialization
    
    @property
    def cookie_manager(self):
        """
        Lazy initialization of CookieManager
        This prevents caching issues since CookieManager uses Streamlit widgets
        """
        if self._cookie_manager is None:
            try:
                self._cookie_manager = stx.CookieManager()
            except Exception as e:
                # If cookie manager fails, create a dummy that does nothing
                class DummyCookieManager:
                    def get_all(self):
                        return {}
                    def get(self, key):
                        return None
                    def set(self, key, value, **kwargs):
                        pass
                    def delete(self, key):
                        pass
                self._cookie_manager = DummyCookieManager()
        return self._cookie_manager
    
    def create_auth_token(self, username):
        """
        Create secure authentication token
        
        Args:
            username: Username to encode in token
            
        Returns:
            Encrypted token string
        """
        timestamp = datetime.now().isoformat()
        token_data = {
            'username': username,
            'timestamp': timestamp,
            'random': secrets.token_hex(16)
        }
        token_string = json.dumps(token_data)
        token_hash = hashlib.sha256(token_string.encode()).hexdigest()
        return f"{token_hash}:{username}:{timestamp}"
    
    def verify_token(self, token):
        """
        Verify authentication token
        
        Args:
            token: Token string to verify
            
        Returns:
            Username if valid, None otherwise
        """
        if not token:
            return None
        
        try:
            parts = token.split(':')
            if len(parts) != 3:
                return None
            
            token_hash, username, timestamp = parts
            token_time = datetime.fromisoformat(timestamp)
            age = datetime.now() - token_time
            
            if age > timedelta(days=self.cookie_expiry_days):
                return None
            
            return username
        except Exception:
            return None
    
    def set_auth_cookie(self, username):
        """
        Set authentication cookie
        
        Args:
            username: Username to store in cookie
        """
        token = self.create_auth_token(username)
        expiry_date = datetime.now() + timedelta(days=self.cookie_expiry_days)
        self.cookie_manager.set(self.cookie_name, token, expires_at=expiry_date)
    
    def get_auth_cookie(self):
        """
        Get authentication cookie
        
        Returns:
            Token string if cookie exists, None otherwise
        """
        try:
            cookies = self.cookie_manager.get_all()
            return cookies.get(self.cookie_name)
        except Exception:
            return None
    
    def clear_auth_cookie(self):
        """Clear authentication cookie"""
        try:
            self.cookie_manager.delete(self.cookie_name)
        except Exception:
            pass
    
    def check_authentication(self, valid_users):
        """
        Check if user is authenticated via cookie or session
        
        Args:
            valid_users: Dictionary of valid users {username: {password, role}}
            
        Returns:
            Tuple of (is_authenticated, username)
        """
        # Check session state first
        if st.session_state.get('authenticated', False):
            username = st.session_state.get('username', '')
            return True, username
        
        # Check cookie
        token = self.get_auth_cookie()
        if token:
            username = self.verify_token(token)
            if username and username in valid_users:
                # Restore session from cookie
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.user_role = valid_users[username].get('role', 'user')
                return True, username
        
        return False, None
    
    def login(self, username, password, valid_users, remember_me=True):
        """
        Perform login with optional remember me
        
        Args:
            username: Entered username
            password: Entered password
            valid_users: Dictionary of valid users
            remember_me: Whether to set persistent cookie
            
        Returns:
            True if login successful, False otherwise
        """
        if username in valid_users and password == valid_users[username]['password']:
            # Set session
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.user_role = valid_users[username].get('role', 'user')
            
            # Set cookie if remember me
            if remember_me:
                self.set_auth_cookie(username)
            
            return True
        
        return False
    
    def logout(self):
        """Perform logout - clear session and cookie"""
        # Clear session
        st.session_state.authenticated = False
        if 'username' in st.session_state:
            del st.session_state.username
        if 'user_role' in st.session_state:
            del st.session_state.user_role
        
        # Clear cookie
        self.clear_auth_cookie()
