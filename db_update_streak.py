import db

def update_schema():
    con = db.get_connection()
    if not con:
        print("Failed to connect to DB.")
        return
    cur = con.cursor()

    try:
        cur.execute("ALTER TABLE users ADD COLUMN streak_days INT DEFAULT 0")
        print("Added streak_days.")
    except Exception as e:
        print("streak_days error (likely exists):", e)

    try:
        cur.execute("ALTER TABLE users ADD COLUMN last_active_date DATE")
        print("Added last_active_date.")
    except Exception as e:
        print("last_active_date error (likely exists):", e)

    con.commit()
    con.close()
    print("Streak DB update complete.")

if __name__ == "__main__":
    update_schema()
