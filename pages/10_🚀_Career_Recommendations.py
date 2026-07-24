import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "database"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "genai"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "prompts"))

from db_utils import update_analysis
from groq_client import call_llm, parse_json_response
from career_recommendation_prompts import build_career_recommendations_prompt
from auth_guard import require_login

st.set_page_config(page_title="Career Recommendations - HireSense AI", page_icon="🚀")

require_login()

st.title("🚀 Career Recommendations")
st.write(
    "Get personalized course, certification, project, and roadmap "
    "recommendations based on your resume and skill gaps."
)

if "current_resume_text" not in st.session_state:
    st.warning("⚠️ Please upload a resume first.")
    st.info("Go to the **Resume Upload** page in the sidebar.")
    st.stop()

# --- Automatically pull missing skills from Stage 6, if available ---
missing_skills_list = []
if "current_skill_gap_result" in st.session_state:
    missing_items = st.session_state.current_skill_gap_result.get("missing_skills", [])
    missing_skills_list = [item["skill"] for item in missing_items]

if missing_skills_list:
    st.success(
        f"✅ Using your skill gap results — recommendations will target "
        f"these missing skills: {', '.join(missing_skills_list[:8])}"
        + (f" and {len(missing_skills_list) - 8} more" if len(missing_skills_list) > 8 else "")
    )
else:
    st.info(
        "ℹ️ No skill gap data found for this session. Recommendations will be "
        "based on your resume alone. For more targeted results, run the "
        "**Skill Gap Analysis** page first (requires a job description)."
    )

has_jd = "current_jd_text" in st.session_state

if st.button("🚀 Generate Recommendations"):
    with st.spinner("Building your personalized career roadmap... this may take 15-25 seconds"):
        jd_text = st.session_state.get("current_jd_text") if has_jd else None
        system_prompt, user_prompt = build_career_recommendations_prompt(
            st.session_state.current_resume_text,
            missing_skills=missing_skills_list if missing_skills_list else None,
            jd_text=jd_text
        )
        raw_response = call_llm(system_prompt, user_prompt, temperature=0.6)

        try:
            parsed = parse_json_response(raw_response)
            st.session_state.current_career_recommendations = parsed

            if "current_analysis_id" in st.session_state:
                update_analysis(
                    st.session_state.current_analysis_id,
                    career_recommendations=parsed
                )
        except Exception as e:
            st.error("⚠️ Something went wrong generating recommendations. Please try again.")
            with st.expander("Technical details (for debugging)"):
                st.code(str(e))
                st.text(raw_response)

if "current_career_recommendations" in st.session_state:
    rec = st.session_state.current_career_recommendations

    tab_courses, tab_certs, tab_projects, tab_roadmap, tab_roles = st.tabs(
        ["📚 Courses", "📜 Certifications", "🛠️ Projects", "🗺️ Roadmap", "🎯 Career Roles"]
    )

    with tab_courses:
        for c in rec.get("recommended_courses", []):
            st.markdown(f"**{c['title']}** — *{c['platform']}*")
            st.caption(c["reason"])
            st.divider()

    with tab_certs:
        for c in rec.get("recommended_certifications", []):
            st.markdown(f"**{c['title']}** — *{c['issuing_body']}*")
            st.caption(c["reason"])
            st.divider()

    with tab_projects:
        for p in rec.get("recommended_projects", []):
            st.markdown(f"**{p['title']}**")
            st.write(p["description"])
            skills = p.get("skills_practiced", [])
            if skills:
                st.caption("Practices: " + ", ".join(f"`{s}`" for s in skills))
            st.divider()

    with tab_roadmap:
        for phase in rec.get("learning_roadmap", []):
            st.markdown(f"### {phase['phase']} — {phase['focus']}")
            for goal in phase.get("goals", []):
                st.write(f"- {goal}")
            st.divider()

    with tab_roles:
        for role in rec.get("suggested_career_roles", []):
            badge = "🟢 Natural next step" if role.get("typical_next_step") else "🔵 Stretch goal"
            st.markdown(f"**{role['role']}** — {badge}")
            st.caption(role["why_fit"])
            st.divider()

    st.caption(
        "💡 These are AI-generated suggestions meant as a starting point — "
        "always verify course/certification details independently before enrolling."
    )