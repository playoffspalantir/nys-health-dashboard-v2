# pages/9_🧮_Hanlon_Prioritization.py
import streamlit as st
import pandas as pd
from modules import utils, ai_analysis
from pathlib import Path  # <-- Import the Path library

# --- Page Configuration ---
st.set_page_config(page_title="Hanlon Prioritization", page_icon="🧮", layout="wide")


# --- Load Data (with ROBUST path) ---
@st.cache_data
def load_pa_data():
    # --- THE FIX IS HERE ---
    # Build the absolute path to the data file, making it runnable from anywhere
    script_path = Path(__file__)
    project_root = script_path.parent.parent  # Go up two levels (from pages/ to the root)
    data_file = project_root / "data" / "PreventionAgendaTrackingIndicators-CountyTrendData.csv"
    return utils.load_prevention_data(data_file)


pa_df = load_pa_data()

st.title("🧮 Hanlon Method: Data-Driven Prioritization")
st.write("A tool to prioritize Prevention Agenda indicators using a data-driven approach.")
with st.expander("What is the Hanlon Method?"):
    st.markdown("The formula is: **Priority Score = (A: Size + B: Seriousness) * C: Effectiveness**")
st.divider()

if pa_df is not None:
    st.header("1. Select an Indicator to Prioritize")

    # --- Selections ---
    c1, c2, c3, c4 = st.columns(4)
    all_counties = sorted(pa_df['County Name'].dropna().unique())
    # Use a default county that is likely to be in the list
    default_county = "Dutchess" if "Dutchess" in all_counties else all_counties[0]
    selected_county = c1.selectbox("Select County:", all_counties, index=all_counties.index(default_county))

    priority_areas = sorted(pa_df['Priority Area'].dropna().unique())
    selected_priority = c2.selectbox("Select Priority Area:", priority_areas)

    focus_areas = sorted(pa_df[pa_df['Priority Area'] == selected_priority]['Focus Area'].dropna().unique())
    selected_focus = c3.selectbox("Select Focus Area:", focus_areas)

    indicators = sorted(pa_df[pa_df['Focus Area'] == selected_focus]['Indicator'].dropna().unique())
    selected_indicator = c4.selectbox("Select Indicator:", indicators)

    # --- Fetch Data for the selection ---
    hanlon_data = utils.get_hanlon_data(pa_df, selected_county, selected_priority, selected_focus, selected_indicator)

    if hanlon_data is not None and not hanlon_data.empty:
        latest_data = hanlon_data.iloc[0]

        # --- Automated Scoring Logic ---
        size_score_suggestion = 5
        if pd.notna(latest_data.get('Event Count/Rate')):
            try:
                event_count = float(str(latest_data['Event Count/Rate']).replace(',', ''))
                if event_count > 1000:
                    size_score_suggestion = 8
                elif event_count > 500:
                    size_score_suggestion = 7
                elif event_count > 100:
                    size_score_suggestion = 6
            except (ValueError, TypeError):
                pass

        seriousness_score_suggestion = 5
        quartile = str(latest_data.get('Quartile', ''))
        if 'Q4' in quartile:
            seriousness_score_suggestion = 9
        elif 'Q3' in quartile:
            seriousness_score_suggestion = 7
        elif 'Q1' in quartile or 'Q2' in quartile:
            seriousness_score_suggestion = 4

        st.divider()
        st.header("2. Score the Problem")
        st.info("Scores are pre-filled based on the latest available data. Adjust them based on your expertise.")

        col1_scores, col2_scores, col3_scores = st.columns(3)
        score_a = col1_scores.slider("Component A: Size (1-10)", 1, 10, int(size_score_suggestion))
        score_b = col2_scores.slider("Component B: Seriousness (1-10)", 1, 10, int(seriousness_score_suggestion))
        score_c = col3_scores.slider("Component C: Effectiveness (0.5-1.5)", 0.5, 1.5, 1.0, 0.1)

        # --- Calculation and Results ---
        priority_score = (score_a + score_b) * score_c
        st.latex(f"({score_a} + {score_b}) \\times {score_c} = {priority_score:.2f}")
        st.metric(label=f"Hanlon Priority Score for '{selected_indicator}'", value=f"{priority_score:.2f}")

        st.divider()
        st.header("3. AI-Powered Prioritization Summary")

        if st.button("🤖 Generate AI Prioritization Rationale", use_container_width=True):
            with st.spinner("AI is analyzing the priority..."):
                prompt = (
                    f"You are a public health strategist. Based on the selected health indicator '{selected_indicator}' for {selected_county} County, "
                    f"the latest data shows a value of {latest_data.get('Percentage/Rate/Ratio', 'N/A')} "
                    f"which falls into quartile '{latest_data.get('Quartile', 'N/A')}'. "
                    f"The calculated Hanlon Priority Score is {priority_score:.2f} (Size={score_a}, Seriousness={score_b}, Effectiveness={score_c}).\n\n"
                    f"Write a concise, one-paragraph rationale in formal prose explaining why this problem warrants its priority level. "
                    f"Integrate the data and Hanlon scores into your justification. Do not use bullet points or markdown titles.")

                rationale = ai_analysis._get_ai_response(prompt)
                st.markdown(rationale)

    else:
        st.warning("No data found for this specific combination. Please make another selection.")
else:
    st.error("Could not load Prevention Agenda data.")