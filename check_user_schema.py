import db
import json
con = db.get_connection()
cur = con.cursor(dictionary=True)
cur.execute("SHOW COLUMNS FROM users")
print(json.dumps([c['Field'] for c in cur.fetchall()]))
con.close()
