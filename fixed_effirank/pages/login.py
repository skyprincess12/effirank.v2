# pages/login.py
import streamlit as st
from config import logger

def login_page(auth_manager, users):
    """Login page with persistent authentication"""
    try:
        st.markdown('''
        <div class="login-container">
            <h1 style="text-align:center;">🚛 TLS System</h1>
            <p style="text-align:center; color:#64748b;">Cost Input & Ranking System</p>
        </div>
        ''', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            remember_me = st.checkbox("Remember me for 30 days", value=True)
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if auth_manager.login(username, password, users, remember_me):
                    st.success("Login successful!")
                    logger.info(f"User logged in: {username}")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
                    logger.warning(f"Failed login attempt for: {username}")
    
    except Exception as e:
        logger.error(f"Login page error: {e}")
        st.error("Login system error. Please refresh the page.")
