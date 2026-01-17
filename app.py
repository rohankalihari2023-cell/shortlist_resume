from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import os

from config import Config
from utils.resume_parser import extract_text
from utils.similarity import calculate_similarity

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

SHORTLIST_THRESHOLD = 0.6

# ---------------- MODELS ----------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    score = db.Column(db.Float)
    skills = db.Column(db.String(300))
    shortlisted = db.Column(db.Boolean, default=False)

# ---------------- LOGIN ----------------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------- ROUTES ----------------

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(
            username=request.form["username"],
            password=request.form["password"]
        ).first()
        if user:
            login_user(user)
            return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = User(
            username=request.form["username"],
            password=request.form["password"]
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        job_desc = request.form["job_description"]
        resumes = request.files.getlist("resumes")

        results = []

        for resume in resumes:
            path = os.path.join(app.config["UPLOAD_FOLDER"], resume.filename)
            resume.save(path)

            text = extract_text(path)
            result = calculate_similarity(job_desc, text)
            if isinstance(result, tuple):
                score, skills = result
            else:
                score = result
                skills = []
            shortlisted = score >= SHORTLIST_THRESHOLD

            r = Resume(
                filename=resume.filename,
                score=round(score * 100, 2),
                skills=", ".join(skills),
                shortlisted=shortlisted
            )

            db.session.add(r)
            db.session.commit()
            results.append(r)

        return render_template("results.html", results=results)

    return render_template("dashboard.html")


@app.route("/shortlisted")
@login_required
def shortlisted():
    resumes = Resume.query.filter_by(shortlisted=True).all()
    return render_template("shortlisted.html", resumes=resumes)


@app.route("/download/<int:resume_id>")
@login_required
def download_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        resume.filename,
        as_attachment=True
    )


@app.route("/delete/<int:resume_id>")
@login_required
def delete_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], resume.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(resume)
    db.session.commit()
    return redirect(url_for("shortlisted"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# ---------------- MAIN ----------------

if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs("instance", exist_ok=True)

    with app.app_context():
        db.create_all()

    app.run(debug=True)

