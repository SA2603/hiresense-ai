import streamlit as st

# Page configuration - this MUST be the first Streamlit command in the script
st.set_page_config(
    page_title="HireSense AI",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 HireSense AI")
st.subheader("Smart Resume Analyzer & AI Interview Coach")

st.write("If you can see this, your toolchain is working end-to-end! 🎉")

st.divider()

st.write("Environment check:")
st.success("✅ Python is running")
st.success("✅ Streamlit is installed and rendering")
st.success("✅ Virtual environment is active")