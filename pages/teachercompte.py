import streamlit as st
from datetime import date
import base64
from user_logic import logout_user
# Configuration
st.set_page_config(page_title="Mon Compte", layout="centered")

# ---------------- BACKGROUND LOGO ----------------
def set_background_image(image_file):
    try:
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
        .block-container {{ padding-top: 1rem; }}
        </style>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Fichier logo.png non trouvé pour l'arrière-plan.")

set_background_image("logo.png")

# --- INITIALISATION ---
if 'user_data' not in st.session_state:
    st.session_state.user_data = {
        "nom": "Dupont", 
        "prenom": "Jean", 
        "date_naissance": date(2000, 1, 1),
        "telephone": "21612345678", 
        "email": "jean@exemple.com"
    }

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
    
    with col2:
        date_n = st.date_input("Date de naissance", value=st.session_state.user_data["date_naissance"])

    submitted = st.form_submit_button("Enregistrer les modifications")
    if submitted:
        # Mise à jour des données sans le type et sans la classe
        st.session_state.user_data.update({
            "nom": nom, 
            "prenom": prenom, 
            "date_naissance": date_n
        })
        st.success("✅ Profil mis à jour !")

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
                st.success("✅ Mot de passe modifié avec succès !")

st.divider()

# --- 4. CONTACT & VÉRIFICATIONS ---
st.subheader("📞 Contact & Vérifications")

# Section Email
col_em, col_btn_em = st.columns([3, 1])
with col_em:
    email_input = st.text_input("Email", value=st.session_state.user_data["email"])
with col_btn_em:
    st.write("##") 
    if st.button("Vérifier Email"):
        st.info(f"📧 Lien envoyé à {email_input}")

# Section Téléphone / OTP
col_tel, col_otp = st.columns(2)
with col_tel:
    tel_input = st.text_input("Téléphone", value=st.session_state.user_data["telephone"])
    if st.button("Envoyer code OTP"):
        st.toast(f"SMS envoyé au {tel_input}")

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