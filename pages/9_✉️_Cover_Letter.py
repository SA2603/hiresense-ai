import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "database"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "genai"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "prompts"))

from db_utils import update_analysis
from groq_client import call_llm
from cover_letter_prompts import build_cover_letter_prompt
from auth_guard import require_login, render_sidebar_reset_button

st.set_page_config(page_title="Cover Letter - HireSense AI", page_icon="✉️")

require_login()
render_sidebar_reset_button()

st.title("✉️ AI Cover Letter Generator")
st.write("Generate a personalized cover letter based on your resume and a specific job description.")

# --- PREREQUISITE CHECKS ---
if "current_resume_text" not in st.session_state:
    st.warning("⚠️ Please upload a resume first.")
    st.info("Go to the **Resume Upload** page in the sidebar.")
    st.stop()

if "current_jd_text" not in st.session_state:
    st.warning("⚠️ A cover letter needs a specific job description to be meaningful.")
    st.info("Go to the **Job Description** page in the sidebar to add one first.")
    st.stop()

st.write("Fill in a few details, then generate your cover letter:")

col1, col2 = st.columns(2)
with col1:
    company_name = st.text_input(
        "Company name",
        value=st.session_state.get("current_jd_company", ""),
        placeholder="e.g., Acme Corp"
    )
with col2:
    role_title = st.text_input(
        "Role title",
        value=st.session_state.get("current_jd_role", ""),
        placeholder="e.g., Software Engineer"
    )

if st.button("✉️ Generate Cover Letter"):
    if not company_name.strip() or not role_title.strip():
        st.warning("Please fill in both company name and role title.")
    else:
        with st.spinner("Writing your cover letter... this may take 15-20 seconds"):
            system_prompt, user_prompt = build_cover_letter_prompt(
                st.session_state.current_resume_text,
                st.session_state.current_jd_text,
                company_name,
                role_title
            )
            try:
                cover_letter = call_llm(system_prompt, user_prompt, temperature=0.8)
                st.session_state.current_cover_letter = cover_letter

                if "current_analysis_id" in st.session_state:
                    update_analysis(
                        st.session_state.current_analysis_id,
                        cover_letter=cover_letter
                    )
            except RuntimeError as e:
                st.error(f"⚠️ {str(e)}")
                st.info("Please try again in a moment.")

if "current_cover_letter" in st.session_state:
    st.divider()
    st.subheader("📄 Your Cover Letter")