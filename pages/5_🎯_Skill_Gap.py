import streamlit as st
import sys
import os
import plotly.graph_objects as go

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "database"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "ml_models"))

from database.db_utils import update_analysis
from ml_models.skill_gap import analyze_skill_gap, recommend_skills_to_learn
from auth_guard import require_login, render_sidebar_reset_button

st.set_page_config(page_title="Skill Gap Analysis - HireSense AI", page_icon="🎯")

require_login()
render_sidebar_reset_button()
st.title("🎯 Skill Gap Analysis")
st.write("Compare your resume's skills against a specific job description.")

# --- PREREQUISITE CHECKS ---
if "current_resume_text" not in st.session_state:
    st.warning("⚠️ Please upload a resume first.")
    st.info("Go to the **Resume Upload** page in the sidebar.")
    st.stop()

if "current_jd_text" not in st.session_state:
    st.warning("⚠️ Please add a job description first.")
    st.info("Go to the **Job Description** page in the sidebar. Skill gap analysis needs a specific JD to compare against.")
    st.stop()

st.write(f"Comparing your resume against the saved job description.")

if st.button("🔍 Analyze Skill Gap"):
    with st.spinner("Comparing skills..."):
        result = analyze_skill_gap(
            st.session_state.current_resume_text,
            st.session_state.current_jd_text
        )
        st.session_state.current_skill_gap_result = result

        # Update the existing analysis row (created in Step 5.2) with this new data
        if "current_analysis_id" in st.session_state:
            update_analysis(
                st.session_state.current_analysis_id,
                missing_skills=result["missing_skills"],
                matched_skills=result["matched_skills"]
            )

if "current_skill_gap_result" in st.session_state:
    result = st.session_state.current_skill_gap_result

    # --- MATCH PERCENTAGE GAUGE ---
    match_pct = result["match_percentage"]
    gauge_color = "#2ecc71" if match_pct >= 70 else "#f39c12" if match_pct >= 40 else "#e74c3c"

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=match_pct,
        number={"suffix": "%"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": gauge_color},
        },
        title={"text": "Skill Match Percentage"}
    ))
    fig_gauge.update_layout(height=300, margin=dict(t=50, b=10, l=30, r=30))
    st.plotly_chart(fig_gauge, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("✅ Matched Skills")
        if result["matched_skills"]:
            for skill in result["matched_skills"]:
                st.markdown(f"- ✅ `{skill}`")
        else:
            st.info("No matched skills found.")

    with col2:
        st.subheader("❌ Missing Skills")
        if result["missing_skills"]:
            for item in result["missing_skills"]:
                st.markdown(f"- ❌ `{item['skill']}` — mentioned {item['importance']}x in JD")
        else:
            st.success("No missing skills — great match!")

    if result["extra_skills"]:
        with st.expander("💡 Bonus skills you have (not required by this JD)"):
            st.write(", ".join(f"`{s}`" for s in result["extra_skills"]))

    st.divider()

    st.subheader("📚 Recommended Skills to Learn")
    top_skills = recommend_skills_to_learn(result["missing_skills"], top_n=5)
    if top_skills:
        for i, skill in enumerate(top_skills, 1):
            st.write(f"{i}. **{skill}**")
    else:
        st.info("You already cover all the key skills for this role!")

    st.caption(
        "💡 A richer, AI-generated learning roadmap (courses, projects, certifications) "
        "will be available in the Career Recommendations page."
    )