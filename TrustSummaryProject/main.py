import re
from flask import Flask, request, session, g, redirect, url_for, render_template, flash
#for encrypting passwords
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os
from functools import wraps
from flask import Flask
from dotenv import load_dotenv

app = Flask(__name__)

# Load variables from .env into environment
load_dotenv()
# Configure sqlite database
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, os.getenv('DATABASE', 'data.db')),
    SECRET_KEY=os.getenv('SECRET_KEY'),
    #USERNAME=os.getenv('USERNAME', 'admin'),
    #PASSWORD=os.getenv('PASSWORD', 'default')
))


def connect_db():
    # Connects to the database#
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    # initailse database an and run sql script to build and populate tables
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.executescript(f.read())
            #encrypt the exisiting users passwords
            db.execute("UPDATE users SET password=? WHERE username=?",
            (generate_password_hash("Test1234"), "SRogers"))
            db.execute("UPDATE users SET password=? WHERE username=?",
            (generate_password_hash("Test6789"), "SJones"))

        db.commit()


def get_db():
    # Opens a new database connection
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def check_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "loggedin" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.teardown_appcontext
def close_db(error):
    # Closes the database
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/', methods=['GET', 'POST'])
def login():
    with app.app_context():
        db = get_db()
        # Output message
        msg = ''
        # Check if "username" and "password"  requests from the form
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            # create variables for username and password submitted from the login form
            username = request.form['username']
            password = request.form['password']
            cursor = db.execute("SELECT * from users where username = ? AND password = ?",
                                (username, password))

            acc = cursor.fetchone()
            # if account is found set the session
            if acc and check_password_hash(acc['password'], password):
                session['loggedin'] = True
                session['userid'] = acc['id']
                session['username'] = acc['username']
                session['accounttype'] = acc['accounttype']
                return redirect(url_for('summarylist'))
            else:
                # Account doesnt exist or username/password incorrect
                msg = 'Incorrect username/password!'
        return render_template('index.html', msg=msg)


@app.route('/register', methods=['GET', 'POST'])
def register():
    db = get_db()

    msg = ''
    # Check if fields are filled out
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'fullname' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        acctype = request.form['acounttype']
        cursor = db.execute("SELECT * from users where username = ?", (username,))

        acc = cursor.fetchone()
        # validations checks
        if acc:
            msg = "An account with this username is already in use"
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = "Username can only contain characters and numbers"
        elif not re.match(r'[A-Za-z]+', fullname):
            msg = "Fullname can only contain letters"
        elif not username or not password or not fullname:
            msg = 'Please fill out all fields'
        elif len(password) < 8:
            msg = 'Password must be at least 8 characters long'
        else:
            #encrypt the password before inserting into the database
            encyrpt_pass = generate_password_hash(password)
            # if checks are passed add new user
            db.execute("INSERT INTO users(username, password, fullname,accounttype) VALUES (?,?,?,?)",
                       (username, encyrpt_pass, fullname, acctype))
            db.commit()
            msg = 'Registration successful, please log in'

    elif request.method == 'POST':
        # Form is empty
        msg = 'Please fill out all fields'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


@app.route('/summarylist')
# Check if the user is logged in
@check_login
def summarylist():
    db = get_db()
    cur = db.execute('select * from DailySummary order by id desc')
    entries = cur.fetchall()
    return render_template('summarylist.html', username=session['username'], entries=entries)




@app.route('/dailydetail/<string:dayid>', methods=['GET', 'POST'])
# Check if the user is logged in
@check_login
def dailydetail(dayid):
    db = get_db()

    # User is logged in take them to the daily detail page for the chosen record and for a POST request
    #  validate the fields, save the record and return to the summary
    if request.method == 'POST':
        # if the user is posting data validation checks are done before commiting changes to the database

        # check if number fields are blank insert a 0
        if request.form['PatientsInCorridor'] == "":
            PatientsInCorridor = 0
        else:
            PatientsInCorridor = int(request.form['PatientsInCorridor'])
        if request.form['PatientsAwaitingBeds'] == "":
            PatientsAwaitingBeds = 0
        else:
            PatientsAwaitingBeds = int(request.form['PatientsAwaitingBeds'])
        if request.form['TotalPatientsED'] == "":
            TotalPatientsED = 0
        else:
            TotalPatientsED = int(request.form['TotalPatientsED'])

        TriageTime = request.form['TriageTimehrs']

        WaitingTimeMajors = request.form['WaitingTimeMajorshrs']

        EscalationLevel = request.form['EscalationLevel']
        Smanager = request.form['SiteManager']


        if len(Smanager) == 0:
            msg = "You must enter a site manager"
        elif not Smanager.isalpha():
            msg = "Site manager must only contain letters"
        elif len(Smanager) > 50:
            msg = "Site manager name cannot exceed 50 characters"
        elif PatientsInCorridor > 50:
            msg = "Number of patients waiting in the corridor cannot exceed 50"
        elif PatientsInCorridor < 0:
            msg = "Number of patients waiting in the corridor cannot be less than 0 "
        elif not re.match(r'[A-Za-z]+', EscalationLevel):
            msg = "Escalation level can only contain letters"
        elif EscalationLevel not in ("Red", "Amber", "Green"):
            msg = "Escalation level must be set as Red, Amber or Green"
        elif TotalPatientsED > 200:
            msg = "Number of patients in ED cannot exceed 200"
        elif TotalPatientsED < 0:
            msg = "Number of patients in ED cannot  be less than 0"
        else:
            db.execute("UPDATE DailySummary SET SiteManager=?,PatientsInCorridor=?,EscalationLevel=?,"
                        "TriageTimehrs=?,PatientsAwaitingBeds=?,WaitingTimeMajorshrs=?,TotalPatientsED=? "
                        "WHERE id =?", (Smanager, PatientsInCorridor, EscalationLevel, TriageTime,
                                        PatientsAwaitingBeds, WaitingTimeMajors, TotalPatientsED, dayid))
            db.commit()
            msg = "Record successfully saved"
            cur = db.execute('select * from DailySummary order by id desc')
            entries = cur.fetchall()
            return render_template('summarylist.html', username=session['username'], entries=entries, msg=msg)

        cur = db.execute('select * from DailySummary WHERE id =?', (dayid,))
        entries = cur.fetchone()
        return render_template('dailydetail.html', username=session['username'], acctype=session['accounttype'],
                                entries=entries, dayid=dayid, msg=msg)
    else:

        cur = db.execute('select * from DailySummary WHERE id =?', (dayid,))
        entries = cur.fetchone()
        return render_template('dailydetail.html', username=session['username'], acctype=session['accounttype'],
                                entries=entries, dayid=dayid)


