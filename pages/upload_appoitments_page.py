import streamlit as st
import pandas as pd
from db_connection import get_db_connection, get_all_the_doctors
from mysql.connector import Error

st.title("Upload Patients and Appointments")

def extract_patients_from_excel(excel_file):
    try:
        df = pd.read_excel(excel_file)
    except Exception as e:
        st.write(f"Error reading the Excel file: {e}")
        return

    df = df.rename(columns={
        'Nombre': 'first_name',
        'Apellido': 'last_name',
        'Fecha de nacimiento': 'birth_date',
        'Teléfono': 'phone',
        'Dirección': 'address',
        'Correo electrónico': 'email'
    })

    required_columns = ['first_name', 'last_name', 'birth_date', 'phone', 'address', 'email']
    for column in required_columns:
        if column not in df.columns:
            st.error(f"Missing column: {column}")
            return

    df['birth_date'] = pd.to_datetime(df['birth_date'], errors='coerce').dt.strftime('%Y-%m-%d')

    insert_patients_in_bulk(df)
    st.write(df)

def extract_appointments_from_excel(excel_file):
    try:
        df = pd.read_excel(excel_file)
    except Exception as e:
        st.write(f"Error reading the Excel file: {e}")
        return

    df = df.rename(columns={
        'ID paciente': 'patient_id',
        'Nombre del médico': 'doctor_name',
        'Especialidad': 'specialty',
        'Fecha de la cita': 'appointment_date',
        'Hora de la cita': 'appointment_time',
        'Tipo de consulta': 'consultation_type'
    })

    required_columns = ['patient_id', 'doctor_name', 'specialty', 'appointment_date', 'appointment_time', 'consultation_type']
    for column in required_columns:
        if column not in df.columns:
            st.error(f"Missing column: {column}")
            return

    df['appointment_date'] = pd.to_datetime(df['appointment_date'], errors='coerce').dt.strftime('%Y-%m-%d')

    insert_appointments_in_bulk(df)
    st.write(df)

def insert_patients_in_bulk(df):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO patients (first_name, last_name, birth_date, phone, address, email)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        for index, row in df.iterrows():
            cursor.execute(sql, tuple(row))
        conn.commit()

    except Error as e:
        st.error(f"Error inserting patients into the database: {e}")
    finally:
        cursor.close()
        conn.close()

def insert_appointments_in_bulk(df):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        for index, row in df.iterrows():
            cursor.execute("SELECT COUNT(*) FROM patients WHERE patient_id = %s", (row['patient_id'],))
            result = cursor.fetchone()

            if result[0] == 0:
                st.error(f"Error: Patient with ID {row['patient_id']} does not exist.")
                return

        sql = """
            INSERT INTO medical_appointments (patient_id, doctor_name, specialty, appointment_date, appointment_time, consultation_type)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        for index, row in df.iterrows():
            cursor.execute(sql, tuple(row))
        conn.commit()

    except Error as e:
        st.error(f"Error inserting appointments into the database: {e}")
    finally:
        cursor.close()
        conn.close()

uploaded_patients_file = st.file_uploader("Upload Patients Excel file", type=["xls", "xlsx"], key='patients')
uploaded_appointments_file = st.file_uploader("Upload Appointments Excel file", type=["xls", "xlsx"], key='appointments')

if st.button("Save Patients and Appointments"):
    if uploaded_patients_file is not None:
        extract_patients_from_excel(uploaded_patients_file)
        st.write("Patients have been created successfully")
    
    if uploaded_appointments_file is not None:
        extract_appointments_from_excel(uploaded_appointments_file)
        st.write("Appointments have been created successfully")

    doctors = get_all_the_doctors()
    doctors_dict = {doctor['id']: f"{doctor['first_name']} {doctor['last_name']}" for doctor in doctors}
    doctors_names = {f"{doctor['first_name']} {doctor['last_name']}": doctor['id'] for doctor in doctors}
    doctors_ids = list(doctors_names.keys())

    st.session_state.doctors_names = doctors_names
    st.session_state.doctors_dict = doctors_dict

if 'doctors_names' in st.session_state:
    selected_doctor_name = st.selectbox("Select a doctor", st.session_state.doctors_names.keys())

    if selected_doctor_name:
        selected_doctor_id = st.session_state.doctors_names[selected_doctor_name]
        st.write(f"Selected Doctor ID: {selected_doctor_id}")

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            query = """
                SELECT p.first_name, p.last_name, a.specialty, a.appointment_date, a.appointment_time
                FROM medical_appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                WHERE a.doctor_name = %s
            """
            cursor.execute(query, (selected_doctor_name,))
            data = cursor.fetchall()

            if data:
                df = pd.DataFrame(data, columns=['Patient First Name', 'Patient Last Name', 'Specialty', 'Appointment Date', 'Appointment Time'])
                st.write(df)
            else:
                st.write("No appointments found for the selected doctor.")
        except Error as e:
            st.error(f"Error fetching data from the database: {e}")
        finally:
            cursor.close()
            conn.close()
