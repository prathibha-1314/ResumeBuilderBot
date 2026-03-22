"""
ResumeBuilder.Bot – Smart ATS Resume Generator
Main Flask Application (Frontend PDF Edition)
"""

import os
import re
import sqlite3
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# ---------------------------------------------------------------------------
# App Configuration
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = "resumebuilder-bot-secret-key-change-me"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------------------------------------------------------
# Database Helpers
# ---------------------------------------------------------------------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            skills TEXT NOT NULL,
            experience TEXT,
            education TEXT,
            projects TEXT,
            certifications TEXT,
            achievements TEXT,
            linkedin TEXT NOT NULL,
            github TEXT,
            job_role TEXT NOT NULL,
            company_name TEXT NOT NULL,
            job_description TEXT NOT NULL,
            matched_keywords TEXT,
            profile_photo TEXT,
            cover_letter TEXT,
            filename_cover_letter TEXT,
            filename_ats TEXT,
            filename_balanced TEXT,
            filename_creative TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    for col, coltype in [("experience", "TEXT"), ("education", "TEXT"),
                         ("profile_photo", "TEXT"), ("cover_letter", "TEXT"),
                         ("filename_cover_letter", "TEXT")]:
        try:
            cursor.execute(f"ALTER TABLE resumes ADD COLUMN {col} {coltype}")
        except sqlite3.OperationalError:
            pass
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Auth Decorator
# ---------------------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Keyword & Cover Letter Extraction
# ---------------------------------------------------------------------------

PREDEFINED_SKILLS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "c",
    "ruby", "go", "golang", "rust", "swift", "kotlin", "php", "r",
    "scala", "perl", "dart", "lua", "matlab",
    "html", "css", "react", "angular", "vue", "node.js", "express",
    "django", "flask", "spring", "next.js", "nuxt.js", "tailwind",
    "bootstrap", "jquery", "sass", "less", "webpack", "vite",
    "machine learning", "deep learning", "nlp", "natural language processing",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
    "data analysis", "data science", "data engineering", "big data",
    "hadoop", "spark", "tableau", "power bi", "matplotlib",
    "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite",
    "oracle", "firebase", "dynamodb", "cassandra", "elasticsearch",
    "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd",
    "jenkins", "terraform", "ansible", "linux", "nginx", "apache",
    "git", "github", "gitlab", "bitbucket",
    "api", "rest", "graphql", "microservices", "agile", "scrum",
    "jira", "confluence", "figma", "photoshop", "illustrator",
    "project management", "communication", "leadership", "teamwork",
    "problem solving", "critical thinking",
]

def extract_keywords(job_description: str) -> list[str]:
    jd_lower = job_description.lower()
    matched = []
    for skill in PREDEFINED_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, jd_lower):
            matched.append(skill.title())
    return sorted(set(matched))

def generate_cover_letter(data: dict) -> str:
    skills = [s.strip() for s in data["skills"].split(",") if s.strip()]
    top_skills = ", ".join(skills[:3]) if skills else "relevant technologies"
    
    cl = f"Dear Hiring Manager,\n\n"
    cl += f"I am writing to express my strong interest in the {data['job_role']} position at {data['company_name']}. With my background and strong skill set in {top_skills}, I am confident in my ability to make a meaningful contribution to your team.\n\n"
    cl += f"Throughout my career and academic journey, I have developed a deep passion for building impactful solutions. My experience includes working on various projects where I successfully applied my knowledge to solve complex problems and deliver high-quality results. I am particularly drawn to {data['company_name']} because of your commitment to innovation and excellence in the industry.\n\n"
    cl += f"Enclosed is my resume, which provides more details about my background and achievements. I would welcome the opportunity to discuss how my skills and experiences align with the goals of your team.\n\n"
    cl += f"Thank you for considering my application. I look forward to the possibility of contributing to the continued success of {data['company_name']}.\n\n"
    cl += f"Sincerely,\n{data['name']}"
    return cl


