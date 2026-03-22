import mysql.connector
from db import get_connection

con = get_connection()
cur = con.cursor()

try:
    # Add is_active to users
    cur.execute("ALTER TABLE users ADD COLUMN is_active TINYINT(1) DEFAULT 1;")
    print("Added is_active column to users.")
except Exception as e:
    print("is_active column might already exist:", e)

try:
    # Create learning_content table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS learning_content (
            id INT AUTO_INCREMENT PRIMARY KEY,
            course_id INT NOT NULL,
            title VARCHAR(255) NOT NULL,
            content_type ENUM('video', 'pdf', 'article') NOT NULL,
            file_url VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
        );
    """)
    print("Created learning_content table.")
except Exception as e:
    print("Error creating learning_content:", e)

con.commit()
con.close()
print("Database successfully expanded for Admin and Teacher panels.")
