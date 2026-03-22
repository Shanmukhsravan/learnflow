import mysql.connector
from db import get_connection

con = get_connection()
cur = con.cursor()

try:
    cur.execute("ALTER TABLE enrollments ADD COLUMN completed_modules TEXT;")
    print("Added completed_modules to enrollments.")
except Exception as e:
    print("completed_modules exists?", e)

try:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            course_id INT NOT NULL,
            level INT NOT NULL,
            score DECIMAL(5, 2) NOT NULL,
            passed BOOLEAN DEFAULT FALSE,
            attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        );
    """)
    print("Created quiz_attempts table.")
except Exception as e:
    print("Failed creating quiz_attempts:", e)

con.commit()
con.close()
print("Phase 8 database schema successfully updated")
