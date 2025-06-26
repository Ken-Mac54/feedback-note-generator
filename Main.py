import streamlit as st
import pandas as pd
import openai
import os

# Streamlit App Configuration
st.set_page_config(page_title="Feedback Note Generator", layout="wide")
st.title("📋 Feedback Note Generator")
st.markdown("Answer the following questions to generate a structured feedback note.")

# Load Excel Definitions
try:
    excel_path = "PAR Writing Guide (1).xlsx"
    competency_df = pd.read_excel(excel_path, engine="openpyxl")
    st.success("Competency definitions loaded successfully.")
except Exception as e:
    st.error(f"Error loading competency definitions: {e}")
    competency_df = None

# Set up OpenAI Client
try:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception as e:
    st.error(f"Failed to initialize OpenAI client: {e}")
    client = None

# Form for Input
with st.form("feedback_form"):
    rank = st.selectbox("Select rank level", ["Cpl", "MCpl", "Sgt", "WO"], index=1)

    event_description = st.text_area("Event Description", placeholder="Brief summary of the event")
    q_who = st.text_area("Who was this task completed for? Who did it affect?")
    q_what = st.text_area("What was done and what was the impact?")
    q_where = st.text_area("Where was this completed?")
    q_why = st.text_area("Why was this needed?")
    q_how = st.text_area("How was the task completed? Include any specific actions or processes.")
    q_outcome = st.text_area("What was the result or outcome of the work?")

    submitted = st.form_submit_button("Generate Feedback Note")

# Build Prompt and Generate Feedback Note
if submitted and client:
    try:
        full_input = f"""
Rank: {rank}
Event Description: {event_description}
Who: {q_who}
What: {q_what}
Where: {q_where}
Why: {q_why}
How: {q_how}
Outcome: {q_outcome}

Using the input above, generate a military-style feedback note. Begin with 3–5 competencies with performance ratings (E, HE, etc.). Use the following format:

Event Description:
Competency Name (Score) – short rationale
...
[1-2 paragraph description]

Outcome:
[2-3 sentence measurable or strategic result]
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a military admin assistant trained to write professional performance feedback notes."
                },
                {
                    "role": "user",
                    "content": full_input
                }
            ]
        )

        output_text = response.choices[0].message.content
        st.markdown("### ✏️ Generated Feedback Note")
        st.text_area("Output", output_text, height=400)

    except Exception as e:
        st.error(f"Failed to connect to OpenAI API: {e}")