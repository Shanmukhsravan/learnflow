import mysql.connector
from db import get_connection

con = get_connection()
cur = con.cursor()

try:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS weak_topics (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            course_id INT,
            topic VARCHAR(100) NOT NULL,
            failed_count INT DEFAULT 1,
            recommended_video_url VARCHAR(255),
            recommended_video_title VARCHAR(255),
            last_failed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_user_video (user_id, recommended_video_title),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    print("Created weak_topics table.")
except Exception as e:
    print("Failed creating weak_topics:", e)

con.commit()
con.close()
print("Database schema successfully updated with weak_topics")
