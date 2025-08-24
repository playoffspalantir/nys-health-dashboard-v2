# pages/2_📈_CHIRS_Indicators.py
import streamlit as st
from modules.config import CONFIGS
from modules.ui_components import render_dashboard

st.title("📈 CHIRS Indicators Dashboard")

# Get the configuration for this specific dashboard
config = CONFIGS["CHIRS Indicators"]

# Load the data using the function defined in the config
df = config["loader_func"](config["file_path"])

# Render the main part of the app
if df is not None:
    if "last_dashboard" not in st.session_state or st.session_state.last_dashboard != "CHIRS Indicators":
        st.session_state.current_ai_analysis = None
    st.session_state.last_dashboard = "CHIRS Indicators"

    render_dashboard(config, df)