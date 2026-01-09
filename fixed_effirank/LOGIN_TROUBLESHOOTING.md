# 🔐 Login Troubleshooting Guide

## Problem: "Invalid username or password" Error

If you can't log in and keep getting "Invalid username or password", follow these steps:

---

## ✅ Quick Fix Checklist

### 1. Check Your secrets.toml File Location

**File must be at**: `.streamlit/secrets.toml`

```bash
# Check if file exists
ls -la .streamlit/secrets.toml

# If it doesn't exist, create it:
mkdir -p .streamlit
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
```

### 2. Check secrets.toml Format

Open `.streamlit/secrets.toml` and verify the format:

**✅ CORRECT Format (Recommended):**
```toml
[users.admin]
password = "admin"
role = "admin"

[users.user]
password = "user123"
role = "user"
```

**✅ ALTERNATIVE Format (Also Works):**
```toml
USERNAME = "admin"
PASSWORD = "admin"
```

**❌ WRONG Formats:**
```toml
# Missing quotes
[users.admin]
password = admin  # ❌ WRONG - needs quotes

# Wrong indentation
  [users.admin]  # ❌ WRONG - no indentation
  password = "admin"

# Typos in section names
[user.admin]  # ❌ WRONG - should be "users" (plural)
password = "admin"
```

### 3. Default Credentials

If you haven't set up secrets.toml, the app uses these defaults:

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin` | admin |
| `user` | `user` | user |

**Try logging in with:**
- Username: `admin`
- Password: `admin`

### 4. Common Issues

#### Issue: Spaces in Password
```toml
# ❌ WRONG
password = " admin "  # Has spaces

# ✅ CORRECT
password = "admin"
```

#### Issue: Case Sensitivity
Usernames and passwords are **case-sensitive**:
- `Admin` ≠ `admin`
- `Password` ≠ `password`

#### Issue: Special Characters
If your password has special characters, use quotes:
```toml
# ✅ CORRECT
password = "my@password123!"
```

#### Issue: Cached Secrets
If you just changed secrets.toml, restart the app:
```bash
# Press Ctrl+C in terminal
# Then restart:
streamlit run app.py
```

Or click "Rerun" in Streamlit Cloud.

---

## 🔍 Debug Mode

### Enable Debug Login Page

Replace the login page with debug version:

```bash
# Backup original
cp pages/login.py pages/login_original.py

# Use debug version
cp pages/login_debug.py pages/login.py

# Restart app
streamlit run app.py
```

The debug page will show:
- ✅ Which users are loaded
- ✅ Password lengths
- ✅ Exact error reasons
- ✅ Helpful hints

### What Debug Mode Shows

When login fails, click "🔍 DEBUG: Click here if login fails" to see:

1. **Loaded Users**: Shows all usernames found in secrets
2. **Password Lengths**: Helps verify passwords are loading correctly
3. **Roles**: Shows assigned roles
4. **Format Examples**: Shows correct secrets.toml format

---

## 🛠️ Step-by-Step Troubleshooting

### Step 1: Verify secrets.toml Exists

```bash
cat .streamlit/secrets.toml
```

Should show your configuration. If you get "No such file", create it:

```bash
mkdir -p .streamlit
nano .streamlit/secrets.toml
```

Paste this minimal config:
```toml
[users.admin]
password = "admin"
role = "admin"
```

Save (Ctrl+O, Enter, Ctrl+X in nano).

### Step 2: Test with Default Credentials

Restart app and try:
- Username: `admin`
- Password: `admin`

### Step 3: Check App Logs

```bash
# Check log file
tail -f ~/.tls_app_data/app.log
```

Look for lines like:
```
Login attempt - Username: 'admin', Password length: 5
Available users: ['admin', 'user']
```

### Step 4: Verify Secrets Loaded

Add this to your app temporarily to debug:

In `app.py`, after line 114 (after `managers = initialize_managers()`), add:
```python
st.sidebar.write("DEBUG - Loaded users:", list(managers['users'].keys()))
```

This will show which users were loaded.

---

## 📋 Streamlit Cloud Specific

### If Deploying to Streamlit Cloud:

1. **Go to app settings** in Streamlit Cloud dashboard
2. **Click "Secrets"** in left sidebar
3. **Paste your secrets** in TOML format:

```toml
[users.admin]
password = "your_secure_password"
role = "admin"
```

4. **Click "Save"**
5. **Redeploy** the app

**Important**: Don't use test passwords like "admin" in production!

---

## 🔐 Security Best Practices

### For Production:

1. **Use Strong Passwords**
```bash
# Generate a secure password
python -c "import secrets; print(secrets.token_urlsafe(16))"
```

2. **Never Commit secrets.toml**
```bash
# Check .gitignore includes:
echo ".streamlit/secrets.toml" >> .gitignore
```

3. **Different Passwords per Environment**
- Local: Simple passwords for testing
- Staging: Medium security
- Production: Strong passwords

---

## 🎯 Most Common Solutions

### Solution 1: File Not Found
```bash
# Create .streamlit directory
mkdir -p .streamlit

