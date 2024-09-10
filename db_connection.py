import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """Creates and returns a connection to the database."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="medical_appointments_service",
            port=3308
        )
        
        if connection.is_connected():
            print("Connected to the database")
            return connection
        else:
            print("Failed to connect to the database.")
            return None
    except Error as e:
        print(f"Error connecting to the database: {e}")
        return None
    
def get_all_the_doctors():
    connection = get_db_connection()
    if connection is None:
        raise ValueError("Failed to connect to the database")

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, first_name, last_name FROM doctors")
        doctors = cursor.fetchall()
        return doctors
    except Error as e:
        print(f"Error: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

