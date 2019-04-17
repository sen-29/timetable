from flask import Flask, flash, redirect, render_template, request, session, url_for ,Markup
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import *
from generate import *
from datetime import datetime
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

engine = create_engine("postgres:///tat")
#engine = create_engine("postgres://qqiqlhzydfpsxs:26c1fca3380b9d7b46fd0925b1b1e58fc995d6cccd1f926e9c9c83eda30b5c13@ec2-75-101-131-79.compute-1.amazonaws.com:5432/d1ak4rtao1o18l")
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
@login_required
def index():
    id = session["user_id"]
    row = db.execute("SELECT * FROM users WHERE id=:id",{"id":id}).fetchone()
    return render_template("index.html",isadmin=check_admin(),row=row)

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
                    message = Markup("Password is Wrong")
                    flash(message)
                    return render_template("login.html")
                    
        else:
            message = Markup("<strong>User with this mobile no. doesn't exist</strong>")
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
    x = admin_permission()
    if x is not 1:
        return x
    g = 1
    if request.method == "POST":
        db.execute("DELETE FROM timetable")
        db.commit()
        g = 0
        success = gen(0)
        if success == -1:
            message = Markup('<strong>Something goes wrong try again</strong>')
            flash(message)
            return render_template("generate.html",isadmin=check_admin(),generate=g)
        message = Markup('<strong>Timetable Successfully generated</strong>')
        flash(message)
        return render_template("generate.html",isadmin=check_admin(),generate=g)
    else:
        return render_template("generate.html",isadmin=check_admin(),generate=g)

@app.route("/add_faculty" , methods=["GET","POST"])
@login_required
def add_faculty():
    x = admin_permission()
    if x is not 1:
        return x
    if request.method == "POST":
        num = [0,1,2,3,4,5,6,7,8,9]
        name = request.form.get("name")
        email = request.form.get("email")
        mobile = request.form.get("mobile")
        date = request.form.get("birthdate")
        current_date = datetime.now()
        current_year = current_date.year
        if int(date) >= current_year or abs(current_year-int(date)) > 200:
            message = Markup('<strong>Please Enter Right Year</strong>')
            flash(message)
            return render_template("AddFaculty.html",isadmin=check_admin())
        if len(mobile) != 10 or mobile.isdigit() == False:
            message = Markup('<strong>Please Enter Mobile Number</strong>')
            flash(message)
            return render_template("AddFaculty.html",isadmin=check_admin())
        
        password = date 
        row = db.execute("SELECT * from users WHERE mobile = :mobile",{'mobile':mobile}).fetchall()
        x = len(row)
        if x == 0:
            db.execute("INSERT INTO users (name,email,mobile,password,isadmin) VALUES (:name,:email,:mobile,:password,0)",{"name": name,"email":email,"mobile":mobile,"password":password})
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


@app.route("/remove_faculty" , methods=["GET","POST"])
@login_required
def remove_faculty():
    x = admin_permission()
    if x is not 1:
        return x
    rows = db.execute("SELECT * FROM users WHERE isadmin = 0").fetchall()
    if request.method == "POST":
        id = int(request.form.get("id"))
        row = db.execute("SELECT * from users WHERE id = :id and isadmin = 0",{"id":id}).fetchall()
        x = len(row)
        if x == 1:
            name = row[0][1]
            db.execute("DELETE FROM users WHERE id = :id and isadmin = 0",{"id":id})
            db.commit()
            rows = db.execute("SELECT * FROM users WHERE isadmin = 0").fetchall()
            message = Markup(name + '<strong> Successfully Deleted</strong>')
            flash(message)
            return render_template("RemoveFaculty.html",isadmin=check_admin(),rows=rows)
        else:
            message = Markup('<strong>Faculty does not exist</strong>')
            flash(message)
            return render_template("RemoveFaculty.html",isadmin=check_admin(),rows=rows)
    else:
        return render_template("RemoveFaculty.html",isadmin=check_admin(),rows=rows)

@app.route("/list_faculty")
@login_required
def list_faculty():
    x = admin_permission()
    if x is not 1:
        return x
    rows = db.execute("SELECT * FROM users WHERE isadmin = 0").fetchall()
    return render_template("ListFaculty.html",isadmin=check_admin(),rows=rows)

@app.route("/add_courses" , methods=["GET","POST"])
@login_required
def add_courses():
    x = admin_permission()
    if x is not 1:
        return x
    if request.method == "POST":
        name = request.form.get("name")
        courseid = request.form.get("courseid")
        lecture = int(request.form.get("lecture"))
        lab = float(request.form.get("lab"))
        tut = int(request.form.get("tutorial"))
        credit = lecture + tut + (lab / 2)
        if len(courseid) != 5:
            message = Markup('<strong>Please Enter Right Course Id</strong>')
            flash(message)
            return render_template("AddCourse.html",isadmin=check_admin())
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

