import streamlit as st
import pandas as pd
import openai
import os
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
from io import BytesIO

# --- Streamlit App Configuration ---
st.set_page_config(page_title="PAR Writing Assistant", layout="wide")
st.title("📋 Feedback Note Generator")
st.markdown("Answer the following questions to generate a structured feedback note.")

# --- Load Excel Definitions ---
try:
    excel_path = "PAR Writing Guide (1).xlsx"
    competency_df = pd.read_excel(excel_path, engine="openpyxl")
    st.success("Competency definitions loaded successfully.")
except Exception as e:
    st.error(f"Error loading competency definitions: {e}")
    competency_df = None

# --- Set up OpenAI Client ---
try:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception as e:
    st.error(f"Failed to initialize OpenAI client: {e}")
    client = None

# --- Feedback Form ---
with st.form("feedback_form"):
    rank = st.selectbox("Select rank level", ["Cpl", "MCpl", "Sgt", "WO"], index=1)
    last_name = st.text_input("Enter last name of the member")

    event_description = st.text_area("Event Description", placeholder="Brief summary of the event or project")
    q1 = st.text_area("Who was involved and what was done?",
                      placeholder="Describe who completed the task, who was impacted, and what actions were taken.")
    q2 = st.text_area("Where and why did this happen?",
                      placeholder="Explain the location or context and the reason the task or project was necessary.")
    q3 = st.text_area("How was it done and what was the outcome?",
                      placeholder="Highlight any notable processes, tools, or innovations used and the final result.")

# Optional: Select focus competencies
if competency_df is not None:
    focus_areas = st.multiselect(
        "Optional: Select 1–3 competencies to focus on (optional)",
        options=sorted(competency_df['Core Competency'].dropna().unique()),
        help="If selected, the AI will try to include these if they logically apply. It may omit them if not justified."
    )
else:
    focus_areas = []

submitted = st.form_submit_button("Generate Feedback Note")

# --- Generate Feedback Note with OpenAI ---
if submitted and client:
    try:
        focus_string = ", ".join(focus_areas) if focus_areas else "None"

        prompt = f"""
        Rank: {rank}
        Last Name: {last_name}
        Event Description: {event_description}
        Who and What: {q1}
        Where and Why: {q2}
        How and Outcome: {q3}
        User-selected Competency Focus Areas:          {focus_string}

        Using the input above, generate a formal       military-style feedback note.

        Start with 3–5 competencies and  sub-competencies with performance ratings (E, HE,   etc.). Use the following format:

Event Description:
Communication: Written Communication (HE) – [short rationale]
...
[1–2 paragraph description using the member's rank and last name on first mention, then only they/them/their pronouns thereafter.]

Outcome:
[2–3 sentence measurable or strategic result.]

Note:

Use only the format "Core Competency: Sub-competency (Score) – rationale".

If a competency is pulled from a higher rank, it must be labeled with that rank and scored no lower than HE (e.g. "(HE – Sgt Competency: [definition])").

If the user has selected specific competencies, prioritize including them when reasonably justified by the event. If they are a stretch or not applicable, omit them.

Avoid referring to the member only by rank. Use the abbreviated rank format (e.g., "MCpl") followed by the last name for the first mention (e.g., "MCpl Macpherson"), and then refer to them using they/them pronouns only. Do not spell out rank names like 'Master Corporal'.
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a military admin assistant trained to write professional performance feedback notes. "
                        "Always use abbreviated rank formats (e.g., MCpl, WO). Do not spell out full rank names like 'Master Corporal'. "
                        "When referring to the member, use the format 'Rank Lastname' for the first mention only, then use gender-neutral pronouns (they/them/their) exclusively."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        output_text = response.choices[0].message.content
        st.markdown("### ✏️ Generated Feedback Note")
        st.text_area("Output", output_text, height=400)

        # --- Create Word Document ---
        def create_word_doc(text):
            doc = Document()
            doc.add_heading("Performance Feedback Note", 0)
            lines = text.strip().splitlines()
            for line in lines:
                line = line.strip()
                if line.lower().startswith("event description"):
                    doc.add_paragraph("Event Description:", style='Heading 2')
                elif line.lower().startswith("outcome"):
                    doc.add_paragraph("Outcome:", style='Heading 2')
                elif not line.strip():
                    doc.add_paragraph("")
                else:
                    para = doc.add_paragraph()
                    run = para.add_run(line)
                    run.font.name = 'Arial'
                    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
                    run.font.size = Pt(11)
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            return buffer

        doc_buffer = create_word_doc(output_text)

        # --- Download Button ---
        st.download_button(
            label="📄 Download as Word Document",
            data=doc_buffer,
            file_name="feedback_note.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    except Exception as e:
        st.error(f"Failed to connect to OpenAI API: {e}")