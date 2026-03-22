import mysql.connector
from db import get_connection

con = get_connection()
cur = con.cursor()

try:
    # Create student_progress table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS student_progress (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            module_id INT NOT NULL,
            course_id INT NOT NULL,
            watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (module_id) REFERENCES learning_content(id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
            UNIQUE KEY unique_watch (user_id, module_id)
        );
    """)
    print("Created student_progress table.")
except Exception as e:
    print("Error creating student_progress:", e)

con.commit()
con.close()
print("Database schema updated for progress tracking.")
