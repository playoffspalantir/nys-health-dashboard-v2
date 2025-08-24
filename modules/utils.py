# modules/utils.py
import streamlit as st
import pandas as pd
import altair as alt
import requests
import re
import json

# ==============================================================================
# --- Constants ---
# ==============================================================================
CENSUS_API_BASE_URL = "https://api.census.gov/data"
VALID_DATASETS = {
    "acs/acs5": {"name": "ACS 5-Year Estimates", "years": ["2022", "2021", "2020", "2019"]},
    "acs/acs1": {"name": "ACS 1-Year Estimates", "years": ["2022", "2021", "2019"]},
    "dec/pl": {"name": "Decennial Census (PL)", "years": ["2020", "2010"]},
    "pep/population": {"name": "Population Estimates", "years": ["2022", "2021"]}
}
STATE_FIPS_MAP = { "New York": "36", "New Jersey": "34", "Connecticut": "09", "Pennsylvania": "42", "Massachusetts": "25", "Alabama": "01", "Alaska": "02", "Arizona": "04", "Arkansas": "05", "California": "06", "Colorado": "08", "Delaware": "10", "District of Columbia": "11", "Florida": "12", "Georgia": "13", "Hawaii": "15", "Idaho": "16", "Illinois": "17", "Indiana": "18", "Iowa": "19", "Kansas": "20", "Kentucky": "21", "Louisiana": "22", "Maine": "23", "Maryland": "24", "Michigan": "26", "Minnesota": "27", "Mississippi": "28", "Missouri": "29", "Montana": "30", "Nebraska": "31", "Nevada": "32", "New Hampshire": "33", "New Mexico": "35", "North Carolina": "37", "North Dakota": "38", "Ohio": "39", "Oklahoma": "40", "Oregon": "41", "Rhode Island": "44", "South Carolina": "45", "South Dakota": "46", "Tennessee": "47", "Texas": "48", "Utah": "49", "Vermont": "50", "Virginia": "51", "Washington": "53", "West Virginia": "54", "Wisconsin": "55", "Wyoming": "56" }
NY_COUNTY_FIPS_MAP = { "Albany": "001", "Allegany": "003", "Bronx": "005", "Broome": "007", "Cattaraugus": "009", "Cayuga": "011", "Chautauqua": "013", "Chemung": "015", "Chenango": "017", "Clinton": "019", "Columbia": "021", "Cortland": "023", "Delaware": "025", "Dutchess": "027", "Erie": "029", "Essex": "031", "Franklin": "033", "Fulton": "035", "Genesee": "037", "Greene": "039", "Hamilton": "041", "Herkimer": "043", "Jefferson": "045", "Kings (Brooklyn)": "047", "Lewis": "049", "Livingston": "051", "Madison": "053", "Monroe": "055", "Montgomery": "057", "Nassau": "059", "New York (Manhattan)": "061", "Niagara": "063", "Oneida": "065", "Onondaga": "067", "Ontario": "069", "Orange": "071", "Orleans": "073", "Oswego": "075", "Otsego": "077", "Putnam": "079", "Queens": "081", "Rensselaer": "083", "Richmond (Staten Island)": "085", "Rockland": "087", "Saratoga": "091", "Schenectady": "093", "Schoharie": "095", "Schuyler": "097", "Seneca": "099", "St. Lawrence": "089", "Steuben": "101", "Suffolk": "103", "Sullivan": "105", "Tioga": "107", "Tompkins": "109", "Ulster": "111", "Warren": "113", "Washington": "115", "Wayne": "117", "Westchester": "119", "Wyoming": "121", "Yates": "123" }

# ==============================================================================
# --- Data Loading Functions ---
# ==============================================================================
@st.cache_data
def load_chirs_data(file_path):
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        for col in ['Geographic area', 'Year', 'Topic Area', 'Indicator Title', 'Data Source', 'Data Notes']:
            if col in df.columns: df[col] = df[col].astype(str).replace('nan', '')
        return df
    except Exception as e:
        st.error(f"Error loading CHIRS data: {e}"); return None

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
        st.error(f"Error loading Prevention Agenda data: {e}"); return None

@st.cache_data
def load_mch_data(file_path):
    try:
        df = pd.read_excel(file_path, engine='openpyxl', header=0)
        df.columns = df.columns.str.strip()
        if 'County Name' in df.columns:
            df['County Name'] = df['County Name'].str.strip()
        df['Percentage/Rate'] = pd.to_numeric(df['Percentage/Rate'], errors='coerce')
        df['MCH Objective'] = pd.to_numeric(df['MCH Objective'], errors='coerce')
        df['Data Years'] = df['Data Years'].astype(str)
        for col in ['Data Comments', 'Date Source']:
             if col in df.columns: df[col] = df[col].astype(str).replace('nan', '')
        return df
    except Exception as e:
        st.error(f"Error loading MCH data: {e}"); return None

