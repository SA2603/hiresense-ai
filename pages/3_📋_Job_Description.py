import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "database"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))

from database.db_utils import save_job_description, get_job_descriptions_for_user
from utils.text_extraction import extract_text
from auth_guard import require_login, render_sidebar_reset_button

st.set_page_config(page_title="Job Description - HireSense AI", page_icon="📋")

require_login()
render_sidebar_reset_button()

st.title("📋 Add a Job Description (Optional)")
st.write(
    "Adding a job description lets us calculate skill gaps and similarity "
    "score against a specific role. You can skip this and still get a "
    "general ATS score."
)

input_method = st.radio(
    "How would you like to provide the job description?",
    ["Paste text", "Upload file (PDF/DOCX)"],
    horizontal=True
)

jd_text = None

if input_method == "Paste text":
    jd_text = st.text_area(
        "Paste the job description here",
        height=250,
        placeholder="Paste the full job posting text..."
    )
else:
    uploaded_jd = st.file_uploader("Choose a JD file", type=["pdf", "docx"])
    if uploaded_jd is not None:
        with st.spinner("Extracting text..."):
            try:
                jd_text = extract_text(uploaded_jd)
            except ValueError as e:
                st.error(str(e))
                st.stop()
        with st.expander("📋 Preview extracted text", expanded=True):
            st.text_area("Extracted content", jd_text, height=250, disabled=True)

col1, col2 = st.columns(2)
with col1:
    company_name = st.text_input("Company name (optional)")
with col2:
    role_title = st.text_input("Role / job title (optional)")

if st.button("💾 Save job description"):
    if not jd_text or not jd_text.strip():
        st.warning("Please paste or upload a job description first.")
    else:
        jd_id = save_job_description(
            user_id=st.session_state.user_id,
            raw_text=jd_text,
            company_name=company_name or None,
            role_title=role_title or None
        )
        st.session_state.current_jd_id = jd_id
        st.session_state.current_jd_text = jd_text
        st.session_state.current_jd_company = company_name or ""
        st.session_state.current_jd_role = role_title or ""
        st.success(f"Job description saved! (ID: {jd_id})")

st.divider()
st.info(
    "💡 You can also skip this step entirely and go straight to the "
    "**ATS Score** page for a general resume analysis without a specific JD."
)

st.divider()
st.subheader("📚 Your previously saved job descriptions")
past_jds = get_job_descriptions_for_user(st.session_state.user_id)

if not past_jds:
    st.info("No job descriptions saved yet.")
else:
    for jd in past_jds:
        label = f"{jd['role_title'] or 'Untitled role'}"
        if jd['company_name']:
            label += f" @ {jd['company_name']}"
        label += f" — {jd['uploaded_at']}"
        with st.expander(label):
            st.text_area(
                "Content",
                jd["raw_text"][:1000] + ("..." if len(jd["raw_text"]) > 1000 else ""),
                height=150,
                disabled=True,
                key=f"jd_{jd['jd_id']}"
            )