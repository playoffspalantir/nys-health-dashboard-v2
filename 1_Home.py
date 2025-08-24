# 1_🏠_Home.py
import streamlit as st

st.set_page_config(
    page_title="NYS Health Data Explorer",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Welcome to the NYS Health Data Explorer")

st.markdown("""
This application is an interactive tool designed for exploring, visualizing, and analyzing key public health datasets for New York State.

### What You Can Do:

- **Explore Dashboards:** Use the navigation sidebar on the left to choose from multiple health data dashboards, including CHIRS, the Prevention Agenda, and Maternal & Child Health.
- **Filter and Visualize:** Each dashboard provides dynamic filters to drill down into specific indicators, counties, and years, with interactive charts that update in real-time.
- **Generate AI Insights:** Leverage the power of AI to get a professional, epidemiologist-level summary of the data you are viewing.
- **Build Reports:** Save your AI-generated analyses from any dashboard. Then, navigate to the **Report Builder** page to view all your saved insights and export them as a single, professional HTML document.

### How to Get Started:
1.  **Select a dashboard** from the sidebar to begin your analysis.
2.  Use the **Data Filters** to customize your view.
3.  Click the **"Generate Insights"** button to get an AI summary.
4.  Click **"Save This Analysis"** to add it to your report.
5.  Visit the **"Report Builder"** to download your final report.
""")

st.info("This application is for informational purposes only and does not constitute medical or public health advice.")