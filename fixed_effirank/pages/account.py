# pages/account.py
import streamlit as st
from config import logger

def account_page(auth_manager):
    """Account management page"""
    try:
        st.title("👤 Account")
        
        user_info = st.session_state.get('username', 'Unknown')
        role = st.session_state.get('user_role', 'user')
        
        st.write(f"**Username:** {user_info}")
        st.write(f"**Role:** {role.title()}")
        
        st.markdown("---")
        
        if st.button("🚪 Logout"):
            auth_manager.logout()
            logger.info(f"User logged out: {user_info}")
            st.rerun()
    
    except Exception as e:
        logger.error(f"Account page error: {e}")
        st.error("Error loading account page")
