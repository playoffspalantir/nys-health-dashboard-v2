# 1_Home.py
import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="NYS Health Data Explorer",
    page_icon="🗽",  # NY Liberty Torch Icon
    layout="wide"
)

# --- Main Title ---
st.title("🗽 Welcome to the NYS Community Health Explorer")
st.markdown("---")

st.markdown("""
A suite of interactive tools for public health professionals, community leaders, and residents to explore, understand, and act upon the health data that shapes communities across New York State.
""")
st.markdown("---")

# --- Feature Showcase using Columns ---
st.header("What This Application Provides")
st.write("\n")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📊 Data Exploration Tools")
    st.write("Visualize trends and compare counties across multiple key public health datasets.")
    st.page_link("pages/2_CHIRS_Indicators.py", label="CHIRS Indicators", icon="📈")
    st.page_link("pages/3_Prevention_Agenda.py", label="Prevention Agenda Trends", icon="🎯")
    st.page_link("pages/4_MCH_Dashboard.py", label="Maternal & Child Health", icon="🤰")
    st.page_link("pages/6_Census_Explorer.py", label="Census Demographics", icon="🌎")
    st.page_link("pages/11_CHR_Trends.py", label="County Health Rankings", icon="🏆")

with col2:
    st.subheader("⚖️ Analysis & Prioritization")
    st.write("Synthesize data and make informed decisions with AI-powered summaries and structured planning frameworks.")
    st.page_link("pages/12_County_Snapshot.py", label="County Health Snapshot", icon="🏥")
    st.page_link("pages/9_Hanlon_Prioritization.py", label="Hanlon Prioritization Tool", icon="🧮")
    st.page_link("pages/10_SDoH_Explorer.py", label="Social Determinants of Health", icon="📊") # Corrected page number for SDoH

with col3:
    st.subheader("✍️ Strategic Planning & Reporting")
    st.write("Translate data insights into actionable plans and generate comprehensive reports.")
    st.page_link("pages/7_CHIP_Wizard.py", label="CHIP Drafting Wizard", icon="✍️")
    st.page_link("pages/5_Report_Builder.py", label="Consolidated Report Builder", icon="📋")


st.markdown("---")

# --- Getting Started Guide ---
st.header("Recommended Workflow")
st.markdown("""
1.  **Explore:** Use the **Data Exploration Tools** to identify trends and disparities.
2.  **Analyze:** Use the **County Snapshot** and **Hanlon** tools to synthesize findings and prioritize issues.
3.  **Plan:** Draft specific goals and strategies with the **CHIP Wizard**.
4.  **Report:** Collect all saved analyses in the **Report Builder** and export the final document.
""")