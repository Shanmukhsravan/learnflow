from app import get_connection
con = get_connection()
cur = con.cursor(dictionary=True)
cur.execute('DESCRIBE quizzes')
print('---- Quizzes Schema ----')
for x in cur.fetchall():
    print(x['Field'])
