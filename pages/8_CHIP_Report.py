# pages/8_📄_CHIP_Report.py
import streamlit as st
import io
import pandas as pd
import altair as alt
import markdown
from datetime import datetime
import html

st.set_page_config(page_title="CHIP Report", page_icon="📄", layout="wide")
st.title("📄 Community Health Improvement Plan Report")

if 'chip_report_sections' not in st.session_state or not st.session_state.chip_report_sections:
    st.info(
        "No CHIP sections have been added yet. Go to the '✍️ CHIP Wizard' to draft and add sections to this report.")
    st.stop()

# --- Display saved sections and allow removal ---
indices_to_remove = []
for i, section in enumerate(st.session_state.chip_report_sections):
    with st.expander(f"Section {i + 1}: {section['priority_area']} - {section['focus_area']}", expanded=True):
        st.subheader("Overarching Goal")
        st.write(section['overarching_goal'])
        if st.button(f"🗑️ Remove Section #{i + 1}", key=f"remove_{i}"):
            indices_to_remove.append(i)

# Remove items in reverse order if requested
for i in sorted(indices_to_remove, reverse=True):
    st.session_state.chip_report_sections.pop(i)
    st.rerun()

st.divider()
st.header("Download Full CHIP Document")

# --- Report Generation Logic ---
html_parts = []
for i, plan in enumerate(st.session_state.chip_report_sections):
    # Recreate trend chart from saved data
    trend_df = pd.DataFrame(plan['trend_data'])
    chart_html = ""
    if not trend_df.empty:
        trend_chart = alt.Chart(trend_df).mark_line(point=True).encode(
            x=alt.X('Data Years:O', title='Year', sort='ascending'),
            y=alt.Y('Percentage/Rate/Ratio:Q', title='Rate / Percent', scale=alt.Scale(zero=False))
        ).properties(
            title=f"Recent Trend for '{plan['indicator']}' in {plan['county']} County",
            width='container'
        )
        buffer = io.StringIO()
        trend_chart.save(buffer, format='html')
        chart_html = buffer.getvalue()

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
        {chart_html}
        <h3>STRATEGIES</h3>
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <thead><tr style="background-color: #f2f2f2;">
                <th>Evidence-Based Strategy Activities</th><th>Lead Partners</th><th>Timeframe</th><th>Evaluation Measure</th><th>Outcome: Product/Result</th>
            </tr></thead><tbody>{strategy_rows_html}</tbody></table>
    </div>"""
    html_parts.append(section_html)

html_style = "<style>body{{font-family:sans-serif;}} h1,h2,h3,h4{{color:#2c3e50;}} table{{font-size: 12px; border: 1px solid #ccc; width: 100%;}} th, td {{border: 1px solid #ccc; padding: 8px; text-align: left; vertical-align: top;}}</style>"
final_html = f"""<!DOCTYPE html><html><head><title>CHIP Report for {st.session_state.chip_report_sections[0]['county']} County</title>{html_style}</head><body>
    <h1>Community Health Improvement Plan (CHIP)</h1>
    <h2>{st.session_state.chip_report_sections[0]['county']} County</h2>
    <p><em>Draft generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
    {''.join(html_parts)}
</body></html>"""

st.download_button(
    label="📥 Download Full CHIP as HTML", data=final_html,
    file_name=f"CHIP_Report_{st.session_state.chip_report_sections[0]['county']}.html",
    mime="text/html")