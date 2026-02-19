from flask import Flask, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from db import get_connection
from datetime import datetime, timedelta, date
import secrets

ADMIN_SECRET = "learnflow_admin_2026"

app = Flask(__name__)
app.secret_key = "super_secret_key"

# ---------------- MAIL CONFIG ----------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'studentsravan05@gmail.com'
app.config['MAIL_PASSWORD'] = 'uxtwbajxvslrjrfz'

mail = Mail(app)

# =====================================================
# HOME
# =====================================================
@app.route("/")
def home():
    return redirect(url_for("login"))

# =====================================================
# REGISTER
# =====================================================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        con = get_connection()
        cur = con.cursor()

        try:
            cur.execute(
                "INSERT INTO users (full_name, email, password) VALUES (%s,%s,%s)",
                (
                    request.form["full_name"],
                    request.form["email"],
                    generate_password_hash(request.form["password"])
                )
            )
            con.commit()
            flash("Account created successfully!", "success")
            return redirect(url_for("login"))
        except:
            flash("Email already exists!", "danger")
        finally:
            con.close()

    return render_template("register.html")

# =====================================================
# LOGIN (ONLY ONE VERSION)
# =====================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        con = get_connection()
        cur = con.cursor(dictionary=True)

        cur.execute("SELECT * FROM users WHERE email=%s",
                    (request.form["email"],))
        user = cur.fetchone()

        if user and check_password_hash(user["password"],
                                        request.form["password"]):

            session["user_id"] = user["id"]
            session["user_name"] = user["full_name"]
            session["role"] = user.get("role", "student")

            # 🔥 CALL THIS FUNCTION HERE
            update_streak_and_notifications(cur, user)

            con.commit()
            con.close()

            return redirect(url_for("overview", page=1))

        con.close()
        flash("Invalid Credentials!", "danger")

    return render_template("login.html")


# =====================================================
# OVERVIEW
# =====================================================
@app.route("/overview/<int:page>")
def overview(page):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if page > 4:
        return redirect(url_for("select_role"))

    return render_template("overview.html", page=page)

# =====================================================
# ROLE SELECTION
# =====================================================
@app.route("/select-role", methods=["GET", "POST"])
def select_role():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        if request.form["role"] == "admin":
            return redirect(url_for("admin_auth"))

        con = get_connection()
        cur = con.cursor()
        cur.execute("UPDATE users SET role='student' WHERE id=%s",
                    (session["user_id"],))
        con.commit()
        con.close()

        session["role"] = "student"
        return redirect(url_for("select_subject"))

    return render_template("select_role.html")

# =====================================================
# ADMIN AUTH
# =====================================================
@app.route("/admin-auth", methods=["GET", "POST"])
def admin_auth():
    if request.method == "POST":
        if request.form["admin_password"] == ADMIN_SECRET:

            con = get_connection()
            cur = con.cursor()
            cur.execute("UPDATE users SET role='admin' WHERE id=%s",
                        (session["user_id"],))
            con.commit()
            con.close()

            session["role"] = "admin"
            flash("Admin Access Granted", "success")
            return redirect(url_for("admin_dashboard"))

        flash("Invalid Admin Password", "danger")

    return render_template("admin_auth.html")

# =====================================================
# SELECT SUBJECT
# =====================================================
@app.route('/select-subject', methods=['GET','POST'])
def select_subject():

    if request.method == 'POST':
        subject = request.form['subject']

        con = get_connection()
        cur = con.cursor()

        cur.execute("""
            UPDATE users
            SET preferred_subject=%s
            WHERE id=%s
        """, (subject, session["user_id"]))

        con.commit()
        con.close()

        return render_template(
            "select_subject.html",
            step=2,
            subject=subject
        )

    return render_template("select_subject.html", step=1)




