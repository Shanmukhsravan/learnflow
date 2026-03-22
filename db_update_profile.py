import mysql.connector
from db import get_connection

if __name__ == "__main__":
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute("ALTER TABLE users ADD COLUMN profile_pic VARCHAR(255) DEFAULT 'default_avatar.png';")
        print("profile_pic added")
    except Exception as e:
        print("profile_pic error:", e)

    try:
        cur.execute("ALTER TABLE users ADD COLUMN certificate_name VARCHAR(100) NULL;")
        print("certificate_name added")
    except Exception as e:
        print("certificate_name error:", e)

    con.commit()
    con.close()
    print("Profile DB fix applied.")
