# modules/utils.py
import streamlit as st
import pandas as pd
import altair as alt
import requests
import re

# --- Define a custom chart theme ---
def my_custom_theme():
    return {
        'config': {
            'view': {
                'continuousWidth': 400,
                'continuousHeight': 300,
                'stroke': None  # No border around the chart
            },
            'title': {
                'fontSize': 16,
                'fontWeight': 'bold',
                'anchor': 'start' # Align title to the left
            },
            'axis': {
                'labelFontSize': 12,
                'titleFontSize': 14,
                'gridColor': '#e6e6e6' # Lighter grid lines
            },
            'line': {
                'strokeWidth': 3
            },
            'point': {
                'size': 75,
                'filled': True
            }
        }
    }

# Register and enable the theme
alt.themes.register('my_custom_theme', my_custom_theme)
alt.themes.enable('my_custom_theme')

# --- Constants for Census API ---
# (Pasting again for completeness)
CENSUS_API_BASE_URL = "https://api.census.gov/data"
VALID_DATASETS = {
    "acs/acs5": {"name": "ACS 5-Year Estimates", "years": ["2022", "2021", "2020", "2019"]},
    "acs/acs1": {"name": "ACS 1-Year Estimates", "years": ["2022", "2021", "2019"]},
    "dec/pl": {"name": "Decennial Census (PL)", "years": ["2020", "2010"]},
    "pep/population": {"name": "Population Estimates", "years": ["2022", "2021"]}
}
STATE_FIPS_MAP = {"New York": "36", "New Jersey": "34", "Connecticut": "09", "Pennsylvania": "42",
                  "Massachusetts": "25", "Alabama": "01", "Alaska": "02", "Arizona": "04", "Arkansas": "05",
                  "California": "06", "Colorado": "08", "Delaware": "10", "District of Columbia": "11", "Florida": "12",
                  "Georgia": "13", "Hawaii": "15", "Idaho": "16", "Illinois": "17", "Indiana": "18", "Iowa": "19",
                  "Kansas": "20", "Kentucky": "21", "Louisiana": "22", "Maine": "23", "Maryland": "24",
                  "Michigan": "26", "Minnesota": "27", "Mississippi": "28", "Missouri": "29", "Montana": "30",
                  "Nebraska": "31", "Nevada": "32", "New Hampshire": "33", "New Mexico": "35", "North Carolina": "37",
                  "North Dakota": "38", "Ohio": "39", "Oklahoma": "40", "Oregon": "41", "Rhode Island": "44",
                  "South Carolina": "45", "South Dakota": "46", "Tennessee": "47", "Texas": "48", "Utah": "49",
                  "Vermont": "50", "Virginia": "51", "Washington": "53", "West Virginia": "54", "Wisconsin": "55",
                  "Wyoming": "56"}
NY_COUNTY_FIPS_MAP = {"Albany": "001", "Allegany": "003", "Bronx": "005", "Broome": "007", "Cattaraugus": "009",
                      "Cayuga": "011", "Chautauqua": "013", "Chemung": "015", "Chenango": "017", "Clinton": "019",
                      "Columbia": "021", "Cortland": "023", "Delaware": "025", "Dutchess": "027", "Erie": "029",
                      "Essex": "031", "Franklin": "033", "Fulton": "035", "Genesee": "037", "Greene": "039",
                      "Hamilton": "041", "Herkimer": "043", "Jefferson": "045", "Kings (Brooklyn)": "047",
                      "Lewis": "049", "Livingston": "051", "Madison": "053", "Monroe": "055", "Montgomery": "057",
                      "Nassau": "059", "New York (Manhattan)": "061", "Niagara": "063", "Oneida": "065",
                      "Onondaga": "067", "Ontario": "069", "Orange": "071", "Orleans": "073", "Oswego": "075",
                      "Otsego": "077", "Putnam": "079", "Queens": "081", "Rensselaer": "083",
                      "Richmond (Staten Island)": "085", "Rockland": "087", "Saratoga": "091", "Schenectady": "093",
                      "Schoharie": "095", "Schuyler": "097", "Seneca": "099", "St. Lawrence": "089", "Steuben": "101",
                      "Suffolk": "103", "Sullivan": "105", "Tioga": "107", "Tompkins": "109", "Ulster": "111",
                      "Warren": "113", "Washington": "115", "Wayne": "117", "Westchester": "119", "Wyoming": "121",
                      "Yates": "123"}


def clean_variable_label(label: str) -> str:
    if not isinstance(label, str): return "N/A"
    readable_label = label.replace("Estimate!!", "").replace("Total:!!", "").replace("!!", " | ")
    return re.sub(r'\s+', ' ', readable_label).strip()


@st.cache_data
def fetch_census_variables(dataset: str, year: str):
    url = f"{CENSUS_API_BASE_URL}/{year}/{dataset}/variables.json"
    try:
        response = requests.get(url);
        response.raise_for_status()
        data = response.json().get("variables", {})
        return {var: clean_variable_label(info.get("label", "")) for var, info in data.items() if
                "label" in info and not var.endswith(("A", "M", "MA", "EA")) and (
                            var.endswith("E") or var.endswith("N"))}
    except requests.exceptions.RequestException:
        st.sidebar.warning(f"Could not automatically load variables for {dataset} {year}.");
        return {}


