import streamlit as st
import pandas as pd
from src.data_processor import get_column_mapping

def manual_entry_ui():
    """Renders the manual entry interface."""
    st.subheader("📝 Manual Trade Entry")
    st.write("Enter your trades directly in the table below. You can add rows as needed.")
    
    # Define the template columns based on the mapping
    col_map = get_column_mapping()
    default_cols = ["date", "market", "direction", "entry", "exit_price", "quantity", "pnl", "notes"]
    
    # Create an empty dataframe with these columns
    if 'manual_df' not in st.session_state:
        st.session_state.manual_df = pd.DataFrame(columns=default_cols)
        # Add a couple of empty rows to start
        st.session_state.manual_df = pd.concat([
            st.session_state.manual_df, 
            pd.DataFrame([["" for _ in default_cols]], columns=default_cols),
            pd.DataFrame([["" for _ in default_cols]], columns=default_cols)
        ], ignore_index=True)

    # st.data_editor allows users to edit the dataframe directly
    edited_df = st.data_editor(
        st.session_state.manual_df, 
        num_rows="dynamic",
        use_container_width=True,
        key="trade_editor"
    )
    
    if st.button("Submit Manual Logs"):
        # Remove empty rows or rows with all empty strings
        clean_df = edited_df.replace("", pd.NA).dropna(how='all')
        if not clean_df.empty:
            st.session_state.dataset = clean_df
            st.success("✅ Manual logs loaded! Click 'Get Full Analysis' below.")
        else:
            st.warning("⚠️ Please enter some trade data before submitting.")
    
    return st.session_state.get('dataset')

def sidebar_credits():
    """Renders credits and links in the sidebar."""
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🚀 About TradeTrack")
        st.write("An advanced trading journal for data-driven traders.")
        st.markdown("[Deployment Link](https://tradetrack.streamlit.app/)")
        st.info("Tip: Use the 'Manual Entry' tab if you don't have a CSV file ready.")
        
        if st.button("🔄 Reset / Clear Data"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