# =====================================================
# START ASSESSMENT
# =====================================================
@app.route("/assessment", methods=["POST"])
def start_assessment():

    subject = request.form.get("subject")
    print("Subject from form:", subject)

    con = get_connection()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT id FROM quizzes
        WHERE subject=%s
        AND type='assessment'
        AND status='published'
        LIMIT 1
    """, (subject,))

    quiz = cur.fetchone()
    print("Quiz fetched:", quiz)

    con.close()

    if not quiz:
        flash("Assessment not available for this subject", "danger")
        return redirect(url_for("dashboard"))

    return redirect(url_for("attempt_quiz", quiz_id=quiz["id"]))



# =====================================================
# ATTEMPT QUIZ
# =====================================================
@app.route("/attempt/<int:quiz_id>")
def attempt_quiz(quiz_id):

    con = get_connection()
    cur = con.cursor(dictionary=True)

    cur.execute("SELECT * FROM questions WHERE quiz_id=%s", (quiz_id,))
    questions = cur.fetchall()
    con.close()

    if not questions:
        flash("No questions added to this quiz yet!", "danger")
        return redirect(url_for("dashboard"))

    return render_template("attempt_quiz.html",
                           questions=questions,
                           quiz_id=quiz_id)

# =====================================================
# SUBMIT QUIZ (FINAL VERSION)
# =====================================================
@app.route("/submit-quiz/<int:quiz_id>", methods=["POST"])
def submit_quiz(quiz_id):

    con = get_connection()
    cur = con.cursor(dictionary=True)

    cur.execute("SELECT * FROM quizzes WHERE id=%s", (quiz_id,))
    quiz = cur.fetchone()

    cur.execute("SELECT * FROM questions WHERE quiz_id=%s", (quiz_id,))
    questions = cur.fetchall()

    score = 0
    total = len(questions)

    for q in questions:
        selected = request.form.getlist(f"q{q['id']}")
        correct = q["correct_answers"].split(",")

        if set(selected) == set(correct):
            score += 1

    percentage = int((score / total) * 100) if total else 0

    cur.execute("""
        INSERT INTO quiz_attempts
        (user_id, quiz_id, score, total, percentage)
        VALUES (%s,%s,%s,%s,%s)
    """, (session["user_id"], quiz_id, score, total, percentage))

    con.commit()
    con.close()

    return redirect(url_for("quiz_result",
                            percentage=percentage,
                            score=score,
                            total=total))
#-----------Quiz Result -----------------------------------
@app.route("/quiz-result")
def quiz_result():

    percentage = request.args.get("percentage")
    score = request.args.get("score")
    total = request.args.get("total")

    return render_template("quiz_result.html",
                           percentage=percentage,
                           score=score,
                           total=total)


# =====================================================
# ADMIN DASHBOARD
# =====================================================
@app.route("/admin")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    return render_template("admin_dashboard.html")

# =====================================================
# DASHBOARD (FULL ORIGINAL LOGIC)
# =====================================================
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    user_id = session["user_id"]

    con = get_connection()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT subject, score
        FROM performance
        WHERE user_id = %s
        ORDER BY date_taken
    """, (user_id,))
    data = cur.fetchall()

    cur.execute("""
        SELECT id, message
        FROM notifications
        WHERE user_id = %s AND is_read = FALSE
        ORDER BY created_at DESC
    """, (user_id,))
    notifications = cur.fetchall()

    if notifications:
        ids = ",".join(str(note["id"]) for note in notifications)
        cur.execute(f"""
            UPDATE notifications
            SET is_read = TRUE
            WHERE id IN ({ids})
        """)
        con.commit()

    total_tests = 0
    avg_score = 0
    subjects = []
    scores = []
    status = "No Data Yet"
    recommendation = "Start attempting tests to unlock insights."

    if data:
        total_tests = len(data)
        avg_score = int(sum(row["score"] for row in data) / total_tests)
        subjects = [row["subject"] for row in data]
        scores = [row["score"] for row in data]

        if avg_score >= 80:
            status = "Excellent 🔥"
            recommendation = "You are ready for ADVANCED batches 🚀"
        elif avg_score >= 60:
            status = "Good 👍"
            recommendation = "Try INTERMEDIATE level batches 📘"
        else:
            status = "Needs Improvement ⚠️"
            recommendation = "Start with BEGINNER foundation batches 📗"