@app.route("/remove_courses", methods=["GET","POST"])
@login_required
def remove_courses():
    x = admin_permission()
    if x is not 1:
        return x
    rows = db.execute("SELECT * FROM courses").fetchall()
    if request.method == "POST":
        id = request.form.get("id")
        row = db.execute("SELECT * from courses WHERE id = :id",{"id":id}).fetchall()
        x = len(row)
        if x == 1:
            name = row[0][1]
            db.execute("DELETE FROM courses WHERE id = :id",{"id":id})
            db.commit()
            rows = db.execute("SELECT * FROM courses").fetchall()
            message = Markup(name + '<strong> Successfully Deleted</strong>')
            flash(message)
            return render_template("RemoveCourse.html",isadmin=check_admin(),rows=rows)
        else:
            message = Markup(id + '<strong> does not exist</strong>')
            flash(message)
            return render_template("RemoveCourse.html",isadmin=check_admin(),rows=rows)
    else:
        return render_template("RemoveCourse.html",isadmin=check_admin(),rows=rows)


@app.route("/list_courses")
@login_required
def list_courses():
    x = admin_permission()
    if x is not 1:
        return x
    rows = db.execute("SELECT * FROM courses").fetchall()
    return render_template("ListCourse.html",isadmin=check_admin(),rows=rows)

@app.route("/add_offer", methods=["GET","POST"])
@login_required
def add_offer():
    x = admin_permission()
    if x is not 1:
        return x
    courses = db.execute("SELECT * FROM courses").fetchall()
    profs = db.execute("SELECT * FROM users WHERE isadmin = 0").fetchall()
    if request.method == "POST":
        id = request.form.get("course_id")
        prof = request.form.get("prof")
        year = int(request.form.get("year"))
        exist = db.execute("SELECT * FROM offers WHERE course_id = :id",{'id':id}).fetchall()
        x = len(exist)
        if x == 0:
            db.execute("INSERT INTO offers (course_id,user_id,batch) VALUES (:id,:prof,:year)",{"id":id,"prof":prof,"year":year})
            db.commit()
            message = Markup("<strong> Course Added </strong>")
            flash(message)
            return render_template('AddOffer.html',isadmin = check_admin(),profs=profs,courses = courses )
        else:
            message = Markup("<strong> Course already Assigned </strong>")
            flash(message)
            return render_template('AddOffer.html',isadmin = check_admin(),profs=profs,courses = courses)
    else:
        return render_template('AddOffer.html',isadmin=check_admin(),profs=profs,courses = courses)

@app.route("/remove_offer", methods=["GET","POST"])
@login_required
def remove_offer():
    x = admin_permission()
    if x is not 1:
        return x
    rows = db.execute("SELECT * FROM offers").fetchall()
    if request.method == "POST":
        id = request.form.get("course_id")
        exist = db.execute("SELECT * FROM offers WHERE course_id = :id",{'id':id}).fetchall()
        x = len(exist)
        if x == 1:
            db.execute("DELETE FROM offers WHERE course_id = :id",{"id":id})
            db.commit()
            rows = db.execute("SELECT * FROM offers").fetchall()
            message = Markup(id + "<strong> removed from current year </strong>")
            flash(message)
            return render_template('RemoveOffer.html',isadmin = check_admin(),rows=rows)
        else:
            message = Markup("<strong> Course does not Offered </strong>")
            flash(message)
            return render_template('RemoveOffer.html',isadmin = check_admin(),rows=rows)
    else:
        return render_template('RemoveOffer.html',isadmin=check_admin(),rows=rows)


@app.route("/list_offer")
@login_required
def list_offer():
    x = admin_permission()
    if x is not 1:
        return x
    rows = db.execute("SELECT name,course_id,batch FROM offers JOIN users ON offers.user_id = users.id ORDER BY batch").fetchall()
    return render_template("ListOffer.html",isadmin=check_admin(),rows=rows)

@app.route("/add_slot", methods=["GET","POST"])
@login_required
def add_slot():
    x = admin_permission()
    if x is not 1:
        return x
    rows = db.execute("SELECT * FROM offers WHERE batch = 3 OR batch = 4").fetchall()
    if request.method == "POST":
        id = request.form.get("course_id")
        slot = request.form.get("slot")
        exist = db.execute("SELECT * FROM slots WHERE course_id = :id",{'id':id}).fetchall()
        x = len(exist)
        if x == 0:
            db.execute("INSERT INTO slots (course_id,slot) VALUES (:id,:slot)",{"id":id,"slot":slot})
            db.commit()
            message = Markup(id + "<strong> added in slot </strong>" + slot)
            flash(message)
            return render_template('AddSlot.html',isadmin = check_admin(),rows=rows)
        else:
            message = Markup("<strong> Course already exist in other slot </strong>")
            flash(message)
            return render_template('AddSlot.html',isadmin = check_admin(),rows=rows)
    else:
        return render_template('AddSlot.html',isadmin=check_admin(),rows=rows)

