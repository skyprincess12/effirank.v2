# pages/cost_input.py
import streamlit as st
from utils.data_persistence import DataPersistence
from config import logger, VALIDATION_RULES

def validate_input(field, value):
    """Validate input against rules"""
    rules = VALIDATION_RULES.get(field, {})
    if not rules:
        return True, value
    
    try:
        val = rules['type'](value)
        if val < rules.get('min', float('-inf')):
            return False, f"{field} must be >= {rules['min']}"
        if val > rules.get('max', float('inf')):
            return False, f"{field} must be <= {rules['max']}"
        return True, val
    except:
        return False, f"{field} must be a valid number"

@st.cache_data(ttl=60)
def get_locations_list(locations_data):
    """Cached location list"""
    return sorted(locations_data.keys())

def cost_input_page(weather_api, weather_locations):
    """Cost input page"""
    try:
        st.title("💰 Cost Input")
        
        locations_data = st.session_state.locations_data
        locations = get_locations_list(locations_data)
        
        selected_location = st.selectbox("Select Location", locations)
        
        if selected_location:
            loc_data = locations_data[selected_location]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Cost Inputs")
                brgy_fee = st.number_input("Barangay Fee", value=float(loc_data['barangay_fee']), min_value=0.0)
                rental = st.number_input("Rental Rate", value=float(loc_data['rental_rate']), min_value=0.0)
                tls_opn = st.number_input("TLS OPN", value=float(loc_data['tls_opn']), min_value=0.0)
                drivers = st.number_input("Drivers/Hauler", value=float(loc_data['drivers_hauler']), min_value=0.0)
                
            with col2:
                st.subheader("Fuel & Productivity")
                fuel_cons = st.number_input("Fuel Consumption", value=float(loc_data['fuel_cons']), min_value=0.0)
                diesel_price = st.number_input("Diesel Price", value=float(loc_data['diesel_price']), min_value=0.0)
                ta_inc = st.number_input("TA Inc", value=float(loc_data['ta_inc']), min_value=0.0)
                lkgtc = st.number_input("LKGTC", value=float(loc_data['lkgtc']), min_value=0.0)
            
            if st.button("💾 Save Data"):
                locations_data[selected_location] = {
                    'region': loc_data['region'],
                    'barangay_fee': brgy_fee,
                    'rental_rate': rental,
                    'tls_opn': tls_opn,
                    'drivers_hauler': drivers,
                    'fuel_cons': fuel_cons,
                    'diesel_price': diesel_price,
                    'ta_inc': ta_inc,
                    'lkgtc': lkgtc
                }
                st.session_state.locations_data = locations_data
                DataPersistence.save_locations_data(locations_data)
                st.success(f"✅ Data saved for {selected_location}")
                logger.info(f"Cost data saved for {selected_location}")
    
    except Exception as e:
        logger.error(f"Cost input error: {e}")
        st.error("Error loading cost input page")
