import mysql.connector
from db import get_connection

if __name__ == "__main__":
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute("ALTER TABLE quiz_attempts ADD COLUMN course_id INT NULL;")
        print("course_id added")
    except Exception as e:
        print("course_id error:", e)

    try:
        cur.execute("ALTER TABLE quiz_attempts ADD COLUMN level INT NULL;")
        print("level added")
    except Exception as e:
        print("level error:", e)

    try:
        cur.execute("ALTER TABLE quiz_attempts ADD COLUMN passed BOOLEAN DEFAULT FALSE;")
        print("passed added")
    except Exception as e:
        print("passed error:", e)

    con.commit()
    con.close()
    print("DB fix applied.")