@st.cache_data
def load_chr_trend_data(file_path):
    try:
        df = pd.read_csv(file_path, dtype=str)
        df_ny = df[df['statecode'] == '36'].copy()
        if df_ny.empty:
            st.error("No data for New York (statecode 36) found. Please check the CSV file.")
            return pd.DataFrame()
        df_ny.rename(columns={'county': 'county', 'measuren': 'measurename', 'yearspan': 'yearspan', 'rawvalue': 'rawvalue', 'cilow': 'cilow', 'cihigh': 'cihigh'}, inplace=True, errors='ignore')
        df_ny['year'] = df_ny['yearspan'].str.split('-').str[-1]
        df_ny['rawvalue'] = pd.to_numeric(df_ny['rawvalue'], errors='coerce')
        df_ny['year'] = pd.to_numeric(df_ny['year'], errors='coerce')
        df_ny.dropna(subset=['county', 'year', 'rawvalue'], inplace=True)
        return df_ny
    except FileNotFoundError:
        st.error(f"File not found: {file_path}. Please ensure it is in the 'data' folder."); return None
    except Exception as e:
        st.error(f"An error occurred while loading the CHR Trend data: {e}"); return None

@st.cache_data
def load_ejscreen_data(file_path):
    try:
        columns_to_keep = ['ID', 'STATE_FIPS', 'P_LDPNT_D2', 'P_PM25_D2', 'P_OZONE_D2', 'P_CANCR_D2', 'P_RESP_D2', 'P_TRAFF_D2', 'P_PROXPN_D2', 'P_LOWINC_D2', 'P_LMINR_D2', 'P_LESHSP_D2', 'P_LNGISP_D2', 'P_UNDR5_D2', 'P_OVR64_D2', 'ACSTOTPOP']
        column_rename_map = {'ID': 'Census Tract ID', 'ACSTOTPOP': 'Total Population', 'P_LDPNT_D2': 'Lead Paint Indicator (%ile)', 'P_PM25_D2': 'PM2.5 Air Pollution (%ile)', 'P_OZONE_D2': 'Ozone Air Pollution (%ile)', 'P_CANCR_D2': 'Air Toxics Cancer Risk (%ile)', 'P_RESP_D2': 'Respiratory Hazard Index (%ile)', 'P_TRAFF_D2': 'Traffic Proximity (%ile)', 'P_PROXPN_D2': 'Proximity to Superfund Sites (%ile)', 'P_LOWINC_D2': 'Low Income Population (%ile)', 'P_LMINR_D2': 'Minority Population (%ile)', 'P_LESHSP_D2': 'Less than High School Education (%ile)', 'P_LNGISP_D2': 'Linguistically Isolated (%ile)', 'P_UNDR5_D2': 'Population Under Age 5 (%ile)', 'P_OVR64_D2': 'Population Over Age 64 (%ile)'}
        df = pd.read_csv(file_path, usecols=columns_to_keep, dtype={'ID': str, 'STATE_FIPS': str})
        df_ny = df[df['STATE_FIPS'] == '36'].copy()
        if df_ny.empty:
            st.error("No data for New York (STATE_FIPS 36) found in the national EJScreen file."); return pd.DataFrame()
        df_ny['County FIPS'] = df_ny['ID'].str.slice(0, 5)
        fips_to_name = {f"36{fips}": name.split(' (')[0] for name, fips in NY_COUNTY_FIPS_MAP.items()}
        df_ny['County Name'] = df_ny['County FIPS'].map(fips_to_name)
        df_ny.rename(columns=column_rename_map, inplace=True)
        df_ny.dropna(subset=['County Name'], inplace=True)
        return df_ny
    except FileNotFoundError:
        st.error(f"File not found: {file_path}. Please ensure the national EJScreen CSV is in the 'data' folder."); return None
    except Exception as e:
        st.error(f"An error occurred while loading the EJScreen data: {e}"); return None

@st.cache_data
def load_county_geojson(file_path):
    """Loads the GeoJSON file containing county boundaries."""
    try:
        with open(file_path) as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"GeoJSON file not found at {file_path}. Please ensure it is in the 'data' folder.")
        return None
    except Exception as e:
        st.error(f"Error loading or parsing GeoJSON file: {e}")
        return None

# ==============================================================================
# --- CENSUS HELPER FUNCTIONS ---
# ==============================================================================
def clean_variable_label(label: str) -> str:
    if not isinstance(label, str): return "N/A"
    readable_label = label.replace("Estimate!!", "").replace("Total:!!", "").replace("!!", " | ")
    return re.sub(r'\s+', ' ', readable_label).strip()

