import streamlit as st
import pymongo

@st.cache_resource
def get_client():
    # Use a try-except here to catch connection errors
    try:
        client = pymongo.MongoClient(st.secrets["mongo"]["uri"])
        # Ping to verify
        client.admin.command('ping')
        return client
    except Exception as e:
        st.error(f"❌ Connection failed: {e}")
        return None

client = get_client()

def get_database(db_name):
    if client:
        return client[db_name]
    return None

# Helper objects to export
db_users = get_database("UserBase")
db_students= get_database("StudentsBase")
db_teachers= get_database("TeacherssBase")