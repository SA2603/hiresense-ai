import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "database"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))

from database.db_utils import save_resume, get_resumes_for_user
from utils.text_extraction import extract_text
from utils.auth_guard import require_login

st.set_page_config(page_title="Resume Upload - HireSense AI", page_icon="📄")

require_login()  # blocks anyone not logged in - everything below only runs if logged in

st.title("📄 Upload Your Resume")
st.write("Upload a PDF or DOCX resume to get started with analysis.")

uploaded_file = st.file_uploader(
    "Choose your resume file",
    type=["pdf", "docx"],
    help="Supported formats: PDF, DOCX"
)

if uploaded_file is not None:
    with st.spinner("Extracting text from your resume..."):
        try:
            extracted_text = extract_text(uploaded_file)
        except ValueError as e:
            st.error(str(e))
            st.stop()

    st.success(f"Successfully extracted text from **{uploaded_file.name}**")

    # Show a preview so the user can sanity-check the extraction worked well
    with st.expander("📋 Preview extracted text", expanded=True):
        st.text_area("Extracted content", extracted_text, height=300, disabled=True)

    if st.button("💾 Save this resume"):
        resume_id = save_resume(
            user_id=st.session_state.user_id,
            filename=uploaded_file.name,
            raw_text=extracted_text
        )
        st.session_state.current_resume_id = resume_id
        st.session_state.current_resume_text = extracted_text
        st.success(f"Resume saved! (ID: {resume_id}) You can now proceed to analysis.")

st.divider()

st.subheader("📚 Your previously uploaded resumes")
past_resumes = get_resumes_for_user(st.session_state.user_id)

if not past_resumes:
    st.info("You haven't uploaded any resumes yet.")
else:
    for resume in past_resumes:
        with st.expander(f"{resume['filename']} — uploaded {resume['uploaded_at']}"):
            st.text_area(
                "Content",
                resume["raw_text"][:1000] + ("..." if len(resume["raw_text"]) > 1000 else ""),
                height=150,
                disabled=True,
                key=f"resume_{resume['resume_id']}"
            )