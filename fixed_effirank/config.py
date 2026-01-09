# config.py
"""
Configuration and Constants
All app-wide constants and configuration settings
Enhanced with caching, validation, and error handling
"""

import os
import platform
import tempfile
from pathlib import Path

# =============================================================================
# VERSION INFO
# =============================================================================

APP_VERSION = "2.1.0"
APP_NAME = "TLS Cost Input & Ranking System"
APP_LAST_UPDATED = "2026-01-09"

# =============================================================================
# FILE PATHS & DIRECTORIES
# =============================================================================

# Cross-platform data directory with better error handling
def get_data_directory():
    """Get or create data directory with fallback options"""
    try:
        if platform.system() == "Windows":
            base_dir = os.path.join(tempfile.gettempdir(), "tls_app_data")
        else:
            base_dir = os.path.expanduser("~/.tls_app_data")
        
        # Create directory if it doesn't exist
        Path(base_dir).mkdir(parents=True, exist_ok=True)
        
        # Test write permission
        test_file = Path(base_dir) / ".test_write"
        test_file.touch()
        test_file.unlink()
        
        return base_dir
    except Exception as e:
        print(f"Cannot create data directory: {e}")
        # Final fallback to system temp
        fallback = tempfile.mkdtemp(prefix="tls_app_")
        print(f"Using fallback directory: {fallback}")
        return fallback

DATA_DIR = get_data_directory()

# File paths
LOCATIONS_FILE = os.path.join(DATA_DIR, "locations_data.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history_snapshots.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "app_settings.json")
CACHE_DIR = os.path.join(DATA_DIR, "cache")

# Create cache directory
Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)

# =============================================================================
# APP CONFIGURATION
# =============================================================================

# Page configuration for Streamlit
PAGE_CONFIG = {
    "page_title": f"{APP_NAME} v{APP_VERSION}",
    "page_icon": "🚛",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    "menu_items": {
        'About': f"{APP_NAME}\nVersion {APP_VERSION}\nLast Updated: {APP_LAST_UPDATED}"
    }
}

# Cookie settings
COOKIE_NAME = "tls_auth_v2"
COOKIE_EXPIRY_DAYS = 30

# Default KPI weights
DEFAULT_COST_WEIGHT = 50
DEFAULT_LKG_WEIGHT = 50

# KPI slider options
KPI_SLIDER_OPTIONS = [0, 25, 50, 75, 100]

# =============================================================================
# CACHING CONFIGURATION
# =============================================================================

# Cache TTL (Time To Live) in seconds
CACHE_TTL = {
    'weather_current': 600,      # 10 minutes
    'weather_forecast': 1800,    # 30 minutes
    'database_query': 300,       # 5 minutes
    'calculations': 60,          # 1 minute
    'locations_data': 3600,      # 1 hour
}

# =============================================================================
# API CONFIGURATION
# =============================================================================

# API Timeouts (seconds)
API_TIMEOUT = 10
API_MAX_RETRIES = 3

# Rate limiting
RATE_LIMIT_CALLS = 60  # calls per minute
RATE_LIMIT_WINDOW = 60  # seconds

# =============================================================================
# VALIDATION RULES
# =============================================================================

# Input validation ranges
VALIDATION_RULES = {
    'barangay_fee': {'min': 0, 'max': 100000, 'type': float},
    'rental_rate': {'min': 0, 'max': 100000, 'type': float},
    'tls_opn': {'min': 0, 'max': 100000, 'type': float},
    'drivers_hauler': {'min': 0, 'max': 100000, 'type': float},
    'fuel_cons': {'min': 0, 'max': 1000, 'type': float},
    'diesel_price': {'min': 0, 'max': 500, 'type': float},
    'ta_inc': {'min': 0, 'max': 100000, 'type': float},
    'lkgtc': {'min': 0, 'max': 1000000, 'type': float},
}

# =============================================================================
# DEFAULT LOCATIONS DATA
# =============================================================================

