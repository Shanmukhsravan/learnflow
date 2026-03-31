from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_mail import Mail, Message
from db import get_connection
from datetime import datetime, timedelta, date
import secrets
import os
from werkzeug.utils import secure_filename
import random
import os
import json
from functools import wraps
import ai_engine
import quiz_data
import quiz_ai_engine
import video_recommender
from authlib.integrations.flask_client import OAuth
from authlib.integrations.base_client.errors import OAuthError

ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "learnflow_admin_2026")

# Do not hardcode API keys!
# os.environ["GEMINI_API_KEY"] = "AIzaSy..."  <- Removed for security

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
app.secret_key = "super_secret_key"
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'profiles')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# ---------------- MAIL CONFIG ----------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")

try:
    mail = Mail(app)
except ImportError:
    mail = None
    print("Flask-Mail missing, run 'pip install Flask-Mail'")

@app.context_processor
def inject_user():
    user = None
    if "user_id" in session:
        con = get_connection()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE id=%s", (session["user_id"],))
        user = cur.fetchone()
        con.close()
    return dict(global_user=user)

# --- ROLE DECORATORS ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session or session.get("role") != "admin":
            flash("Unauthorized access. Admin privileges required.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session or session.get("role") not in ["admin", "teacher"]:
            flash("Unauthorized access. Teacher privileges required.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

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
        cur = con.cursor(dictionary=True)

        email = request.form["email"]
        
        # Explicitly check if email already exists
        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        existing_user = cur.fetchone()
        
        if existing_user:
            con.close()
            flash("Email already exists!", "danger")
            return render_template("register.html")

        try:
            cur.execute(
                "INSERT INTO users (full_name, email, password) VALUES (%s,%s,%s)",
                (
                    request.form["full_name"],
                    email,
                    generate_password_hash(request.form["password"])
                )
            )
            
            # Auto-login the user after registration
            user_id = cur.lastrowid
            session["user_id"] = user_id
            session["user_name"] = request.form["full_name"]
            session["role"] = "student"
            
            # Construct user dict for the streak function
            user = {
                "id": user_id,
                "full_name": request.form["full_name"]
            }
            update_streak_and_notifications(cur, user)
            
            con.commit()
            flash("Account created successfully! Welcome to LearnFlow.", "success")
            return redirect(url_for("overview", page=1))
        except Exception as e:
            print(f"Registration Error: {e}")
            flash("An error occurred during registration. Please try again.", "danger")
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

            if session.get("role") == "admin":
                return redirect(url_for("admin_dashboard"))
            elif session.get("role") == "teacher":
                return redirect(url_for("teacher_dashboard"))
            else:
                return redirect(url_for("dashboard"))

        con.close()
        flash("Invalid Credentials!", "danger")

    return render_template("login.html")


# =====================================================
# GOOGLE LOGIN
# =====================================================
@app.route('/login/google')
def login_google():
    redirect_uri = url_for('authorize_google', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/google/authorize')
def authorize_google():
    try:
        token = google.authorize_access_token()
    except OAuthError as e:
        print(f"Google OAuth Error: {e}")
        flash("Google login failed. Please try again from the login page without refreshing.", "danger")
        return redirect(url_for('login'))
        
    user_info = token.get('userinfo')
    
    if not user_info:
        flash("Failed to get Google user info.", "danger")
        return redirect(url_for('login'))
        
    email = user_info['email']
    full_name = user_info.get('name', '')
    profile_pic = user_info.get('picture', '')

    con = get_connection()
    if not con:
        flash("Database connection failed. Please ensure your database is running.", "danger")
        return redirect(url_for('login'))
        
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()

    if not user:
        # Register user
        try:
            cur.execute(
                "INSERT INTO users (full_name, email, password, profile_pic) VALUES (%s,%s,%s,%s)",
                (full_name, email, generate_password_hash(secrets.token_hex(16)), profile_pic)
            )
            user_id = cur.lastrowid
            session["user_id"] = user_id
            session["user_name"] = full_name
            session["role"] = "student"
            user = {"id": user_id, "full_name": full_name}
            update_streak_and_notifications(cur, user)
            con.commit()
            con.close()
            flash("Account created successfully with Google!", "success")
            return redirect(url_for('overview', page=1))
        except Exception as e:
            print(f"Google Registration Error: {e}")
            flash("Error during Google registration.", "danger")
            con.close()
            return redirect(url_for('login'))
    else:
        # Login user
        session["user_id"] = user["id"]
        session["user_name"] = user["full_name"]
        session["role"] = user.get("role", "student")
        
        # update profile pic if not present
        if not user.get("profile_pic") and profile_pic:
            cur.execute("UPDATE users SET profile_pic=%s WHERE id=%s", (profile_pic, user["id"]))
            
        update_streak_and_notifications(cur, user)
        con.commit()
        
    con.close()
    
    if session.get("role") == "admin":
        return redirect(url_for("admin_dashboard"))
    elif session.get("role") == "teacher":
        return redirect(url_for("teacher_dashboard"))
    else:
        return redirect(url_for("dashboard"))


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
            
        role = request.form.get("role", "student")
        
        con = get_connection()
        cur = con.cursor()
        cur.execute("UPDATE users SET role=%s WHERE id=%s",
                    (role, session["user_id"]))
        con.commit()
        con.close()

        session["role"] = role
        if role == "teacher":
             return redirect(url_for("teacher_dashboard"))
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

        # Route immediately to AI recommendations
        return redirect(url_for("recommendations"))

    return render_template("select_subject.html", step=1)

# =====================================================
# AI RECOMMENDATIONS
# =====================================================
@app.route("/recommendations")
def recommendations():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    con = get_connection()
    cur = con.cursor(dictionary=True)
    
    cur.execute("SELECT preferred_subject FROM users WHERE id=%s", (session["user_id"],))
    user = cur.fetchone()
    con.close()
    
    subject = user["preferred_subject"] if user else "General"
    
    # Run the Random Forest AI model
    recommended_courses = ai_engine.get_recommendations(subject, top_n=3)
    
    return render_template(
        "recommendations.html",
        subject=subject,
        courses=recommended_courses
    )




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

    # --- DAILY STREAK LOGIC ---
    from datetime import date, timedelta
    today = date.today()
    cur.execute("SELECT streak_days, last_active_date FROM users WHERE id=%s", (user_id,))
    user_streak_data = cur.fetchone()
    
    if user_streak_data:
        last_active = user_streak_data["last_active_date"]
        
        if last_active == today:
            pass # Already logged in today
        elif last_active == today - timedelta(days=1):
            cur.execute("UPDATE users SET streak_days = streak_days + 1, last_active_date = %s WHERE id = %s", (today, user_id))
            con.commit()
        else:
            cur.execute("UPDATE users SET streak_days = 1, last_active_date = %s WHERE id = %s", (today, user_id))
            con.commit()

    # Legacy notifications logic
    cur.execute("""
        SELECT id, message
        FROM notifications
        WHERE user_id = %s AND is_read = FALSE
        ORDER BY created_at DESC
    """, (user_id,))
    notifications = cur.fetchall()

    if notifications:
        ids = ",".join(str(note["id"]) for note in notifications)
        cur.execute(f"UPDATE notifications SET is_read = TRUE WHERE id IN ({ids})")
        con.commit()

    # Advanced Learning Analytics
    cur.execute("SELECT COUNT(*) as total_tests FROM quiz_attempts WHERE user_id=%s", (user_id,))
    total_result = cur.fetchone()
    total_tests = total_result["total_tests"] if total_result and total_result["total_tests"] else 0

    cur.execute("SELECT AVG(score) as avg_score, SUM(passed) as total_passed FROM quiz_attempts WHERE user_id=%s", (user_id,))
    agg_result = cur.fetchone()
    avg_score = int(agg_result["avg_score"]) if agg_result and agg_result["avg_score"] is not None else 0
    total_passed = int(agg_result["total_passed"]) if agg_result and agg_result["total_passed"] is not None else 0
    pass_rate = int((total_passed / total_tests) * 100) if total_tests > 0 else 0

    cur.execute("""
        SELECT q.id, q.score, q.passed, q.level, c.title as course_name, q.attempted_at, (q.report_data IS NOT NULL) as has_report
        FROM quiz_attempts q
        JOIN courses c ON q.course_id = c.id
        WHERE q.user_id=%s
        ORDER BY q.attempted_at DESC LIMIT 10
    """, (user_id,))
    recent_quizzes = cur.fetchall()

    # Logic for status
    status = "No Data Yet"
    recommendation = "Start attempting Level Quizzes to unlock insights."
    if total_tests > 0:
        if avg_score >= 80:
            status = "Excellent 🔥"
            recommendation = "You are ready for ADVANCED mastery 🚀"
        elif avg_score >= 60:
            status = "Good 👍"
            recommendation = "Keep reviewing intermediate concepts 📘"
        else:
            status = "Needs Improvement ⚠️"
            recommendation = "Focus on the foundational video modules 📗"

    # Fetch All Published Quizzes (legacy table references)
    cur.execute("SELECT id, title FROM quizzes WHERE status='published' ORDER BY created_at DESC")
    all_quizzes = cur.fetchall()

    # Fetch Weak Topics Analytics
    cur.execute("""
        SELECT topic, recommended_video_title, recommended_video_url, failed_count 
        FROM weak_topics 
        WHERE user_id=%s 
        ORDER BY last_failed_at DESC, failed_count DESC 
        LIMIT 3
    """, (user_id,))
    weak_topics = cur.fetchall()

    # Fetch Latest Quiz Report
    cur.execute("""
        SELECT report_data FROM quiz_attempts 
        WHERE user_id=%s AND report_data IS NOT NULL 
        ORDER BY attempted_at DESC LIMIT 1
    """, (user_id,))
    latest_attempt = cur.fetchone()
    
    latest_report = None
    if latest_attempt and latest_attempt.get("report_data"):
        try:
            latest_report = json.loads(latest_attempt["report_data"])
        except Exception as e:
            print("Error loading latest_report", e)

    con.close()

    return render_template(
        "dashboard.html",
        name=session["user_name"],
        total_tests=total_tests,
        avg_score=avg_score,
        pass_rate=pass_rate,
        status=status,
        recommendation=recommendation,
        notifications=notifications,
        all_quizzes=all_quizzes,
        recent_quizzes=recent_quizzes,
        weak_topics=weak_topics,
        latest_report=latest_report
    )

# =====================================================
# PROFILE
# =====================================================
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    con = get_connection()
    cur = con.cursor(dictionary=True)

    if request.method == "POST":
        full_name = request.form.get("full_name")
        certificate_name = request.form.get("certificate_name")
        
        # Handle file upload
        profile_pic_filename = None
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename != '':
                filename = secure_filename(f"{session['user_id']}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                profile_pic_filename = filename
        
        if profile_pic_filename:
            cur.execute("""
                UPDATE users 
                SET full_name=%s, certificate_name=%s, profile_pic=%s 
                WHERE id=%s
            """, (full_name, certificate_name, profile_pic_filename, session["user_id"]))
        else:
            cur.execute("""
                UPDATE users 
                SET full_name=%s, certificate_name=%s 
                WHERE id=%s
            """, (full_name, certificate_name, session["user_id"]))
            
        con.commit()
        session["user_name"] = full_name
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))

    cur.execute("SELECT * FROM users WHERE id=%s", (session["user_id"],))
    user = cur.fetchone()

    # Fetch Enrollments for Display
    cur.execute("""
        SELECT c.title, c.level, c.image_url, e.enrolled_at, e.expires_at 
        FROM enrollments e 
        JOIN courses c ON e.course_id = c.id 
        WHERE e.user_id = %s
    """, (session["user_id"],))
    paid_courses = cur.fetchall()

    con.close()

    return render_template("profile.html", user=user, paid_courses=paid_courses)

# =====================================================
# GLOBAL QUIZZES VIEW (/tests)
# =====================================================
@app.route("/tests")
def tests():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    con = get_connection()
    cur = con.cursor(dictionary=True)
    
    cur.execute("""
        SELECT c.id, c.title, c.subject, e.current_level, e.completed_modules 
        FROM courses c
        JOIN enrollments e ON c.id = e.course_id
        WHERE e.user_id = %s
    """, (session["user_id"],))
    
    enrolled = cur.fetchall()
    con.close()
    
    unlocked_quizzes = []
    
    mock_modules_len = {1: 2, 2: 2, 3: 2} # Based on learning UI
    
    for course in enrolled:
        c_level = int(course.get("current_level") or 1)
        comp_mod_str = course.get("completed_modules")
        completed_modules = json.loads(comp_mod_str) if comp_mod_str else {"1": [], "2": [], "3": []}
        
        for lvl in range(1, c_level + 1):
            lbl = str(lvl)
            if lvl < c_level or (lbl in completed_modules and len(completed_modules[lbl]) == mock_modules_len[lvl]):
                status = "Passed" if lvl < c_level else "Ready"
                unlocked_quizzes.append({
                    "course_id": course["id"],
                    "course_title": course["title"],
                    "subject": course["subject"],
                    "level": lvl,
                    "status": status
                })
                
    return render_template("tests.html", unlocked_quizzes=unlocked_quizzes)


# ---------------- LEARNING FLOW (3 Levels) ----------------
@app.route("/learning/<int:course_id>")
def learning(course_id):
    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    con = get_connection()
    cur = con.cursor(dictionary=True)

    cur.execute("SELECT * FROM courses WHERE id=%s", (course_id,))
    course = cur.fetchone()

    if not course:
        con.close()
        flash("Course not found.", "danger")
        return redirect(url_for("my_courses"))

    # Check enrollment
    cur.execute("SELECT * FROM enrollments WHERE user_id=%s AND course_id=%s", (session["user_id"], course_id))
    enrollment = cur.fetchone()

    if not enrollment:
        con.close()
        flash("You are not enrolled in this course.", "warning")
        return redirect(url_for("course_details", course_id=course_id))

    current_level = enrollment.get("current_level", 1)
    if current_level is None: current_level = 1
    
    badges_str = enrollment.get("badges")
    badges = json.loads(badges_str) if badges_str else []
    
    completed = enrollment.get("completed", False)
    if completed is None: completed = False
    # Fetch explicit module progression map from DB
    cur.execute("SELECT * FROM learning_content WHERE course_id=%s ORDER BY level ASC, id ASC", (course_id,))
    modules = cur.fetchall()
    
    mock_modules = {
        1: [m for m in modules if m.get("level", 1) == 1],
        2: [m for m in modules if m.get("level", 1) == 2],
        3: [m for m in modules if m.get("level", 1) == 3]
    }

    # Fetch real progress from DB
    cur.execute("SELECT module_id FROM student_progress WHERE user_id=%s AND course_id=%s", (session["user_id"], course_id))
    watched_modules = [r["module_id"] for r in cur.fetchall()]
    
    l1_completed = sum(1 for m in mock_modules[1] if m["id"] in watched_modules)
    l2_completed = sum(1 for m in mock_modules[2] if m["id"] in watched_modules)
    l3_completed = sum(1 for m in mock_modules[3] if m["id"] in watched_modules)

    con.close()
    return render_template("learning.html", course=course, current_level=current_level, badges=badges, completed=completed, mock_modules=mock_modules, watched_modules=watched_modules, l1_comp=l1_completed, l2_comp=l2_completed, l3_comp=l3_completed)

# =====================================================
# AI STUDY ASSISTANT (GEMINI)
# =====================================================
@app.route("/chat", methods=["POST"])
def chat():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not authenticated"})

    data = request.json
    user_query = data.get("query", "").strip()
    if not user_query:
        return jsonify({"success": False, "error": "Empty query"})

    user_id = session["user_id"]
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"success": False, "error": "GEMINI_API_KEY missing in environment."})

    con = get_connection()
    cur = con.cursor(dictionary=True)

    try:
        # Save user message
        cur.execute("INSERT INTO chat_history (user_id, role, message) VALUES (%s, %s, %s)", 
                    (user_id, "user", user_query))
        
        # Load last 5 interactions for context
        cur.execute("SELECT role, message FROM chat_history WHERE user_id=%s ORDER BY created_at DESC LIMIT 5", (user_id,))
        history = cur.fetchall()[::-1]
        
        # Build prompt
        context = "You are an AI Study Assistant. Help students understand concepts clearly with simple explanations, examples, and step-by-step solutions.\n\n"
        for h in history[:-1]:
            context += f"{'Student' if h['role'] == 'user' else 'Tutor'}: {h['message']}\n"
        context += f"Student: {user_query}\nTutor:"

        # REST API Call
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": context}]}]
        }
        
        import requests
        resp = requests.post(url, headers=headers, json=payload)
        resp_data = resp.json()

        if resp.status_code == 200 and "candidates" in resp_data:
            bot_reply = resp_data["candidates"][0]["content"]["parts"][0]["text"]
            # Save bot message
            cur.execute("INSERT INTO chat_history (user_id, role, message) VALUES (%s, %s, %s)", 
                        (user_id, "bot", bot_reply))
            con.commit()
            return jsonify({"success": True, "reply": bot_reply})
        else:
            return jsonify({"success": False, "error": "AI provider connection failed."})

    except Exception as e:
        print("Chat Error:", e)
        con.rollback()
        return jsonify({"success": False, "error": "Internal server error."})
    finally:
        con.close()

