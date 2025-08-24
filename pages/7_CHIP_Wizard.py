# pages/7_✍️_CHIP_Wizard.py
import streamlit as st
import pandas as pd
import altair as alt
from modules import utils, ai_analysis
from pathlib import Path

st.set_page_config(page_title="CHIP Wizard", page_icon="✍️", layout="wide")


@st.cache_data
def load_pa_data():
    script_path = Path(__file__)
    project_root = script_path.parent.parent
    data_file = project_root / "data" / "PreventionAgendaTrackingIndicators-CountyTrendData.csv"
    return utils.load_prevention_data(data_file)


pa_df = load_pa_data()

# Initialize session state for this page if it doesn't exist
if 'chip_wizard' not in st.session_state:
    st.session_state.chip_wizard = {
        "overarching_goal": "", "disparities": "",
        "objectives": [{"text": ""}],
        "strategies": [{"activity": "", "partners": "", "timeframe": "", "evaluation": "", "outcome": ""}]
    }

st.title("✍️ Community Health Improvement Plan (CHIP) Wizard")
st.info(
    "This tool helps you draft a section of your CHIP. Fill out the form, then click 'Add Section to Report' to save it. You can add multiple sections before exporting from the 'CHIP Report' page.")
st.divider()

if pa_df is not None:
    st.header("Step 1: Select Your County and Priority")
    all_counties = sorted(pa_df['County Name'].dropna().unique())
    default_county = "Dutchess" if "Dutchess" in all_counties else all_counties[0]
    st.session_state.chip_wizard['county'] = st.selectbox("**Select the County for this Plan Section:**", all_counties,
                                                          index=all_counties.index(
                                                              st.session_state.chip_wizard.get('county',
                                                                                               default_county)))

    c1, c2 = st.columns(2)
    priority_areas = sorted(pa_df['Priority Area'].dropna().unique())
    if 'priority_area' not in st.session_state.chip_wizard:
        st.session_state.chip_wizard['priority_area'] = priority_areas[0]
    priority_index = priority_areas.index(st.session_state.chip_wizard['priority_area'])
    st.session_state.chip_wizard['priority_area'] = c1.selectbox("Prevention Agenda Priority Area:", priority_areas,
                                                                 index=priority_index, key="chip_priority")

    focus_areas = sorted(
        pa_df[pa_df['Priority Area'] == st.session_state.chip_wizard['priority_area']]['Focus Area'].dropna().unique())
    if 'focus_area' not in st.session_state.chip_wizard or st.session_state.chip_wizard[
        'focus_area'] not in focus_areas:
        st.session_state.chip_wizard['focus_area'] = focus_areas[0]
    focus_index = focus_areas.index(st.session_state.chip_wizard['focus_area'])
    st.session_state.chip_wizard['focus_area'] = c2.selectbox("Focus Area:", focus_areas, index=focus_index,
                                                              key="chip_focus")

    indicator_list = sorted(
        pa_df[pa_df['Focus Area'] == st.session_state.chip_wizard['focus_area']]['Indicator'].dropna().unique())
    if 'indicator' not in st.session_state.chip_wizard or st.session_state.chip_wizard[
        'indicator'] not in indicator_list:
        st.session_state.chip_wizard['indicator'] = indicator_list[0]
    indicator_index = indicator_list.index(st.session_state.chip_wizard['indicator'])
    st.session_state.chip_wizard['indicator'] = st.selectbox("Select a related PA Indicator:", indicator_list,
                                                             index=indicator_index, key="chip_indicator")

    official_objective, latest_data, trend_df = utils.get_pa_data_for_chip(pa_df, st.session_state.chip_wizard[
        'priority_area'], st.session_state.chip_wizard['focus_area'], st.session_state.chip_wizard['indicator'],
                                                                           st.session_state.chip_wizard['county'])

    st.subheader("Data Context")
    col1, col2 = st.columns(2)
    col1.metric("Official 2024 Objective", official_objective)
    col2.metric(f"{st.session_state.chip_wizard['county']} County's Most Recent Data", latest_data)

    if not trend_df.empty:
        trend_chart = alt.Chart(trend_df).mark_line(point=True).encode(
            x=alt.X('Data Years:O', title='Year', sort='ascending'),
            y=alt.Y('Percentage/Rate/Ratio:Q', title='Rate / Percent', scale=alt.Scale(zero=False)),
            tooltip=['Data Years', 'Percentage/Rate/Ratio']
        ).properties(
            title=f"Recent Trend for '{st.session_state.chip_wizard['indicator']}' in {st.session_state.chip_wizard['county']} County")
        st.altair_chart(trend_chart, use_container_width=True)

    st.divider()

    st.header("Step 2: Define Goals and Objectives")
    st.session_state.chip_wizard['overarching_goal'] = st.text_input("**Overarching Goal:**",
                                                                     st.session_state.chip_wizard.get(
                                                                         'overarching_goal', ""))

    if st.button("🤖 Suggest a SMART Goal (AI)"):
        prompt = f"Based on the indicator '{st.session_state.chip_wizard['indicator']}' where the most recent data for {st.session_state.chip_wizard['county']} County is {latest_data} and the state objective is {official_objective}, draft a single, specific, measurable, achievable, relevant, and time-bound (SMART) goal for a community health improvement plan. Write only the goal text."
        with st.spinner("AI is drafting a goal..."):
            suggested_goal = ai_analysis._get_ai_response(prompt)
            st.session_state.chip_wizard['overarching_goal'] = suggested_goal
            st.rerun()

    st.session_state.chip_wizard['disparities'] = st.text_input("**Disparities Addressed:**",
                                                                st.session_state.chip_wizard.get('disparities', ""))

    st.subheader("Plan Objectives")
    for i, objective in enumerate(st.session_state.chip_wizard['objectives']):
        objective['text'] = st.text_input(f"**Objective #{i + 1}**", objective['text'], key=f"obj_{i}")

    c1_obj, c2_obj = st.columns([1, 5])
    # --- INDENTATION FIX IS HERE ---
    if c1_obj.button("➕ Add Objective"):
        st.session_state.chip_wizard['objectives'].append({"text": ""})
        st.rerun()
    if c2_obj.button("➖ Remove Last Objective") and len(st.session_state.chip_wizard['objectives']) > 1:
        st.session_state.chip_wizard['objectives'].pop()
        st.rerun()

    st.divider()

    st.header("Step 3: Detail Strategies")
    for i, strategy in enumerate(st.session_state.chip_wizard['strategies']):
        st.subheader(f"Strategy #{i + 1}")
        c1, c2 = st.columns(2)
        c3, c4, c5 = st.columns(3)
        strategy['activity'] = c1.text_area("Strategy/Activity", strategy.get('activity', ""), key=f"act_{i}")
        strategy['partners'] = c2.text_area("Partners", strategy.get('partners', ""), key=f"part_{i}")
        strategy['timeframe'] = c3.text_input("Timeframe", strategy.get('timeframe', ""), key=f"time_{i}")
        strategy['evaluation'] = c4.text_input("Evaluation", strategy.get('evaluation', ""), key=f"eval_{i}")
        strategy['outcome'] = c5.text_input("Outcome", strategy.get('outcome', ""), key=f"out_{i}")
        st.markdown("---")

    c1_strat, c2_strat = st.columns([1, 5])
    # --- INDENTATION FIX IS HERE ---
    if c1_strat.button("➕ Add Strategy"):
        st.session_state.chip_wizard['strategies'].append(
            {"activity": "", "partners": "", "timeframe": "", "evaluation": "", "outcome": ""})
        st.rerun()
    if c2_strat.button("➖ Remove Last Strategy") and len(st.session_state.chip_wizard['strategies']) > 1:
        st.session_state.chip_wizard['strategies'].pop()
        st.rerun()

    st.divider()

    st.header("Step 4: Add Section to Final Report")
    if st.button("➕ Add This Section to the CHIP Report", use_container_width=True, type="primary"):
        plan_snapshot = st.session_state.chip_wizard.copy()
        plan_snapshot['trend_data'] = trend_df.to_dict(orient='records')
        plan_snapshot['official_objective'] = official_objective
        plan_snapshot['latest_data'] = latest_data

        if 'chip_report_sections' not in st.session_state:
            st.session_state.chip_report_sections = []

        st.session_state.chip_report_sections.append(plan_snapshot)

        # Clear the form for the next entry
        st.session_state.chip_wizard = {
            "county": st.session_state.chip_wizard['county'],
            "overarching_goal": "", "disparities": "",
            "objectives": [{"text": ""}],
            "strategies": [{"activity": "", "partners": "", "timeframe": "", "evaluation": "", "outcome": ""}]
        }
        st.success(
            f"Added section for '{plan_snapshot['focus_area']}' to the report! The form is now clear for the next section.")
        st.rerun()
else:
    st.error("Could not load Prevention Agenda data.")