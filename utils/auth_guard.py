import streamlit as st


def require_login():
    """
    Call this at the top of any page that should only be visible to
    logged-in users. Stops execution and shows a message if not logged in.
    """
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.warning("🔒 Please log in first.")
        st.info("Go to the **Login** page in the sidebar to log in or create an account.")
        st.stop()


def render_sidebar_reset_button():
    """
    Renders a 'Start New Analysis' button in the sidebar that clears
    all analysis-related session state (but keeps the user logged in).
    Call this from any page where a fresh start makes sense.
    """
    keys_to_clear = [
        "current_resume_id", "current_resume_text", "current_parsed_data",
        "current_resume_filename", "current_jd_id", "current_jd_text",
        "current_jd_company", "current_jd_role", "current_analysis_id",
        "current_ats_result", "current_skill_gap_result",
        "current_similarity_score", "current_ai_review",
        "current_interview_questions", "current_cover_letter",
        "current_career_recommendations", "current_report_bytes"
    ]

    with st.sidebar:
        st.divider()
        if st.button("🔄 Start New Analysis"):
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.success("Session cleared! Upload a new resume to start fresh.")
            st.rerun()