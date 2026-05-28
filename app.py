
import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# Database Connection
conn = sqlite3.connect('patients.db', check_same_thread=False)
c = conn.cursor()

# Create Table
c.execute("""
CREATE TABLE IF NOT EXISTS patients(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT,
    dob TEXT,
    email TEXT,
    glucose REAL,
    haemoglobin REAL,
    cholesterol REAL,
    remarks TEXT
)
""")
conn.commit()

# Prediction Function
def predict_health(glucose, haemoglobin, cholesterol):

    if glucose > 140:
        return "Possible Diabetes Risk"

    elif cholesterol > 240:
        return "Possible Heart Disease Risk"

    elif haemoglobin < 12:
        return "Possible Anemia Risk"

    else:
        return "Healthy"

# Insert Patient
def add_patient(full_name, dob, email, glucose, haemoglobin, cholesterol, remarks):
    c.execute("""
    INSERT INTO patients
    (full_name, dob, email, glucose, haemoglobin, cholesterol, remarks)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (full_name, dob, email, glucose, haemoglobin, cholesterol, remarks))

    conn.commit()

# Fetch All Patients
def view_patients():
    c.execute('SELECT * FROM patients')
    data = c.fetchall()
    return data

# Delete Patient
def delete_patient(patient_id):
    c.execute('DELETE FROM patients WHERE id=?', (patient_id,))
    conn.commit()

# Update Patient
def update_patient(full_name, dob, email, glucose, haemoglobin, cholesterol, remarks, patient_id):

    c.execute("""
    UPDATE patients
    SET full_name=?, dob=?, email=?, glucose=?, haemoglobin=?, cholesterol=?, remarks=?
    WHERE id=?
    """,
    (full_name, dob, email, glucose, haemoglobin, cholesterol, remarks, patient_id))

    conn.commit()

# Streamlit UI
st.set_page_config(page_title="Health Prediction App", layout="wide")

st.title("AI-Based Health Prediction System")
st.write("Patient Health Record Management with Prediction")

menu = ["Add Patient", "View Patients", "Update Patient", "Delete Patient"]
choice = st.sidebar.selectbox("Menu", menu)

# Add Patient Section
if choice == "Add Patient":

    st.subheader("Add Patient Details")

    full_name = st.text_input("Full Name")
    dob = st.date_input("Date of Birth", min_value=date(1950,1,1), max_value=date.today())
    email = st.text_input("Email Address")

    glucose = st.number_input("Glucose Level", min_value=0.0)
    haemoglobin = st.number_input("Haemoglobin", min_value=0.0)
    cholesterol = st.number_input("Cholesterol", min_value=0.0)

    if st.button("Generate Prediction"):

        remarks = predict_health(glucose, haemoglobin, cholesterol)

        st.success(f"Prediction: {remarks}")

        add_patient(
            full_name,
            str(dob),
            email,
            glucose,
            haemoglobin,
            cholesterol,
            remarks
        )

        st.success("Patient Added Successfully")

# View Patients
elif choice == "View Patients":

    st.subheader("Patient Records")

    patient_data = view_patients()

    df = pd.DataFrame(patient_data, columns=[
        "ID",
        "Full Name",
        "DOB",
        "Email",
        "Glucose",
        "Haemoglobin",
        "Cholesterol",
        "Remarks"
    ])

    st.dataframe(df)

# Update Patient
elif choice == "Update Patient":

    st.subheader("Update Patient Details")

    patient_data = view_patients()

    patient_ids = [row[0] for row in patient_data]

    selected_id = st.selectbox("Select Patient ID", patient_ids)

    selected_patient = None

    for patient in patient_data:
        if patient[0] == selected_id:
            selected_patient = patient
            break

    if selected_patient:

        full_name = st.text_input("Full Name", selected_patient[1])
        dob = st.text_input("DOB", selected_patient[2])
        email = st.text_input("Email", selected_patient[3])

        glucose = st.number_input("Glucose", value=float(selected_patient[4]))
        haemoglobin = st.number_input("Haemoglobin", value=float(selected_patient[5]))
        cholesterol = st.number_input("Cholesterol", value=float(selected_patient[6]))

        if st.button("Update Patient"):

            remarks = predict_health(glucose, haemoglobin, cholesterol)

            update_patient(
                full_name,
                dob,
                email,
                glucose,
                haemoglobin,
                cholesterol,
                remarks,
                selected_id
            )

            st.success("Patient Updated Successfully")

# Delete Patient
elif choice == "Delete Patient":

    st.subheader("Delete Patient Record")

    patient_data = view_patients()

    patient_ids = [row[0] for row in patient_data]

    selected_id = st.selectbox("Select Patient ID to Delete", patient_ids)

    if st.button("Delete"):

        delete_patient(selected_id)

        st.warning("Patient Deleted Successfully")

# Footer
st.markdown("---")
st.write("Developed using Python, Streamlit, SQLite and AI/ML Concepts")
