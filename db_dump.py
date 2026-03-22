import mysql.connector
from db import get_connection

con = get_connection()
cur = con.cursor(dictionary=True)

cur.execute("SHOW TABLES")
tables = [list(t.values())[0] for t in cur.fetchall()]

for t in tables:
    print(f"--- Table: {t} ---")
    cur.execute(f"DESCRIBE {t}")
    for col in cur.fetchall():
        print(col['Field'], col['Type'])
    print()

con.close()
