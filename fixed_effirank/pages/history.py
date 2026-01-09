# pages/history.py
import streamlit as st
from config import logger

def history_page(db_manager, passcode):
    """History page"""
    try:
        st.title("📜 History")
        
        snapshots = st.session_state.get('history_snapshots', [])
        
        if snapshots:
            st.write(f"Total snapshots: {len(snapshots)}")
            
            for i, snap in enumerate(snapshots):
                with st.expander(f"Snapshot {i+1} - {snap.get('date', 'Unknown')}"):
                    if 'rankings_df' in snap:
                        st.dataframe(snap['rankings_df'])
        else:
            st.info("No history available")
        
        st.markdown("---")
        if st.button("🗑️ Clear All History"):
            user_passcode = st.text_input("Enter passcode", type="password")
            if user_passcode == passcode:
                st.session_state.history_snapshots = []
                st.success("History cleared")
    
    except Exception as e:
        logger.error(f"History page error: {e}")
        st.error("Error loading history")
