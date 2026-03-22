import mysql.connector
from db import get_connection

try:
    con = get_connection()
    cur = con.cursor(dictionary=True)
    
    # 1. Test Courses Table Insertion
    print("Testing Courses INSERT...")
    cur.execute("""
        INSERT INTO courses (title, subject, level, description, youtube_link, created_by)
        VALUES (%s, %s, %s, %s, '', %s)
    """, ("Test Course", "Science", 1, "Test Desc", 1))
    course_id = cur.lastrowid
    print(f"Course inserted with ID {course_id}")
    
    # 2. Test learning_content Insertion
    print("Testing Learning Content INSERT...")
    cur.execute("""
        INSERT INTO learning_content (course_id, title, content_type, file_url, level)
        VALUES (%s, %s, %s, %s, %s)
    """, (course_id, "Test Title", "video", "http://test.com", 1))
    print("Learning content inserted.")
    
    # 3. Test Student Learn Course Select
    print("Testing Learning Content SELECT...")
    cur.execute("SELECT * FROM learning_content WHERE course_id=%s ORDER BY level ASC, id ASC", (course_id,))
    modules = cur.fetchall()
    print(f"Fetched {len(modules)} modules.")
    
    # Clean up
    cur.execute("DELETE FROM courses WHERE id=%s", (course_id,))
    cur.execute("DELETE FROM learning_content WHERE course_id=%s", (course_id,))
    con.commit()
    print("All tests passed, cleanup complete.")
except Exception as e:
    print(f"FAILED WITH ERROR: {type(e).__name__} - {e}")
finally:
    if 'con' in locals() and con.is_connected():
        con.close()
