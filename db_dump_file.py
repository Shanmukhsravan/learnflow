import mysql.connector
from db import get_connection

con = get_connection()
cur = con.cursor(dictionary=True)

cur.execute("SHOW TABLES")
tables = [list(t.values())[0] for t in cur.fetchall()]

with open("schema_utf8.txt", "w", encoding="utf-8") as f:
    for t in tables:
        f.write(f"--- Table: {t} ---\n")
        cur.execute(f"DESCRIBE {t}")
        for col in cur.fetchall():
            f.write(f"{col['Field']} {col['Type']}\n")
        f.write("\n")

con.close()
