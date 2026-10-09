import sqlite3
from flask import Flask, render_template, session, request, redirect, url_for, Response, g
from users import User, Student, Teacher
from init_db import init_db
from teachers import teacher_bp
from study import study_bp
from quiz import quiz_bp
import bcrypt
import os


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")


app.register_blueprint(teacher_bp, url_prefix='/teacher')
app.register_blueprint(study_bp, url_prefix='/study')
app.register_blueprint(quiz_bp, url_prefix='/quiz')


@app.route('/', methods=['GET', 'POST'])
def login():
    init_db()
    message = None
    # get user info from form
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        is_student = request.form.get('account')

        if not email:
            message = 'Please enter an email.'
            valid = False
        elif '@' not in email:
            message = 'Please enter a valid email'
            valid = False
        elif not password:
            message = 'Please enter password.'
            valid = False
        else:
            valid = True
        
        # if the inputs are valid check that an account with that information exists before logging in
        if valid == True:
            # this is the validation for a student account
            if int(is_student) == 1:
                student = Student('data.db')
                if student.checkDatabaseForMatch(email, is_student) == False:
                    message = 'A student account with this email does not exist. Please register first.'
                elif student.validateLogin(email, password) == False:
                    message = 'Incorrect email or password'
                else: # logged in successfully
                    user_ID = student.validateLogin(email, password)
                    if 'user_ID' not in session:
                        session['user_ID'] = user_ID
                    session['user_ID'] = user_ID
                    return redirect(url_for('study.studycards'))

            else:
                # this is the validation for a teacher account
                teacher = Teacher('data.db')
                if teacher.checkDatabaseForMatch(email, is_student) == False:
                    message = 'A teacher account with this email does not exist. Please register first.'
                elif teacher.validateLogin(email, password) == False:
                    message = 'Incorrect email or password'
                else: # logged in successfully
                    user_ID = teacher.validateLogin(email, password)
                    if 'user_ID' not in session:
                        session['user_ID'] = user_ID
                    session['user_ID'] = user_ID
                    return redirect(url_for('teacher.teacherhome'))
    return render_template('login.html', message = message)

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = None

    # get user info from form
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        is_student = request.form.get('account')

        if not email:
            message = 'Please enter an email.'
            valid = False
        elif '@' not in email:
            message = 'Please enter a valid email'
            valid = False
        elif not password:
            message = 'Please enter password.'
            valid = False
        elif len(password) < 8:
            message = 'Please enter a password longer than 8 characters'
            valid = False
        elif not name: 
            valid = False
            message = 'Please enter name.'
        else:
            valid = True
        
        # create account if the inputs are valid and an account with that info doesnt already exist
        if valid == True:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            if int(is_student) == 1:
                student = Student('data.db')
                if student.checkDatabaseForMatch(email, is_student) == False:
                    student.createAccount(email, hashed_password, name, int(is_student))
                    return redirect(url_for('login'))
                else: 
                    message = 'An account already exixts with this email.'
            else:
                teacher = Teacher('data.db')
                if teacher.checkDatabaseForMatch(email, is_student) == False:
                    teacher.createAccount(email, hashed_password, name, int(is_student))
                    return redirect(url_for('login'))
                else: 
                    message = 'An account already exixts with this email.'

    return render_template('register.html', message=message)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    #clear the session to log the user out and redirect to login page
    session.clear()
    return redirect(url_for('login'))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    session['user_ID'] = session.get('user_ID', 0)
    user_ID = session['user_ID']

    # get current users info from database
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, email, is_student FROM users WHERE user_ID = ?', (user_ID,))
    user = cursor.fetchone()
    name = user[0]
    email = user[1]
    account_type = int(user[2])

    # decide on base template depending on account_type
    base_template = "teacherhome.html" if account_type == 0 else "base.html"
    if 'base_template' not in session:
        session['base_template'] = base_template
    return render_template('account_settings.html', name=name, email=email, base_template=base_template)

@app.route('/resetpassword', methods=['GET', 'POST'])
def resetpassword():
    message = None

    if request.method == 'POST':
        session['user_ID'] = session.get('user_ID', 0)
        user_ID = session['user_ID']

        #fetch hashed password
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM users WHERE user_ID = ?', (user_ID,))
        hashed_password = cursor.fetchone()[0]
        conn.close()
        # get current password from user
        current_password = request.form.get('current_password')

        # compare with each other to check password is correct
        if bcrypt.checkpw(current_password.encode('utf-8'), hashed_password):
            new_password = request.form.get('new_password')
            new_hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            user = User('data.db')
            user.resetPassword(user_ID, new_hashed_password)
        else:
            message = 'Current password is incorrect'

    if message == None:
        message = ''
    
    session['base_template'] = session.get('base_template', 0)
    base_template = session['base_template']
    return render_template('reset_password.html', message=message, base_template=base_template, name=session['name'])

@app.route('/updateprofile', methods=['POST', 'GET'])
def updateprofile():
    session['user_ID'] = session.get('user_ID', 0)
    user_ID = session['user_ID']

    # fetch name and email
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, email FROM users WHERE user_ID = ?', (user_ID,))
    user = cursor.fetchone()
    conn.close()
    name, email = user


    # update name and email
    new_name = request.form.get('name') or name
    new_email = request.form.get('email') or email
    user = User('data.db')
    user.updateProfile(new_name, new_email, user_ID)
    name, email = new_name, new_email

    session['name'] = name
    session['base_template'] = session.get('base_template', 0)
    base_template = session['base_template']

    return render_template('update_profile.html', name=name, email=email, base_template=base_template)

@app.route('/deleteaccount', methods=['POST', 'GET'])
def deleteaccount():
    session['user_ID'] = session.get('user_ID', 0)
    user_ID = session['user_ID']
    
    # delete account
    user = User('data.db')
    user.deleteAccount(user_ID)
    session.clear()
    return redirect(url_for('login'))

@app.before_request # runs before every request
def studystreak():
    # this is run before the login request so the database needs to be initialised here
    init_db()
    if 'user_ID' in session:  # ensure the user is logged in
        user_ID = session['user_ID']
        # check user is a student
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT is_student FROM users WHERE user_ID = ?', (user_ID,))
        is_student = int(cursor.fetchone()[0])
        if is_student == 1:
            # get student_ID
            cursor.execute('SELECT student_ID from students WHERE user_ID = ?', (user_ID,))
            student_ID = cursor.fetchone()[0]

            student = Student('data.db')
            g.streak_count = student.getStreak(student_ID)  # store streak in Flask's `g` object (so its global)
        else:
            g.streak_count = None # no streak for users that arent logged in

if __name__ == '__main__':
    app.run(debug=True, port=8080) # debug=True allows python errors to appear on the webpage - makes tracing errors easier - change port if not working eg. port=8000
