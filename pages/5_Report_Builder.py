# pages/5_📋_Report_Builder.py
import streamlit as st
import markdown
from datetime import datetime
import json
import html
import io
from modules.utils import create_chart

st.title("📋 Report Builder")

if "saved_analyses" not in st.session_state or not st.session_state.saved_analyses:
    st.info(
        "No analyses saved yet. Go to a dashboard, generate an analysis, and click '💾 Save This Analysis' to add it here.")
    st.stop()

# This is the view_saved_analyses function, now living on its own page
html_parts = []
indices_to_remove = []

for i, snap in enumerate(st.session_state.saved_analyses):
    with st.container():
        st.subheader(f"{i + 1}. {snap['dashboard']}: {snap['indicator']}")
        if st.button(f"🗑️ Remove Analysis #{i + 1}", key=f"remove_{i}"):
            indices_to_remove.append(i)
        st.markdown(snap['analysis_text'])
        st.markdown("---")

    chart = create_chart(snap['raw_data'], snap['config']).properties(width='container')
    html_buffer = io.StringIO()
    chart.save(html_buffer, format='html')
    chart_html = html_buffer.getvalue()

    html_parts.append(f"<h2>{i + 1}. {snap['dashboard']}: {snap['indicator']}</h2>")
    html_parts.append(f"<p><strong>Filters:</strong> <code>{snap['filters']}</code></p>")
    html_parts.append(chart_html)
    if snap['data_source']: html_parts.append(f"<p><strong>Source:</strong> {', '.join(snap['data_source'])}</p>")
    if snap['data_notes']:
        notes_html = "<ul>" + "".join([f"<li>{note}</li>" for note in snap['data_notes']]) + "</ul>"
        html_parts.append(f"<div><strong>Data Notes:</strong>{notes_html}</div>")
    analysis_html = markdown.markdown(snap['analysis_text'])
    html_parts.append(f"<div><h3>AI-Generated Analysis</h3>{analysis_html}</div>")
    html_parts.append("<hr>")

for i in sorted(indices_to_remove, reverse=True):
    st.session_state.saved_analyses.pop(i)
    st.rerun()

html_style = "<style>body{font-family:sans-serif;line-height:1.6;}h1,h2{color:#2c3e50;border-bottom:2px solid #eee;padding-bottom:5px;}h3{color:#34495e;}code{background-color:#f4f4f4;padding:2px 5px;border-radius:4px;}</style>"
final_html = f"<!DOCTYPE html><html><head><title>NYS Health Report</title>{html_style}</head><body><h1>NYS Health Data Report</h1><p><em>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>{''.join(html_parts)}</body></html>"

st.download_button(
    label="📥 Download Full Report as HTML (Print to PDF from Browser)",
    data=final_html, file_name="NYS_Health_Data_Report.html", mime="text/html")