@app.route("/remove_slot", methods=["GET","POST"])
@login_required
def remove_slot():
    x = admin_permission()
    if x is not 1:
        return x
    rows = db.execute("SELECT * FROM slots").fetchall()
    if request.method == "POST":
        id = request.form.get("course_id")
        exist = db.execute("SELECT * FROM slots WHERE course_id = :id",{'id':id}).fetchall()
        x = len(exist)
        if x == 1:
            db.execute("DELETE FROM slots WHERE course_id = :id",{"id":id})
            db.commit()
            rows = db.execute("SELECT * FROM slots").fetchall()
            message = Markup(id + "<strong> Deleted From Slot </strong>")
            flash(message)
            return render_template('RemoveSlot.html',isadmin = check_admin(),rows=rows)
        else:
            message = Markup("<strong> Course does not exist in any slot </strong>")
            flash(message)
            return render_template('RemoveSlot.html',isadmin = check_admin(),rows=rows)
    else:
        return render_template('RemoveSlot.html',isadmin=check_admin(),rows=rows)

@app.route("/list_slot")
@login_required
def list_slot():
    x = admin_permission()
    if x is not 1:
        return x
    rows = db.execute("SELECT * FROM slots ORDER BY slot").fetchall()
    return render_template("ListSlot.html",isadmin=check_admin(),rows=rows)

@app.route("/list_req")
@login_required
def list_req():
    x = admin_permission()
    if x is not 1:
        return x
    cur_date = datetime.now()
    rows = db.execute("SELECT * FROM requests JOIN users ON users.id=requests.user_id AND leave_date > :cur_date ORDER BY leave_date",{"cur_date":cur_date}).fetchall()
    return render_template("Listreq.html",isadmin=check_admin(),rows=rows)

@app.route("/view")
@login_required
def view():
    if check_admin():
        rows = db.execute("SELECT * FROM timetable join users ON user_id = id ORDER BY batch,slot").fetchall()
        return render_template("view_admin.html",isadmin=check_admin(),rows=rows)
    else:
        id = session["user_id"]
        rows = db.execute("SELECT * FROM timetable WHERE user_id=:id ORDER BY slot",{"id":id}).fetchall()
        return render_template("view_faculty.html",isadmin=check_admin(),rows=rows)

@app.route("/preference", methods=["GET","POST"])
@login_required
def preference():
    x = faculty_premission()
    if x is not 1:
        return x
    id = session["user_id"]
    if request.method == "POST":
        preferences = request.form.getlist("preference")
        db.execute("DELETE FROM preferences WHERE user_id=:id",{"id":id})
        db.commit()
        for preference in preferences:
            slot = int(preference)
            db.execute("INSERT INTO preferences (user_id,slot) VALUES (:id,:slot)",{"id":id,"slot":slot})
            db.commit()
        message = Markup("<strong> Preference is updated </strong>")
        flash(message)

    return render_template("preference.html",isadmin=check_admin())

@app.route("/change_password", methods=["GET","POST"])
@login_required
def change_password():
    if request.method == "POST":
        old = request.form.get("oldpass")
        new = request.form.get("newpass")
        confirm = request.form.get("confirmpass")
        id = session["user_id"]
        row = db.execute("SELECT * FROM users WHERE id = :id",{"id":id}).fetchone()
        password = row[4]
        if old != password:
            message = Markup("<strong> Password is wrong </strong>")
            flash(message)
        elif new!= confirm:
            message = Markup("<strong> New Password and Confirm Password is different </strong>")
            flash(message)
        else:
            db.execute("UPDATE users SET password = :password WHERE id = :id",{"password" : new,"id":id})
            db.commit()
            message = Markup("<strong> Password Updated </strong>")
            flash(message)
    return render_template("ChangePassword.html",isadmin=check_admin())

@app.route("/requests", methods=["GET","POST"])
@login_required
def requests():
    x = faculty_premission()
    if x is not 1:
        return x
    if request.method == "POST":
        id = session["user_id"]
        type_req = request.form.get("type")
        reason = request.form.get("reason")
        date = request.form.get("leavedate")
        current_date = str(datetime.now())
        if(current_date < date):
            db.execute("INSERT INTO requests (user_id,leave_type,reason,leave_date) VALUES (:id,:type_req,:reason,:date)",{"id":id,"type_req":type_req,"reason":reason,"date":date})
            db.commit()
            message = Markup("<strong> Your Request Successfully sended </strong>")
            flash(message)
        else:
            message = Markup("<strong> Please Enter Right Date </strong>")
            flash(message)
    return render_template("FormforLeave.html",isadmin=check_admin())

def check_admin():
    x = db.execute("SELECT isadmin from users WHERE id = :id",{'id':session["user_id"]}).fetchone()
    if len(x) == 0:
        session.clear()
        message = Markup("<strong>Something goes wrong login again!!</strong>")
        flash(message)
        return render_template("login.html")
    return x[0]

def admin_permission():
    if check_admin() == 0:
        message = Markup("<strong>You don't have premission to access this page</strong>")
        flash(message)
        id = session["user_id"]
        row = db.execute("SELECT * FROM users WHERE id=:id",{"id":id}).fetchone()
        return render_template("index.html",isadmin=check_admin(),row=row)
    return 1

def faculty_premission():
    if check_admin() == 1:
        id = session["user_id"]
        row = db.execute("SELECT * FROM users WHERE id=:id",{"id":id}).fetchone()
        message = Markup("<strong>You don't have premission to access this page</strong>")
        flash(message)
        return render_template("index.html",isadmin=check_admin(),row=row)
    return 1