import streamlit as st
from pathlib import Path

st.title("Maryland Case Study")

BASE_DIR = Path(__file__).resolve().parent.parent
PDF_PATH = BASE_DIR / "data" / "Maryland Case Study Text.pdf"

if PDF_PATH.exists():
    pdf_bytes = PDF_PATH.read_bytes()

    # Display PDF
    st.pdf(
        pdf_bytes,
        height=1000,
    )

    # Download button
    st.download_button(
        label="Download Case Study",
        data=pdf_bytes,
        file_name="Maryland_Case_Study.pdf",
        mime="application/pdf",
        icon=":material/download:",
    )
else:
    st.error("Maryland Case Study PDF not found.")