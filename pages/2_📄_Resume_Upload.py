import streamlit as st
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "database"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "ml_models"))

from db_utils import save_resume, get_resumes_for_user
from text_extraction import extract_text
from auth_guard import require_login
from resume_parser import parse_resume

st.set_page_config(page_title="Resume Upload - HireSense AI", page_icon="📄")

require_login()

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

    with st.spinner("Parsing resume content..."):
        parsed = parse_resume(extracted_text)

    st.success(f"Successfully processed **{uploaded_file.name}**")

    # --- DASHBOARD DISPLAY ---
    st.subheader("📊 Parsed Resume Dashboard")

    col1, col2, col3 = st.columns(3)
    col1.metric("Name", parsed["name"] or "Not detected")
    col2.metric("Email", parsed["email"] or "Not detected")
    col3.metric("Phone", parsed["phone"] or "Not detected")

    st.markdown("### 🛠️ Skills Detected")
    if parsed["skills"]:
        # Display skills as nice pill-style tags using columns
        skill_cols = st.columns(4)
        for i, skill in enumerate(parsed["skills"]):
            skill_cols[i % 4].markdown(f"`{skill}`")
    else:
        st.info("No skills detected from our known skills list.")

    with st.expander("🎓 Education"):
        st.write(parsed["education"] or "No education section detected.")

    with st.expander("💼 Experience"):
        st.write(parsed["experience"] or "No experience section detected.")

    with st.expander("🚀 Projects"):
        st.write(parsed["projects"] or "No projects section detected.")

    with st.expander("📜 Certifications"):
        st.write(parsed["certifications"] or "No certifications section detected.")

    with st.expander("📋 Raw extracted text (full)"):
        st.text_area("Extracted content", extracted_text, height=300, disabled=True)

    if st.button("💾 Save this resume"):
        resume_id = save_resume(
            user_id=st.session_state.user_id,
            filename=uploaded_file.name,
            raw_text=extracted_text,
            parsed_data=parsed
        )
        st.session_state.current_resume_id = resume_id
        st.session_state.current_resume_text = extracted_text
        st.session_state.current_parsed_data = parsed
        st.success(f"Resume saved! (ID: {resume_id}) You can now proceed to analysis.")

st.divider()

st.subheader("📚 Your previously uploaded resumes")
past_resumes = get_resumes_for_user(st.session_state.user_id)

if not past_resumes:
    st.info("You haven't uploaded any resumes yet.")
else:
    for resume in past_resumes:
        with st.expander(f"{resume['filename']} — uploaded {resume['uploaded_at']}"):
            if resume["parsed_data"]:
                parsed_saved = json.loads(resume["parsed_data"])
                st.write(f"**Name:** {parsed_saved.get('name', 'N/A')}")
                st.write(f"**Email:** {parsed_saved.get('email', 'N/A')}")
                st.write(f"**Skills:** {', '.join(parsed_saved.get('skills', [])) or 'None detected'}")
            st.text_area(
                "Raw content",
                resume["raw_text"][:1000] + ("..." if len(resume["raw_text"]) > 1000 else ""),
                height=150,
                disabled=True,
                key=f"resume_{resume['resume_id']}"
            )