# -------- Fetch All Published Quizzes --------
    cur.execute("""
            SELECT id, title 
            FROM quizzes 
            WHERE status='published'
              ORDER BY created_at DESC
                """)

    all_quizzes = cur.fetchall()

    con.close()

    return render_template(
        "dashboard.html",
        name=session["user_name"],
        total_tests=total_tests,
        avg_score=avg_score,
        subjects=subjects,
        scores=scores,
        status=status,
        recommendation=recommendation,
        notifications=notifications,
        all_quizzes=all_quizzes

    )

# ---------------- BATCHES ----------------
@app.route("/batches")
def batches():
    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    con = get_connection()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT title, subject, level, youtube_link, image_url
        FROM courses
    """)
    batches = cur.fetchall()
    con.close()

    return render_template(
        "batches.html",
        batches=batches,
        name=session["user_name"]
    )

# ---------------- STREAK FUNCTION ----------------
def update_streak_and_notifications(cur, user):
    today = date.today()

    cur.execute("SELECT last_login, streak FROM users WHERE id=%s", (user["id"],))
    user_data = cur.fetchone()

    last_login = user_data["last_login"]
    streak = user_data["streak"] if user_data["streak"] else 0

    if last_login:
        diff = (today - last_login).days
        if diff == 1:
            streak += 1
        elif diff > 1:
            streak = 1
    else:
        streak = 1

    cur.execute("""
        UPDATE users
        SET last_login=%s, streak=%s
        WHERE id=%s
    """, (today, streak, user["id"]))

    cur.execute("""
        INSERT INTO notifications (user_id, message)
        VALUES (%s, %s)
    """, (user["id"], f"👋 Welcome back {user['full_name']}!"))

    cur.execute("""
        INSERT INTO notifications (user_id, message)
        VALUES (%s, %s)
    """, (user["id"], f"🔥 Daily Streak: {streak} days! Keep going!"))
#----------------tests (sidebar)-----------------
@app.route("/tests")
def tests():
    if "user_id" not in session:
        return redirect(url_for("login"))

    con = get_connection()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT id, title
        FROM quizzes
        WHERE status='published'
        ORDER BY created_at DESC
    """)

    all_quizzes = cur.fetchall()
    con.close()

    return render_template("tests.html", all_quizzes=all_quizzes)
#------------------------------create quiz---------
@app.route("/create-quiz", methods=["GET", "POST"])
def create_quiz():

    if session.get("role") != "admin":
        flash("Admin access required!", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":

        con = get_connection()
        cur = con.cursor()

        cur.execute("""
            INSERT INTO quizzes
            (title, subject, level, created_by, created_at, type, status)
            VALUES (%s, %s, %s, %s, NOW(), %s, %s)
        """, (
            request.form["title"],
            request.form["subject"],
            request.form["level"],
            session["user_id"],
            request.form["type"],      # assessment / regular
            request.form["status"]     # draft / published
        ))

        con.commit()
        con.close()

        flash("Quiz created successfully!", "success")
        return redirect(url_for("view_quizzes"))

    return render_template("create_quiz.html")
#-------------------------------VIEW QUIZZES (ADMIN)----------------------
@app.route("/view-quizzes")
def view_quizzes():

    if session.get("role") != "admin":
        flash("Admin access required!", "danger")
        return redirect(url_for("login"))

    con = get_connection()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT id, title, subject, level, type, status, created_at
        FROM quizzes
        ORDER BY created_at DESC
    """)

    quizzes = cur.fetchall()
    con.close()

    return render_template("admin_view_quizzes.html", quizzes=quizzes)
#------------------ADD QUESTION (UPDATED FOR YOUR QUESTIONS TABLE)--------------
@app.route("/add-question/<int:quiz_id>", methods=["GET", "POST"])
def add_question(quiz_id):

    if session.get("role") != "admin":
        flash("Admin access required!", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":

        # 🔥 Get multiple correct answers
        correct_answers = ",".join(request.form.getlist("correct_answers"))

        con = get_connection()
        cur = con.cursor()

        cur.execute("""
            INSERT INTO questions
            (quiz_id, question, option_a, option_b, option_c, option_d, correct_answers, difficulty)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            quiz_id,
            request.form.get["question"],
            request.form["option_a"],
            request.form["option_b"],
            request.form["option_c"],
            request.form["option_d"],
            correct_answers,
            request.form["difficulty"]
        ))

        con.commit()
        con.close()

        flash("Question added successfully!", "success")
        return redirect(url_for("view_quizzes"))

    return render_template("add_question.html", quiz_id=quiz_id)
 #-----------publish quize -----------