DEFAULT_LOCATIONS = {
    'DIRECT MILLSITE': {
        'region': 'NORTH',
        'barangay_fee': 0.0,
        'rental_rate': 0.0,
        'tls_opn': 0.0,
        'drivers_hauler': 0.0,
        'fuel_cons': 0.0,
        'diesel_price': 0.0,
        'ta_inc': 0.0,
        'lkgtc': 0.0
    },
    'CROSSING VITO': {
        'region': 'NORTH',
        'barangay_fee': 0.0,
        'rental_rate': 0.0,
        'tls_opn': 0.0,
        'drivers_hauler': 0.0,
        'fuel_cons': 0.0,
        'diesel_price': 0.0,
        'ta_inc': 0.0,
        'lkgtc': 0.0
    },
    'BATO': {
        'region': 'NORTH',
        'barangay_fee': 0.0,
        'rental_rate': 0.0,
        'tls_opn': 0.0,
        'drivers_hauler': 0.0,
        'fuel_cons': 0.0,
        'diesel_price': 0.0,
        'ta_inc': 0.0,
        'lkgtc': 0.0
    },
    'ESCALANTE': {
        'region': 'NORTH',
        'barangay_fee': 0.0,
        'rental_rate': 0.0,
        'tls_opn': 0.0,
        'drivers_hauler': 0.0,
        'fuel_cons': 0.0,
        'diesel_price': 0.0,
        'ta_inc': 0.0,
        'lkgtc': 0.0
    },
    'SAN JOSE': {
        'region': 'NORTH',
        'barangay_fee': 0.0,
        'rental_rate': 0.0,
        'tls_opn': 0.0,
        'drivers_hauler': 0.0,
        'fuel_cons': 0.0,
        'diesel_price': 0.0,
        'ta_inc': 0.0,
        'lkgtc': 0.0
    },
    'BAGAWINES': {
        'region': 'NORTH',
        'barangay_fee': 0.0,
        'rental_rate': 0.0,
        'tls_opn': 0.0,
        'drivers_hauler': 0.0,
        'fuel_cons': 0.0,
        'diesel_price': 0.0,
        'ta_inc': 0.0,
        'lkgtc': 0.0
    },
    'CANIBUNGAN': {
        'region': 'SOUTH',
        'barangay_fee': 0.0,
        'rental_rate': 0.0,
        'tls_opn': 0.0,
        'drivers_hauler': 0.0,
        'fuel_cons': 0.0,
        'diesel_price': 0.0,
        'ta_inc': 0.0,
        'lkgtc': 0.0
    },
    'MANAPLA': {
        'region': 'SOUTH',
        'barangay_fee': 0.0,
        'rental_rate': 0.0,
        'tls_opn': 0.0,
        'drivers_hauler': 0.0,
        'fuel_cons': 0.0,
        'diesel_price': 0.0,
        'ta_inc': 0.0,
        'lkgtc': 0.0
    },
    'SAN ISIDRO': {
        'region': 'SOUTH',
        'barangay_fee': 0.0,
        'rental_rate': 0.0,
        'tls_opn': 0.0,
        'drivers_hauler': 0.0,
        'fuel_cons': 0.0,
        'diesel_price': 0.0,
        'ta_inc': 0.0,
        'lkgtc': 0.0
    },
    'SARAVIA': {
        'region': 'SOUTH',
        'barangay_fee': 0.0,
        'rental_rate': 0.0,
        'tls_opn': 0.0,
        'drivers_hauler': 0.0,
        'fuel_cons': 0.0,
        'diesel_price': 0.0,
        'ta_inc': 0.0,
        'lkgtc': 0.0
    },
    'MURCIA': {
        'region': 'SOUTH',
        'barangay_fee': 0.0,
        'rental_rate': 0.0,
        'tls_opn': 0.0,
        'drivers_hauler': 0.0,
        'fuel_cons': 0.0,
        'diesel_price': 0.0,
        'ta_inc': 0.0,
        'lkgtc': 0.0
    },
    'MA-AO': {
        'region': 'SOUTH',
        'barangay_fee': 0.0,
        'rental_rate': 0.0,
        'tls_opn': 0.0,
        'drivers_hauler': 0.0,
        'fuel_cons': 0.0,
        'diesel_price': 0.0,
        'ta_inc': 0.0,
        'lkgtc': 0.0
    },
    'LA CASTELLANA': {
        'region': 'SOUTH',
        'barangay_fee': 0.0,
        'rental_rate': 0.0,
        'tls_opn': 0.0,
        'drivers_hauler': 0.0,
        'fuel_cons': 0.0,
        'diesel_price': 0.0,
        'ta_inc': 0.0,
        'lkgtc': 0.0
    }
}

