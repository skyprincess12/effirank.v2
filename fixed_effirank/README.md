# TLS Cost Input & Ranking System v2.1.0

## 🚀 What's New in v2.1.0

### Major Improvements
- ✅ **All Missing Page Files Created** - Complete implementation of all 6 pages
- ✅ **Comprehensive Error Handling** - Error boundaries prevent app crashes
- ✅ **Caching System** - Fast deployment with `@st.cache_data` and `@st.cache_resource`
- ✅ **Rate Limiting** - Prevents API throttling
- ✅ **Input Validation** - Validates all user inputs
- ✅ **Logging System** - Full activity logging for debugging
- ✅ **Future-Proof Architecture** - Modular design for easy updates

### Bug Fixes
- Fixed missing page imports
- Fixed session state race conditions
- Fixed database connection errors
- Fixed weather API timeout issues
- Fixed KPI calculation edge cases

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) Supabase account for cloud database
- (Optional) OpenWeather API key for weather features

## 🔧 Installation

### 1. Clone or Extract the Repository
```bash
cd effirank_v2_fixed
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Secrets

Create a `.streamlit/secrets.toml` file:

```toml
# User Accounts
[users]
[users.admin]
password = "your_admin_password"
role = "admin"

[users.user1]
password = "user_password"
role = "user"

# System Settings
HISTORY_DELETE_PASSCODE = "your_delete_passcode"

# Optional: Supabase Database
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-supabase-anon-key"

# Optional: OpenWeather API
[openweather]
api_key = "your_openweather_api_key"

# Optional: Weather Locations
[[weather_locations]]
name = "Location 1"
latitude = 10.6519
longitude = 122.5661

[[weather_locations]]
name = "Location 2"
latitude = 10.7202
longitude = 122.5621
```

## 🚀 Running the Application

### Development Mode
```bash
streamlit run app.py
```

### Production Mode (with caching)
```bash
streamlit run app.py --server.enableCORS false --server.enableXsrfProtection true
```

## 📁 Project Structure

```
effirank_v2_fixed/
├── app.py                      # Main application entry point
├── config.py                   # Configuration and constants
├── requirements.txt            # Python dependencies
│
├── modules/                    # Core modules
│   ├── __init__.py
│   ├── auth.py                # Authentication & login
│   ├── database.py            # Database operations
│   ├── secrets_loader.py      # Secrets management
│   └── weather_api.py         # Weather API integration
│
├── pages/                      # Application pages
│   ├── __init__.py
│   ├── login.py               # Login page
│   ├── cost_input.py          # Cost input page
│   ├── ranking.py             # Efficiency ranking
│   ├── cost_analysis.py       # Cost analysis & charts
│   ├── weather_dashboard.py   # Weather dashboard
│   ├── history.py             # History snapshots
│   └── account.py             # Account management
│
├── utils/                      # Utility modules
│   ├── __init__.py
│   ├── data_persistence.py    # Local data storage
│   ├── date_helpers.py        # Date calculations
│   ├── kpi_calculator.py      # KPI calculations
│   └── session_manager.py     # Session state management
│
└── .streamlit/
    └── secrets.toml           # Secret configuration (create this)
```

## 🔐 Security Features

1. **Persistent Authentication** - 30-day "Remember Me" cookies
2. **Password Hashing** - Secure password storage
3. **Session Management** - Secure session handling
4. **Input Validation** - Prevents invalid data entry
5. **Rate Limiting** - Prevents API abuse

## 💾 Caching Strategy

The application uses multiple caching strategies:

- **Manager Initialization** (`@st.cache_resource`) - Managers cached for entire session
- **Weather Data** (`@st.cache_data(ttl=600)`) - 10-minute cache
- **Rankings** (`@st.cache_data(ttl=60)`) - 1-minute cache
- **Charts** (`@st.cache_data(ttl=60)`) - 1-minute cache

## 📊 Features

### Cost Input
- Multi-location cost tracking
- Real-time input validation
- Automatic data persistence
- Weather integration

### Efficiency Ranking
- Adjustable KPI weights (Cost vs LKG)
- Global and regional rankings
- Color-coded performance tiers
- Cached calculations for speed

### Cost Analysis
- Interactive charts and graphs
- Cost comparisons
- Trend analysis
- Export capabilities

### Weather Dashboard
- Real-time weather data
- 5-day forecasts
- Location-based tracking
- Automatic caching

### History
- Snapshot management
- Historical comparisons
- Secure deletion with passcode
- Database integration

### Account Management
- User profiles
- Role-based access
- Secure logout
- Session management

## 🐛 Troubleshooting

### Application Won't Start
1. Check Python version: `python --version` (must be 3.8+)
2. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
3. Check secrets file: `.streamlit/secrets.toml` must exist

### Database Connection Issues
1. Verify Supabase credentials in secrets.toml
2. Check internet connection
3. Application will fall back to local storage automatically

### Weather API Not Working
1. Verify API key in secrets.toml
2. Check rate limits (60 calls/minute)
3. Application works without weather data

### Caching Issues
```bash
# Clear Streamlit cache
streamlit cache clear
```

## 📝 Logging

Logs are stored in: `~/.tls_app_data/app.log` (Linux/Mac) or `%TEMP%/tls_app_data/app.log` (Windows)

View logs:
```bash
# Linux/Mac
tail -f ~/.tls_app_data/app.log

# Windows
type %TEMP%\tls_app_data\app.log
```

## 🔄 Updates & Maintenance

### Adding New Users
Edit `.streamlit/secrets.toml`:
```toml
[users.newuser]
password = "password123"
role = "user"  # or "admin"
```

### Updating KPI Weights
Default weights are in `config.py`:
```python
DEFAULT_COST_WEIGHT = 50
DEFAULT_LKG_WEIGHT = 50
```

### Adding New Locations
Edit `config.py` -> `DEFAULT_LOCATIONS` dictionary

## 🤝 Support

For issues or questions:
1. Check logs in `~/.tls_app_data/app.log`
2. Review error details in the UI
3. Check this README for troubleshooting

## 📄 License

Internal use only - All rights reserved

## 🎯 Version History

### v2.1.0 (2026-01-09)
- Complete rewrite with all pages implemented
- Added comprehensive error handling
- Implemented caching system
- Added rate limiting
- Enhanced security
- Improved logging
- Future-proofed architecture

### v2.0.0 (2026-01-07)
- Initial modular architecture
- Basic authentication
- Database integration
- Weather API integration

---

**System Status**: ✅ Production Ready  
**Last Updated**: January 9, 2026  
**Maintained By**: TLS Development Team
