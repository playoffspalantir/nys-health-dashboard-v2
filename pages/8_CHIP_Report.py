# pages/8_CHIP_Report.py
import streamlit as st
import pandas as pd
import altair as alt
import markdown
from datetime import datetime
import json
import html
from modules.utils import create_chart  # We need the create_chart function

st.set_page_config(page_title="CHIP Report", page_icon="📄", layout="wide")
st.title("📄 Community Health Improvement Plan Report")

if 'chip_report_sections' not in st.session_state or not st.session_state.chip_report_sections:
    st.info("No CHIP sections have been added yet. Go to the '✍️ CHIP Wizard' to add sections to this report.")
    st.stop()

# --- UI for managing saved sections (unchanged) ---
indices_to_remove = []
for i, section in enumerate(st.session_state.chip_report_sections):
    with st.expander(f"Section {i + 1}: {section['priority_area']} - {section['focus_area']}", expanded=True):
        st.subheader("Overarching Goal")
        st.write(section['overarching_goal'])
        if st.button(f"🗑️ Remove Section #{i + 1}", key=f"remove_{i}"):
            indices_to_remove.append(i)

for i in sorted(indices_to_remove, reverse=True):
    st.session_state.chip_report_sections.pop(i)
    st.rerun()

st.divider()
st.header("Download Full CHIP Document")

# ==============================================================================
# --- FINAL, CORRECT REPORT GENERATION LOGIC ---
# ==============================================================================
report_html_parts = []
vega_embed_scripts = []
report_county = st.session_state.chip_report_sections[0]['county']

for i, plan in enumerate(st.session_state.chip_report_sections):
    trend_df = pd.DataFrame(plan['trend_data'])
    chart_script_part = ""

    if not trend_df.empty:
        trend_chart = alt.Chart(trend_df).mark_line(point=True).encode(
            x=alt.X('Data Years:O', title='Year', sort='ascending'),
            y=alt.Y('Percentage/Rate/Ratio:Q', title='Rate / Percent', scale=alt.Scale(zero=False))
        ).properties(
            title=f"Recent Trend for '{plan['indicator']}' in {plan['county']} County"
        )

        chart_div_id = f"vis_chip_{i}"
        chart_json = trend_chart.to_json()

        # Add this chart's script to our list
        vega_embed_scripts.append(f"""
            const spec_chip_{i} = {chart_json};
            spec_chip_{i}.width = 'container';
            spec_chip_{i}.height = 300;
            vegaEmbed('#{chart_div_id}', spec_chip_{i}, {{"actions": false}});
        """)
        chart_script_part = f'<div id="{chart_div_id}" class="chart-container"></div>'

    objectives_html = "".join([f"<li><strong>OBJECTIVE #{j + 1}:</strong> {html.escape(obj['text'])}</li>" for j, obj in
                               enumerate(plan.get('objectives', [])) if obj.get('text')])
    strategy_rows_html = "".join([f"""<tr>
        <td>{html.escape(strat.get('activity', '')).replace('\n', '<br>')}</td>
        <td>{html.escape(strat.get('partners', '')).replace('\n', '<br>')}</td>
        <td>{html.escape(strat.get('timeframe', ''))}</td>
        <td>{html.escape(strat.get('evaluation', ''))}</td>
        <td>{html.escape(strat.get('outcome', ''))}</td>
    </tr>""" for strat in plan.get('strategies', []) if any(strat.values())])

    section_html = f"""
    <div style="page-break-after: always;">
        <h2>SECTION {i + 1}: {html.escape(plan.get('priority_area', ''))}</h2>
        <h3>Focus Area: {html.escape(plan.get('focus_area', ''))}</h3>
        <h4>Overarching Goal: {html.escape(plan.get('overarching_goal', ''))}</h4>
        <ul>{objectives_html}</ul>
        <p><strong>Context - Official 2024 Objective:</strong> {html.escape(plan.get('official_objective', ''))}</p>
        <p><strong>Context - {html.escape(plan.get('county', ''))} County's Most Recent Data:</strong> {html.escape(plan.get('latest_data', ''))}</p>
        <p><strong>Disparities Addressed:</strong> {html.escape(plan.get('disparities', ''))}</p>
        <hr>
        {chart_script_part}
        <h3>STRATEGIES</h3>
        <table border="1">
            <thead><tr><th>Strategy Activities</th><th>Partners</th><th>Timeframe</th><th>Evaluation</th><th>Outcome</th></tr></thead>
            <tbody>{strategy_rows_html}</tbody>
        </table>
    </div>"""
    report_html_parts.append(section_html)

# --- Create the single, master script tag for all charts ---
master_script = f"""
<script type="text/javascript">
    window.onload = function() {{
        {';'.join(vega_embed_scripts)}
    }};
</script>
"""

# --- Assemble the final HTML document ---
final_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>CHIP Report for {report_county} County</title>
    <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
    <script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
    <script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
    <style>
        body{{font-family:sans-serif;}} h1,h2{{color:#2c3e50;border-bottom:2px solid #eee;}} 
        table{{font-size:12px; width:100%; border-collapse:collapse;}} 
        th,td{{border:1px solid #ccc; padding:8px; vertical-align: top; text-align: left;}}
        .chart-container{{width: 100%; height: 350px;}}
    </style>
</head>
<body>
    <h1>Community Health Improvement Plan</h1>
    <h2>{report_county} County</h2>
    <p><em>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
    {''.join(report_html_parts)}
    {master_script}
</body>
</html>
"""

st.download_button(
    label="📥 Download Full CHIP as HTML", data=final_html,
    file_name=f"CHIP_Report_{report_county}.html",
    mime="text/html")