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
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

def validate_dob(dob):
    return dob <= date.today()

def check_duplicate(name, email):
    c.execute("SELECT * FROM patients WHERE name=? AND email=?", (name, email))
    return c.fetchone()

# =========================
# ML PREDICTION FUNCTION
# =========================
def health_prediction(glucose, haemoglobin, cholesterol):
    pred = model.predict([[glucose, haemoglobin, cholesterol]])[0]
    return pred

# =========================
# AI MEDICAL REPORT LAYER (UPGRADED)
# =========================
def generate_medical_ai_report(glucose, haemoglobin, cholesterol, prediction):

    issues = []

    # Glucose analysis
    if glucose > 140:
        issues.append("High glucose → Possible Diabetes Risk")
    elif glucose < 70:
        issues.append("Low glucose → Hypoglycemia Risk")

    # Hemoglobin analysis
    if haemoglobin < 12:
        issues.append("Low haemoglobin → Anemia Risk")
    elif haemoglobin > 17:
        issues.append("High haemoglobin → Blood abnormality")

    # Cholesterol analysis
    if cholesterol > 240:
        issues.append("High cholesterol → Cardiovascular Risk")
    elif cholesterol < 120:
        issues.append("Low cholesterol → Nutritional imbalance")

    # ML prediction interpretation
    if prediction == "High":
        risk_msg = "HIGH RISK PATIENT - Immediate attention required"
    elif prediction == "Medium":
        risk_msg = "MODERATE RISK PATIENT - Lifestyle changes needed"
    else:
        risk_msg = "LOW RISK PATIENT - Stable condition"

    return risk_msg + " | " + " ; ".join(issues)

# =========================
# UI
# =========================
st.title("AI Health Prediction System")
st.write("Random Forest ML + AI Medical Interpretation + SQLite")

# =========================
# INPUT
# =========================
name = st.text_input("Full Name")
dob = st.date_input("Date of Birth")
email = st.text_input("Email")
glucose = st.number_input("Glucose", min_value=0.0)
haemoglobin = st.number_input("Haemoglobin", min_value=0.0)
cholesterol = st.number_input("Cholesterol", min_value=0.0)

# =========================
# CREATE (INSERT)
# =========================
if st.button("Add Patient Record"):

    if not validate_email(email):
        st.error("Invalid Email Address")

    elif not validate_dob(dob):
        st.error("Future DOB Not Allowed")

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
# READ
# =========================
st.subheader("All Patient Records")
data = pd.read_sql("SELECT * FROM patients", conn)
st.dataframe(data)

# =========================
# UPDATE
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
# DELETE
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
