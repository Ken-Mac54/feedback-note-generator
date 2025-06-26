import streamlit as st
import openai

# --- Streamlit App Config ---
st.set_page_config(page_title="Feedback Note Generator", layout="wide")
st.title("Feedback Note Generator")
st.markdown("Answer the following questions to generate a structured feedback note. This tool works for supervisors or individuals.")

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
    rank = st.selectbox("What is the member's rank?", ["Cpl", "MCpl", "Sgt", "WO"], index=1)
    role = st.text_input("What is their role or position?")

    q1 = st.text_area("1. What task or project was completed?", placeholder="Describe the main task, project, or effort.")
    q2 = st.text_area("2. What problem, need, or opportunity was being addressed?", placeholder="Describe the context or gap.")
    q3 = st.text_area("3. What steps were taken to achieve the result?", placeholder="List actions or decisions taken.")
    q4 = st.text_area("4. Who else was impacted or involved?", placeholder="Mention collaboration, stakeholders, or beneficiaries.")
    q5 = st.text_area("5. What was the result or benefit to the organization?", placeholder="Highlight the outcome or improvement.")

    submitted = st.form_submit_button("Generate Feedback Note")

# --- AI Prompt Formatting and Processing ---
if submitted:
    client = get_openai_client()
    if not client:
        st.stop()

    prompt = f"""
Rank: {rank}
Role: {role}

Task: {q1}
Problem/Context: {q2}
Actions Taken: {q3}
Stakeholders: {q4}
Outcome: {q5}

Using the following structure and tone, generate a formal military-style feedback note starting with 3–5 competencies and ratings, followed by an Event Description and an Outcome section. Use the scoring format like:

Event Description:

Initiative (HE) – [short rationale]
Communication (E) – [short rationale]

Then write a 1–2 paragraph description of the event with the details provided above.

Outcome:

Write a 2–3 sentence summary of the measurable or strategic benefit to the unit or organization.
"""

    try:
        openai.ai_key = api_key
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that writes structured military feedback notes using event descriptions."},
                {"role": "user", "content": f"{combined_input}"}
            ]
        )
        ai_output = response['choices'][0]['message']['content']
        st.markdown("🧾 Generated Feedback Note"
        st.text_area("Output", value=ai_output, height=400)
    except Exception as e:
       st.error(f"❌ Failed to generate feedback note: {e}")
