import streamlit as st
from auth_guard import require_login

require_login("enseignant") 
if "logged_in" not in st.session_state:
    st.switch_page("main.py")
    st.stop()

if st.session_state.role != "enseignant":
    st.error("Page réservée aux enseignants.")
    st.stop()

st.write("Bienvenue professeur:", st.session_state.user)


