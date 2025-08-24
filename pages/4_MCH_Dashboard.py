# pages/4_MCH_Dashboard.py
import streamlit as st
from modules.config import CONFIGS
from modules.ui_components import render_dashboard

st.title("🤰 Maternal & Child Health (MCH) Dashboard")

config = CONFIGS["MCH Dashboard"]
df = config["loader_func"](config["file_path"])

if df is not None:
    if "last_dashboard" not in st.session_state or st.session_state.last_dashboard != "MCH Dashboard":
        st.session_state.current_ai_analysis = None
    st.session_state.last_dashboard = "MCH Dashboard"

    render_dashboard(config, df)