# pages/cost_analysis.py
import streamlit as st
import plotly.express as px
import pandas as pd
from config import logger

@st.cache_data(ttl=60)
def create_cost_chart(locations_data):
    """Create cached cost comparison chart"""
    data = []
    for loc, vals in locations_data.items():
        if vals['lkgtc'] > 0:
            data.append({'Location': loc, 'Total Cost': vals['tls_opn'] + vals['drivers_hauler'] + vals['ta_inc']})
    
    df = pd.DataFrame(data)
    return px.bar(df, x='Location', y='Total Cost', title='Cost Comparison')

def analysis_page():
    """Cost analysis page"""
    try:
        st.title("📊 Cost Analysis")
        
        fig = create_cost_chart(st.session_state.locations_data)
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        logger.error(f"Analysis page error: {e}")
        st.error("Error loading analysis")