# ---------------------------------------------------------------------------
# Routes — Authentication
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("splash.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm_password", "").strip()

        if not email or not password:
            flash("Email and password are required.", "danger")
            return redirect(url_for("signup"))
        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("signup"))

        conn = get_db()
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            conn.close()
            flash("Email already registered.", "danger")
            return redirect(url_for("signup"))

        hashed = generate_password_hash(password)
        conn.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed))
        conn.commit()
        conn.close()
        flash("Account created! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_email"] = user["email"]
            flash("Logged in successfully!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


# ---------------------------------------------------------------------------
# Routes — Core Flow (Create -> Templates Browser -> Preview)
# ---------------------------------------------------------------------------

@app.route("/create-resume", methods=["GET", "POST"])
@login_required
def create_resume():
    if request.method == "POST":
        edu_lines = []
        if request.form.get("uni_name") and request.form.get("uni_degree"):
            cgpa = f" - {request.form.get('uni_cgpa')}" if request.form.get("uni_cgpa") else ""
            edu_lines.append(f"{request.form.get('uni_degree')} - {request.form.get('uni_name')}{cgpa}")
        if request.form.get("hs_name") and request.form.get("hs_percentage"):
            edu_lines.append(f"12th Grade (HSLC) - {request.form.get('hs_name')} - {request.form.get('hs_percentage')}")
        if request.form.get("sslc_name") and request.form.get("sslc_percentage"):
            edu_lines.append(f"10th Grade (SSLC) - {request.form.get('sslc_name')} - {request.form.get('sslc_percentage')}")
            
        education_str = "\n".join(edu_lines)

        data = {
            "name": request.form.get("name", "").strip(),
            "email": request.form.get("email", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "skills": request.form.get("skills", "").strip(),
            "experience": request.form.get("experience", "").strip(),
            "education": education_str,
            "projects": request.form.get("projects", "").strip(),
            "certifications": request.form.get("certifications", "").strip(),
            "achievements": request.form.get("achievements", "").strip(),
            "linkedin": request.form.get("linkedin", "").strip(),
            "github": request.form.get("github", "").strip(),
            "job_role": request.form.get("job_role", "").strip(),
            "company_name": request.form.get("company_name", "").strip(),
            "job_description": request.form.get("job_description", "").strip(),
        }

        profile_photo_filename = ""
        if "profile_photo" in request.files:
            photo = request.files["profile_photo"]
            if photo and photo.filename and allowed_file(photo.filename):
                fname = secure_filename(f"{session['user_id']}_{int(datetime.now().timestamp())}_{photo.filename}")
                photo_path = os.path.join(UPLOAD_DIR, fname)
                photo.save(photo_path)
                profile_photo_filename = fname

        matched_keywords = extract_keywords(data["job_description"])
        data["cover_letter"] = generate_cover_letter(data)

        conn = get_db()
        conn.execute("""
            INSERT INTO resumes
            (user_id, name, email, phone, skills, experience, education,
             projects, certifications, achievements, linkedin, github,
             job_role, company_name, job_description, matched_keywords,
             profile_photo, cover_letter)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            data["name"], data["email"], data["phone"],
            data["skills"], data["experience"], data["education"],
            data["projects"], data["certifications"], data["achievements"],
            data["linkedin"], data["github"],
            data["job_role"], data["company_name"],
            data["job_description"], ", ".join(matched_keywords),
            profile_photo_filename, data["cover_letter"]
        ))
        conn.commit()
        resume_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.close()

        flash("Resume data saved! Choose a template to preview.", "success")
        return redirect(url_for("templates_browser", resume_id=resume_id))

    return render_template("create_resume.html")


@app.route("/templates-browser/<int:resume_id>")
@login_required
def templates_browser(resume_id):
    conn = get_db()
    resume = conn.execute(
        "SELECT * FROM resumes WHERE id = ? AND user_id = ?",
        (resume_id, session["user_id"])
    ).fetchone()
    conn.close()

    if not resume:
        flash("Resume not found.", "danger")
        return redirect(url_for("my_resumes"))

    return render_template("templates_browser.html", resume=resume)


@app.route("/preview/<int:resume_id>/<style>")
@login_required
def render_preview(resume_id, style):
    if style not in ("ats", "balanced", "creative"):
        return redirect(url_for("templates_browser", resume_id=resume_id))

    conn = get_db()
    resume = conn.execute(
        "SELECT * FROM resumes WHERE id = ? AND user_id = ?",
        (resume_id, session["user_id"])
    ).fetchone()
    conn.close()

    if not resume:
        flash("Resume not found.", "danger")
        return redirect(url_for("my_resumes"))

    return render_template("resume_preview.html", resume=resume, style=style)


@app.route("/my-resumes")
@login_required
def my_resumes():
    conn = get_db()
    resumes = conn.execute(
        "SELECT * FROM resumes WHERE user_id = ? ORDER BY created_at DESC",
        (session["user_id"],)
    ).fetchall()
    conn.close()
    return render_template("my_resumes.html", resumes=resumes)


@app.route("/delete-resume/<int:resume_id>", methods=["POST"])
@login_required
def delete_resume(resume_id):
    conn = get_db()
    resume = conn.execute(
        "SELECT * FROM resumes WHERE id = ? AND user_id = ?",
        (resume_id, session["user_id"])
    ).fetchone()

    if not resume:
        flash("Resume not found.", "danger")
        conn.close()
        return redirect(url_for("my_resumes"))

    if resume["profile_photo"]:
        ppath = os.path.join(UPLOAD_DIR, resume["profile_photo"])
        if os.path.exists(ppath):
            os.remove(ppath)

    conn.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
    conn.commit()
    conn.close()
    flash("Resume deleted.", "info")
    return redirect(url_for("my_resumes"))


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    init_db()
    print("  * ResumeBuilder.Bot is running! (Frontend PDF Engine)")
    print("  * Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True)
