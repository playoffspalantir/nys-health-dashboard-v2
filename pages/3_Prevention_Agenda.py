# pages/3_Prevention_Agenda.py
import streamlit as st
from modules.config import CONFIGS
from modules.ui_components import render_dashboard

st.title("🎯 Prevention Agenda Trends Dashboard")

config = CONFIGS["Prevention Agenda Trends"]
df = config["loader_func"](config["file_path"])

if df is not None:
    if "last_dashboard" not in st.session_state or st.session_state.last_dashboard != "Prevention Agenda Trends":
        st.session_state.current_ai_analysis = None
    st.session_state.last_dashboard = "Prevention Agenda Trends"

    render_dashboard(config, df)
