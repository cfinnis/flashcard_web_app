from flask import Blueprint, session, render_template, request, redirect, url_for
from users import Teacher
import sqlite3

teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/teacherhome', methods=['POST', 'GET'])
def teacherhome():
    session['user_ID'] = session.get('user_ID', 0)
    user_ID = session['user_ID']
    
    #get teacher's name
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM users WHERE user_ID = ?', (user_ID,))
    name = cursor.fetchone()[0]
    session['name'] = name
    return render_template('teacherhome.html', name=name)

@teacher_bp.route('/classes', methods=['POST', 'GET'])
def classes():
    # get user_ID from session then get equivalent teacher_ID from database
    session['user_ID'] = session.get('user_ID', 0)
    user_ID = session['user_ID']

    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT teacher_ID FROM teachers WHERE user_ID = ?', (user_ID,))
    teacher_ID = cursor.fetchone()[0]

    # get info from form
    if request.method == 'POST':
        classname = str(request.form['class'])
        teacher = Teacher('data.db')
        teacher.addClass(classname, teacher_ID)

    # list of all students
    cursor.execute('''
        SELECT students.user_ID, users.name
        FROM students
        INNER JOIN users ON students.user_ID=users.user_ID''')
    students = cursor.fetchall()

    # fetch all classes the current teacher teaches
    cursor.execute('''
        SELECT class_ID, classname
        FROM classes
        WHERE teacher_ID = ?''', (teacher_ID,))
    classes = cursor.fetchall()

    # get all students in that class
    session['class_ID'] = session.get('class_ID', 0)
    if session['class_ID'] != 0:
        class_ID = session['class_ID']
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT cm.user_ID, users.name
                        FROM class_members cm 
                        INNER JOIN users ON users.user_ID=cm.user_ID
                        WHERE class_ID = ?''', (class_ID,))
        class_members = cursor.fetchall()
    else:
        class_members = []
    return render_template('classes.html', students=students, classes=classes, class_members=class_members, name=session['name'])
    
@teacher_bp.route('/addstudents', methods=['POST', 'GET'])
def addstudents():
    students = request.form.getlist("check") # list of user_IDs
    class_ID = request.form.get('class')
    for student in students:
        teacher = Teacher('data.db')
        teacher.addStudent(student, class_ID)
    return redirect(url_for('teacher.classes'))

@teacher_bp.route('/selectclass', methods=['POST', 'GET'])
def selectclass():
    class_ID = request.form.get('class')
    if 'class_ID' not in session:
        session['class_ID'] = class_ID
    session['class_ID'] = class_ID
    return redirect(url_for('teacher.classes'))

@teacher_bp.route('/deletestudent', methods=['POST', 'GET'])
def deletestudent():
    session['class_ID'] = session.get('class_ID', 0)
    class_ID = session['class_ID']
    if request.method == 'POST':
        students = request.form.getlist("checkbox") # list of user_IDs
        for student in students:
            teacher = Teacher('data.db')
            teacher.deleteStudent(student, class_ID)
        return redirect(url_for('teacher.classes'))

@teacher_bp.route('/deleteclass', methods=['GET','POST'])
def deleteclass():
    # get info from form and database so object can be created then class is deleted
    if request.method == 'POST':
        class_ID = int(request.form['delete_class']) # id of selected class
        teacher = Teacher('data.db')
        teacher.deleteClass(class_ID)
    return redirect(url_for('teacher.classes'))