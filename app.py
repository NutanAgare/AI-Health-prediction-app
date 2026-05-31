import pandas as pd
import streamlit as st
import sqlite3
import re
from datetime import date
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

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
# LOAD DATA & TRAIN MODEL
# =========================
df = pd.read_csv("health_data.csv")

X = df[['Glucose', 'Hemoglobin', 'Cholesterol']]
y = df['Risk_Level']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# =========================
# VALIDATION FUNCTIONS
# =========================
def validate_email(email):
    email = email.strip()
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return re.match(pattern, email)

def validate_dob(dob):
    return date(1900, 1, 1) <= dob <= date.today()

def check_duplicate(name, email):

    c.execute("""
    SELECT *
    FROM patients
    WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))
    AND LOWER(TRIM(email)) = LOWER(TRIM(?))
    """,
    (
        name,
        email
    ))

    return c.fetchone()

# =========================
# ML PREDICTION
# =========================
def health_prediction(glucose, haemoglobin, cholesterol):
    return model.predict([[glucose, haemoglobin, cholesterol]])[0]

# =========================
# AI MEDICAL REPORT
# =========================
def generate_medical_ai_report(glucose, haemoglobin, cholesterol, prediction):

    issues = []

    if glucose > 140:
        issues.append("High glucose → Diabetes Risk")
    elif glucose < 70:
        issues.append("Low glucose → Hypoglycemia Risk")

    if haemoglobin < 12:
        issues.append("Low haemoglobin → Anemia Risk")
    elif haemoglobin > 17:
        issues.append("High haemoglobin → Blood abnormality")

    if cholesterol > 240:
        issues.append("High cholesterol → Heart Risk")
    elif cholesterol < 120:
        issues.append("Low cholesterol → Nutritional imbalance")

    if prediction == "High":
        risk_msg = "HIGH RISK PATIENT"
    elif prediction == "Medium":
        risk_msg = "MODERATE RISK PATIENT"
    else:
        risk_msg = "LOW RISK PATIENT"

    return risk_msg + " | " + " ; ".join(issues)

# =========================
# UI
# =========================
st.title("AI Health Prediction System")
st.write("AI Health Prediction System built using Machine Learning and Python")

# =========================
# INPUT FIELDS (FIXED DOB RANGE)
# =========================
name = st.text_input("Full Name")

dob = st.date_input(
    "Date of Birth",
    min_value=date(1900, 1, 1),
    max_value=date.today()
)

email = st.text_input("Email")
glucose = st.number_input("Glucose", min_value=0.0)
haemoglobin = st.number_input("Haemoglobin", min_value=0.0)
cholesterol = st.number_input("Cholesterol", min_value=0.0)

# =========================
# CREATE RECORD
# =========================
if st.button("Add Patient Record"):

    if not validate_email(email):
        st.error("Invalid Email Address")

    elif not validate_dob(dob):
        st.error("DOB must be between 1900 and today")

    elif check_duplicate(name, email):
        st.error("Duplicate Record Found")

    else:
        prediction = health_prediction(glucose, haemoglobin, cholesterol)

        remarks = generate_medical_ai_report(
            glucose,
            haemoglobin,
            cholesterol,
            prediction
        )

        c.execute("""
        INSERT INTO patients (name, dob, email, glucose, haemoglobin, cholesterol, remarks)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, str(dob), email, glucose, haemoglobin, cholesterol, remarks))

        conn.commit()
        st.success("Record Added Successfully")

# =========================
# READ RECORDS
# =========================
st.subheader("All Patient Records")
data = pd.read_sql("SELECT * FROM patients", conn)
st.dataframe(data)

# =========================
# UPDATE RECORD
# =========================
st.subheader("Update Email")

update_id = st.number_input("Patient ID for Update", min_value=1, step=1)
new_email = st.text_input("New Email")

if st.button("Update Record"):

    if not validate_email(new_email):
        st.error("Invalid Email Address")

    else:
        c.execute("""
        UPDATE patients
        SET email=?
        WHERE id=?
        """, (new_email, update_id))

        conn.commit()
        st.success("Email Updated Successfully")

# =========================
# DELETE RECORD
# =========================
st.subheader("Delete Record")

delete_id = st.number_input("Patient ID to Delete", min_value=1, step=1, key="delete")

if st.button("Delete Record"):
    c.execute("DELETE FROM patients WHERE id=?", (delete_id,))
    conn.commit()
    st.success("Record Deleted Successfully")

# =========================
# CLOSE CONNECTION
# =========================
conn.close()
