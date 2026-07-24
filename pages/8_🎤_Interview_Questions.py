import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "database"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "genai"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "prompts"))

from db_utils import update_analysis
from groq_client import call_llm, parse_json_response
from interview_prompts import build_interview_questions_prompt
from auth_guard import require_login

st.set_page_config(page_title="Interview Questions - HireSense AI", page_icon="🎤")

require_login()

st.title("🎤 AI Interview Question Generator")
st.write(
    "Generate personalized interview questions based on your resume — "
    "HR, technical, behavioral, project-based, and scenario-based, "
    "across Easy/Medium/Hard difficulty."
)

if "current_resume_text" not in st.session_state:
    st.warning("⚠️ Please upload a resume first.")
    st.info("Go to the **Resume Upload** page in the sidebar.")
    st.stop()

has_jd = "current_jd_text" in st.session_state
if has_jd:
    st.info("✅ Questions will be tailored to your resume AND the saved job description.")
else:
    st.info("ℹ️ No job description added — questions will be based on your resume alone.")

if st.button("🎤 Generate Interview Questions"):
    with st.spinner("Generating personalized questions... this may take 15-25 seconds"):
        jd_text = st.session_state.get("current_jd_text") if has_jd else None
        system_prompt, user_prompt = build_interview_questions_prompt(
            st.session_state.current_resume_text,
            jd_text
        )
        raw_response = call_llm(system_prompt, user_prompt, temperature=0.6)

        try:
            parsed_questions = parse_json_response(raw_response)
            st.session_state.current_interview_questions = parsed_questions

            if "current_analysis_id" in st.session_state:
                update_analysis(
                    st.session_state.current_analysis_id,
                    interview_questions=parsed_questions
                )
        except Exception as e:
            st.error(
                "⚠️ Something went wrong generating questions in the expected "
                "format. Please try again."
            )
            with st.expander("Technical details (for debugging)"):
                st.code(str(e))
                st.text(raw_response)

if "current_interview_questions" in st.session_state:
    questions = st.session_state.current_interview_questions

    difficulty_filter = st.multiselect(
        "Filter by difficulty",
        options=["Easy", "Medium", "Hard"],
        default=["Easy", "Medium", "Hard"]
    )

    category_labels = {
        "hr_questions": "🧑‍💼 HR Questions",
        "technical_questions": "💻 Technical Questions",
        "behavioral_questions": "🤝 Behavioral Questions",
        "project_based_questions": "🚀 Project-Based Questions",
        "scenario_based_questions": "🧩 Scenario-Based Questions"
    }

    tabs = st.tabs(list(category_labels.values()))

    difficulty_colors = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}

    for tab, (category_key, category_label) in zip(tabs, category_labels.items()):
        with tab:
            category_questions = questions.get(category_key, [])
            filtered = [q for q in category_questions if q.get("difficulty") in difficulty_filter]

            if not filtered:
                st.info("No questions match the selected difficulty filter.")
            else:
                for i, q in enumerate(filtered, 1):
                    diff = q.get("difficulty", "Medium")
                    icon = difficulty_colors.get(diff, "⚪")
                    st.markdown(f"**{i}. {q['question']}**")
                    st.caption(f"{icon} {diff}")
                    st.divider()