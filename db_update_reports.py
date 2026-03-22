import mysql.connector
from db import get_connection

con = get_connection()
cur = con.cursor()

try:
    cur.execute("ALTER TABLE quiz_attempts ADD COLUMN report_data LONGTEXT;")
    print("Added report_data to quiz_attempts table. Success.")
except Exception as e:
    print("report_data column likely exists, or error:", e)

con.commit()
con.close()