@app.route("/chat/history", methods=["GET"])
def chat_history():
    if "user_id" not in session: return jsonify({"success": False})
    con = get_connection()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT role, message FROM chat_history WHERE user_id=%s ORDER BY created_at ASC", (session["user_id"],))
    hist = cur.fetchall()
    con.close()
    return jsonify({"success": True, "history": hist})

@app.route("/chat/clear", methods=["POST"])
def clear_chat():
    if "user_id" not in session: return jsonify({"success": False})
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM chat_history WHERE user_id=%s", (session["user_id"],))
    con.commit()
    con.close()
    return jsonify({"success": True})

# =====================================================
# MARK MODULE AS WATCHED
# =====================================================
@app.route("/course/<int:course_id>/mark_watched/<int:module_id>", methods=["POST"])
def mark_module_watched(course_id, module_id):
    if "user_id" not in session: return jsonify({"success": False})
    
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO student_progress (user_id, module_id, course_id) VALUES (%s, %s, %s)", 
                    (session["user_id"], module_id, course_id))
        con.commit()
    except Exception as e:
        print("Duplicate watch or err:", e)
        pass # Probably already watched (unique constraint)
    finally:
        con.close()
        
    return redirect(url_for("learning", course_id=course_id))

# ---------------- LEVEL QUIZ (AI Graded) ----------------
@app.route("/course/<int:course_id>/quiz/<int:level>", methods=["GET", "POST"])
def level_quiz(course_id, level):
    if "user_id" not in session:
        return redirect(url_for("login"))

    con = get_connection()
    cur = con.cursor(dictionary=True)

    cur.execute("SELECT * FROM courses WHERE id=%s", (course_id,))
    course = cur.fetchone()

    cur.execute("SELECT * FROM enrollments WHERE user_id=%s AND course_id=%s", (session["user_id"], course_id))
    enrollment = cur.fetchone()

    if not enrollment:
        con.close()
        flash("You are not enrolled.", "danger")
        return redirect(url_for("learning", course_id=course_id))
        
    current_level_raw = enrollment.get("current_level")
    current_level = int(current_level_raw) if current_level_raw is not None else 1

    if current_level < level:
        con.close()
        flash("You do not have access to this level yet.", "danger")
        return redirect(url_for("learning", course_id=course_id))

    questions = quiz_data.get_questions_for_course(course["subject"], level)

    if request.method == "POST":
        # Grade the quiz
        correct_answers = 0
        total_questions = len(questions)
        weak_topics_recorded = []
        weak_topics_this_attempt = []
        strong_topics_this_attempt = []
        quiz_report = []
        
        for i, q in enumerate(questions):
            ans = request.form.get(f"q_{i}")
            is_correct = (ans == q["answer"])
            
            try:
                rec = video_recommender.get_video_recommendation_for_question(q["question"])
                
                quiz_report.append({
                    "number": i + 1,
                    "question": q["question"],
                    "user_answer": ans or "Not Answered",
                    "correct_answer": q["answer"],
                    "is_correct": is_correct,
                    "learn_link": rec["url"]
                })
                
                if is_correct:
                    correct_answers += 1
                    if rec["title"] not in strong_topics_this_attempt:
                        strong_topics_this_attempt.append(rec["title"])
                else:
                    if rec["title"] not in weak_topics_recorded:
                        cur.execute("""
                            INSERT INTO weak_topics (user_id, course_id, topic, recommended_video_url, recommended_video_title, failed_count)
                            VALUES (%s, %s, %s, %s, %s, 1)
                            ON DUPLICATE KEY UPDATE 
                            failed_count = failed_count + 1,
                            last_failed_at = CURRENT_TIMESTAMP
                        """, (session["user_id"], course_id, course["subject"], rec["url"], rec["title"]))
                        weak_topics_recorded.append(rec["title"])
                        weak_topics_this_attempt.append({
                            "topic": course["subject"],
                            "recommended_video_url": rec["url"],
                            "recommended_video_title": rec["title"]
                        })
            except Exception as e:
                print("Weak Topic AI DB error:", e)
                
        score_percentage = (correct_answers / total_questions) * 100.0 if total_questions > 0 else 100.0
        time_taken_sec = int(request.form.get("time_taken", 60))
        
        # AI EVALUATION
        passed = quiz_ai_engine.evaluate_performance(score_percentage, time_taken_sec, level)

        report_data_json = json.dumps({
            "score_percentage": int(score_percentage),
            "correct_answers": correct_answers,
            "total_questions": total_questions,
            "passed": bool(passed),
            "weak_topics": weak_topics_this_attempt,
            "strong_topics": strong_topics_this_attempt,
            "quiz_report": quiz_report
        })

        cur.execute("INSERT INTO quiz_attempts (user_id, course_id, level, score, passed, report_data) VALUES (%s, %s, %s, %s, %s, %s)",
                    (session["user_id"], course_id, level, float(score_percentage), bool(passed), report_data_json))
        con.commit()

        if passed:
            new_level = current_level
            completed = enrollment.get("completed", False)
            if completed is None: completed = False
            
            badges_str = enrollment.get("badges")
            badges = json.loads(badges_str) if badges_str else []
            level_name = ["Beginner", "Intermediate", "Advanced"][level-1]
            badge_name = f"{level_name} Master 🏅"
            
            if badge_name not in badges:
                badges.append(badge_name)

            if level == current_level:
                if level < 3:
                    new_level += 1
                else:
                    completed = True

            badges_json = json.dumps(badges)
            cur.execute("""
                UPDATE enrollments 
                SET current_level=%s, badges=%s, completed=%s 
                WHERE id=%s
            """, (int(new_level), badges_json, bool(completed), enrollment["id"]))
            con.commit()
            
            message = f"Congratulations! You passed Level {level} with {score_percentage:.0f}% and earned a badge!"
        else:
            message = f"You failed Level {level} with {score_percentage:.0f}%. The AI determined you need more practice."
            
        con.close()
        
        return render_template(
            "level_quiz_result.html",
            course=course,
            level=level,
            score_percentage=int(score_percentage),
            correct_answers=correct_answers,
            total_questions=total_questions,
            passed=passed,
            message=message,
            weak_topics=weak_topics_this_attempt,
            strong_topics=strong_topics_this_attempt,
            quiz_report=quiz_report
        )

    con.close()
    return render_template(
        "level_quiz.html",
        course=course,
        level=level,
        questions=questions
    )

