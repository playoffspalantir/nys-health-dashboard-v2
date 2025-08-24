# pages/6_🌎_Census_Explorer.py
import streamlit as st
import pandas as pd
import altair as alt
from modules import utils  # Import our shared utility functions

st.set_page_config(page_title="Census Explorer", page_icon="🌎", layout="wide")
st.title("🌎 US Census Data Explorer")
st.write("An interface to query, visualize, and compare data directly from the US Census Bureau API.")

# --- Sidebar for User Inputs ---
st.sidebar.header("Data Selection")
dataset_key = st.sidebar.selectbox("Select Dataset", options=list(utils.VALID_DATASETS.keys()),
                                   format_func=lambda x: utils.VALID_DATASETS[x]["name"])
year = st.sidebar.selectbox("Select Year", options=utils.VALID_DATASETS[dataset_key]["years"])

# Fetch variable options and create the selector
variable_options = utils.fetch_census_variables(dataset_key, year)
if not variable_options:
    st.sidebar.info("Enter variable codes manually if they fail to load.")
    # Fallback to manual entry if API for variables fails
    selected_variables_raw = st.sidebar.text_input("Enter Variable Codes (comma-separated)", "B01001_001E")
    selected_variables = [v.strip() for v in selected_variables_raw.split(",")]
else:
    # A cleaner multiselect for variables
    selected_variables = st.sidebar.multiselect("Select Variables",
                                                options=variable_options.keys(),
                                                format_func=lambda x: f"{x} - {variable_options.get(x, '')}",
                                                default=["B01001_001E"] if "B01001_001E" in variable_options else [])

st.sidebar.header("Geography Selection")
geo_level = st.sidebar.selectbox("Geography Level", ["All NY Counties", "Specific NY Counties", "All States"])

# Determine API parameters based on geography selection
geo_for_param, geo_in_param, fips_to_filter = None, None, None
if geo_level == "All States":
    geo_for_param = "state:*"
elif geo_level == "All NY Counties":
    geo_for_param = "county:*"
    geo_in_param = {"in": f"state:{utils.STATE_FIPS_MAP['New York']}"}
elif geo_level == "Specific NY Counties":
    default_ny_counties = ["Dutchess", "Orange", "Rockland", "Putnam", "Sullivan", "Westchester", "Ulster"]
    selected_counties = st.sidebar.multiselect("Select NY Counties", options=list(utils.NY_COUNTY_FIPS_MAP.keys()),
                                               default=default_ny_counties)
    if selected_counties:
        geo_for_param = "county:*"
        geo_in_param = {"in": f"state:{utils.STATE_FIPS_MAP['New York']}"}
        fips_to_filter = [utils.NY_COUNTY_FIPS_MAP[c] for c in selected_counties]
    else:
        st.sidebar.warning("Please select at least one NY county.")

# --- Main Content Area ---
if st.sidebar.button("🚀 Fetch Census Data", use_container_width=True):
    if geo_for_param and selected_variables:
        df = utils.fetch_census_data(dataset_key, year, selected_variables, geo_for_param, geo_in_param)

        # After fetching, perform local filtering for specific counties
        if fips_to_filter and not df.empty and "county" in df.columns:
            df = df[df["county"].isin(fips_to_filter)].copy()

        if not df.empty:
            st.success(f"Successfully fetched {len(df)} records.")
            st.subheader(f"Data for {', '.join(selected_variables)}")
            st.dataframe(df)

            # --- Data Visualization with Altair ---
            # Ensure we only try to plot the numeric variables that were actually returned
            numeric_cols = [col for col in selected_variables if
                            col in df.columns and pd.api.types.is_numeric_dtype(df[col])]

            if numeric_cols:
                st.subheader("Visualization")
                # Let user choose which variable to plot on the Y-axis
                y_axis_var = st.selectbox("Choose a variable to plot:", numeric_cols,
                                          format_func=lambda x: f"{x} - {variable_options.get(x, '')}")

                if y_axis_var:
                    chart = alt.Chart(df).mark_bar().encode(
                        x=alt.X('NAME:N', title='Geography', sort='-y'),
                        y=alt.Y(f'{y_axis_var}:Q', title=variable_options.get(y_axis_var, y_axis_var)),
                        tooltip=['NAME'] + numeric_cols
                    ).properties(
                        title=f"{variable_options.get(y_axis_var, y_axis_var)} in {year}"
                    ).interactive()
                    st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No numeric variables selected or returned to visualize.")
        else:
            st.error("No data returned from API. Please check your selections or try a different combination.")
    else:
        st.warning("Please ensure you have selected at least one variable and a valid geography.")
else:
    st.info("Select your desired dataset, year, variables, and geography, then click 'Fetch Data'.")