# Copy template
cp .streamlit/secrets.toml.template .streamlit/secrets.toml

# Edit it
nano .streamlit/secrets.toml
```

### Solution 2: Wrong Format
Check your secrets.toml matches EXACTLY:
```toml
[users.admin]
password = "admin"
role = "admin"
```

No extra spaces, correct quotes, correct indentation.

### Solution 3: Restart App
After changing secrets.toml:
```bash
# Stop app (Ctrl+C)
# Clear cache
streamlit cache clear
# Restart
streamlit run app.py
```

### Solution 4: Use Debug Mode
```bash
cp pages/login_debug.py pages/login.py
streamlit run app.py
# Click debug expander to see what's loaded
```

---

## 🆘 Still Not Working?

### Create a Test File

Create `test_secrets.py`:
```python
import streamlit as st

st.write("Testing secrets loading...")

# Try to load secrets
try:
    users = st.secrets.get("users", {})
    st.write("Loaded users:", users)
    
    if not users:
        st.warning("No users in [users] section, trying old format...")
        username = st.secrets.get("USERNAME")
        password = st.secrets.get("PASSWORD")
        st.write(f"Old format - Username: {username}, Password: {password}")
    else:
        for user, data in users.items():
            st.write(f"User: {user}")
            st.write(f"  - Password: {data.get('password')}")
            st.write(f"  - Role: {data.get('role')}")
            
except Exception as e:
    st.error(f"Error loading secrets: {e}")
    st.write("Using fallback defaults")
```

Run it:
```bash
streamlit run test_secrets.py
```

This will show exactly what's being loaded from your secrets file.

---

## 📞 Quick Reference

### Working secrets.toml Examples

**Example 1: Single Admin User**
```toml
[users.admin]
password = "MySecurePassword123"
role = "admin"
```

**Example 2: Multiple Users**
```toml
[users.admin]
password = "admin_pass"
role = "admin"

[users.john]
password = "john_pass"
role = "user"

[users.mary]
password = "mary_pass"
role = "user"
```

**Example 3: Old Format (Backward Compatible)**
```toml
USERNAME = "admin"
PASSWORD = "admin"
```

### Test Command
```bash
# Quick test
streamlit run app.py

# Then try:
# Username: admin
# Password: admin
```

---

## ✅ Checklist Before Asking for Help

- [ ] `.streamlit/secrets.toml` exists
- [ ] File has correct TOML format (no syntax errors)
- [ ] Tried default credentials (admin/admin)
- [ ] Restarted app after changing secrets
- [ ] Checked app logs for errors
- [ ] Used debug login page
- [ ] Verified passwords have no extra spaces
- [ ] Checked username case (admin vs Admin)

---

**Still stuck?** Check the logs at `~/.tls_app_data/app.log` and look for the error messages!