# ---------------- LATEST QUIZ ANALYSIS ROUTE ----------------
@app.route("/quiz-analysis/latest")
def quiz_analysis_latest():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    con = get_connection()
    cur = con.cursor(dictionary=True)
    
    cur.execute("""
        SELECT * FROM quiz_attempts 
        WHERE user_id=%s AND report_data IS NOT NULL 
        ORDER BY attempted_at DESC LIMIT 1
    """, (session["user_id"],))
    attempt = cur.fetchone()
    
    if not attempt:
        con.close()
        flash("No detailed quiz analysis found.", "warning")
        return redirect(url_for("dashboard"))
        
    report = json.loads(attempt["report_data"])
    
    cur.execute("SELECT * FROM courses WHERE id=%s", (attempt["course_id"],))
    course = cur.fetchone()
    con.close()
    
    return render_template(
        "level_quiz_result.html",
        course=course,
        level=attempt["level"],
        score_percentage=report.get("score_percentage", 0),
        correct_answers=report.get("correct_answers", 0),
        total_questions=report.get("total_questions", 0),
        passed=report.get("passed", False),
        message=f"Detailed Analysis for Level {attempt['level']}",
        weak_topics=report.get("weak_topics", []),
        strong_topics=report.get("strong_topics", []),
        quiz_report=report.get("quiz_report", [])
    )

