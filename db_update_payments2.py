import db

def update_schema():
    con = db.get_connection()
    if not con:
        print("Failed to connect to database.")
        return
    cur = con.cursor()

    # Add course_id to payments
    try:
        cur.execute("ALTER TABLE payments ADD COLUMN course_id INT")
        print("Added course_id to payments.")
    except Exception as e:
        print("course_id may already exist or error:", e)

    # Add expires_at to enrollments
    try:
        cur.execute("ALTER TABLE enrollments ADD COLUMN expires_at DATETIME")
        print("Added expires_at to enrollments.")
    except Exception as e:
        print("expires_at may already exist or error:", e)

    con.commit()
    con.close()
    print("Database update complete.")

if __name__ == "__main__":
    update_schema()
