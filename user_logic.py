import bcrypt
import random
import smtplib
from email.mime.text import MIMEText
from db_utils import db_users
from db_utils import db_students
from db_utils import db_teachers
import secrets

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())
def generate_otp():
    return str(random.randint(100000, 999999))
def send_email_otp(email, otp):
    SMTP_USER = "emnamastouri4@gmail.com"
    SMTP_PASS = "hrtn lypy kcnt tzpm"

    msg = MIMEText(f"Votre code de vérification est : {otp}")
    msg["Subject"] = "MathTutor — Code de vérification"
    msg["From"] = SMTP_USER
    msg["To"] = email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
def create_user(name, firstname, dateofbirth, email, phonenumber, password, role):
    if db_users is None:
        return None
    if db_users.users.find_one({"email": email}):
        return None
    user = {
        "name": name,
        "firstname": firstname,
        "dateofbirth": str(dateofbirth),
        "email": email,
        "phonenumber": phonenumber,
        "password": hash_password(password),
        "role": role
    }
    result = db_users.users.insert_one(user)
    
    return str(result.inserted_id)
def create_student_profile(user_id, grade):
    if db_students is None:
        return False
    db_students.students.insert_one({
        "user_id": user_id,
        "grade": grade
    })
    return True
def create_teacher_profile(user_id):
    if db_teachers is None:
        return False
    db_teachers.teachers.insert_one({
        "user_id": user_id
    })
    return True
def login_user(email, password):

    if db_users is None:
        return None

    user = db_users.users.find_one({"email": email})
    if not user:
        return None

    if verify_password(password, user["password"]):
        return user


    return None
def find_user_by_email(email):
    if db_users is None:
        return None
    return db_users.users.find_one({"email": email})
def update_password(email, old_password, new_password):

    user = find_user_by_email(email)
    if not user:
        return False, "User not found"

    if not verify_password(old_password, user["password"]):
        return False, "Old password incorrect"

    db_users.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"password": hash_password(new_password)}}
    )

    return True, "Password updated successfully"
def send_reset_otp(email):

    user = find_user_by_email(email)
    if not user:
        return False, "Email not found"

    otp = generate_otp()

    db_users.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"reset_otp": otp}}
    )

    send_email_otp(email, otp)

    return True, "OTP sent"
def reset_password_with_otp(email, otp, new_password):

    user = find_user_by_email(email)
    if not user:
        return False, "User not found"

    if user.get("reset_otp") != otp:
        return False, "Invalid OTP"

    db_users.users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"password": hash_password(new_password)},
            "$unset": {"reset_otp": ""}
        }
    )

    return True, "Password reset successful"
def send_email_change_otp(current_email, new_email):

    user = find_user_by_email(current_email)
    if not user:
        return False, "User not found"

    if find_user_by_email(new_email):
        return False, "New email already used"

    otp = generate_otp()

    db_users.users.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "email_change_otp": otp,
            "pending_new_email": new_email
        }}
    )

    send_email_otp(new_email, otp)

    return True, "OTP sent to new email"
def confirm_email_change(current_email, otp):

    user = find_user_by_email(current_email)
    if not user:
        return False, "User not found"

    if user.get("email_change_otp") != otp:
        return False, "Invalid OTP"

    db_users.users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"email": user["pending_new_email"]},
            "$unset": {"email_change_otp": "", "pending_new_email": ""}
        }
    )

    return True, "Email updated successfully"
def create_google_user(email, name, firstname, phone, role):

    if db_users.users.find_one({"email": email}):
        return None

    random_pw = secrets.token_hex(16)

    user = {
        "name": name,
        "firstname": firstname,
        "dateofbirth": "",
        "email": email,
        "phonenumber": phone,
        "password": hash_password(random_pw),
        "role": role,
        "auth_provider": "google"
    }

    result = db_users.users.insert_one(user)
    return user
    # return str(result.inserted_id)
def logout_user():
    """
    Efface la session Streamlit utilisateur
    """
    try:
        import streamlit as st

        keys_to_clear = [
            "user",
            "role",
            "google_pending",
            "google_email",
            "google_name",
            "google_firstname",
            "oauth_state",
            "fp_step",
            "fp_email_saved",
            "reg_pending",
            "reg_otp"
        ]

        for k in keys_to_clear:
            if k in st.session_state:
                del st.session_state[k]
            st.switch_page("main.py")    

        return True

    except Exception:
        return False
    




def get_user_full_profile(email):
    """
    Retourne user + profil étudiant si existe
    """
    if db_users is None:
        return None

    user = db_users.users.find_one({"email": email})
    if not user:
        return None

    student_profile = db_students.students.find_one(
        {"user_id": str(user["_id"])}
    )

    return {
        "user": user,
        "student": student_profile
    }


def update_user_personal_info(email, name, firstname, dateofbirth):
    user = find_user_by_email(email)
    if not user:
        return False

    db_users.users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "name": name,
                "firstname": firstname,
                "dateofbirth": str(dateofbirth)
            }
        }
    )
    return True


def update_student_grade(email, new_grade):
    user = find_user_by_email(email)
    if not user:
        return False

    db_students.students.update_one(
        {"user_id": str(user["_id"])},
        {"$set": {"grade": new_grade}},
        upsert=True
    )

    return True


def update_user_phone(email, new_phone):
    user = find_user_by_email(email)
    if not user:
        return False

    db_users.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"phonenumber": new_phone}}
    )

    return True


def get_user_safe_dict(user_doc):
    """
    Convert Mongo doc → dict utilisable Streamlit
    """
    if not user_doc:
        return None

    return {
        "nom": user_doc.get("name", ""),
        "prenom": user_doc.get("firstname", ""),
        "date_naissance": user_doc.get("dateofbirth", ""),
        "email": user_doc.get("email", ""),
        "telephone": user_doc.get("phonenumber", ""),
        "type": user_doc.get("role", "")
    }
