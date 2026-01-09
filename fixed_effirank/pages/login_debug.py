# pages/login.py - DEBUG VERSION
import streamlit as st
from config import logger

def login_page(auth_manager, users):
    """Login page with persistent authentication - DEBUG VERSION"""
    try:
        st.markdown('''
        <div class="login-container">
            <h1 style="text-align:center;">🚛 TLS System</h1>
            <p style="text-align:center; color:#64748b;">Cost Input & Ranking System</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # DEBUG: Show what users are loaded
        with st.expander("🔍 DEBUG: Click here if login fails", expanded=False):
            st.write("**Loaded users from secrets:**")
            if users:
                for username in users.keys():
                    st.write(f"- Username: `{username}`")
                    st.write(f"  - Password length: {len(users[username].get('password', ''))} characters")
                    st.write(f"  - Role: {users[username].get('role', 'not set')}")
            else:
                st.error("❌ No users loaded! Check your secrets.toml file")
            
            st.markdown("---")
            st.write("**Expected secrets.toml format:**")
            st.code('''
[users.admin]
password = "your_password_here"
role = "admin"

[users.user]
password = "user_password"
role = "user"
            ''', language='toml')
            
            st.markdown("---")
            st.write("**Alternative format (also supported):**")
            st.code('''
USERNAME = "admin"
PASSWORD = "admin"
            ''', language='toml')
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            remember_me = st.checkbox("Remember me for 30 days", value=True)
            submitted = st.form_submit_button("Login")
            
            if submitted:
                # DEBUG: Log attempt
                logger.info(f"Login attempt - Username: '{username}', Password length: {len(password)}")
                logger.info(f"Available users: {list(users.keys())}")
                
                # Check if username exists
                if username not in users:
                    st.error(f"❌ Username '{username}' not found")
                    st.info(f"Available usernames: {', '.join(users.keys())}")
                    logger.warning(f"Username '{username}' not in users dict")
                    return
                
                # Check password
                expected_password = users[username].get('password', '')
                if password != expected_password:
                    st.error("❌ Incorrect password")
                    logger.warning(f"Password mismatch for user '{username}'")
                    logger.debug(f"Expected length: {len(expected_password)}, Got length: {len(password)}")
                    
                    # Show hint if very close
                    if len(password) == len(expected_password):
                        st.info("💡 Hint: Password length is correct, but characters don't match. Check for typos.")
                    return
                
                # Attempt login
                if auth_manager.login(username, password, users, remember_me):
                    st.success("✅ Login successful!")
                    logger.info(f"User logged in: {username}")
                    st.rerun()
                else:
                    st.error("❌ Login failed (auth manager returned False)")
                    logger.error(f"Auth manager login failed for: {username}")
    
    except Exception as e:
        logger.error(f"Login page error: {e}")
        st.error(f"Login system error: {e}")
        st.info("Please refresh the page or check the logs.")
        
        import traceback
        with st.expander("Error details"):
            st.code(traceback.format_exc())
