import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "database"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "genai"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "prompts"))

from db_utils import update_analysis
from groq_client import call_llm, parse_structured_review
from resume_review_prompts import build_resume_review_prompt
from auth_guard import require_login, render_sidebar_reset_button
st.set_page_config(page_title="AI Resume Review - HireSense AI", page_icon="🤖")

require_login()
render_sidebar_reset_button()

st.title("🤖 AI Resume Review")
st.write(
    "Get detailed, AI-generated feedback on your resume — strengths, "
    "weaknesses, and specific suggestions for improvement."
)

if "current_resume_text" not in st.session_state:
    st.warning("⚠️ Please upload a resume first.")
    st.info("Go to the **Resume Upload** page in the sidebar.")
    st.stop()

has_jd = "current_jd_text" in st.session_state
if has_jd:
    st.info("✅ A job description is available — feedback will be tailored to this specific role.")
else:
    st.info("ℹ️ No job description added — you'll get a general resume quality review. Add one on the **Job Description** page for role-specific feedback.")

if st.button("🤖 Generate AI Review"):
    with st.spinner("Analyzing your resume with AI... this may take 10-20 seconds"):
        jd_text = st.session_state.get("current_jd_text") if has_jd else None
        system_prompt, user_prompt = build_resume_review_prompt(
            st.session_state.current_resume_text,
            jd_text
        )
        try:
            raw_response = call_llm(system_prompt, user_prompt, temperature=0.5)
            parsed_review = parse_structured_review(raw_response)

            st.session_state.current_ai_review = parsed_review

            if "current_analysis_id" in st.session_state:
                update_analysis(
                    st.session_state.current_analysis_id,
                    ai_review=raw_response
                )
        except RuntimeError as e:
            st.error(f"⚠️ {str(e)}")
            st.info("Please try again in a moment.")

if "current_ai_review" in st.session_state:
    review = st.session_state.current_ai_review

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💪 Strengths")
        st.markdown(review["strengths"] or "_No strengths identified._")

    with col2:
        st.subheader("⚠️ Weaknesses")
        st.markdown(review["weaknesses"] or "_No weaknesses identified._")

    st.divider()

    with st.expander("📐 Formatting Suggestions", expanded=True):
        st.markdown(review["formatting_suggestions"] or "_No formatting suggestions._")

    with st.expander("✍️ Grammar Suggestions"):
        st.markdown(review["grammar_suggestions"] or "_No grammar issues found._")

    with st.expander("🔑 Keyword Suggestions"):
        st.markdown(review["keyword_suggestions"] or "_No keyword suggestions._")

    st.divider()

    st.subheader("🗣️ Recruiter Feedback")
    st.info(review["recruiter_feedback"] or "No feedback available.")

    st.caption(
        "💡 This feedback is AI-generated and should be used as guidance, "
        "not an absolute judgment — always apply your own judgment too."
    )