@app.route("/publish-quiz/<int:quiz_id>")
def publish_quiz(quiz_id):   # ✅ parameter added

    if session.get("role") != "admin":
        return redirect(url_for("login"))

    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        UPDATE quizzes
        SET status='published'
        WHERE id=%s
    """, (quiz_id,))

    con.commit()
    con.close()

    flash("Quiz Published Successfully!", "success")
    return redirect(url_for("view_quizzes"))

#----------delete quiz ---------------------------
@app.route("/delete-quiz/<int:quiz_id>")
def delete_quiz(quiz_id):   # ✅ parameter added

    if session.get("role") != "admin":
        return redirect(url_for("login"))

    con = get_connection()
    cur = con.cursor()

    # Delete related questions first
    cur.execute("DELETE FROM questions WHERE quiz_id=%s", (quiz_id,))

    # Delete quiz
    cur.execute("DELETE FROM quizzes WHERE id=%s", (quiz_id,))

    con.commit()
    con.close()

    flash("Quiz Deleted Successfully!", "danger")
    return redirect(url_for("view_quizzes"))


# =====================================================
# FORGOT PASSWORD
# =====================================================
@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        email = request.form["email"]
        otp = str(secrets.randbelow(900000) + 100000)
        expiry = datetime.now() + timedelta(minutes=5)

        con = get_connection()
        cur = con.cursor()
        cur.execute("UPDATE users SET otp=%s, otp_expiry=%s WHERE email=%s",
                    (otp, expiry, email))
        con.commit()

        msg = Message("LearnFlow Password Reset OTP",
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[email])
        msg.body = f"Your OTP is {otp}. Valid for 5 minutes."
        mail.send(msg)

        con.close()
        return redirect(url_for("verify_reset"))

    return render_template("forgot.html")

@app.route("/verify-reset", methods=["GET", "POST"])
def verify_reset():
    if request.method == "POST":
        email = request.form["email"]
        otp = request.form["otp"]

        con = get_connection()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email=%s AND otp=%s",
                    (email, otp))
        user = cur.fetchone()

        if user and user["otp_expiry"] > datetime.now():
            con.close()
            return redirect(url_for("reset", email=email))

        flash("Invalid or expired OTP", "danger")
        con.close()

    return render_template("verify_reset.html")

@app.route("/reset/<email>", methods=["GET", "POST"])
def reset(email):
    if request.method == "POST":
        con = get_connection()
        cur = con.cursor()
        cur.execute("UPDATE users SET password=%s WHERE email=%s",
                    (generate_password_hash(request.form["password"]), email))
        con.commit()
        con.close()
        return redirect(url_for("login"))

    return render_template("reset.html")

# =====================================================
@app.route("/logout")
def logout():
    name = session.get("user_name", "User")
    session.clear()
    return render_template("logout.html", name=name)

if __name__ == "__main__":
    app.run(debug=True)