@st.cache_data
def fetch_census_variables(dataset: str, year: str):
    url = f"{CENSUS_API_BASE_URL}/{year}/{dataset}/variables.json"
    try:
        response = requests.get(url); response.raise_for_status()
        data = response.json().get("variables", {})
        return { var: clean_variable_label(info.get("label", "")) for var, info in data.items() if "label" in info and not var.endswith(("A", "M", "MA", "EA")) and (var.endswith("E") or var.endswith("N")) }
    except requests.exceptions.RequestException:
        st.sidebar.warning(f"Could not automatically load variables for {dataset} {year}."); return {}

@st.cache_data
def fetch_census_data(dataset: str, year: str, variables: list, geo_for: str, geo_in: dict = None):
    if not variables: return pd.DataFrame()
    if "NAME" not in variables: variables.insert(0, "NAME")
    params = {"get": ",".join(variables), "for": geo_for}
    if geo_in: params.update(geo_in)
    url = f"{CENSUS_API_BASE_URL}/{year}/{dataset}"
    try:
        response = requests.get(url, params=params); response.raise_for_status()
        data = response.json()
        if len(data) < 2: return pd.DataFrame()
        df = pd.DataFrame(data[1:], columns=data[0])
        for col in variables:
            if col != 'NAME' and col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except requests.exceptions.HTTPError as e:
        st.error(f"API Error: {e}. This combination may not be supported."); return pd.DataFrame()
    except (KeyError, IndexError, requests.exceptions.JSONDecodeError):
        st.error("API Error: Received unexpected data format."); return pd.DataFrame()

def get_census_snapshot(county_name):
    """Fetches key demographic data from the latest ACS5 census for a specific county."""
    county_fips = NY_COUNTY_FIPS_MAP.get(county_name)
    if not county_fips:
        return {"error": "County FIPS code not found."}
    variables = {"B01003_001E": "Total Population", "B19013_001E": "Median Household Income", "B17001_002E": "Population Below Poverty Level"}
    df = fetch_census_data(dataset="acs/acs5", year="2022", variables=list(variables.keys()), geo_for=f"county:{county_fips}", geo_in={"in": "state:36"})
    if df.empty or len(df) == 0:
        return {"Total Population": "N/A", "Median Household Income": "N/A", "Population Below Poverty Level": "N/A"}
    results = {}
    for code, name in variables.items():
        try:
            value = int(df[code].iloc[0])
            results[name] = f"{value:,}"
        except (ValueError, TypeError, KeyError):
            results[name] = "N/A"
    return results

# ==============================================================================
# --- DASHBOARD HELPER FUNCTIONS ---
# ==============================================================================
def find_best_indicator_match(keyword, indicator_list):
    """Finds the best matching indicator name from a list based on a keyword."""
    keyword_lower = keyword.lower()
    matches = [ind for ind in indicator_list if keyword_lower in ind.lower()]
    if not matches:
        return None
    matches.sort(key=len)
    return matches[0]

def get_latest_metric_smart(df, county, county_col, year_col, value_col, indicator_keyword, indicator_col):
    """Finds the most recent data point using a smart matching function for the indicator."""
    if df is None: return "N/A", ""
    all_indicators = df[indicator_col].unique()
    best_match_indicator = find_best_indicator_match(indicator_keyword, all_indicators)
    if best_match_indicator is None:
        return "N/A", ""
    filtered_df = df[(df[county_col] == county) & (df[indicator_col] == best_match_indicator)].copy()
    if filtered_df.empty: return "N/A", ""
    filtered_df[year_col] = pd.to_numeric(filtered_df[year_col], errors='coerce')
    filtered_df.dropna(subset=[year_col, value_col], inplace=True)
    if filtered_df.empty: return "N/A", ""
    latest_entry = filtered_df.sort_values(by=year_col, ascending=False).iloc[0]
    value = latest_entry[value_col]
    year = int(latest_entry[year_col])
    try:
        return f"{float(value):.1f}", str(year)
    except (ValueError, TypeError):
        return str(value), str(year)


# In modules/utils.py, REPLACE the entire get_snapshot_data function

