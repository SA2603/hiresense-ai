import streamlit as st
import sys
import os

# Allow importing from the database/ folder (which isn't a package by default)
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "database"))
from database.db_utils import init_db, create_user, verify_user

st.set_page_config(page_title="Login - HireSense AI", page_icon="🔐")

# Make sure tables exist every time this page loads (safe - uses IF NOT EXISTS)
init_db()

st.title("🔐 Login / Sign Up")

# Initialize session state keys if they don't exist yet
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

# If already logged in, just show a welcome message and stop here
if st.session_state.logged_in:
    st.success(f"You're already logged in as **{st.session_state.username}**")
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()
    st.stop()  # prevents the rest of this script from running

# Tabs let us switch between Login and Sign Up forms cleanly
tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

with tab_login:
    st.subheader("Login to your account")
    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Log in", key="login_button"):
        if not login_username or not login_password:
            st.warning("Please enter both username and password.")
        else:
            user = verify_user(login_username, login_password)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user["username"]
                st.session_state.user_id = user["user_id"]
                st.success("Login successful! Redirecting...")
                st.rerun()
            else:
                st.error("Invalid username or password.")

with tab_signup:
    st.subheader("Create a new account")
    new_username = st.text_input("Choose a username", key="signup_username")
    new_email = st.text_input("Email address", key="signup_email")
    new_password = st.text_input("Choose a password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm password", type="password", key="signup_confirm")

    if st.button("Create account", key="signup_button"):
        if not new_username or not new_email or not new_password:
            st.warning("Please fill in all fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        elif len(new_password) < 6:
            st.error("Password must be at least 6 characters.")
        else:
            success = create_user(new_username, new_email, new_password)
            if success:
                st.success("Account created! Please log in using the Login tab.")
            else:
                st.error("That username or email is already taken.")