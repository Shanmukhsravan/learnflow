import mysql.connector
import os

def get_connection():
    try:
        return mysql.connector.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            user=os.environ.get("DB_USER", "root"),
            password=os.environ.get("DB_PASSWORD", "123456789"),
            database=os.environ.get("DB_NAME", "learnflow")
        )
    except Exception as e:
        print("DB ERROR:", e)
        return None
