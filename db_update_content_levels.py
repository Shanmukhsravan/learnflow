import mysql.connector
from db import get_connection

con = get_connection()
cur = con.cursor()

try:
    # Add level to learning_content
    cur.execute("ALTER TABLE learning_content ADD COLUMN level INT DEFAULT 1;")
    print("Added level column to learning_content.")
except Exception as e:
    print("Error (or already exists):", e)

con.commit()
con.close()
print("Module level schema update complete.")
