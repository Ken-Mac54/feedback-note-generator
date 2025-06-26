import streamlit as st
import openai
import pandas as pd
import os

# --- App Config ---
st.set_page_config(page_title="Feedback Note Generator", layout="wide")
st.title("📋 Feedback Note Generator")
st.markdown("Answer the following questions to generate a structured feedback note.")

# --- Load Definitions from Excel ---
def load_definitions(path):
    try:
        df = pd.read_excel(path)
        definitions = {}
        for _, row in df.iterrows():
            competency = str(row.get("Competency")).strip()
            definition = str(row.get("Definition")).strip()
            if competency and definition:
                definitions[competency] = definition
        return definitions
    except Exception as e:
        st.error(f"Could not load definitions: {e}")
        return {}

definitions_path = "/mnt/data/PAR Writing Guide (1).xlsx"
competency_definitions = load_definitions(definitions_path)

# --- OpenAI Client ---
def get_openai_client():
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
        openai.api_key = api_key
        return True
    except KeyError:
        st.warning("OpenAI API key not found in secrets.")
        return False

# --- Input Form ---
with st.form("feedback_form"):
    rank = st.selectbox("Rank", ["Cpl", "MCpl", "Sgt", "WO"], index=1)
    role = st.text_input("Role or position")
    q1 = st.text_area("1. What task or project was completed?")
    q2 = st.text_area("2. What problem, need, or opportunity was being addressed?")
    q3 = st.text_area("3. What steps were taken to achieve the result?")
    q4 = st.text_area("4. Who else was impacted or involved?")
    q5 = st.text_area("5. What was the result or benefit to the organization?")
    submitted = st.form_submit_button("Generate Feedback Note")

# --- Prompt to OpenAI ---
if submitted and get_openai_client():
    definition_block = "\n".join([f"{k}: {v}" for k, v in competency_definitions.items()])
    prompt = f"""
You are writing a formal military feedback note for a {rank} in the role of {role}.

Below are competency definitions:
{definition_block}

Task: {q1}
Context: {q2}
Actions: {q3}
Stakeholders: {q4}
Outcome: {q5}

Generate a feedback note with the following format:
1. Start with 3–5 relevant competencies and performance scores (E, HE, etc.), referencing the competency definitions.
2. Provide a 1–2 paragraph Event Description using the user's input.
3. Finish with an Outcome section summarizing the strategic or measurable benefit.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that writes structured military feedback notes."},
                {"role": "user", "content": prompt}
            ]
        )
        ai_output = response["choices"][0]["message"]["content"]
        st.markdown("### ✍️ Feedback Note Output")
        st.text(ai_output)
    except Exception as e:
        st.error(f"OpenAI call failed: {e}")