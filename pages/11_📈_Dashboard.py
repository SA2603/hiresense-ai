import streamlit as st
import sys
import os
import plotly.graph_objects as go

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "database"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))

from database.db_utils import get_full_analysis_history
from auth_guard import require_login, render_sidebar_reset_button
from utils.chart_helpers import make_gauge_chart

st.set_page_config(page_title="Dashboard - HireSense AI", page_icon="📈", layout="wide")
require_login()
render_sidebar_reset_button()

st.title("📈 Your Dashboard")
st.write(f"Welcome back, **{st.session_state.username}**")

# --- CURRENT SESSION SNAPSHOT ---
st.subheader("📊 Current Session Snapshot")

has_ats = "current_ats_result" in st.session_state
has_similarity = "current_similarity_score" in st.session_state
has_skill_gap = "current_skill_gap_result" in st.session_state

if not (has_ats or has_similarity or has_skill_gap):
    st.info(
        "No analysis run yet in this session. Visit **ATS Score**, "
        "**Skill Gap Analysis**, or **Resume Similarity** to generate results."
    )
else:
    col1, col2, col3 = st.columns(3)

    with col1:
        if has_ats:
            score = st.session_state.current_ats_result["overall_score"]
            fig = make_gauge_chart(score, "ATS Score", suffix=" / 100", thresholds=(50, 70))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ATS Score not yet calculated.")

    with col2:
        if has_skill_gap:
            match_pct = st.session_state.current_skill_gap_result["match_percentage"]
            fig = make_gauge_chart(match_pct, "Skill Match", suffix="%", thresholds=(40, 70))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Skill Gap not yet analyzed.")

    with col3:
        if has_similarity:
            sim = st.session_state.current_similarity_score
            fig = make_gauge_chart(sim, "Similarity", suffix="%", thresholds=(45, 70))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Similarity not yet calculated.")

    # --- SKILLS SUMMARY ---
    if has_skill_gap:
        st.subheader("🛠️ Skills Summary")
        result = st.session_state.current_skill_gap_result
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Matched Skills", len(result["matched_skills"]))
        with col_b:
            st.metric("Missing Skills", len(result["missing_skills"]))

        if result["missing_skills"]:
            top_missing = [item["skill"] for item in result["missing_skills"][:5]]
            st.write("**Top missing skills:** " + ", ".join(f"`{s}`" for s in top_missing))

    # --- FEATURE COMPLETION CHECKLIST ---
    st.subheader("✅ Analysis Progress")
    checklist = {
        "Resume Uploaded": "current_resume_text" in st.session_state,
        "Job Description Added": "current_jd_text" in st.session_state,
        "ATS Score Calculated": has_ats,
        "Skill Gap Analyzed": has_skill_gap,
        "Similarity Calculated": has_similarity,
        "AI Review Generated": "current_ai_review" in st.session_state,
        "Interview Questions Generated": "current_interview_questions" in st.session_state,
        "Cover Letter Generated": "current_cover_letter" in st.session_state,
        "Career Recommendations Generated": "current_career_recommendations" in st.session_state,
    }
    completed = sum(checklist.values())
    total = len(checklist)
    st.progress(completed / total, text=f"{completed} / {total} steps completed")

    check_cols = st.columns(3)
    for i, (label, done) in enumerate(checklist.items()):
        with check_cols[i % 3]:
            st.write(f"{'✅' if done else '⬜'} {label}")

st.divider()

# --- HISTORY FROM DATABASE ---
st.subheader("📚 Analysis History")

history = get_full_analysis_history(st.session_state.user_id)

if not history:
    st.info("No past analyses found. Run an ATS Score or Skill Gap analysis to start building your history.")
else:
    for entry in history:
        label_parts = [entry["resume_filename"] or "Unknown resume"]
        if entry["role_title"] or entry["company_name"]:
            role_company = " @ ".join(filter(None, [entry["role_title"], entry["company_name"]]))
            label_parts.append(role_company)
        label_parts.append(str(entry["created_at"]))
        label = " — ".join(label_parts)

        with st.expander(label):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("ATS Score", f"{entry['ats_score']:.1f}" if entry['ats_score'] is not None else "N/A")
            with col2:
                st.metric("Similarity", f"{entry['similarity_score']:.1f}%" if entry['similarity_score'] is not None else "N/A")