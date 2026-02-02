import streamlit as st
from auth_guard import require_login

require_login("étudiant") 
# BLOCK NOT LOGGED IN USERS
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("main.py")
    st.stop()

# BLOCK WRONG ROLE
if st.session_state.role != "étudiant":
    st.error("🚫 Page réservée aux étudiants.")
    st.stop()

st.write("Bienvenue étudiant:", st.session_state.user)
