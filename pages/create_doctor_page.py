import streamlit as st
from db_connection import get_db_connection
from mysql.connector import Error

st.title("Create Doctor")

first_name = st.text_input('First Name')
last_name = st.text_input('Last Name')
specialization = st.text_input('Specialization')
phone = st.text_input('Phone Number')
address = st.text_area('Address')
email = st.text_input('Email')

submit = st.button("Submit")

if submit:
    st.write(f"Doctor name is: {first_name} {last_name}")

    connection = get_db_connection()

    if connection is None:
        st.error("Failed to connect to the database.")
    else:
        try:
            cursor = connection.cursor(dictionary=True)

            query = """
            INSERT INTO doctors (first_name, last_name, specialization, phone, address, email)
            VALUES (%s, %s, %s, %s, %s, %s)
            """

            values = (
                first_name,
                last_name,
                specialization,
                phone,
                address,
                email
            )

            cursor.execute(query, values)
            connection.commit()

            st.write("The doctor has been successfully saved")
        except Error as e:
            st.error(f"Error while inserting doctor: {str(e)}")
        finally:
            cursor.close()
            connection.close()
