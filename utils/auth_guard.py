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