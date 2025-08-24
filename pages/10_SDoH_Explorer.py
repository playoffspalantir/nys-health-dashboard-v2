# pages/10_📊_SDoH_Explorer.py
import streamlit as st
import pandas as pd
import altair as alt
from modules import utils, ai_analysis

st.set_page_config(page_title="SDoH Explorer", page_icon="📊", layout="wide")
st.title("📊 Social Determinants of Health (SDoH) Explorer")
st.write(
    "Compare key socio-economic indicators across New York counties using data from the US Census Bureau's American Community Survey (ACS).")

# --- Sidebar for User Inputs ---
st.sidebar.header("Data Selection")

# Use a fixed dataset for SDoH for consistency
DATASET_KEY = "acs/acs5"
dataset_info = utils.VALID_DATASETS[DATASET_KEY]

# Let the user select a year
year = st.sidebar.selectbox(f"Select Year for {dataset_info['name']}", options=dataset_info["years"])

# --- Define Core SDoH Variables ---
SDOH_VARIABLES = {
    "B19013_001E": "Median Household Income ($)",
    "B17001_002E": "Population Below Poverty Level",
    "B25003_002E": "Owner-Occupied Housing Units",
    "B25003_003E": "Renter-Occupied Housing Units",
    "B15003_022E": "Population with Bachelor's Degree or Higher",
    "C27001_001E": "Civilian Population with Health Insurance",
    "B01003_001E": "Total Population"  # Often useful for context or calculating percentages
}

# Fetch all available variables to ensure our defaults exist
all_variables = utils.fetch_census_variables(DATASET_KEY, year)
# Filter our SDoH list to only those available in the selected year's data
available_sdoh_vars = {code: label for code, label in SDOH_VARIABLES.items() if code in all_variables}

selected_variables = st.sidebar.multiselect(
    "Select SDoH Variables",
    options=list(available_sdoh_vars.keys()),
    format_func=lambda x: f"{x} - {available_sdoh_vars.get(x, '')}",
    default=list(available_sdoh_vars.keys())  # Default to all available SDoH vars
)

st.sidebar.header("Geography Selection")
default_ny_counties = ["Dutchess", "Orange", "Rockland", "Putnam", "Sullivan", "Westchester", "Ulster"]
selected_counties = st.sidebar.multiselect("Select NY Counties", options=list(utils.NY_COUNTY_FIPS_MAP.keys()),
                                           default=default_ny_counties)

# --- Main Content Area ---
if st.sidebar.button("🚀 Fetch SDoH Data", use_container_width=True):
    if selected_variables and selected_counties:

        # Define API parameters
        geo_for_param = "county:*"
        geo_in_param = {"in": f"state:{utils.STATE_FIPS_MAP['New York']}"}
        fips_to_filter = [utils.NY_COUNTY_FIPS_MAP[c] for c in selected_counties]

        # Fetch the data
        df = utils.fetch_census_data(DATASET_KEY, year, selected_variables, geo_for_param, geo_in_param)

        # Filter for the selected counties
        if not df.empty and "county" in df.columns:
            df = df[df["county"].isin(fips_to_filter)].copy()

        if not df.empty:
            st.success(f"Successfully fetched SDoH data for {len(df)} counties.")

            # Clean up the dataframe for display and charting
            display_df = df.set_index('NAME')
            # Rename columns to be human-readable
            display_df.rename(columns=available_sdoh_vars, inplace=True)

            st.subheader("Raw SDoH Data")
            st.dataframe(display_df)

            # --- Visualization ---
            st.subheader("Indicator Comparison")
            # Let user choose which indicator to plot
            y_axis_var_label = st.selectbox(
                "Choose an indicator to visualize:",
                options=display_df.columns.tolist()
            )

            if y_axis_var_label:
                # Need to reset index to make 'NAME' a column for Altair
                chart_df = display_df.reset_index()

                chart = alt.Chart(chart_df).mark_bar().encode(
                    x=alt.X('NAME:N', title='County', sort='-y'),
                    y=alt.Y(f'{y_axis_var_label}:Q', title=y_axis_var_label),
                    tooltip=['NAME', alt.Tooltip(y_axis_var_label, format=',')]  # Format tooltip for numbers
                ).properties(
                    title=f"{y_axis_var_label} in {year}"
                ).interactive()
                st.altair_chart(chart, use_container_width=True)

            # --- AI Analysis Section ---
            st.divider()
            st.subheader("🤖 AI-Powered Socio-Economic Summary")
            if st.button("Generate AI Summary"):
                with st.spinner("AI is analyzing the socio-economic context..."):
                    ai_summary = ai_analysis.analyze_sdoh_data(display_df, year, selected_counties)
                    st.markdown(ai_summary)
        else:
            st.error("No data returned from API. This can sometimes happen for specific years or variables.")
    else:
        st.warning("Please select at least one variable and one county.")
else:
    st.info("Select your desired variables and counties, then click 'Fetch Data'.")