# =============================================================================
# CSS STYLES
# =============================================================================

APP_CSS = '''
<style>
    .main-header { 
        background: linear-gradient(90deg,#1e40af 0%,#7c3aed 100%); 
        padding:2rem; 
        border-radius:10px; 
        color:white; 
        margin-bottom:2rem; 
        text-align:center;
    }
    .main-header h1 { color:white !important; margin:0; font-size:2.5rem;}
    .main-header p { color:rgba(255,255,255,0.9)!important; margin:0.5rem 0 0 0;}
    .metric-card{
        background:#f8fafc; 
        padding:1rem; 
        border-radius:8px; 
        border-left:4px solid #3b82f6; 
        margin-bottom:0.5rem;
    }
    .weather-card{
        background:#f0f9ff; 
        padding:1rem; 
        border-radius:8px; 
        border:1px solid #0ea5e9; 
        margin:0.5rem 0;
    }
    .calculation-box{
        background:#fef3c7; 
        padding:1rem; 
        border-radius:8px; 
        border:1px solid #f59e0b; 
        margin:0.5rem 0;
    }
    .efficiency-excellent{
        background:#d1fae5; 
        color:#059669; 
        font-weight:bold; 
        padding:0.5rem 1rem; 
        border-radius:8px; 
        border:2px solid #059669; 
        text-align:center; 
        margin:1rem 0;
    }
    .efficiency-good{
        background:#fef3c7; 
        color:#d97706; 
        font-weight:bold; 
        padding:0.5rem 1rem; 
        border-radius:8px; 
        border:2px solid #d97706; 
        text-align:center; 
        margin:1rem 0;
    }
    .efficiency-average{
        background:#e0f2fe; 
        color:#0369a1; 
        font-weight:bold; 
        padding:0.5rem 1rem; 
        border-radius:8px; 
        border:2px solid #0369a1; 
        text-align:center; 
        margin:1rem 0;
    }
    .efficiency-poor{
        background:#fee2e2; 
        color:#dc2626; 
        font-weight:bold; 
        padding:0.5rem 1rem; 
        border-radius:8px; 
        border:2px solid #dc2626; 
        text-align:center; 
        margin:1rem 0;
    }
    .date-header{
        background:linear-gradient(90deg,#10b981 0%,#059669 100%); 
        padding:1.5rem; 
        border-radius:10px; 
        color:white; 
        margin-bottom:1rem; 
        text-align:center;
    }
    .login-container{
        max-width:400px; 
        margin:2rem auto; 
        padding:2rem; 
        background:#f8fafc; 
        border-radius:10px; 
        box-shadow:0 4px 6px rgba(0,0,0,0.1);
    }
    .error-boundary{
        background:#fee2e2; 
        border:1px solid #dc2626; 
        padding:1rem; 
        border-radius:8px; 
        margin:1rem 0;
    }
    .kpi-slider-container{
        background:#f0fdf4; 
        padding:1.5rem; 
        border-radius:8px; 
        border:2px solid #10b981; 
        margin:1rem 0;
    }
    .version-info{
        background:#f8fafc;
        border-left:3px solid #6366f1;
        padding:0.5rem 1rem;
        margin:0.5rem 0;
        font-size:0.85rem;
    }
</style>
'''

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

import logging

def setup_logging():
    """Setup application logging"""
    log_file = os.path.join(DATA_DIR, 'app.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('TLS_App')

# Create logger
logger = setup_logging()
