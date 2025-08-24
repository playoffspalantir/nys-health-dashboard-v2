# modules/ai_analysis.py
import streamlit as st
import google.generativeai as genai

# --- More Robust API Key Configuration ---
# This allows the app to run locally without a secrets file.
API_KEY_CONFIGURED = False
try:
    # This will succeed on Streamlit Cloud if the secret is set.
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    API_KEY_CONFIGURED = True
except (KeyError, FileNotFoundError):
    # This block will be executed during local development if no secrets file is found.
    # We will pass silently and handle the missing key in the functions below.
    # This prevents the app from crashing on startup.
    st.warning("🔑 AI features disabled. For local development, create a .streamlit/secrets.toml file with your GEMINI_API_KEY. For deployment, add it to your Streamlit Cloud secrets.", icon="⚠️")
    pass

def _get_ai_response(prompt):
    """Internal function to handle API calls and errors."""
    if not API_KEY_CONFIGURED:
        return "AI Analysis is disabled because the API key is not configured."
    try:
        model = genai.GenerativeModel(model_name='gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Analysis Error: {str(e)}"

def analyze_chirs_data(df, indicator_name):
    if df.empty: return "No data for analysis."
    data_string = df[['Geographic area', 'Year', 'Rate/Percent']].to_csv(index=False)
    prompt = (f"You are a professional epidemiologist providing an objective, data-driven summary. "
              f"Based *only* on the trend data for the indicator '{indicator_name}', write a concise analysis in one or two paragraphs of formal prose. "
              f"Do not use bullet points, markdown formatting (like bolding), or section titles. "
              f"Focus on the overall trend, identify any significant county-level outliers or divergences, and conclude with a statement on the general pattern observed.\n\n"
              f"Data:\n```{data_string}```")
    return _get_ai_response(prompt)

def analyze_prevention_data(df, indicator_name):
    if df.empty: return "No data for analysis."
    data_for_ai = df[['County Name', 'Data Years', 'Percentage/Rate/Ratio', '2024 Objective']]
    data_string = data_for_ai.to_csv(index=False)
    prompt = (f"You are a professional epidemiologist providing an objective, data-driven summary. "
              f"Based *only* on the trend data for the indicator '{indicator_name}', write a concise analysis in one or two paragraphs of formal prose. "
              f"Do not use bullet points, markdown formatting (like bolding), or section titles. "
              f"Focus on the overall progress of the selected counties toward the 2024 objective, highlighting any counties with notable improvement or worsening trends.\n\n"
              f"Data:\n```{data_string}```")
    return _get_ai_response(prompt)

def analyze_mch_data(df, indicator_name):
    if df.empty: return "No data for analysis."
    data_for_ai = df[['County Name', 'Data Years', 'Percentage/Rate', 'MCH Objective']]
    data_string = data_for_ai.to_csv(index=False)
    prompt = (f"You are a professional epidemiologist specializing in Maternal and Child Health (MCH), providing an objective, data-driven summary. "
              f"Based *only* on the trend data for the indicator: '{indicator_name}', write a concise analysis in one or two paragraphs of formal prose. "
              f"Do not use bullet points, markdown formatting (like bolding), or section titles. "
              f"Focus on county-level progress towards the MCH Objective and mention if data quality comments (e.g., 'Unstable Estimate') warrant cautious interpretation of the trends.\n\n"
              f"Data:\n```{data_string}```")
    return _get_ai_response(prompt)