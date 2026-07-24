import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "database"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "ml_models"))

from database.db_utils import save_analysis
from ml_models.ats_scorer import calculate_ats_score
from utils.auth_guard import require_login
from utils.chart_helpers import make_gauge_chart, make_breakdown_bar_chart

st.set_page_config(page_title="ATS Score - HireSense AI", page_icon="📊")

require_login()

st.title("📊 ATS Score Analysis")

# This page depends on a resume already being uploaded in this session
if "current_resume_id" not in st.session_state or "current_resume_text" not in st.session_state:
    st.warning("⚠️ Please upload a resume first.")
    st.info("Go to the **Resume Upload** page in the sidebar.")
    st.stop()

if "current_parsed_data" not in st.session_state:
    st.warning("⚠️ No parsed data found for your resume. Please re-upload it.")
    st.stop()

st.write(f"Analyzing resume: **{st.session_state.get('current_resume_filename', 'your uploaded resume')}**")

if st.button("🔍 Calculate ATS Score"):
    with st.spinner("Calculating your ATS score..."):
        result = calculate_ats_score(
            st.session_state.current_parsed_data,
            st.session_state.current_resume_text
        )
        st.session_state.current_ats_result = result

        # Save this as a new analysis record right away
        analysis_id = save_analysis(
            user_id=st.session_state.user_id,
            resume_id=st.session_state.current_resume_id,
            jd_id=st.session_state.get("current_jd_id"),  # None if no JD was uploaded
            ats_score=result["overall_score"],
            ats_breakdown=result["breakdown"]
        )
        st.session_state.current_analysis_id = analysis_id

if "current_ats_result" in st.session_state:
    result = st.session_state.current_ats_result
    overall = result["overall_score"]
    breakdown = result["breakdown"]

    # --- CIRCULAR PROGRESS (GAUGE) CHART ---
    fig_gauge = make_gauge_chart(overall, "Overall ATS Score", suffix=" / 100", thresholds=(50, 70))
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Interpretation message
    if overall >= 70:
        st.success("✅ Strong ATS compatibility! Your resume should pass most automated screenings.")
    elif overall >= 50:
        st.warning("⚠️ Moderate ATS compatibility. There's room to improve keyword coverage and formatting.")
    else:
        st.error("❌ Low ATS compatibility. Consider revising skills, keywords, and formatting.")

    # --- BREAKDOWN BAR CHART ---
    st.subheader("📈 Score Breakdown")

    category_labels = {
        "skills": "Skills Match",
        "formatting": "Formatting",
        "keywords": "Keywords",
        "experience": "Experience",
        "education": "Education",
        "projects_certifications": "Projects/Certs"
    }

    labels = [category_labels[k] for k in breakdown.keys()]
    values = list(breakdown.values())

    fig_bar = make_breakdown_bar_chart(labels, values)
    st.plotly_chart(fig_bar, use_container_width=True)

    with st.expander("ℹ️ How is this score calculated?"):
        st.write("""
        Your ATS score is a weighted average across six categories:
        - **Skills Match (30%)** — number of recognized skills found in your resume
        - **Formatting (20%)** — contact info completeness, section structure, resume length
        - **Keywords (20%)** — presence of strong action verbs and quantified achievements
        - **Experience (15%)** — substance of your experience section
        - **Education (10%)** — presence of an education section
        - **Projects/Certifications (5%)** — bonus signal from supplementary sections

        *Note: this is an educational approximation based on commonly cited ATS best
        practices, not a reverse-engineered clone of any specific commercial ATS software.*
        """)