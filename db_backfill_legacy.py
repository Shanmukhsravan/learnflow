import mysql.connector
from db import get_connection

def backfill_legacy_courses():
    con = get_connection()
    cur = con.cursor(dictionary=True)
    
    try:
        # 1. Fetch all courses
        cur.execute("SELECT id, title, youtube_link FROM courses")
        courses = cur.fetchall()
        
        migrated_count = 0
        
        for course in courses:
            c_id = course["id"]
            c_link = course["youtube_link"]
            
            # Check if it already has modules
            cur.execute("SELECT COUNT(*) as cnt FROM learning_content WHERE course_id=%s", (c_id,))
            cnt = cur.fetchone()["cnt"]
            
            if cnt == 0:
                print(f"Migrating Course #{c_id}: {course['title']}")
                # If there's no link, use a dummy one
                primary_url = c_link if c_link and c_link.strip() != "" else "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                
                # Insert Level 1 (Beginner)
                cur.execute("""
                    INSERT INTO learning_content (course_id, title, content_type, file_url, level)
                    VALUES (%s, %s, %s, %s, %s)
                """, (c_id, "Module 1: Getting Started", "video", primary_url, 1))
                
                # Insert Level 2 (Intermediate)
                cur.execute("""
                    INSERT INTO learning_content (course_id, title, content_type, file_url, level)
                    VALUES (%s, %s, %s, %s, %s)
                """, (c_id, "Module 2: Core Fundamentals", "article", "https://en.wikipedia.org/wiki/Systems_architecture", 2))
                
                # Insert Level 3 (Advanced)
                cur.execute("""
                    INSERT INTO learning_content (course_id, title, content_type, file_url, level)
                    VALUES (%s, %s, %s, %s, %s)
                """, (c_id, "Module 3: Advanced Applications", "video", "https://www.youtube.com/watch?v=jNQXAC9IVRw", 3))
                
                migrated_count += 1
                
        con.commit()
        print(f"Success! Backfilled {migrated_count} legacy courses with dynamic curriculums.")
        
    except Exception as e:
        print(f"FAILED: {e}")
        con.rollback()
    finally:
        con.close()

if __name__ == "__main__":
    backfill_legacy_courses()
