import streamlit as st

st.set_page_config(page_title="HireSense AI", page_icon="🧠", layout="wide")

st.title("🧠 HireSense AI")
st.subheader("Smart Resume Analyzer & AI Interview Coach")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    st.success(f"Welcome back, **{st.session_state.username}**! Use the sidebar to navigate.")
else:
    st.info("👋 Please log in or sign up using the **Login** page in the sidebar to get started.")

st.divider()
st.write("This app will analyze your resume against a job description and give you an ATS score, skill gap analysis, AI-generated feedback, and interview prep — all in one place.")