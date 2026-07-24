import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))

from auth_guard import require_login, render_sidebar_reset_button
from utils.report_generator import generate_report

st.set_page_config(page_title="Full Report - HireSense AI", page_icon="📄")

require_login()
render_sidebar_reset_button()

st.title("📄 Generate Full Report")
st.write(
    "Compile everything you've analyzed this session into one downloadable "
    "PDF report — resume summary, ATS score, skill gap, similarity, AI "
    "review, interview questions, and career recommendations."
)

if "current_parsed_data" not in st.session_state:
    st.warning("⚠️ Please upload and analyze a resume first.")
    st.info("Go to the **Resume Upload** page in the sidebar.")
    st.stop()

# --- Show what will be INCLUDED vs MISSING, so the user knows what to expect ---
st.subheader("📋 What will be included")

sections_status = {
    "Resume Summary": True,  # always available if we've gotten this far
    "ATS Score": "current_ats_result" in st.session_state,
    "Semantic Similarity": "current_similarity_score" in st.session_state,
    "Skill Gap Analysis": "current_skill_gap_result" in st.session_state,
    "AI Resume Review": "current_ai_review" in st.session_state,
    "Interview Questions": "current_interview_questions" in st.session_state,
    "Career Recommendations": "current_career_recommendations" in st.session_state,
}

cols = st.columns(2)
for i, (section, included) in enumerate(sections_status.items()):
    with cols[i % 2]:
        st.write(f"{'✅' if included else '⬜ (not run yet — will be skipped)'} {section}")

missing_count = sum(1 for v in sections_status.values() if not v)
if missing_count > 0:
    st.caption(
        f"💡 {missing_count} section(s) haven't been generated yet this session. "
        "Visit those pages first if you'd like them included, or generate the "
        "report now with just what's available."
    )

st.divider()

if st.button("📄 Generate PDF Report"):
    with st.spinner("Compiling your report..."):
        pdf_bytes = generate_report(
            parsed_data=st.session_state.current_parsed_data,
            ats_result=st.session_state.get("current_ats_result"),
            similarity_score=st.session_state.get("current_similarity_score"),
            skill_gap_result=st.session_state.get("current_skill_gap_result"),
            ai_review=st.session_state.get("current_ai_review"),
            interview_questions=st.session_state.get("current_interview_questions"),
            career_recommendations=st.session_state.get("current_career_recommendations"),
        )
        st.session_state.current_report_bytes = pdf_bytes

if "current_report_bytes" in st.session_state:
    st.success("✅ Report generated successfully!")
    st.download_button(
        label="⬇️ Download Report (PDF)",
        data=st.session_state.current_report_bytes,
        file_name=f"HireSense_Report_{st.session_state.username}.pdf",
        mime="application/pdf"
    )