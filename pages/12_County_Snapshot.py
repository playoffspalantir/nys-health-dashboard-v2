# pages/12_County_Snapshot.py
import streamlit as st
import pandas as pd
import pydeck as pdk
from modules import utils, ai_analysis
from pathlib import Path

# Remove st.set_page_config from this page file

st.title("🏥 County Health Snapshot")
st.write("A high-level overview of key health indicators for a selected county.")


@st.cache_data
def load_all_data():
    script_path = Path(__file__);
    project_root = script_path.parent.parent
    chirs_path = project_root / "data" / "chir_county_trend.xlsx"
    pa_path = project_root / "data" / "PreventionAgendaTrackingIndicators-CountyTrendData.csv"
    mch_path = project_root / "data" / "MCH-CountyTrendData.xlsx"
    geojson_path = project_root / "data" / "NYS_Counties.geojson"
    return {
        "chirs": utils.load_chirs_data(chirs_path), "pa": utils.load_prevention_data(pa_path),
        "mch": utils.load_mch_data(mch_path), "geojson": utils.load_county_geojson(geojson_path)
    }


data = load_all_data()
pa_df = data["pa"]

if pa_df is None:
    st.error("Could not load Prevention Agenda data, which is required for the county list.")
else:
    st.sidebar.header("Selection")
    all_counties = sorted(pa_df['County Name'].dropna().unique())
    default_county = "Dutchess" if "Dutchess" in all_counties else all_counties[0]
    selected_county = st.sidebar.selectbox("Select a County to Profile:", all_counties,
                                           index=all_counties.index(default_county))

    st.header(f"Health Profile for: {selected_county} County, NY")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Demographics (2022 ACS)")
        census_data = utils.get_census_snapshot(selected_county)
        st.metric("Total Population", census_data.get("Total Population", "N/A"))
        st.metric("Median Household Income", f"${census_data.get('Median Household Income', 'N/A')}")
        st.metric("Population Below Poverty", census_data.get("Population Below Poverty Level", "N/A"))

        st.subheader("Location")
        geojson = data.get("geojson")
        if geojson:
            county_name_for_geojson = f"{selected_county} County"
            county_feature = next(
                (f for f in geojson['features'] if f['properties']['name'] == county_name_for_geojson), None)
            if county_feature:
                bbox = county_feature['properties'].get('bbox', [-75.5, 42.5, -73.5, 41.5])
                center_lon, center_lat = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
                view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=6.5, pitch=0)

                geojson_layer = pdk.Layer('GeoJsonLayer', geojson,
                                          stroked=True, filled=True,
                                          get_fill_color='[200, 200, 200, 40]',
                                          get_line_color=[100, 100, 100], get_line_width=100,
                                          highlight_color=[65, 182, 196, 200], auto_highlight=True, pickable=True
                                          )
                st.pydeck_chart(pdk.Deck(layers=[geojson_layer], initial_view_state=view_state,
                                         map_style='mapbox://styles/mapbox/light-v10', tooltip={"text": "{name}"}))
            else:
                st.warning(f"Boundary data not found for {county_name_for_geojson}.")
        else:
            st.error("County boundary GeoJSON file could not be loaded.")

    with col2:
        st.subheader("Key Health Indicators")
        all_metrics = utils.get_snapshot_data(data["chirs"], data["pa"], data["mch"], selected_county)
        sub_col1, sub_col2, sub_col3, sub_col4 = st.columns(4)


        def display_metric(column, label):
            val, year, indicator_name = all_metrics.get(label, ("N/A", "", "Not Found"))
            column.metric(f"{label} ({year or '...'})", val if val != "N/A" else "No Data")


        # --- THIS IS THE FINAL, CORRECTED BLOCK ---
        # Distribute the 8 metrics across the 4 columns
        display_metric(sub_col1, "All Cancer Incidence")
        display_metric(sub_col2, "Premature Deaths (%)")
        display_metric(sub_col3, "Adult Smoking (%)")
        display_metric(sub_col4, "Adult Obesity (%)")

        # Use the new, correct MCH and PA metric labels for the second row
        display_metric(sub_col1, "Early Prenatal Care (%)")
        display_metric(sub_col2, "Infant Mortality Rate")
        display_metric(sub_col3, "Preterm Births (%)")
        display_metric(sub_col4, "Preventable Hospitalizations")

    st.divider()

    st.subheader("🤖 AI-Powered Executive Summary")
    if st.button(f"Generate Summary for {selected_county} County", use_container_width=True):
        with st.spinner("AI is analyzing..."):
            metrics_for_ai = {label: (val, year) for label, (val, year, name) in all_metrics.items()}
            metrics_for_ai.update({k: (v, "2022") for k, v in census_data.items()})
            summary = ai_analysis.summarize_county_snapshot(selected_county, metrics_for_ai)
            st.markdown(summary)