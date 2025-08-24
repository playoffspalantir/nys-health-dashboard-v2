# pages/12_🏆_CHR_Trends.py
import streamlit as st
import pandas as pd
import altair as alt
from modules import utils
from pathlib import Path

st.title("🏆 County Health Rankings - Trend Explorer")
st.write("Visualize trends over time for key health measures from the County Health Rankings & Roadmaps program.")


# --- Load the Data ---
@st.cache_data
def load_data():
    script_path = Path(__file__)
    project_root = script_path.parent.parent
    # --- FIX IS HERE: Use the exact filename from your disk ---
    data_file = project_root / "data" / "chr_trends_csv_2024.csv"
    return utils.load_chr_trend_data(data_file)

df = load_data()

if df is not None:
    # --- Sidebar for User Selections ---
    st.sidebar.header("Selections")

    # Let user select a measure to analyze
    all_measures = sorted(df['measurename'].unique())
    selected_measure = st.sidebar.selectbox("Select a Health Measure:", all_measures)

    # Let user select counties
    all_counties = sorted(df['county'].dropna().unique())
    default_counties = ["Dutchess", "Orange", "Rockland", "Putnam", "Sullivan", "Westchester", "Ulster"]
    selected_counties = st.sidebar.multiselect(
        "Select Counties to Compare:",
        options=all_counties,
        default=[c for c in default_counties if c in all_counties]
    )

    if not selected_counties:
        st.warning("Please select at least one county.")
    else:
        # --- Filter Data ---
        filtered_df = df[
            (df['measurename'] == selected_measure) &
            (df['county'].isin(selected_counties))
            ]

        st.header(f"Trend for: {selected_measure}")

        if not filtered_df.empty:
            # --- Create and Display Chart ---
            chart = alt.Chart(filtered_df).mark_line(point=True).encode(
                x=alt.X('year:O', title='Year'),  # 'O' for Ordinal to treat year as a category
                y=alt.Y('rawvalue:Q', title='Value (Lower is generally better)', scale=alt.Scale(zero=False)),
                color=alt.Color('county:N', title='County'),
                tooltip=['county', 'year', 'rawvalue']
            ).properties(
                title=f"Trend of {selected_measure}"
            ).interactive()

            st.altair_chart(chart, use_container_width=True)

            # --- Data Table Expander ---
            with st.expander("View Detailed Trend Data"):
                st.dataframe(filtered_df[['yearspan', 'county', 'rawvalue', 'cilow', 'cihigh']])
        else:
            st.info("No data available for the selected measure and counties.")
else:
    st.error("Could not load the County Health Rankings trend data.")