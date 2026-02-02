# ============= IMPORTS =============
import streamlit as st
import datetime
from authlib.integrations.requests_client import OAuth2Session
from user_logic import (create_google_user, send_reset_otp, reset_password_with_otp,create_user,create_student_profile,create_teacher_profile,login_user,generate_otp,send_email_otp)
from functions_file import (set_background_image, validate_password, google_callback, google_login, valid_email)

# ========================= CONFIG =========================
st.set_page_config(page_title="MathTutor Auth")
if "fp_step" not in st.session_state:
    st.session_state.fp_step = False

if "google_pending" not in st.session_state:
    st.session_state.google_pending = False
    
# ========================= UI =========================
google_callback()
set_background_image("logo.png")
st.title("MathTutor")
tab1, tab2 = st.tabs(["🔐 Connexion", "➕ Créer un compte"])

# ========================= LOGIN TAB =========================
with tab1:
    st.markdown("### Connexion à votre compte")
    email_login = st.text_input("Email", key="login_email_input")
    pw_login = st.text_input("Mot de passe", type="password", key="login_pw_input")
    
    col1, col2 = st.columns([2, 9], vertical_alignment="top")
    with col1:
      if st.button("Connecter ", key="login_btn"):
        user = login_user(email_login, pw_login)

        if user:
            st.session_state.user = user["email"]
            st.success("Login OK")

            if user["role"] == "enseignant":
                st.switch_page("pages/teachercompte.py")
            elif user["role"] == "étudiant":
                st.switch_page("pages/studentcompte.py")
        else:
            st.error("Identifiants invalides")

    with col2:
    # ================= FORGOT PASSWORD =================
     with st.expander("🔑 Mot de passe oublié ?"):

      fp_email_input = st.text_input("Votre email", key="fp_email")

      col1, col2 = st.columns(2)

    # ---------- SEND OTP ----------
      with col1:
        if st.button("Envoyer OTP", key="fp_send_btn"):

            if not valid_email(fp_email_input):
                st.error("Email invalide")
            else:
                ok, msg = send_reset_otp(fp_email_input)

                if ok:
                    st.session_state.fp_email_saved = fp_email_input   # ✅ different key
                    st.session_state.fp_step = True
                    st.success(" OTP envoyé par email")
                else:
                    st.error(msg)

    # ---------- RESET STEP ----------
        if st.session_state.get("fp_step"):

          otp_input = st.text_input("Code OTP reçu", key="fp_code")
          new_pw = st.text_input("Nouveau mot de passe", type="password", key="fp_new_pw")
          conf_pw = st.text_input("Confirmer mot de passe", type="password", key="fp_conf_pw")

          with col2:
            if st.button("Réinitialiser mot de passe", key="fp_reset_btn"):

                is_valid, pw_error = validate_password(new_pw, conf_pw)
                if not is_valid:
                  st.error(pw_error)
                  st.stop()
                else:  
                    ok, msg = reset_password_with_otp(st.session_state.fp_email_saved, otp_input,new_pw)
                    if ok:
                     st.success("✅ Mot de passe réinitialisé")
                     st.session_state.fp_step = False
                    else:
                     st.error(msg)
                

    
    st.markdown("### Ou se connecter avec")
    col1, col2 = st.columns([10, 190])
    with col1:
        st.markdown(
            '<img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" width="24">',
            unsafe_allow_html=True
        )
    with col2:
        if st.button("Votre compte google", key="google_btn"):
            google_login()
        # ================= GOOGLE COMPLETE PROFILE =================

if st.session_state.get("google_pending"):

    st.info("Complétez votre profil Google")

    role = st.radio("Je suis :", ["Étudiant", "Enseignant"], key="g_role")

    phone = st.text_input("Téléphone", key="g_phone")

    grade = None
    if role == "Étudiant":
        grade = st.selectbox(
            "Niveau",
            [
                "Bac Sciences expérimentales",
                "Bac Économie",
                "Bac Lettres",
                "Bac Sport",
                "Bac Informatique",
                "Bac Technique",
                "1ère année Licence",
                "2ème année Licence"
            ],
            key="g_grade"
        )

    if st.button("Créer le compte Google"):

        if not phone:
            st.error("Téléphone requis")
            st.stop()

        user_id = create_google_user(
            st.session_state.google_email,
            st.session_state.google_name,
            st.session_state.google_firstname,
            phone,
            role.lower()
        )

        if not user_id:
            st.error("Erreur création utilisateur")
            st.stop()

        if role == "Étudiant":
            create_student_profile(user_id, grade)
        else:
            create_teacher_profile(user_id)

        st.session_state.user = st.session_state.google_email
        st.session_state.role = role.lower()
        st.session_state.google_pending = False

        st.success("Compte Google créé ✅")

        if role == "Étudiant":
            st.switch_page("pages/studentcompte.py")
        else:
            st.switch_page("pages/teachercompte.py")
    
# ========================= CREATE ACCOUNT TAB =========================
with tab2:
    st.markdown("### Créer un nouveau compte")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Nom")
        firstname = st.text_input("Prénom")
        dob = st.date_input("Date de naissance",min_value=datetime.date(1900, 1, 1),max_value=datetime.date(2026, 2, 2))

    with col2:
        email_reg = st.text_input("Email")
        phone = st.text_input("Téléphone")

    st.divider()

    pw_reg = st.text_input("Mot de passe", type="password")
    pw2_reg = st.text_input("Confirmation de mot de passe ", type="password")

    st.divider()

    role = st.radio("Je suis :", ["Étudiant", "Enseignant"], horizontal=True)

    student_class = None
    if role == "Étudiant":
        student_class = st.selectbox(
            "Niveau / Filière",
            [
                "Bac Sciences expérimentales",
                "Bac Économie",
                "Bac Lettres",
                "Bac Sport",
                "Bac Informatique",
                "Bac Technique",
                "1ère année Licence",
                "2ème année Licence"
            ]
        )

    # ---------- OTP SEND ----------
    if st.button("OTP envoyer"):
        if not valid_email(email_reg):
            st.error("Adresse e-mail invalide")
        else:
            otp = generate_otp()
            st.session_state.otp = otp
            st.session_state.pending = True
            send_email_otp(email_reg, otp)
            st.success("OTP envoyer")

    otp_code = st.text_input("Code OTP")

    # ---------- CREATE ACCOUNT ----------
    if st.button("Créer un compte"):
        if not st.session_state.get("pending"):
            st.error("Envoyer d'abord le code OTP")
            st.stop()
        if otp_code != st.session_state.get("otp"):
            st.error("Code OTP incorrect")
            st.stop()
        is_valid, pw_error = validate_password(pw_reg, pw2_reg)
        if not is_valid:
         st.error(pw_error)
         st.stop()
        else :
         user_id = create_user(
            name,
            firstname,
            dob,
            email_reg,
            phone,
            pw_reg,
            role.lower()
        )

        if not user_id:
            st.error("L'utilisateur existe ou erreur de base de données")
            st.stop()

        if role == "Étudiant":
            create_student_profile(user_id, student_class)
            st.switch_page("pages/studentcompte.py")
        elif role == "Enseignant":
            create_teacher_profile(user_id)
            st.switch_page("pages/teachercompte.py")

        st.session_state.user = email_reg
        st.success("Compte créé avec succès🎉")
