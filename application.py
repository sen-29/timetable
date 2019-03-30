from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import *
import os
# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
@login_required
def index():
    return render_template("index.html",isadmin=check_admin())

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()
    wrong = 1
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",{'username':username}).fetchall()
        x = len(rows)
        if x == 1:
            hash = rows[0][2]
            user_id = rows[0][0]
            if username and password:
                if password == hash:
                    session["user_id"] = user_id
                    return redirect(url_for("index"))
                else:
                    return render_template("login.html",wrong=wrong)
                    
        else:
            return render_template("login.html",wrong=wrong)

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        wrong = 0
        return render_template("login.html",wrong=wrong)

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/generate" , methods=["GET","POST"])
def generate():

    return render_template("login.html")

@app.route("/add_faculty" , methods=["GET","POST"])
def add_faculty():
    return render_template("AddFaculty.html",isadmin=check_admin())

@app.route("/add_courses" , methods=["GET","POST"])
def add_courses():
    return render_template("AddCourse.html",isadmin=check_admin())

@app.route("/remove_faculty" , methods=["GET","POST"])
def remove_faculty():
    return render_template("RemoveFaculty.html",isadmin=check_admin())

@app.route("/remove_courses", methods=["GET","POST"])
def remove_courses():
    return render_template("RemoveCourse.html",isadmin=check_admin())

@app.route("/list_faculty")
def list_faculty():
    return render_template("ListFaculty.html",isadmin=check_admin())

@app.route("/list_courses")
def list_courses():
    return render_template("ListCourse.html",isadmin=check_admin())

@app.route("/req_list", methods=["GET","POST"])
def req_list():
    session.clear()
    return render_template("login.html")

@app.route("/view")
def view():
    session.clear()
    return render_template("login.html")

@app.route("/send", methods=["GET","POST"])
def send():
    return render_template("FormforLeave.html",isadmin=check_admin())

@app.route("/change_password", methods=["GET","POST"])
def change_password():
    return render_template("ChangePassword.html",isadmin=check_admin())

def check_admin():
    x = db.execute("SELECT isadmin from users WHERE id = :id",{'id':session["user_id"]}).fetchone()
    return x[0]
