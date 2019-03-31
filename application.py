from flask import Flask, flash, redirect, render_template, request, session, url_for ,Markup
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
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # query database for username
        rows = db.execute("SELECT * FROM users WHERE mobile = :username",{'username':username}).fetchall()
        x = len(rows)
        if x == 1:
            hash = rows[0][4]
            user_id = rows[0][0]
            if username and password:
                if password == hash:
                    session["user_id"] = user_id
                    return redirect(url_for("index"))
                else:
                    message = Markup("<h1>Hello</h1>")
                    flash(message)
                    return render_template("login.html")
                    
        else:
            message = Markup()
            flash(message)
            return render_template("login.html")

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/generate" , methods=["GET","POST"])
@login_required
def generate():
    return render_template("login.html")

@app.route("/add_faculty" , methods=["GET","POST"])
@login_required
def add_faculty():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        mobile = request.form.get("mobile")
        date = request.form.get("birthdate")
        password = date 
        row = db.execute("SELECT * from users WHERE mobile = :mobile",{'mobile':mobile}).fetchall()
        x = len(row)
        if x == 0:
            db.execute("INSERT INTO users (name,email,mobile,password,isadmin) VALUES (:name,:email,:mobile,:password,False)",{"name": name,"email":email,"mobile":mobile,"password":password})
            db.commit()
            message = Markup('<strong>New Faculty Added</strong>')
            flash(message)
            return render_template("AddFaculty.html",isadmin=check_admin())
        else:
            message = Markup('<strong>Faculty with this Mobile Number already exist</strong>')
            flash(message)
            return render_template("AddFaculty.html",isadmin=check_admin())

    else:
        return render_template("AddFaculty.html",isadmin=check_admin())

@app.route("/add_courses" , methods=["GET","POST"])
@login_required
def add_courses():
    if request.method == "POST":
        name = request.form.get("name")
        courseid = request.form.get("courseid")
        lecture = request.form.get("lecture")
        lab = float(request.form.get("lab"))
        tut = int(request.form.get("tutorial"))
        credit = lecture + tut + (lab / 2)
        row = db.execute("SELECT * from courses WHERE id = :id",{'id':courseid}).fetchall()
        x = len(row)
        if x == 0:
            db.execute("INSERT INTO courses (id,name,lecture,lab,tutorial,credit) VALUES (:id,:name,:lecture,:lab,:tutorial,:credit)",{"id":courseid,"name":name,"lecture":lecture,"lab":lab,"tutorial":tut,"credit":credit})
            db.commit()
            message = Markup('<strong>New Course Added</strong>')
            flash(message)
            return render_template("AddCourse.html",isadmin=check_admin())
        else:
            message = Markup('<strong>Course already exist</strong>')
            flash(message)
            return render_template("AddCourse.html",isadmin=check_admin())

    else:
        return render_template("AddCourse.html",isadmin=check_admin())

@app.route("/remove_faculty" , methods=["GET","POST"])
def remove_faculty():
    return render_template("RemoveFaculty.html",isadmin=check_admin())

@app.route("/remove_courses", methods=["GET","POST"])
def remove_courses():
    return render_template("RemoveCourse.html",isadmin=check_admin())

@app.route("/list_faculty")
@login_required
def list_faculty():
    rows = db.execute("SELECT * FROM users WHERE isadmin = false").fetchall()
    return render_template("ListFaculty.html",isadmin=check_admin(),rows=rows)

@app.route("/list_courses")
@login_required
def list_courses():
    rows = db.execute("SELECT * FROM courses").fetchall()
    return render_template("ListCourse.html",isadmin=check_admin(),rows=rows)

@app.route("/offer", methods=["GET","POST"])
def offer():
    session.clear()
    return render_template("login.html")

@app.route("/slot", methods=["GET","POST"])
def slot():
    session.clear()
    return render_template("login.html")

@app.route("/view")
def view():
    session.clear()
    return render_template("login.html")

@app.route("/preference", methods=["GET","POST"])
def preference():
    session.clear()
    return render_template("login.html")

@app.route("/change_password", methods=["GET","POST"])
def change_password():
    return render_template("ChangePassword.html",isadmin=check_admin())

def check_admin():
    x = db.execute("SELECT isadmin from users WHERE id = :id",{'id':session["user_id"]}).fetchone()
    return x[0]
