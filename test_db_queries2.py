import mysql.connector
from db import get_connection

try:
    con = get_connection()
    cur = con.cursor(dictionary=True)
    
    # 1. Test Courses UPDATE
    print("Testing Courses UPDATE...")
    cur.execute("""
        INSERT INTO courses (title, subject, level, description, youtube_link, created_by)
        VALUES (%s, %s, %s, %s, '', %s)
    """, ("Test Edit", "Math", 2, "Desc", 1))
    cid = cur.lastrowid
    
    cur.execute("""
        UPDATE courses SET title=%s, subject=%s, level=%s, description=%s
        WHERE id=%s
    """, ("Updated", "Science", 3, "New Desc", cid))
    print("UPDATE courses passed.")

    # 2. Test Admin Manage Quizzes query (changed previously)
    print("Testing /admin/quizzes query...")
    cur.execute("""
        SELECT id, title, subject, level, created_at, created_by, status 
        FROM quizzes ORDER BY created_at DESC
    """)
    qs = cur.fetchall()
    print("Admin quizzes query passed.")
    
    # 3. Test Admin Manage Courses
    print("Testing /admin/courses query...")
    cur.execute("""
        SELECT c.id, c.title, c.subject, c.level, c.created_at, u.full_name as teacher_name 
        FROM courses c 
        JOIN users u ON c.created_by = u.id
        ORDER BY c.created_at DESC
    """)
    ac = cur.fetchall()
    print("Admin courses query passed.")

    # Clean up
    cur.execute("DELETE FROM courses WHERE id=%s", (cid,))
    con.commit()
    print("All tests passed.")
except Exception as e:
    print(f"FAILED WITH ERROR: {type(e).__name__} - {e}")
finally:
    if 'con' in locals() and con.is_connected():
        con.close()
