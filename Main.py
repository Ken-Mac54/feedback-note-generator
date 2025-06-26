import streamlit as st import pandas as pd import os from openai import OpenAI

--- Streamlit App Config ---

st.set_page_config(page_title="Feedback Note Generator", layout="wide") st.title("📋 Feedback Note Generator") st.markdown("Answer the following questions to generate a structured feedback note.")

--- Load Competency Definitions from Excel ---

def load_competencies(file_path): try: df = pd.read_excel(file_path, engine='openpyxl') return df except Exception as e: st.error(f"Error loading competency definitions: {e}") return None

competency_df = load_competencies("PAR Writing Guide (1).xlsx")

--- OpenAI Client Setup ---

def get_openai_client(): try: api_key = st.secrets["OPENAI_API_KEY"] return OpenAI(api_key=api_key) except KeyError: st.warning("Missing OpenAI API key. Please set it in Streamlit Secrets as 'OPENAI_API_KEY'.") return None

--- Input Form ---

with st.form("feedback_form"): rank = st.selectbox("What is the member's rank?", ["Cpl", "MCpl", "Sgt", "WO"], index=1) event_date = st.date_input("Event Date")

event_description = st.text_area("Event Description")
who = st.text_area("Who was this task completed for or who did it affect?")
what = st.text_area("What was done and what was the impact?")
where = st.text_area("Where was this completed?")
why = st.text_area("Why was this needed?")
how = st.text_area("How was the task completed?")
outcome = st.text_area("What was the outcome or benefit to the organization?")

submitted = st.form_submit_button("Generate Feedback Note")

--- AI Prompt and Completion ---

if submitted: client = get_openai_client() if not client: st.stop()

prompt = f"""

Using the following structure and tone, generate a formal military-style feedback note. Begin with 3–5 scored competencies using this format:

Event Description:

Initiative (HE) – [short rationale]
Communication (E) – [short rationale]

Then write a 1–2 paragraph Event Description incorporating the details below. Conclude with a short Outcome section summarizing the measurable or strategic benefit.

Rank: {rank}
Event Date: {event_date}

Event Description: {event_description}
Who: {who}
What: {what}
Where: {where}
Why: {why}
How: {how}
Outcome: {outcome}

Reference the competencies listed in the provided competency definition table, matching appropriate ones to the described activities. """

try:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that writes structured military feedback notes using provided event details."},
            {"role": "user", "content": prompt}
        ]
    )
    ai_output = response.choices[0].message.content
    st.markdown("---")
    st.subheader("Generated Feedback Note")
    st.text_area("Feedback Note Output", value=ai_output, height=400)

except Exception as e:
    st.error(f"Failed to connect to OpenAI API: {e}")

