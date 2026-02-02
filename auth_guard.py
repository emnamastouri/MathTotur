import streamlit as st

def require_login(role=None):
    if "logged_in" not in st.session_state:
        st.switch_page("main.py")
        st.stop()

    if role and st.session_state.role.lower() != role.lower():
      st.error("Accès interdit")