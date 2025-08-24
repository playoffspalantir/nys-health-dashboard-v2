# modules/ui_components.py
import streamlit as st
from modules import utils


def render_dashboard(config, df):
    st.sidebar.header("Data Filters")
    filters = {}
    for i, f_config in enumerate(config["filters"]):
        temp_df = df.copy()
        for j in range(i):
            prev_filter_config = config["filters"][j]
            if isinstance(filters[prev_filter_config["label"]], list):
                temp_df = temp_df[temp_df[prev_filter_config["col"]].isin(filters[prev_filter_config["label"]])]
            else:
                temp_df = temp_df[temp_df[prev_filter_config["col"]] == filters[prev_filter_config["label"]]]

        options = sorted(temp_df[f_config["col"]].dropna().unique(), reverse=(f_config["col"] == config["year_col"]))

        if f_config["type"] == "selectbox":
            filters[f_config["label"]] = st.sidebar.selectbox(f"{i + 1}. {f_config['label']}", options)
        elif f_config["type"] == "multiselect":
            default_val = f_config.get("default", [])
            if default_val == "all": default_val = options
            default_selection = [d for d in default_val if d in options]
            filters[f_config["label"]] = st.sidebar.multiselect(f"{i + 1}. {f_config['label']}", options,
                                                                default=default_selection)

    filtered_df = df.copy()
    for f_config in config["filters"]:
        selected_val = filters[f_config["label"]]
        if not selected_val:
            st.warning(f"⬅️ Please select at least one {f_config['label']}.");
            return
        if isinstance(selected_val, list):
            filtered_df = filtered_df[filtered_df[f_config["col"]].isin(selected_val)]
        else:
            filtered_df = filtered_df[filtered_df[f_config["col"]] == selected_val]

    if config.get("value_col"):
        filtered_df = filtered_df.dropna(subset=[config["value_col"]])

    st.header(f"📈 Analysis for: {filters[config['indicator_label']]}")

    if filtered_df.empty:
        st.info("No data available for the current filter combination.");
        return

    final_chart = utils.create_chart(filtered_df, config)
    st.altair_chart(final_chart, use_container_width=True)

    st.subheader("Data Context")
    sources = [s for s in filtered_df[config['source_col']].dropna().unique() if s]
    if sources: st.caption(f"Source: {', '.join(sources)}")

    notes = [n for n in filtered_df[config['notes_col']].dropna().unique() if n]
    if notes:
        st.markdown("**Data Comments/Notes:**")
        for note in notes: st.markdown(f"- {note}")

    st.divider()
    st.subheader("🤖 AI-Powered Analysis")

    if st.button(f"Generate Insights for {filters[config['indicator_label']]}"):
        with st.spinner("Analyzing..."):
            ai_text = config["analyzer_func"](filtered_df, filters[config['indicator_label']])
            st.session_state.current_ai_analysis = {
                "dashboard": config["title"], "indicator": filters[config['indicator_label']],
                "filters": {k: v for k, v in filters.items() if not (isinstance(v, list) and len(v) > 5)},
                "analysis_text": ai_text, "data_notes": notes, "data_source": sources,
                "raw_data": filtered_df.copy(), "config": config
            }
            st.rerun()

    if st.session_state.current_ai_analysis and st.session_state.current_ai_analysis["indicator"] == filters[
        config['indicator_label']]:
        current = st.session_state.current_ai_analysis
        st.markdown(current["analysis_text"])
        if st.button("💾 Save This Analysis", key="save_analysis"):
            if "saved_analyses" not in st.session_state: st.session_state.saved_analyses = []
            st.session_state.saved_analyses.append(current)
            st.session_state.current_ai_analysis = None
            st.success(f"Saved analysis for '{current['indicator']}'")
            st.rerun()

    with st.expander("View Filtered Raw Data"):
        st.dataframe(filtered_df)