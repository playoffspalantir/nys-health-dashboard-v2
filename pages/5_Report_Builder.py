# pages/5_Report_Builder.py
import streamlit as st
import markdown
from datetime import datetime
import json
import html

st.title("📋 Consolidated Report Builder")

if "saved_analyses" not in st.session_state or not st.session_state.saved_analyses:
    st.info("No analyses saved yet. Go to a dashboard and click '💾 Save This Analysis'.")
    st.stop()

# --- UI for managing saved analyses (unchanged) ---
indices_to_remove = [];
for i, snap in enumerate(st.session_state.saved_analyses):
    with st.container():
        st.subheader(f"{i + 1}. {snap['dashboard']}: {snap['indicator']}")
        if st.button(f"🗑️ Remove Analysis #{i + 1}", key=f"remove_{i}"):
            indices_to_remove.append(i)
        st.markdown(snap['analysis_text'])
        st.markdown("---")
for i in sorted(indices_to_remove, reverse=True):
    st.session_state.saved_analyses.pop(i);
    st.rerun()

st.divider();
st.header("Download Full Report")

# ==============================================================================
# --- FINAL, CORRECT REPORT GENERATION LOGIC ---
# ==============================================================================
report_html_parts = []
vega_embed_scripts = []

for i, snap in enumerate(st.session_state.saved_analyses):
    chart_div_id = f"vis{i}"

    # --- THIS IS THE FIX: No json.dumps here ---
    # We will pass the raw JSON string directly into the JavaScript template.
    chart_spec = snap['chart_json']

    # Create the JavaScript call for this specific chart
    script = f"""
        const spec{i} = {chart_spec};
        spec{i}.width = 'container';
        spec{i}.height = 300;
        vegaEmbed('#{chart_div_id}', spec{i}, {{"actions": false}});
    """
    vega_embed_scripts.append(script)

    # Build the HTML body part for this section
    section_html = f"""
    <h2>{i + 1}. {snap['dashboard']}: {snap['indicator']}</h2>
    <p><strong>Filters:</strong> <code>{snap['filters']}</code></p>
    <div id="{chart_div_id}" class="chart-container"></div>
    <p><strong>Source:</strong> {', '.join(snap['data_source'])}</p>
    <div><strong>Data Notes:</strong><ul>{''.join([f"<li>{note}</li>" for note in snap['data_notes']])}</ul></div>
    <div><h3>AI-Generated Insights</h3>{markdown.markdown(snap['analysis_text'])}</div>
    <hr>
    """
    report_html_parts.append(section_html)

# --- Create the single, master script tag ---
master_script = f"""
<script type="text/javascript">
    // This function will run after the page is fully loaded
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
    <title>NYS Health Report</title>
    <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
    <script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
    <script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
    <style>
        body{{font-family:sans-serif;}} h1,h2{{color:#2c3e50; border-bottom:2px solid #eee;}}
        code{{background-color:#f4f4f4; padding:2px 5px; border-radius:4px;}}
        .chart-container{{width: 100%; height: 350px;}}
    </style>
</head>
<body>
    <h1>NYS Health Data Report</h1>
    <p><em>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
    {''.join(report_html_parts)}
    {master_script}
</body>
</html>
"""

st.download_button(
    label="📥 Download Full Report as HTML",
    data=final_html, file_name="NYS_Health_Data_Report.html", mime="text/html"
)