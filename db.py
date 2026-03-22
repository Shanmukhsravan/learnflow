import mysql.connector

def get_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456789",
            database="learnflow"
        )
    except Exception as e:
        print("DB ERROR:", e)
        return None
