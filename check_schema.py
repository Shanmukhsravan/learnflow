import db, json
con = db.get_connection()
cur = con.cursor(dictionary=True)

cur.execute('DESCRIBE courses')
courses = [c['Field'] for c in cur.fetchall()]

cur.execute('DESCRIBE enrollments')
enrollments = [c['Field'] for c in cur.fetchall()]

cur.execute('SHOW TABLES')
tables = [list(t.values())[0] for t in cur.fetchall()]

with open('schema.json', 'w') as f:
    json.dump({'courses': courses, 'enrollments': enrollments, 'tables': tables}, f)
