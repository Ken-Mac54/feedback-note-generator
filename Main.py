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

# Feedback Form
with st.form("feedback_form"):
    rank = st.selectbox("Select rank level", ["Cpl", "MCpl", "Sgt", "WO"], index=1)

    event_description = st.text_area("Event Description", placeholder="Brief summary of the event or project")
    
    q1 = st.text_area(
        "Who was involved and what was done?",
        placeholder="Describe who completed the task, who was impacted, and what actions were taken."
    )
    q2 = st.text_area(
        "Where and why did this happen?",
        placeholder="Explain the location or context and the reason the task or project was necessary."
    )
    q3 = st.text_area(
        "How was it done and what was the outcome?",
        placeholder="Highlight any notable processes, tools, or innovations used and the final result."
    )

    submitted = st.form_submit_button("Generate Feedback Note")

# Generate Feedback Note with OpenAI
if submitted and client:
    try:
        prompt = f"""
Rank: {rank}
Event Description: {event_description}
Who and What: {q1}
Where and Why: {q2}
How and Outcome: {q3}

Using the input above, generate a formal military-style feedback note.

Start with 3–5 competencies with performance ratings (E, HE, etc.). Use the following format:

Event Description:
Competency Name (Score) – short rationale
...
[1–2 paragraph description]

Outcome:
[2–3 sentence measurable or strategic result]

Note: Competencies pulled from one rank higher should be labelled (e.g. “Innovation (HE – Sgt Competency: [definition])”). All ratings should be E or higher unless otherwise noted.
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
                    "content": prompt
                }
            ]
        )

        output_text = response.choices[0].message.content
        st.markdown("### ✏️ Generated Feedback Note")
        st.text_area("Output", output_text, height=400)
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
from io import BytesIO

def create_word_doc(text):
    doc = Document()
    doc.add_heading("Performance Feedback Note", 0)

    # Split text into sections
    lines = text.strip().splitlines()
    section = None

    for line in lines:
        line = line.strip()
        if line.lower().startswith("event description"):
            section = "event"
            doc.add_paragraph("Event Description:", style='Heading 2')
            continue
        elif line.lower().startswith("outcome"):
            section = "outcome"
            doc.add_paragraph("Outcome:", style='Heading 2')
            continue
        elif not line:
            doc.add_paragraph("")  # spacing
            continue

        para = doc.add_paragraph()
        run = para.add_run(line)
        run.font.name = 'Arial'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
        run.font.size = Pt(11)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Create and offer Word download
if output_text:
    doc_buffer = create_word_doc(output_text)
    st.download_button(
        label="📄 Download as Word Document",
        data=doc_buffer,
        file_name="feedback_note.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    except Exception as e:
        st.error(f"Failed to connect to OpenAI API: {e}")