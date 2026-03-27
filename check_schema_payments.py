import db, json
con = db.get_connection()
cur = con.cursor(dictionary=True)
cur.execute('DESCRIBE payments')
with open('payments_schema.json', 'w') as f:
    json.dump([c['Field'] for c in cur.fetchall()], f)