# ---------------- SPECIFIC QUIZ ANALYSIS ROUTE ----------------
@app.route("/quiz-analysis/<int:attempt_id>")
def quiz_analysis(attempt_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    con = get_connection()
    cur = con.cursor(dictionary=True)
    
    cur.execute("""
        SELECT * FROM quiz_attempts 
        WHERE id=%s AND user_id=%s AND report_data IS NOT NULL 
    """, (attempt_id, session["user_id"]))
    attempt = cur.fetchone()
    
    if not attempt:
        con.close()
        flash("Detailed quiz analysis not found or unavailable.", "warning")
        return redirect(url_for("dashboard"))
        
    report = json.loads(attempt["report_data"])
    
    cur.execute("SELECT * FROM courses WHERE id=%s", (attempt["course_id"],))
    course = cur.fetchone()
    con.close()
    
    return render_template(
        "level_quiz_result.html",
        course=course,
        level=attempt["level"],
        score_percentage=report.get("score_percentage", 0),
        correct_answers=report.get("correct_answers", 0),
        total_questions=report.get("total_questions", 0),
        passed=report.get("passed", False),
        message=f"Detailed Analysis for Level {attempt['level']}",
        weak_topics=report.get("weak_topics", []),
        strong_topics=report.get("strong_topics", []),
        quiz_report=report.get("quiz_report", [])
    )

# ---------------- CERTIFICATE ----------------
@app.route("/certificate/<int:course_id>")
def certificate(course_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    con = get_connection()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM courses WHERE id=%s", (course_id,))
    course = cur.fetchone()
    
    cur.execute("SELECT * FROM enrollments WHERE user_id=%s AND course_id=%s", (session["user_id"], course_id))
    enrollment = cur.fetchone()

    if not course:
        con.close()
        flash("Course not found.", "danger")
        return redirect(url_for("dashboard"))

    if not enrollment or not enrollment.get("completed"):
        con.close()
        flash("You have not completed this course yet.", "warning")
        return redirect(url_for("learning", course_id=course_id))

    cur.execute("SELECT full_name, certificate_name FROM users WHERE id=%s", (session["user_id"],))
    user_data = cur.fetchone()
    con.close()
    
    cert_name = session.get("user_name", "Student")
    if user_data:
        if user_data.get("certificate_name") and user_data.get("certificate_name").strip() != "":
            cert_name = user_data["certificate_name"]
        elif user_data.get("full_name") and user_data.get("full_name").strip() != "":
            cert_name = user_data["full_name"]

    return render_template(
        "certificate.html",
        name=cert_name,
        course=course,
        date=datetime.now().strftime("%B %d, %Y")
    )

# ---------------- MY COURSES (Enrolled + Recommended) ----------------
@app.route("/my-courses")
def my_courses():
    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    con = get_connection()
    cur = con.cursor(dictionary=True)

    # Get User's Preferred Subject for AI Recommendations
    cur.execute("SELECT preferred_subject FROM users WHERE id=%s", (session["user_id"],))
    user = cur.fetchone()
    subject = user["preferred_subject"] if user else "General"

    # Fetch Enrolled Courses
    cur.execute("""
        SELECT c.* 
        FROM courses c
        JOIN enrollments e ON c.id = e.course_id
        WHERE e.user_id = %s
    """, (session["user_id"],))
    enrolled_courses = cur.fetchall()
    
    # Check what course IDs the user is already enrolled in
    enrolled_ids = [c["id"] for c in enrolled_courses]

    # Fetch AI Recommendations (excluding already enrolled courses)
    recommended_courses = ai_engine.get_recommendations(subject, top_n=6)
    filtered_recommendations = [c for c in recommended_courses if c["id"] not in enrolled_ids][:3]

    con.close()

    return render_template(
        "my_courses.html",
        name=session["user_name"],
        enrolled=enrolled_courses,
        recommended=filtered_recommendations
    )

# ---------------- COURSE DETAILS ----------------
@app.route("/course/<int:course_id>")
def course_details(course_id):
    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    con = get_connection()
    cur = con.cursor(dictionary=True)

    cur.execute("SELECT * FROM courses WHERE id=%s", (course_id,))
    course = cur.fetchone()

    cur.execute("SELECT id FROM enrollments WHERE user_id=%s AND course_id=%s", (session["user_id"], course_id))
    is_enrolled = cur.fetchone() is not None

    con.close()

    if not course:
        flash("Course not found.", "danger")
        return redirect(url_for("batches"))

    # Determine Fee Structure
    if course["level"] == "Beginner":
        fee = "Free"
    elif course["level"] == "Intermediate":
        fee = "$49.99"
    else:
        fee = "$99.99"

    return render_template(
        "course_details.html",
        name=session["user_name"],
        course=course,
        fee=fee,
        is_enrolled=is_enrolled
    )

# ---------------- ENROLL IN COURSE ----------------
@app.route("/enroll/<int:course_id>", methods=["POST"])
def enroll(course_id):
    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    con = get_connection()
    cur = con.cursor(dictionary=True)

    try:
        cur.execute("SELECT level FROM courses WHERE id=%s", (course_id,))
        course = cur.fetchone()

        # If not a free beginner course, route them to checkout.
        if course and course["level"] != "Beginner":
            return redirect(url_for("payment", course_id=course_id))

        cur.execute("INSERT INTO enrollments (user_id, course_id) VALUES (%s, %s)", (session["user_id"], course_id))
        con.commit()
        flash("Successfully enrolled in the free course!", "success")
    except Exception as e:
        flash("You are already enrolled or an error occurred.", "danger")
    finally:
        con.close()

    return redirect(url_for("course_details", course_id=course_id))

# ---------------- PAYMENT ----------------
@app.route("/payment/<int:course_id>")
def payment(course_id):
    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    con = get_connection()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM courses WHERE id=%s", (course_id,))
    course = cur.fetchone()
    con.close()

    if not course:
        flash("Course not found.", "danger")
        return redirect(url_for("batches"))

    if course["level"] == "Beginner":
        flash("This course is free and doesn't require payment.", "info")
        return redirect(url_for("course_details", course_id=course_id))
    elif course["level"] == "Intermediate":
        fee = "$49.99"
    else:
        fee = "$99.99"

    return render_template("payment.html", course=course, fee=fee, name=session["user_name"])

@app.route("/process_payment/<int:course_id>", methods=["POST"])
def process_payment(course_id):
    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    con = get_connection()
    cur = con.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM courses WHERE id=%s", (course_id,))
        course = cur.fetchone()

        fee = 99.99 if course["level"] == "Advanced" else 49.99

        # Insert Payment
        cur.execute("INSERT INTO payments (user_id, course_id, amount, status) VALUES (%s, %s, %s, %s)", 
                   (session["user_id"], course_id, fee, "Completed"))

        # Grant Enrollment with Expiry Time
        from datetime import datetime, timedelta
        expires_at = datetime.now() + timedelta(days=365)
        cur.execute("INSERT INTO enrollments (user_id, course_id, expires_at) VALUES (%s, %s, %s)",
                   (session["user_id"], course_id, expires_at.strftime('%Y-%m-%d %H:%M:%S')))
        con.commit()
        flash("Payment successful! You are now enrolled.", "success")
    except Exception as e:
        print("Payment Error:", e)
        flash("Payment failed or you are already enrolled.", "danger")
    finally:
        con.close()

    return redirect(url_for("course_details", course_id=course_id))

# ---------------- BATCHES (Course Catalog) ----------------
@app.route("/batches")
def batches():
    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    search_query = request.args.get("q", "").strip()

    con = get_connection()
    cur = con.cursor(dictionary=True)

    if search_query:
        # Search by title or subject
        cur.execute("""
            SELECT id, title, subject, level, youtube_link, image_url
            FROM courses
            WHERE title LIKE %s OR subject LIKE %s
        """, (f"%{search_query}%", f"%{search_query}%"))
    else:
        cur.execute("""
            SELECT id, title, subject, level, youtube_link, image_url
            FROM courses
        """)
        
    batches = cur.fetchall()
    con.close()

    return render_template(
        "batches.html",
        batches=batches,
        name=session["user_name"],
        search_query=search_query
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

#------------------------------create quiz---------
@app.route("/create-quiz", methods=["GET", "POST"])
def create_quiz():

    if session.get("role") not in ["admin", "teacher"]:
        flash("Access Denied!", "danger")
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

    if session.get("role") not in ["admin", "teacher"]:
        flash("Access Denied!", "danger")
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

    if session.get("role") not in ["admin", "teacher"]:
        flash("Access Denied!", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":

        #  Get multiple correct answers
        correct_answers = ",".join(request.form.getlist("correct_answers"))

        con = get_connection()
        cur = con.cursor()

        cur.execute("""
            INSERT INTO questions
            (quiz_id, question, option_a, option_b, option_c, option_d, correct_answers, difficulty)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            quiz_id,
            request.form.get("question"),
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

    if session.get("role") not in ["admin", "teacher"]:
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

    if session.get("role") not in ["admin", "teacher"]:
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

@app.route("/admin/quizzes")
def admin_quizzes():
    if session.get("role") != "admin": return redirect(url_for("login"))
    con = get_connection()
    cur = con.cursor(dictionary=True)
    cur.execute("""
        SELECT q.*, u.full_name as created_by_name 
        FROM quizzes q 
        LEFT JOIN users u ON q.created_by = u.id 
        ORDER BY q.id DESC
    """)
    quizzes_data = cur.fetchall()
    con.close()
    return render_template("admin_manage_quizzes.html", quizzes=quizzes_data)

@app.route("/admin/payments")
def admin_payments():
    if session.get("role") != "admin": return redirect(url_for("login"))
    con = get_connection()
    cur = con.cursor(dictionary=True)
    cur.execute("""
        SELECT p.*, u.full_name, u.email 
        FROM payments p 
        JOIN users u ON p.user_id = u.id 
        ORDER BY p.paid_at DESC
    """)
    payments = cur.fetchall()
    con.close()
    return render_template("admin_payments.html", payments=payments)

# ======================= ADMIN REGION =======================
@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    con = get_connection()
    cur = con.cursor(dictionary=True)
    
    # 1. Total Students
    cur.execute("SELECT COUNT(*) as count FROM users WHERE role='student'")
    total_students = cur.fetchone()["count"]
    
    # 2. Total Teachers
    cur.execute("SELECT COUNT(*) as count FROM users WHERE role='teacher'")
    total_teachers = cur.fetchone()["count"]
    
    # 3. Total Courses
    cur.execute("SELECT COUNT(*) as count FROM courses")
    total_courses = cur.fetchone()["count"]
    
    # 4. Total Quizzes
    cur.execute("SELECT COUNT(*) as count FROM quizzes")
    total_quizzes = cur.fetchone()["count"]
    
    # 5. Total Revenue
    cur.execute("SELECT SUM(amount) as total FROM payments WHERE status='completed'")
    result = cur.fetchone()
    total_revenue = result["total"] if result and result["total"] else 0.00
    
    con.close()
    
    return render_template(
        "admin/admin_dashboard.html",
        total_students=total_students,
        total_teachers=total_teachers,
        total_courses=total_courses,
        total_quizzes=total_quizzes,
        total_revenue=total_revenue
    )

@app.route("/admin/quizzes")
@admin_required
def admin_manage_quizzes():
    con = get_connection()
    cur = con.cursor(dictionary=True)
    
    cur.execute("""
        SELECT q.id, q.title, q.subject, q.level, q.type, u.full_name as created_by_name
        FROM quizzes q
        LEFT JOIN users u ON q.created_by = u.id
        ORDER BY q.created_at DESC
    """)
    quizzes = cur.fetchall()
    con.close()
    
    return render_template("admin_manage_quizzes.html", quizzes=quizzes)

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

@app.route("/teacher/course/<int:course_id>/edit", methods=["GET", "POST"])
def teacher_edit_course(course_id):
    if session.get("role") != "teacher": return redirect(url_for("login"))
    con = get_connection()
    cur = con.cursor(dictionary=True)
    
    # Check ownership
    cur.execute("SELECT * FROM courses WHERE id=%s AND created_by=%s", (course_id, session["user_id"]))
    course = cur.fetchone()
    if not course:
        con.close()
        flash("Unauthorized or Course not found.", "danger")
        return redirect(url_for("teacher_courses"))

    if request.method == "POST":
        title = request.form.get("title")
        subject = request.form.get("subject")
        level = request.form.get("level")
        desc = request.form.get("description")
        # Process regular metadata update (removed youtube_link parameter from table edit)
        cur.execute("""
            UPDATE courses SET title=%s, subject=%s, level=%s, description=%s
            WHERE id=%s
        """, (title, subject, level, desc, course_id))
        
        # Process dynamically appended modules during the edit phase
        for lvl in [1, 2, 3]:
            m_titles = request.form.getlist(f"m_title_{lvl}")
            m_types = request.form.getlist(f"m_type_{lvl}")
            m_urls = request.form.getlist(f"m_url_{lvl}")
            
            for i in range(len(m_titles)):
                # If they didn't leave it blank
                if m_titles[i].strip() != "" and m_urls[i].strip() != "":
                    cur.execute("""
                        INSERT INTO learning_content (course_id, title, content_type, file_url, level)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (course_id, m_titles[i], m_types[i], m_urls[i], lvl))
                
        con.commit()
        con.close()
        flash("Course metadata updated and new modules saved successfully!", "success")
        return redirect(url_for("teacher_courses"))
    con.close()
    return render_template("teacher_edit_course.html", course=course)

@app.route("/teacher/course/<int:course_id>/modules", methods=["GET", "POST"])
def teacher_manage_modules(course_id):
    if session.get("role") != "teacher": return redirect(url_for("login"))
    con = get_connection()
    cur = con.cursor(dictionary=True)
    
    # Check ownership
    cur.execute("SELECT * FROM courses WHERE id=%s AND created_by=%s", (course_id, session["user_id"]))
    course = cur.fetchone()
    if not course:
        con.close()
        flash("Unauthorized or Course not found.", "danger")
        return redirect(url_for("teacher_courses"))

    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            title = request.form.get("title")
            c_type = request.form.get("content_type")
            f_url = request.form.get("file_url")
            m_level = request.form.get("level", 1)
            cur.execute("""
                INSERT INTO learning_content (course_id, title, content_type, file_url, level)
                VALUES (%s, %s, %s, %s, %s)
            """, (course_id, title, c_type, f_url, m_level))
            con.commit()
            flash("Module added successfully!", "success")
        elif action == "delete":
            module_id = request.form.get("module_id")
            cur.execute("DELETE FROM learning_content WHERE id=%s AND course_id=%s", (module_id, course_id))
            con.commit()
            flash("Module deleted.", "info")
            
        return redirect(url_for("teacher_manage_modules", course_id=course_id))

    # Fetch existing modules
    cur.execute("SELECT * FROM learning_content WHERE course_id=%s ORDER BY id ASC", (course_id,))
    modules = cur.fetchall()
    con.close()
    
    return render_template("teacher_manage_modules.html", course=course, modules=modules)

@app.route("/teacher/upload", methods=["GET", "POST"])

def teacher_upload_content():
    if session.get("role") != "teacher": return redirect(url_for("login"))
    if request.method == "POST":
        con = get_connection()
        cur = con.cursor()
        title = request.form.get("title")
        subject = request.form.get("subject")
        level_overall = request.form.get("level")
        desc = request.form.get("description")
        
        cur.execute("""
            INSERT INTO courses (title, subject, level, description, youtube_link, created_by)
            VALUES (%s, %s, %s, %s, '', %s)
        """, (title, subject, level_overall, desc, session["user_id"]))
        
        course_id = cur.lastrowid
        
        # Loop over exactly the 3 constructed levels
        for lvl in [1, 2, 3]:
            m_titles = request.form.getlist(f"m_title_{lvl}")
            m_types = request.form.getlist(f"m_type_{lvl}")
            m_urls = request.form.getlist(f"m_url_{lvl}")
            
            for i in range(len(m_titles)):
                cur.execute("""
                    INSERT INTO learning_content (course_id, title, content_type, file_url, level)
                    VALUES (%s, %s, %s, %s, %s)
                """, (course_id, m_titles[i], m_types[i], m_urls[i], lvl))
                
        con.commit()
        con.close()
        flash("Course and explicit modular syllabus uploaded seamlessly!", "success")
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


if __name__ == "__main__":
    app.run(debug=True, port=8000)
