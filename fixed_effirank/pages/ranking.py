# pages/ranking.py
import streamlit as st
import pandas as pd
from utils.kpi_calculator import KPICalculator
from config import logger

@st.cache_data(ttl=60)
def calculate_rankings(locations_data, cost_weight, lkg_weight):
    """Cached ranking calculations"""
    data = []
    for loc, vals in locations_data.items():
        if vals['lkgtc'] > 0:
            metrics = KPICalculator.calculate_metrics(vals)
            data.append({
                'Location': loc,
                'Region': vals['region'],
                'Total Cost': metrics['total_cost'],
                'LKGTC': vals['lkgtc'],
                'Cost/LKG': metrics['cost_per_lkg']
            })
    
    return KPICalculator.rank_tls(data, cost_weight, lkg_weight)

def ranking_page(weather_api, weather_locations, db_manager):
    """Efficiency ranking page"""
    try:
        st.title("🏆 Efficiency Ranking")
        
        col1, col2 = st.columns(2)
        with col1:
            cost_weight = st.slider("Cost Weight %", 0, 100, st.session_state.cost_weight, 25)
        with col2:
            lkg_weight = st.slider("LKG Weight %", 0, 100, st.session_state.lkg_weight, 25)
        
        st.session_state.cost_weight = cost_weight
        st.session_state.lkg_weight = lkg_weight
        
        df = calculate_rankings(st.session_state.locations_data, cost_weight, lkg_weight)
        
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No data available for ranking")
    
    except Exception as e:
        logger.error(f"Ranking page error: {e}")
        st.error("Error calculating rankings")
