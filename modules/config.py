# modules/config.py
from pathlib import Path
from modules import utils, ai_analysis

# Define the absolute path to the data directory
DATA_DIR = Path(__file__).parent.parent / "data"

CONFIGS = {
    "CHIRS Indicators": {
        "loader_func": utils.load_chirs_data,
        "file_path": DATA_DIR / "chir_county_trend.xlsx",
        "analyzer_func": ai_analysis.analyze_chirs_data, "title": "CHIRS Indicators",
        "filters": [
            {"label": "Topic Area", "col": "Topic Area", "type": "selectbox"},
            {"label": "Indicator", "col": "Indicator Title", "type": "selectbox"},
            {"label": "Counties", "col": "Geographic area", "type": "multiselect", "default": ['Westchester County', 'Dutchess County', 'Putnam County', 'Sullivan County', 'Rockland County', 'Orange County', 'Ulster County']},
            {"label": "Years", "col": "Year", "type": "multiselect", "default": []}
        ],
        "indicator_label": "Indicator", "county_col": "Geographic area", "year_col": "Year",
        "value_col": "Rate/Percent", "y_axis_label": "Rate / Percent",
        "source_col": "Data Source", "notes_col": "Data Notes"
    },
    "Prevention Agenda Trends": {
        "loader_func": utils.load_prevention_data,
        "file_path": DATA_DIR / "PreventionAgendaTrackingIndicators-CountyTrendData.csv",
        "analyzer_func": ai_analysis.analyze_prevention_data, "title": "Prevention Agenda Trends",
        "filters": [
            {"label": "Priority Area", "col": "Priority Area", "type": "selectbox"},
            {"label": "Focus Area", "col": "Focus Area", "type": "selectbox"},
            {"label": "Indicator", "col": "Indicator", "type": "selectbox"},
            {"label": "Counties", "col": "County Name", "type": "multiselect", "default": ['Westchester', 'Dutchess', 'Putnam', 'Sullivan', 'Rockland', 'Orange', 'Ulster']},
            {"label": "Years", "col": "Data Years", "type": "multiselect", "default": "all"}
        ],
        "indicator_label": "Indicator", "county_col": "County Name", "year_col": "Data Years",
        "value_col": "Percentage/Rate/Ratio", "y_axis_label": "Percentage / Rate / Ratio",
        "source_col": "Date Source", "notes_col": "Data Comments",
        "objective_col": "2024 Objective", "objective_label": "2024 Objective", "objective_color": "red"
    },
    "MCH Dashboard": {
        "loader_func": utils.load_mch_data,
        "file_path": DATA_DIR / "MCH-CountyTrendData.xlsx",
        "analyzer_func": ai_analysis.analyze_mch_data, "title": "MCH Dashboard",
        "filters": [
            {"label": "Domain Area", "col": "Domain Area", "type": "selectbox"},
            {"label": "Indicator", "col": "Indicator", "type": "selectbox"},
            {"label": "Counties", "col": "County Name", "type": "multiselect", "default": ['Westchester', 'Dutchess', 'Putnam', 'Sullivan', 'Rockland', 'Orange', 'Ulster']},
            {"label": "Years", "col": "Data Years", "type": "multiselect", "default": "all"}
        ],
        "indicator_label": "Indicator", "county_col": "County Name", "year_col": "Data Years",
        "value_col": "Percentage/Rate", "y_axis_label": "Percentage / Rate",
        "source_col": "Date Source", "notes_col": "Data Comments",
        "objective_col": "MCH Objective", "objective_label": "MCH Objective", "objective_color": "green"
    }
}