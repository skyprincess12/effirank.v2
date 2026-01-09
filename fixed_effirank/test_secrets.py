#!/usr/bin/env python3
"""
Quick test to verify secrets.toml is configured correctly
Run this before starting the main app to check your credentials
"""

import streamlit as st

st.title("🔍 TLS System - Secrets Configuration Test")

st.markdown("---")

st.header("1️⃣ Checking secrets.toml file...")

try:
    # Check if secrets are accessible
    secrets_available = hasattr(st, 'secrets') and st.secrets
    
    if secrets_available:
        st.success("✅ Streamlit secrets are accessible")
    else:
        st.error("❌ Streamlit secrets not accessible")
        st.info("Make sure you have .streamlit/secrets.toml file")
        st.stop()
    
    st.markdown("---")
    st.header("2️⃣ Loading User Configuration...")
    
    # Try to load users (same way the app does)
    users = st.secrets.get("users", {})
    
    if users:
        st.success(f"✅ Found {len(users)} user(s) in [users] section")
        
        st.subheader("📋 Loaded Users:")
        for username, user_data in users.items():
            with st.expander(f"👤 {username}", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write("**Username:**")
                    st.code(username)
                with col2:
                    st.write("**Password:**")
                    password = user_data.get('password', '')
                    st.code('*' * len(password) + f" ({len(password)} chars)")
                with col3:
                    st.write("**Role:**")
                    role = user_data.get('role', 'not set')
                    st.code(role)
                
                # Show actual password in a hidden section
                with st.container():
                    if st.checkbox(f"Show actual password for {username}", key=f"show_{username}"):
                        st.warning(f"Password: `{password}`")
    else:
        st.warning("⚠️ No users found in [users] section")
        st.info("Checking alternative format...")
        
        # Try old format
        username = st.secrets.get("USERNAME")
        password = st.secrets.get("PASSWORD")
        
        if username and password:
            st.success("✅ Found credentials in old format (USERNAME/PASSWORD)")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Username:**")
                st.code(username)
            with col2:
                st.write("**Password:**")
                st.code('*' * len(password) + f" ({len(password)} chars)")
            
            if st.checkbox("Show actual password"):
                st.warning(f"Password: `{password}`")
            
            st.info("""
            The app will convert this to:
            ```python
            users = {
                "%s": {
                    "password": "%s",
                    "role": "admin"
                }
            }
            ```
            """ % (username, password))
        else:
            st.error("❌ No user credentials found!")
            st.error("Neither [users] section nor USERNAME/PASSWORD found in secrets.toml")
            
            st.markdown("---")
            st.subheader("📝 How to Fix:")
            st.write("Create or edit `.streamlit/secrets.toml` with this content:")
            
            st.code('''
[users.admin]
password = "admin"
role = "admin"

[users.user]
password = "user123"
role = "user"
            ''', language='toml')
            
            st.stop()
    
    st.markdown("---")
    st.header("3️⃣ Testing Login Function...")
    
    # Get the user dict that will be used
    if users:
        test_users = users
    else:
        username = st.secrets.get("USERNAME", "admin")
        password = st.secrets.get("PASSWORD", "admin")
        test_users = {
            username: {
                "password": password,
                "role": "admin"
            }
        }
    
    st.write("**Users that will be available for login:**")
    for user in test_users.keys():
        st.write(f"- `{user}`")
    
    st.markdown("---")
    st.header("4️⃣ Test Login Here:")
    
    with st.form("test_login"):
        test_username = st.text_input("Username")
        test_password = st.text_input("Password", type="password")
        test_submit = st.form_submit_button("Test Login")
        
        if test_submit:
            if test_username in test_users:
                expected_password = test_users[test_username]['password']
                if test_password == expected_password:
                    st.success(f"✅ Login successful for user '{test_username}'!")
                    st.balloons()
                    st.info("You can now use these credentials in the main app")
                else:
                    st.error(f"❌ Wrong password for user '{test_username}'")
                    st.write(f"Expected password length: {len(expected_password)} characters")
                    st.write(f"Your password length: {len(test_password)} characters")
                    
                    if len(test_password) == len(expected_password):
                        st.warning("💡 Password length matches but characters are different. Check for typos!")
            else:
                st.error(f"❌ Username '{test_username}' not found")
                st.info(f"Available usernames: {', '.join(test_users.keys())}")
    
    st.markdown("---")
    st.header("5️⃣ Other Settings:")
    
    # Check other settings
    with st.expander("🗑️ History Delete Passcode"):
        passcode = st.secrets.get("HISTORY_DELETE_PASSCODE", "delete123")
        st.write(f"Passcode: `{passcode}`")
    
    with st.expander("💾 Supabase Database"):
        supabase_url = st.secrets.get("SUPABASE_URL")
        supabase_key = st.secrets.get("SUPABASE_KEY")
        
        if supabase_url and supabase_key:
            st.success("✅ Supabase credentials configured")
            st.write(f"URL: `{supabase_url}`")
            st.write(f"Key: `{supabase_key[:20]}...`")
        else:
            st.info("ℹ️ Supabase not configured (optional)")
    
    with st.expander("🌤️ Weather API"):
        try:
            weather_key = st.secrets.get("openweather", {}).get("api_key")
            if weather_key:
                st.success("✅ OpenWeather API key configured")
                st.write(f"Key: `{weather_key[:10]}...`")
            else:
                st.info("ℹ️ Weather API not configured (optional)")
        except:
            st.info("ℹ️ Weather API not configured (optional)")
    
    st.markdown("---")
    st.success("✅ Configuration test complete!")
    st.info("If login test worked above, you can now run the main app with: `streamlit run app.py`")

except Exception as e:
    st.error(f"❌ Error during testing: {e}")
    
    import traceback
    with st.expander("Error Details"):
        st.code(traceback.format_exc())
    
    st.markdown("---")
    st.subheader("Common Issues:")
    st.write("""
    1. **File not found**: Create `.streamlit/secrets.toml` file
    2. **Syntax error**: Check TOML format (proper quotes, indentation)
    3. **Wrong location**: File must be in `.streamlit/` directory
    """)
