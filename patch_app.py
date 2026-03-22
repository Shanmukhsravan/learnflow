import re

def patch_app():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update access control checks for quizzes
    old_check = 'if session.get("role") != "admin":\n        flash("Admin access required!", "danger")\n        return redirect(url_for("login"))'
    new_check = 'if session.get("role") not in ["admin", "teacher"]:\n        flash("Access Denied!", "danger")\n        return redirect(url_for("login"))'
    content = content.replace(old_check, new_check)

    # 2. Update publish/delete quiz access control missing flashes
    old_check_2 = 'if session.get("role") != "admin":\n        return redirect(url_for("login"))'
    new_check_2 = 'if session.get("role") not in ["admin", "teacher"]:\n        return redirect(url_for("login"))'
    content = content.replace(old_check_2, new_check_2)

    # 3. Update view_quizzes SELECT query
    old_view_query = '''    cur.execute("""
        SELECT id, title, subject, level, type, status, created_at
        FROM quizzes
        ORDER BY created_at DESC
    """)
    quizzes = cur.fetchall()'''

    new_view_query = '''    if session.get("role") == "admin":
        cur.execute("""
            SELECT id, title, subject, level, type, status, created_at
            FROM quizzes
            ORDER BY created_at DESC
        """)
        quizzes = cur.fetchall()
    else:
        cur.execute("""
            SELECT id, title, subject, level, type, status, created_at
            FROM quizzes
            WHERE created_by = %s
            ORDER BY created_at DESC
        """, (session["user_id"],))
        quizzes = cur.fetchall()'''
    
    # 4. Same for courses if we had a view_courses, but let's just append the new routes
    if "def admin_students():" not in content:
        # We need to insert our new routes before the logout / FORGOT PASSWORD block or simply before `if __name__ == "__main__":`
        
        new_routes = '''

# =====================================================
# SUPER ADMIN ROUTES
# =====================================================

@app.route("/admin/students")
def admin_students():
    if session.get("role") != "admin": return redirect(url_for("login"))
    con = get_connection()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT id, full_name, email, created_at, streak FROM users WHERE role='student' ORDER BY created_at DESC")
    students = cur.fetchall()
    con.close()
    return render_template("admin_manage_students.html", students=students)

@app.route("/admin/teachers", methods=["GET", "POST"])
def admin_teachers():
    if session.get("role") != "admin": return redirect(url_for("login"))
    con = get_connection()
    cur = con.cursor(dictionary=True)
    if request.method == "POST":
        action = request.form.get("action")
        user_id = request.form.get("user_id")
        if action == "promote":
            cur.execute("UPDATE users SET role='teacher' WHERE id=%s AND role='student'", (user_id,))
        elif action == "demote":
            cur.execute("UPDATE users SET role='student' WHERE id=%s AND role='teacher'", (user_id,))
        con.commit()
        flash("Roles updated!", "success")
        return redirect(url_for("admin_teachers"))
        
    cur.execute("SELECT id, full_name, email, created_at FROM users WHERE role='teacher' ORDER BY created_at DESC")
    teachers = cur.fetchall()
    con.close()
    return render_template("admin_manage_teachers.html", teachers=teachers)

@app.route("/admin/courses")
def admin_courses():
    if session.get("role") != "admin": return redirect(url_for("login"))
    con = get_connection()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT c.*, u.full_name as created_by_name FROM courses c LEFT JOIN users u ON c.created_by = u.id ORDER BY c.id DESC")
    courses = cur.fetchall()
    con.close()
    return render_template("admin_manage_courses.html", courses=courses)

@app.route("/admin/payments")
def admin_payments():
    if session.get("role") != "admin": return redirect(url_for("login"))
    con = get_connection()
    cur = con.cursor(dictionary=True)
    cur.execute("""
        SELECT p.*, u.full_name, u.email 
        FROM payments p 
        JOIN users u ON p.user_id = u.id 
        ORDER BY p.created_at DESC
    """)
    payments = cur.fetchall()
    con.close()
    return render_template("admin_payments.html", payments=payments)

@app.route("/admin/reports")
def admin_reports():
    if session.get("role") != "admin": return redirect(url_for("login"))
    con = get_connection()
    cur = con.cursor(dictionary=True)
    
    cur.execute("SELECT COUNT(*) as total_students FROM users WHERE role='student'")
    total_students = cur.fetchone()["total_students"]
    
    cur.execute("SELECT COUNT(*) as total_teachers FROM users WHERE role='teacher'")
    total_teachers = cur.fetchone()["total_teachers"]
    
    cur.execute("SELECT COUNT(*) as total_courses FROM courses")
    total_courses = cur.fetchone()["total_courses"]
    
    cur.execute("SELECT COUNT(*) as total_quizzes FROM quizzes")
    total_quizzes = cur.fetchone()["total_quizzes"]
    
    con.close()
    return render_template("admin_reports.html", 
        total_students=total_students, 
        total_teachers=total_teachers, 
        total_courses=total_courses, 
        total_quizzes=total_quizzes)

# =====================================================
# TEACHER ROUTES
# =====================================================

@app.route("/teacher")
def teacher_dashboard():
    if session.get("role") != "teacher": return redirect(url_for("login"))
    con = get_connection()
    cur = con.cursor(dictionary=True)
    
    cur.execute("SELECT COUNT(*) as count FROM courses WHERE created_by=%s", (session["user_id"],))
    total_courses = cur.fetchone()["count"]
    
    cur.execute("SELECT COUNT(*) as count FROM quizzes WHERE created_by=%s", (session["user_id"],))
    total_quizzes = cur.fetchone()["count"]
    
    # Simple metric: sum of all students enrolled in teacher's courses
    cur.execute("""
        SELECT COUNT(e.id) as students_count 
        FROM enrollments e
        JOIN courses c ON e.course_id = c.id
        WHERE c.created_by = %s
    """, (session["user_id"],))
    total_students = cur.fetchone()["students_count"]

    con.close()
    return render_template("teacher_dashboard.html", 
                           name=session["user_name"],
                           total_courses=total_courses,
                           total_quizzes=total_quizzes,
                           total_students=total_students)

@app.route("/teacher/courses")
def teacher_courses():
    if session.get("role") != "teacher": return redirect(url_for("login"))
    con = get_connection()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM courses WHERE created_by=%s ORDER BY id DESC", (session["user_id"],))
    courses = cur.fetchall()
    con.close()
    return render_template("teacher_my_courses.html", courses=courses)

@app.route("/teacher/upload", methods=["GET", "POST"])
def teacher_upload_content():
    if session.get("role") != "teacher": return redirect(url_for("login"))
    if request.method == "POST":
        con = get_connection()
        cur = con.cursor()
        title = request.form.get("title")
        subject = request.form.get("subject")
        level = request.form.get("level")
        desc = request.form.get("description")
        yt_link = request.form.get("youtube_link")
        
        cur.execute("""
            INSERT INTO courses (title, subject, level, description, youtube_link, created_by)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (title, subject, level, desc, yt_link, session["user_id"]))
        con.commit()
        con.close()
        flash("Course uploaded successfully!", "success")
        return redirect(url_for("teacher_courses"))
    return render_template("teacher_upload_content.html")

@app.route("/teacher/performance")
def teacher_performance():
    if session.get("role") != "teacher": return redirect(url_for("login"))
    con = get_connection()
    cur = con.cursor(dictionary=True)
    cur.execute("""
        SELECT qa.score, qa.passed, qa.attempted_at, u.full_name as student_name, c.title as course_name 
        FROM quiz_attempts qa
        JOIN users u ON qa.user_id = u.id
        JOIN courses c ON qa.course_id = c.id
        WHERE c.created_by = %s
        ORDER BY qa.attempted_at DESC LIMIT 50
    """, (session["user_id"],))
    attempts = cur.fetchall()
    con.close()
    return render_template("teacher_student_performance.html", attempts=attempts)

'''
        # Insert new routes before if __name__ == "__main__":
        content = content.replace('if __name__ == "__main__":', new_routes + '\nif __name__ == "__main__":')

    if old_view_query in content:
        content = content.replace(old_view_query, new_view_query)

    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("Successfully patched app.py with all Admin/Teacher logic.")

if __name__ == "__main__":
    patch_app()
