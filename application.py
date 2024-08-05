import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///journal.db")

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return "must provide username"

        # Ensure password was submitted
        elif not request.form.get("password"):
            return "must provide password"

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return "invalid username and/or password"

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":

        user_name = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        username = request.form.get("username")
        password = request.form.get("password")

        # Render an apology if the user’s input is blank
        if not request.form.get("username"):
            return "must provide username"

        # Ensure password was submitted
        elif not request.form.get("password"):
            return "must provide password"
        # Ensure confirmation password was submitted
        elif not request.form.get("confirmation"):
            return "must provide password confirmation"

        # Ensure confirmation and password match
        elif request.form.get("password") != request.form.get("confirmation"):
            return "password doesn't match confirmation"

        # Ensure username doesn't already exist
        elif len(user_name) != 0:
            return "username already exists"

        # Insert user's data into users' database
        else:
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, generate_password_hash(password))
            return redirect("/")

    return apology("ERROR")


@app.route("/journal", methods=["GET", "POST"])
@login_required
def journal():
    if request.method == "GET":
        return render_template("journal.html")

    if request.method == "POST":

        day = request.form.get("day")
        month = request.form.get("month")
        year = request.form.get("year")
        content = request.form.get("content")

        if not day:
            return "must enter day"
        if not month:
            return "must enter month"
        if not year:
            return "must enter year"
        if not content:
            return "must enter content"

        else:
            db.execute("INSERT INTO journal (id, day, month, year, content) VALUES(?, ?, ?, ?, ?)", session["user_id"], day, month, year, content)
            return redirect("/")
    return "error"

@app.route("/journal_db", methods=["GET", "POST"])
@login_required
def journal_db():
    if request.method == "GET":
        journal = db.execute("SELECT * FROM journal WHERE id = ? ORDER BY year, month, day", session["user_id"])
        if not journal:
            return "You have no entries in record"
        return render_template("journal_db.html", journal=journal)

    else:
        day = request.form.get("day")
        month = request.form.get("month")
        year = request.form.get("year")

        entry = db.execute("SELECT * FROM journal WHERE id = ? AND day = ? AND month = ? AND year = ?", session["user_id"], day, month, year)

        return render_template("jour_result.html", entry=entry)

@app.route("/notes", methods=["GET", "POST"])
@login_required
def notes():
    if request.method == "GET":
        return render_template("notes.html")

    if request.method == "POST":

        title = request.form.get("title")
        note = request.form.get("note")

        if not title:
            return "must enter title"
        if not note:
            return "must enter note"

        else:
            db.execute("INSERT INTO notes (id, title, note) VALUES(?, ?, ?)", session["user_id"], title.lower(), note)
            return redirect("/")
    return "error"

@app.route("/notes_db", methods=["GET", "POST"])
@login_required
def notes_db():
    if request.method == "GET":
        notes = db.execute("SELECT * FROM notes WHERE id = ?", session["user_id"])
        if not notes:
            return "You have no entries in record"
        return render_template("notes_db.html", notes=notes)

    else:
        title = request.form.get("title").lower()

        entry = db.execute("SELECT * FROM notes WHERE id = ? AND title = ?", session["user_id"], title)
        if not entry:
            return "You have no such entry in record"
        return render_template("notes_result.html", entry=entry)

@app.route("/birthdays", methods=["GET", "POST"])
@login_required
def birthdays():
    if request.method == "GET":
        return render_template("birthdays.html")

    if request.method == "POST":

        name = request.form.get("name")
        birthday = request.form.get("birthday")

        if not name:
            return "must enter name"
        if not birthday:
            return "must enter birthday"

        else:
            db.execute("INSERT INTO birthdays (id, name, date) VALUES(?, ?, ?)", session["user_id"], name.lower(), birthday)
            return redirect("/")
    return "error"

@app.route("/birthdays_db", methods=["GET", "POST"])
@login_required
def birthdays_db():
    if request.method == "GET":
        birthdays = db.execute("SELECT * FROM birthdays WHERE id = ?", session["user_id"])
        if not birthdays:
            return "You have no entries in record"
        return render_template("birthdays_db.html", birthdays=birthdays)

    else:
        name = request.form.get("name").lower()

        entry = db.execute("SELECT * FROM birthdays WHERE id = ? AND name = ?", session["user_id"], name)
        if not entry:
            return "You have no such entry in record"
        return render_template("birthdays_result.html", entry=entry)
        
@app.route("/reminder", methods=["GET", "POST"])
@login_required
def reminder():
    if request.method == "GET":
        return render_template("reminder.html")

    if request.method == "POST":

        date = request.form.get("date")
        event = request.form.get("event")

        if not date:
            return "must enter date"
        if not event:
            return "must enter event"

        else:
            db.execute("INSERT INTO reminder (id, date, event) VALUES(?, ?, ?)", session["user_id"], date, event)
            return redirect("/")
    return "error"

@app.route("/reminder_db", methods=["GET", "POST"])
@login_required
def reminder_db():
    if request.method == "GET":
        reminder = db.execute("SELECT * FROM reminder WHERE id = ?", session["user_id"])
        if not reminder:
            return "You have no entries in record"
        return render_template("reminder_db.html", reminder=reminder)

    else:
        date = request.form.get("date")

        entry = db.execute("SELECT * FROM reminder WHERE id = ? AND date = ?", session["user_id"], date)
        if not entry:
            return "You have no such entry in record"
        return render_template("reminder_result.html", entry=entry)

    def errorhandler(e):
        """Handle error"""
        if not isinstance(e, HTTPException):
            e = InternalServerError()
            return apology(e.name, e.code)


        # Listen for errors
        for code in default_exceptions:
            app.errorhandler(code)(errorhandler)