def get_snapshot_data(chirs_df, pa_df, mch_df, county_name):
    """
    A single, robust function to get all key metrics for the County Snapshot page.
    This version uses the confirmed, exact indicator names for maximum reliability.
    """
    results = {}

    def fetch_metric(df, county, county_col, indicator_full_name, indicator_col, year_col, value_col):
        # This internal helper function is correct and does not need changes
        filtered_df = df[(df[county_col] == county) & (df[indicator_col] == indicator_full_name)].copy()
        if filtered_df.empty: return "N/A", ""
        filtered_df[year_col] = pd.to_numeric(filtered_df[year_col], errors='coerce')
        filtered_df.dropna(subset=[year_col, value_col], inplace=True)
        if filtered_df.empty: return "N/A", ""
        latest = filtered_df.sort_values(by=year_col, ascending=False).iloc[0]
        value = latest[value_col]
        year = int(latest[year_col])
        try:
            return f"{float(value):.1f}", str(year)
        except (ValueError, TypeError):
            return str(value), str(year)

    # --- 1. CHIRS Data ---
    val, year = fetch_metric(chirs_df, f"{county_name} County", 'Geographic area',
                             "All cancer incidence rate per 100,000", "Indicator Title", 'Year', 'Rate/Percent')
    results["All Cancer Incidence"] = (val, year, "All cancer incidence rate per 100,000")

    # --- 2. Prevention Agenda Data ---
    val, year = fetch_metric(pa_df, county_name, 'County Name',
                             "Percentage of deaths that are premature (before age 65 years)", "Indicator", 'Data Years',
                             'Percentage/Rate/Ratio')
    results["Premature Deaths (%)"] = (val, year, "Percentage of deaths that are premature (before age 65 years)")
    val, year = fetch_metric(pa_df, county_name, 'County Name', "Prevalence of cigarette smoking among adults",
                             "Indicator", 'Data Years', 'Percentage/Rate/Ratio')
    results["Adult Smoking (%)"] = (val, year, "Prevalence of cigarette smoking among adults")
    val, year = fetch_metric(pa_df, county_name, 'County Name', "Percentage of adults with obesity", "Indicator",
                             'Data Years', 'Percentage/Rate/Ratio')
    results["Adult Obesity (%)"] = (val, year, "Percentage of adults with obesity")

    # --- 3. MCH Data (with CORRECTED, AVAILABLE indicator names) ---
    val, year = fetch_metric(mch_df, county_name, 'County Name',
                             "Percentage of births with early (1st trimester) prenatal care", "Indicator", 'Data Years',
                             'Percentage/Rate')
    results["Early Prenatal Care (%)"] = (val, year, "Percentage of births with early (1st trimester) prenatal care")

    val, year = fetch_metric(mch_df, county_name, 'County Name', "Infant mortality rate per 1,000 live births",
                             "Indicator", 'Data Years', 'Percentage/Rate')
    results["Infant Mortality Rate"] = (val, year, "Infant mortality rate per 1,000 live births")

    # --- 4. Add the two additional indicators WITH DATA ---
    val, year = fetch_metric(mch_df, county_name, 'County Name',
                             "Percentage of preterm births (less than 37 weeks gestation)", "Indicator", 'Data Years',
                             'Percentage/Rate')
    results["Preterm Births (%)"] = (val, year, "Percentage of preterm births (less than 37 weeks gestation)")

    # Let's find a reliable indicator from the Prevention Agenda data
    val, year = fetch_metric(pa_df, county_name, 'County Name', "Preventable hospitalizations, rate per 100,000",
                             "Indicator", 'Data Years', 'Percentage/Rate/Ratio')
    results["Preventable Hospitalizations"] = (val, year, "Preventable hospitalizations, rate per 100,000")

    return results

def get_pa_data_for_chip(df, priority_area, focus_area, indicator_name, county_name):
    """Fetches objective, recent data, and trend data for the CHIP."""
    objective_text = "Not available"; data_point_text = "Not available"; trend_df = pd.DataFrame()
    if df is None: return objective_text, data_point_text, trend_df
    indicator_df = df[(df['Priority Area'] == priority_area) & (df['Focus Area'] == focus_area) & (df['Indicator'] == indicator_name)]
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

# ==============================================================================
# --- Charting Function ---
# ==============================================================================
def create_chart(df, config):
    """Reusable function to create an Altair chart from a config."""
    line = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X(f"{config['year_col']}:N", title='Year', sort=alt.SortField(config['year_col'])),
        y=alt.Y(f"{config['value_col']}:Q", title=config['y_axis_label'], scale=alt.Scale(zero=False)),
        color=alt.Color(f"{config['county_col']}:N", title='County'),
        tooltip=[config['county_col'], config['year_col'], config['value_col']]
    )
    chart = line
    if config.get("objective_col"):
        objective_line = alt.Chart(df).mark_rule(color=config['objective_color'], strokeDash=[5,5]).encode(y=f"mean({config['objective_col']}):Q")
        objective_text = objective_line.mark_text(align='left', baseline='middle', dx=7, text=config['objective_label']).encode(color=alt.value(config['objective_color']))
        return (chart + objective_line + objective_text).interactive()
    return chart.interactive()