@app.route('/adddailyrecord')
# Check if the user is logged in
@check_login
def openadddailyrecord():
        # User is logged in take them to add record page
        return render_template('adddailyrecord.html', username=session['username'])
    # User is not logged in redirect to login page



@app.route('/adddailyrecord', methods=['POST'])
# Check if the user is logged in
@check_login
def adddailyrecord():
    db = get_db()
        # User is logged in take them to the daily detail page for the chosen record and for a POST request
        #  validate the fields, save the record and return to the summary
    if request.method == 'POST':
        # if the user is posting data validation checks are done before inserting record into the database
        # check if number fields are blank insert a 0
        if request.form['PatientsInCorridor'] == "":
            PatientsInCorridor = 0
        else:
            PatientsInCorridor = int(request.form['PatientsInCorridor'])
        if request.form['PatientsAwaitingBeds'] == "":
            PatientsAwaitingBeds = 0
        else:
            PatientsAwaitingBeds = int(request.form['TotalPatientsED'])
        if request.form['TotalPatientsED'] == "":
            TotalPatientsED = 0
        else:
            TotalPatientsED = int(request.form['PatientsAwaitingBeds'])
        Dte = request.form['ReportDate']
        Smanager = request.form['SiteManager']

        EscalationLevel = request.form['EscalationLevel']
        TriageTime = request.form['TriageTimehrs']

        WaitingTimeMajors = request.form['WaitingTimeMajorshrs']
        if len(Smanager) == 0:
            msg = "You must enter a site manager"
        elif not Smanager.isalpha():
            msg = "Site manager must only contain letters"
        elif len(Smanager) > 50:
            msg = "Site manager name cannot exceed 50 characters"
        elif PatientsInCorridor > 50:
            msg = "Number of patients waiting in the corridor cannot exceed 50"
        elif PatientsInCorridor < 0:
            msg = "Number of patients waiting in the corridor cannot be less than 0 "
        elif not re.match(r'[A-Za-z]+', EscalationLevel):
            msg = "Escalation level can only contain letters"
        elif EscalationLevel not in ("Red", "Amber", "Green"):
            msg = "Escalation level must be set as Red, Amber or Green"
        elif TotalPatientsED > 200:
            msg = "Number of patients in ED cannot exceed 200"
        elif TotalPatientsED < 0:
            msg = "Number of patients in ED cannot  be less than 0"
        else:
            # insert new record into database
            db.execute("INSERT INTO DailySummary (dte, SiteManager,PatientsInCorridor,EscalationLevel,"
                       "TriageTimehrs,PatientsAwaitingBeds,WaitingTimeMajorshrs,TotalPatientsED) "
                       " VALUES (?,?,?,?,?,?,?,?)", (Dte, Smanager, PatientsInCorridor, EscalationLevel, TriageTime,
                                                     PatientsAwaitingBeds, WaitingTimeMajors, TotalPatientsED))

            db.commit()
            msg = "Record successfully saved"
            # Return the user to the summary page
            cur = db.execute('select * from DailySummary order by id desc')
            entries = cur.fetchall()
            return render_template('summarylist.html', username=session['username'], entries=entries, msg=msg)

        return render_template('adddailyrecord.html', username=session['username'], msg=msg)
    else:
        # Return the user to the summary page
        cur = db.execute('select * from DailySummary order by id desc')
        entries = cur.fetchall()
        return render_template('summarylist.html', username=session['username'], entries=entries)



@app.route('/summarylist/<string:dayid>')
# Check if the user is logged in
@check_login
def deleterecord(dayid):
    db = get_db()
    # Delete the chosen record
    cur = db.execute('DELETE from DailySummary WHERE id =?', (dayid,))
    db.commit()
    # Return the user to the summary page
    cur = db.execute('select * from DailySummary order by id desc')
    entries = cur.fetchall()
    return render_template('summarylist.html', username=session['username'], entries=entries)


@app.route('/logout')
def logout():
    # Remove session data to log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('accounttype', None)
    # Return them to the login page
    return redirect(url_for('login'))


if __name__ == '__main__':
    init_db()
app.run()
