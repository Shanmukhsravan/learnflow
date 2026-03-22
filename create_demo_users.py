from app import get_connection
from werkzeug.security import generate_password_hash

def insert_demo_users():
    con = get_connection()
    cur = con.cursor(dictionary=True)
    
    # Check Admin
    cur.execute("SELECT * FROM users WHERE email='admin@learnflow.com'")
    if not cur.fetchone():
        print("Inserting Admin...")
        cur.execute("INSERT INTO users (full_name, email, password, role, is_active) VALUES (%s, %s, %s, %s, %s)",
                   ('System Admin', 'admin@learnflow.com', generate_password_hash('admin123'), 'admin', True))
    else:
        print("Admin exists.")

    # Check Teacher
    cur.execute("SELECT * FROM users WHERE email='teacher@learnflow.com'")
    if not cur.fetchone():
        print("Inserting Teacher...")
        cur.execute("INSERT INTO users (full_name, email, password, role, is_active) VALUES (%s, %s, %s, %s, %s)",
                   ('Demo Teacher', 'teacher@learnflow.com', generate_password_hash('teacher123'), 'teacher', True))
    else:
        print("Teacher exists.")
        
    con.commit()
    con.close()
    print("Demo users ready!")

if __name__ == "__main__":
    insert_demo_users()
