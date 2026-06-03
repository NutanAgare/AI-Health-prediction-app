# app.py
import pandas as pd
import streamlit as st
import sqlite3
import re
from datetime import date
import requests
import os

# =========================
# CONFIG: EXTERNAL AI/ML API
# =========================
# Local FastAPI/Flask endpoint acting as external AI/ML service
EXTERNAL_API_URL = "http://127.0.0.1:8000/predict"

# =========================
# DATABASE CONNECTION
# =========================
conn = sqlite3.connect("patients.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    dob TEXT,
    email TEXT,
    glucose REAL,
    haemoglobin REAL,
    cholesterol REAL,
    remarks TEXT
)
""")
conn.commit()

# =========================
# VALIDATION FUNCTIONS
# =========================
def validate_email(email: str) -> bool:
    email = email.strip()
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return re.match(pattern, email) is not None

def validate_dob(dob: date) -> bool:
    return date(1900, 1, 1) <= dob <= date.today()

def check_duplicate(name: str, email: str):
    c.execute(
        """
        SELECT *
        FROM patients
        WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))
          AND LOWER(TRIM(email)) = LOWER(TRIM(?))
        """,
        (name, email)
    )
    return c.fetchone()

# =========================
# EXTERNAL API CALL (FastAPI/Flask)
# =========================
def call_external_health_api(glucose: float, haemoglobin: float, cholesterol: float):
    """
    Calls the external AI/ML health API running locally at EXTERNAL_API_URL.
    The API is expected to return JSON: {"risk": "...", "message": "..."}.
    """
    payload = {
        "glucose": float(glucose),
        "haemoglobin": float(haemoglobin),
        "cholesterol": float(cholesterol)
    }

    try:
        response = requests.post(EXTERNAL_API_URL, json=payload, timeout=10)

        if response.status_code != 200:
            return "Unknown", f"External API error: {response.status_code} - {response.text}"

        data = response.json()
        risk = data.get("risk", "Unknown")
        message = data.get("message", "")
        return risk, message

    except Exception as e:
        return "Unknown", f"External API call failed: {str(e)}"

# =========================
# AI MEDICAL REPORT
# =========================
def generate_medical_ai_report(glucose, haemoglobin, cholesterol, api_risk, api_message):
    issues = []

    if glucose > 140:
        issues.append("High glucose → Possible diabetes risk")
    elif glucose < 70:
        issues.append("Low glucose → Possible hypoglycemia risk")

    if haemoglobin < 12:
        issues.append("Low haemoglobin → Possible anemia risk")
    elif haemoglobin > 17:
        issues.append("High haemoglobin → Possible blood abnormality")

    if cholesterol > 240:
        issues.append("High cholesterol → Possible heart disease risk")
    elif cholesterol < 120:
        issues.append("Low cholesterol → Possible nutritional imbalance")

    rule_based = " ; ".join(issues) if issues else "No major rule-based issues detected"

     # Simple overall risk from rule-based logic
    if not issues:
        risk_text = "LOW RISK PATIENT"
    elif len(issues) == 1:
        risk_text = "MEDIUM RISK PATIENT"
    else:
        risk_text = "HIGH RISK PATIENT"

    detail = " ; ".join(issues) if issues else "No major issues detected"
    return f"{risk_text} – {detail}"

# =========================
# STREAMLIT UI – LAYOUT
# =========================
st.set_page_config(page_title="MIRA Demo - Health Prediction", layout="centered")

st.title("MIRA – Health Prediction Demo")
st.write("Simple health prediction app with CRUD + external AI/ML API integration (local FastAPI/Flask).")

menu = ["Add Patient", "View Records", "Update Record", "Delete Record"]
choice = st.sidebar.selectbox("Navigation", menu)

# =========================
# ADD PATIENT (CREATE)
# =========================
if choice == "Add Patient":
    st.subheader("Add New Patient")

    name = st.text_input("Full Name")

    dob = st.date_input(
        "Date of Birth",
        min_value=date(1900, 1, 1),
        max_value=date.today()
    )

    email = st.text_input("Email")

    glucose = st.number_input("Glucose (mg/dL)", min_value=0.0, max_value=500.0, step=1.0)
    haemoglobin = st.number_input("Haemoglobin (g/dL)", min_value=0.0, max_value=25.0, step=0.1)
    cholesterol = st.number_input("Cholesterol (mg/dL)", min_value=0.0, max_value=500.0, step=1.0)

    if st.button("Add Patient Record"):
        if not name.strip():
            st.error("Name is required.")
        elif not validate_email(email):
            st.error("Invalid Email Address.")
        elif not validate_dob(dob):
            st.error("DOB must be between 1900 and today.")
        elif check_duplicate(name, email):
            st.error("Duplicate Record Found for this Name and Email.")
        else:
            # Call external AI/ML API
            api_risk, api_message = call_external_health_api(glucose, haemoglobin, cholesterol)

            # Generate final remarks
            remarks = generate_medical_ai_report(
                glucose,
                haemoglobin,
                cholesterol,
                api_risk,
                api_message
            )

            c.execute(
                """
                INSERT INTO patients (name, dob, email, glucose, haemoglobin, cholesterol, remarks)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (name, str(dob), email, glucose, haemoglobin, cholesterol, remarks)
            )
            conn.commit()
            st.success("Patient record added successfully!")

# =========================
# VIEW RECORDS (READ)
# =========================
elif choice == "View Records":
    st.subheader("All Patient Records")
    data = pd.read_sql("SELECT * FROM patients", conn)
    st.dataframe(data)

# =========================
# UPDATE RECORD
# =========================
elif choice == "Update Record":
    st.subheader("Update Patient Email")

    update_id = st.number_input("Patient ID to Update", min_value=1, step=1)
    new_email = st.text_input("New Email")

    if st.button("Update Email"):
        if not validate_email(new_email):
            st.error("Invalid Email Address.")
        else:
            c.execute(
                """
                UPDATE patients
                SET email=?
                WHERE id=?
                """,
                (new_email, update_id)
            )
            conn.commit()
            st.success("Email updated successfully!")

# =========================
# DELETE RECORD
# =========================
elif choice == "Delete Record":
    st.subheader("Delete Patient Record")

    delete_id = st.number_input("Patient ID to Delete", min_value=1, step=1, key="delete")

    if st.button("Delete Record"):
        c.execute("DELETE FROM patients WHERE id=?", (delete_id,))
        conn.commit()
        st.success("Record deleted successfully!")

# =========================
# CLOSE CONNECTION
# =========================
# (You can leave the connection open for Streamlit; closing at end is optional)
# conn.close()
