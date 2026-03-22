import mysql.connector
from db import get_connection

con = get_connection()
cur = con.cursor()

try:
    cur.execute("ALTER TABLE enrollments ADD COLUMN current_level INT DEFAULT 1;")
    print("Added current_level.")
except Exception as e:
    print("current_level exists?", e)

try:
    cur.execute("ALTER TABLE enrollments ADD COLUMN badges TEXT;")
    print("Added badges.")
except Exception as e:
    print("badges exists?", e)

try:
    cur.execute("ALTER TABLE enrollments ADD COLUMN completed BOOLEAN DEFAULT FALSE;")
    print("Added completed.")
except Exception as e:
    print("completed exists?", e)

con.commit()
con.close()
print("Database schema successfully updated")