@st.cache_data
def fetch_census_data(dataset: str, year: str, variables: list, geo_for: str, geo_in: dict = None):
    if not variables: return pd.DataFrame()
    if "NAME" not in variables: variables.insert(0, "NAME")
    params = {"get": ",".join(variables), "for": geo_for}
    if geo_in: params.update(geo_in)
    url = f"{CENSUS_API_BASE_URL}/{year}/{dataset}"
    try:
        response = requests.get(url, params=params);
        response.raise_for_status()
        data = response.json()
        if len(data) < 2: return pd.DataFrame()
        df = pd.DataFrame(data[1:], columns=data[0])
        for col in variables:
            if col != 'NAME' and col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except requests.exceptions.HTTPError as e:
        st.error(f"API Error: {e}. This combination may not be supported.");
        return pd.DataFrame()
    except (KeyError, IndexError, requests.exceptions.JSONDecodeError):
        st.error("API Error: Received unexpected data format.");
        return pd.DataFrame()


# --- Data Loading Functions ---
@st.cache_data
def load_chirs_data(file_path):
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        for col in ['Geographic area', 'Year', 'Topic Area', 'Indicator Title', 'Data Source', 'Data Notes']:
            if col in df.columns: df[col] = df[col].astype(str).replace('nan', '')
        return df
    except Exception as e:
        st.error(f"Error loading CHIRS data: {e}");
        return None


@st.cache_data
def load_prevention_data(file_path):
    try:
        df = pd.read_csv(file_path, encoding='latin-1', dtype=str)
        df.columns = df.columns.str.strip()
        df['Percentage/Rate/Ratio'] = pd.to_numeric(df['Percentage/Rate/Ratio'], errors='coerce')
        df['2024 Objective'] = pd.to_numeric(df['2024 Objective'], errors='coerce')
        df['Data Years'] = df['Data Years'].astype(str)
        return df
    except Exception as e:
        st.error(f"Error loading Prevention Agenda data: {e}");
        return None


@st.cache_data
def load_mch_data(file_path):
    try:
        df = pd.read_excel(file_path, engine='openpyxl', header=0)
        df.columns = df.columns.str.strip()
        df['Percentage/Rate'] = pd.to_numeric(df['Percentage/Rate'], errors='coerce')
        df['MCH Objective'] = pd.to_numeric(df['MCH Objective'], errors='coerce')
        df['Data Years'] = df['Data Years'].astype(str)
        for col in ['Data Comments', 'Date Source']:
            if col in df.columns: df[col] = df[col].astype(str).replace('nan', '')
        return df
    except Exception as e:
        st.error(f"Error loading MCH data: {e}");
        return None


# --- Chart Creation ---
def create_chart(df, config):
    # ... (code is unchanged)
    chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X(f"{config['year_col']}:N", title='Year', sort=alt.SortField(config['year_col'])),
        y=alt.Y(f"{config['value_col']}:Q", title=config['y_axis_label'], scale=alt.Scale(zero=False)),
        color=alt.Color(f"{config['county_col']}:N", title='County'),
        tooltip=[config['county_col'], config['year_col'], config['value_col']])
    if config.get("objective_col"):
        objective_line = alt.Chart(df).mark_rule(color=config['objective_color'], strokeDash=[5, 5]).encode(
            y=f"mean({config['objective_col']}):Q")
        objective_text = objective_line.mark_text(align='left', baseline='middle', dx=7,
                                                  text=config['objective_label']).encode(
            color=alt.value(config['objective_color']))
        return (chart + objective_line + objective_text).interactive()
    return chart.interactive()


# --- CHIP Helper Functions ---
def get_pa_data_for_chip(df, priority_area, focus_area, indicator_name, county_name):
    """Fetches objective, recent data, and trend data for the CHIP."""
    objective_text = "Not available"
    data_point_text = "Not available"
    trend_df = pd.DataFrame()

    if df is None: return objective_text, data_point_text, trend_df

    indicator_df = df[
        (df['Priority Area'] == priority_area) & (df['Focus Area'] == focus_area) & (df['Indicator'] == indicator_name)]
    if not indicator_df.empty:
        objective = indicator_df['2024 Objective'].iloc[0]
        measure = indicator_df['Measure Unit'].iloc[0]
        if pd.notna(objective): objective_text = f"{objective} {measure}"

        county_df = indicator_df[indicator_df['County Name'] == county_name].copy()
        if not county_df.empty:
            county_df['Data Years'] = pd.to_numeric(county_df['Data Years'], errors='coerce')
            trend_df = county_df.sort_values(by='Data Years', ascending=False).head(5)
            latest_data = trend_df.iloc[0]
            value = latest_data['Percentage/Rate/Ratio']
            year = int(latest_data['Data Years'])
            if pd.notna(value): data_point_text = f"{value} {measure} ({year})"
    return objective_text, data_point_text, trend_df