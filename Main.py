import streamlit as st
import pandas as pd
import openai
import os

# --- Streamlit App Config ---
st.set_page_config(page_title="Feedback Note Generator", layout="wide")
st.title("📋 Feedback Note Generator")
st.markdown("Fill out the form below to generate a structured feedback note. Works for both supervisors and individuals.")

# --- Load Competency Definitions from Excel ---
@st.cache_data
def load_definitions():
    try:
        df = pd.read_excel("PAR Writing Guide (1).xlsx")
        return df
    except Exception as e:
        st.error(f"Error loading competency definitions: {e}")
        return pd.DataFrame()

definitions_df = load_definitions()

# --- OpenAI Client Setup ---
def get_openai_client():
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
        openai.api_key = api_key
        return openai
    except KeyError:
        st.warning("Missing OpenAI API key. Please set it in Streamlit Secrets as 'OPENAI_API_KEY'.")
        return None

# --- Input Form ---
with st.form("feedback_form"):
    rank = st.selectbox("Select the member's rank:", ["Cpl", "MCpl", "Sgt", "WO"], index=1)

    event = st.text_area("1. Event Description", placeholder="What was the task, project, or situation?")
    who = st.text_area("2. Who", placeholder="Who was this task completed for, and who did it affect?")
    what = st.text_area("3. What", placeholder="What actions were taken, and what was the impact?")
    where = st.text_area("4. Where", placeholder="Where was this completed (unit, location, platform, etc.)?")
    why = st.text_area("5. Why", placeholder="Why was this task or project important? What need or goal did it support?")
    how = st.text_area("6. How", placeholder="How was the task completed? What tools, methods, or problem-solving approaches were used?")
    outcome = st.text_area("7. Outcome", placeholder="What changed as a result of these actions? What benefit was achieved for the team, unit, or organization?")

    submitted = st.form_submit_button("Generate Feedback Note")

# --- Feedback Note Generation ---
if submitted:
    client = get_openai_client()
    if not client:
        st.stop()

    prompt = f"""
Rank: {rank}

Event Description: {event}
Who: {who}
What: {what}
Where: {where}
Why: {why}
How: {how}
Outcome: {outcome}

Using the following structure and tone, generate a formal military-style feedback note starting with 3–5 competencies and ratings, followed by an Event Description and an Outcome section. Use the scoring format like:

Event Description:
Initiative (HE) – [short rationale]
Communication (E) – [short rationale]

Then write a 1–2 paragraph description of the event with the details provided above.

Outcome:
Write a 2–3 sentence summary of the measurable or strategic benefit to the unit or organization.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that writes structured military feedback notes using input based on a defined prompting structure."},
                {"role": "user", "content": prompt}
            ]
        )
        ai_output = response['choices'][0]['message']['content']
        st.subheader("📄 Generated Feedback Note")
        st.markdown(ai_output)
    except Exception as e:
        st.error(f"Failed to connect to OpenAI API: {e}")
