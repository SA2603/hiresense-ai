import streamlit as st
import sys
import os
import plotly.graph_objects as go

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "database"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "ml_models"))

from db_utils import update_analysis
from similarity_scorer import calculate_similarity
from auth_guard import require_login

st.set_page_config(page_title="Resume Similarity - HireSense AI", page_icon="🧬")

require_login()

st.title("🧬 Resume ↔ Job Description Similarity")
st.write(
    "This measures how closely your resume's **meaning** aligns with the job "
    "description — using AI (sentence embeddings), not just keyword overlap."
)

# --- PREREQUISITE CHECKS ---
if "current_resume_text" not in st.session_state:
    st.warning("⚠️ Please upload a resume first.")
    st.info("Go to the **Resume Upload** page in the sidebar.")
    st.stop()

if "current_jd_text" not in st.session_state:
    st.warning("⚠️ Please add a job description first.")
    st.info("Go to the **Job Description** page in the sidebar.")
    st.stop()

if st.button("🧬 Calculate Similarity"):
    with st.spinner("Encoding text and calculating semantic similarity... (first run may take a moment)"):
        similarity = calculate_similarity(
            st.session_state.current_resume_text,
            st.session_state.current_jd_text
        )
        st.session_state.current_similarity_score = similarity

        if "current_analysis_id" in st.session_state:
            update_analysis(
                st.session_state.current_analysis_id,
                similarity_score=similarity
            )

if "current_similarity_score" in st.session_state:
    similarity = st.session_state.current_similarity_score

    gauge_color = "#2ecc71" if similarity >= 70 else "#f39c12" if similarity >= 45 else "#e74c3c"

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=similarity,
        number={"suffix": "%"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": gauge_color},
        },
        title={"text": "Semantic Similarity"}
    ))
    fig_gauge.update_layout(height=300, margin=dict(t=50, b=10, l=30, r=30))
    st.plotly_chart(fig_gauge, use_container_width=True)

    if similarity >= 70:
        st.success(
            "✅ Strong semantic alignment — your resume's overall content and "
            "experience closely match what this role is asking for."
        )
    elif similarity >= 45:
        st.warning(
            "⚠️ Moderate alignment — there's meaningful overlap, but consider "
            "tailoring your resume's language more closely to this role."
        )
    else:
        st.error(
            "❌ Low alignment — your resume's content may not be well-suited "
            "for this specific role, or needs significant tailoring."
        )

    with st.expander("ℹ️ How is this different from the Skill Gap score?"):
        st.write("""
        - **Skill Gap Analysis** (previous page) compares **exact skill keywords**
          — e.g., does your resume literally contain the word "Python"?
        - **Semantic Similarity** (this page) compares **overall meaning** using
          an AI language model — it can recognize that "built ML pipelines" and
          "developed machine learning models" mean roughly the same thing, even
          with completely different wording.

        Using both together gives a more complete picture than either alone:
        keyword matching catches exact ATS-relevant terms, while semantic
        similarity captures whether your overall experience *reads* as a good
        fit for the role.
        """)