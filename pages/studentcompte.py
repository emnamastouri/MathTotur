import streamlit as st
from datetime import date
import base64
from user_logic import logout_user,get_user_full_profile, get_user_safe_dict, update_password, update_student_grade, update_user_personal_info, update_user_phone

# Configuration
st.set_page_config(page_title="Mon Compte", layout="centered")


# ---------------- BACKGROUND LOGO ----------------
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
    }}

    .stApp > div {{
        background-color: rgba(255,255,255,0.88);
    }}

    header {{visibility: hidden;}}

    .block-container {{
        padding-top: 1rem;
    }}

    /* SOCIAL BUTTON STYLE */
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

    .icon-label {{
        display:flex;
        align-items:center;
        gap:10px;
        font-weight:600;
        margin-bottom:6px;
    }}

    .icon-label img {{
        width:22px;
        height:22px;
    }}

    </style>
    """, unsafe_allow_html=True)
set_background_image("logo.png")
# --- INITIALISATION ---
profile = get_user_full_profile(st.session_state.user)

if profile:
    st.session_state.user_data = get_user_safe_dict(profile["user"])
    if profile["student"]:
        st.session_state.user_data["classe"] = profile["student"]["grade"]

st.title("👤 Mon Compte")

# --- 1. PHOTO DE PROFIL ---
st.subheader("Photo de profil")
uploaded_file = st.file_uploader("Modifier la photo", type=["jpg", "png", "jpeg"])
if uploaded_file:
    st.image(uploaded_file, width=100, caption="Nouvelle photo")

st.divider()

# --- 2. FORMULAIRE INFOS PERSONNELLES ---
with st.form("profil_form"):
    st.subheader("Informations personnelles")
    col1, col2 = st.columns(2)
    
    with col1:
        nom = st.text_input("Nom", value=st.session_state.user_data["nom"])
        prenom = st.text_input("Prénom", value=st.session_state.user_data["prenom"])
        date_n = st.date_input("Date de naissance", value=st.session_state.user_data["date_naissance"])
    
    with col2:
        options_classe = [
            "Bac Sciences expérimentales", "Bac Économie", "Bac Lettres", 
            "Bac Sport", "Bac Informatique", "Bac Technique", 
            "1ère année Licence", "2ème année Licence"
        ]
        # Affichage de la classe uniquement si étudiant
        classe = st.selectbox("Niveau / Filière", options_classe) 

    submitted = st.form_submit_button("Enregistrer les modifications")
    ok1 = update_user_personal_info(st.session_state.user,nom,prenom,date_n)
    ok2 = update_student_grade(st.session_state.user,classe)

    if ok1 and ok2:
     st.success("✅ Profil mis à jour en base")
    else:
     st.error("Erreur DB")

st.divider()



# --- 3. CHANGEMENT DE MOT DE PASSE ---
st.subheader("🔒 Sécurité du compte")
with st.expander("Modifier le mot de passe"):
    with st.form("password_form"):
        old_pw = st.text_input("Ancien mot de passe", type="password")
        new_pw = st.text_input("Nouveau mot de passe", type="password")
        conf_pw = st.text_input("Confirmer le nouveau mot de passe", type="password")
        
        pw_submitted = st.form_submit_button("Mettre à jour le mot de passe")
        if pw_submitted:
            if new_pw != conf_pw:
                st.error("❌ Les nouveaux mots de passe ne correspondent pas.")
            elif len(new_pw) < 6:
                st.warning("⚠️ Le mot de passe doit contenir au moins 6 caractères.")
            else:
                ok, msg = update_password(st.session_state.user,old_pw,new_pw)
                if ok:
                 st.success(msg)
                else:
                 st.error(msg)
            
st.divider()

# --- 4. CONTACT & VÉRIFICATIONS ---
st.subheader("📞 Contact & Vérifications")

# Section Email
col_em, col_btn_em = st.columns([3, 1])
with col_em:
    email_input = st.text_input("Email", value=st.session_state.user_data["email"])
with col_btn_em:
    st.write("##") # Calage vertical
    if st.button("Vérifier Email"):
        st.info(f"📧 Lien envoyé à {email_input}")

# Section Téléphone / OTP
col_tel, col_otp = st.columns(2)
with col_tel:
    tel_input = st.text_input("Téléphone", value=st.session_state.user_data["telephone"])
    if st.button("Envoyer code OTP"):
        update_user_phone(st.session_state.user, tel_input)
        st.success("Téléphone mis à jour")

with col_otp:
    otp = st.text_input("Code OTP", placeholder="123456")
    if st.button("Valider OTP"):
        if otp == "123456":
            st.success("Téléphone vérifié !")
        else:
            st.error("Code incorrect")

if st.button("🚪 Déconnexion"):
    logout_user()
    st.switch_page("main.py")            