import streamlit as st
import pandas as pd
from db_connection import get_db_connection
from mysql.connector import Error

def get_all_appointments():
    """Fetches all appointments from the database using an existing connection."""
    try:
        connection = get_db_connection()
        appointments = []

        if connection and connection.is_connected():
            try:
                cursor = connection.cursor(dictionary=True)
                query = """
                    SELECT id, patient_id, appointment_date, time, doctor_name, notes
                    FROM medical_appointments;
                """
                cursor.execute(query)
                appointments = cursor.fetchall()
            except Error as e:
                st.error(f"Error while getting appointments from database: {e}")
            finally:
                cursor.close()
    except Error as e:
        st.error(f"Error connecting to the database: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
            
    return appointments

st.title("Medical Appointments")

if st.button("Load Appointments"):
    appointments = get_all_appointments()
    
    if appointments:

        df_appointments = pd.DataFrame(appointments)
        st.dataframe(df_appointments)
    else:
        st.write("No appointments found.")
