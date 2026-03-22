import mysql.connector
from db import get_connection

def create_chat_table():
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                role VARCHAR(20) NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        con.commit()
        print("Successfully created 'chat_history' table for the Gemini bot.")
    except Exception as e:
        print(f"Error creating chat table: {e}")
        con.rollback()
    finally:
        con.close()

if __name__ == "__main__":
    create_chat_table()
