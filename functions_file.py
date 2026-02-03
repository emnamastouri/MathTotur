# ========================= imports =========================
import base64
import streamlit as st
import re
from authlib.integrations.requests_client import OAuth2Session
from user_logic import find_user_by_email
import os

# ========================= credentials =========================
google = st.secrets["google_oauth"]

GOOGLE_CLIENT_ID = google["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = google["GOOGLE_CLIENT_SECRET"]
REDIRECT_URI = google["REDIRECT_URI"]

AUTH_URL = google["AUTH_URL"]
TOKEN_URL = google["TOKEN_URL"]
USERINFO_URL = google["USERINFO_URL"]



# ========================= functions =========================
def validate_password(pw1: str, pw2: str) -> tuple[bool, str]:
    """
    Validate password and confirmation.
    
    Returns: (is_valid: bool, error_message: str)
    """
    if not pw1 or not pw2:
        return False, "Les deux mots de passe sont requis"
    
    if pw1 != pw2:
        return False, "Mots de passe incompatibles"
    
    if len(pw1) < 8:
        return False, "Le mot de passe doit faire 8+ caractères"
    
    if not any(c.isupper() for c in pw1):
        return False, "Au moins 1 majuscule requise"
    
    if not any(c.islower() for c in pw1):
        return False, "Au moins 1 minuscule requise"
    
    if not any(c.isdigit() for c in pw1):
        return False, "Au moins 1 chiffre requis"
    
    return True, "Mot de passe valide"    
def set_background_image(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: min(60vw, 700px);
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        background-color: #ffffff;
         color: black; 
    }}

    .stApp > div {{
        background-color: rgba(255,255,255,0.88);
    }}

    header {{visibility: hidden;}}

    .block-container {{
        padding-top: 1rem;
    }}

    .social-wrap button {{
        border-radius: 10px !important;
        padding: 12px !important;
        font-weight: 600 !important;
        border: 1px solid #dadce0 !important;
        background-color: white !important;
        transition: 0.2s !important;
    }}

    .social-wrap button:hover {{
        box-shadow: 0 3px 8px rgba(0,0,0,0.15) !important;
        transform: translateY(-1px);
    }}
    </style>
    """, unsafe_allow_html=True)
def valid_email(e):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", e or "")
def google_callback():

    if "code" not in st.query_params:
        return

    try:
        oauth = OAuth2Session(
            GOOGLE_CLIENT_ID,
            GOOGLE_CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            state=st.session_state.get("oauth_state")
        )

        oauth.fetch_token(TOKEN_URL, code=st.query_params["code"])
        info = oauth.get(USERINFO_URL).json()

    except Exception:
        st.error("Google auth failed — retry")
        return

    st.query_params.clear()

    email = info["email"]
    name = info.get("name", "")
    given = info.get("given_name", "")

    user = find_user_by_email(email)

    if user:
        st.session_state.logged_in = True
        st.session_state.user = user["email"]
        st.session_state.role = user["role"].lower()



        
        if user["role"] == "enseignant":
            st.switch_page("pages/startab_teacher.py")
        else:
            st.switch_page("pages/Startab_student.py")

    else:
        st.session_state.google_pending = True
        st.session_state.google_email = email
        st.session_state.google_name = name
        st.session_state.google_firstname = given
        
def google_login():
    oauth = OAuth2Session(
        GOOGLE_CLIENT_ID,
        GOOGLE_CLIENT_SECRET,
        scope="openid email profile",
        redirect_uri=REDIRECT_URI,
    )

    uri, state = oauth.create_authorization_url(AUTH_URL)
    st.session_state["oauth_state"] = state
    st.experimental_redirect(uri)
