import sqlite3
import bcrypt
from datetime import datetime, timedelta

class User():
    def __init__(self, db):
        self.user_id = None
        self.db = db

    def createAccount(self, email, password, name, is_student):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        # add the user to the students or teachers table 
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS add_student_after_insert
            AFTER INSERT ON users
            FOR EACH ROW
            WHEN NEW.is_student = 1
            BEGIN
                INSERT INTO students (user_ID)
                VALUES (NEW.user_ID);
            END;
            ''')
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS add_teacher_after_insert
            AFTER INSERT ON users
            FOR EACH ROW
            WHEN NEW.is_student = 0
            BEGIN
                INSERT INTO teachers (user_ID)
                VALUES (NEW.user_ID);
            END;
            ''')
        cursor.execute('INSERT INTO users (email, password, name, is_student) VALUES (?,?,?,?)', (email, password, name, is_student))
        user_ID = cursor.lastrowid
        self.user_id = user_ID
        conn.commit()
        conn.close()

    def checkDatabaseForMatch(self, email, is_student):
        # checks the database to see whether a user with this email already exists
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        cursor.execute('SELECT 1 FROM users WHERE email = ? and is_student = ?', (email, is_student))
        user_exists = cursor.fetchone() is not None
        
        if user_exists:
            return True
        else:
            return False

    def validateLogin(self, email, password):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('SELECT user_ID, password FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if user:
            user_ID, hashed_password = user
            # Validate the password
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                # Password is correct, log the user in
                return user_ID
            else:
                return False # Password incorrect
        else:
            return False # no user found with given email

    def getID(self, email):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        cursor.execute('SELECT user_ID FROM users WHERE email = ?', (email,))
        user_ID = cursor.fetchone()[0]
        self.user_ID = user_ID
        return self.user_id

    def resetPassword(self, user_ID, new_hashed_password):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET password = ? WHERE user_ID = ?', (new_hashed_password, user_ID))
        conn.commit()
        conn.close()

    def updateProfile(self, name, email, user_ID):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET name = ?, email = ? WHERE user_ID = ?', (name, email, user_ID))
        conn.commit()
        conn.close()

    def deleteAccount(self, user_ID):
        conn = sqlite3.connect(self.db)
        conn.execute('PRAGMA foreign_keys = ON') # enables foreign keys
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE user_ID = ?', (user_ID,))
        conn.commit()
        conn.close()

class Teacher(User):
    def addClass(self, classname, teacher_ID):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO classes (classname, teacher_ID) VALUES (?, ?)', (classname, teacher_ID))
        conn.commit()
        cursor.close()
        conn.close()

    def addStudent(self, user_ID, class_ID):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
    
        cursor.execute('''
        INSERT OR IGNORE INTO class_members (class_ID, user_ID) VALUES (?,?)''', (class_ID, user_ID))
        conn.commit()
        cursor.close()
        conn.close()
    
    def deleteClass(self, class_ID):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM classes WHERE class_ID = (?)', [class_ID])
        cursor.execute('DELETE FROM class_members WHERE class_ID = (?)', [class_ID])
        conn.commit()
        cursor.close()
        conn.close()

    def deleteStudent(self,user_ID, class_ID):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM class_members WHERE user_ID = ? and class_ID = ?', (user_ID, class_ID))
        conn.commit()
        conn.close()

class Student(User):
    def getStreak(self, student_ID):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT streak_count, last_study_date 
            FROM students 
            WHERE student_ID = ?''', (student_ID,))
        result = cursor.fetchone()

        streak_count = 0  # default streak is 0
        if result:
            streak_count, last_study_date = result
            today = datetime.now().date()

            # if streak is broken, reset to 0
            if last_study_date:
                last_study_date = datetime.strptime(last_study_date, "%Y-%m-%d").date()
                if last_study_date < today - timedelta(days=1):
                    streak_count = 0
                    cursor.execute("""
                        UPDATE students 
                        SET streak_count = ?, last_study_date = ? 
                        WHERE student_ID = ?""", (streak_count, today, student_ID))

        conn.commit()
        conn.close()
        return streak_count

    def updateStudyStreak(self, student_ID):
        # get todays date
        today = datetime.now().date()

        # fetch current streak data
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('''
        SELECT streak_count, last_study_date 
        FROM students 
        WHERE student_ID = ?''', (student_ID,))
        result = cursor.fetchone()

        if result:
            streak_count, last_study_date = result

            if last_study_date:
                last_study_date = datetime.strptime(last_study_date, "%Y-%m-%d").date() # turns date string from db into date object
                
        
                # case 1: last studied yesterday so add one to streak
                if last_study_date == today - timedelta(days=1): # timedelta represents the duration of 1 day
                    streak_count += 1
                    cursor.execute("""
                        UPDATE students 
                        SET streak_count = ?, last_study_date = ? 
                        WHERE student_ID = ?""", (streak_count, today, student_ID))
                    
                # case 2: missed a study day so streak lost/reset to 0
                else:
                    streak_count = 1
                    cursor.execute("""
                        UPDATE students 
                        SET streak_count = ?, last_study_date = ? 
                        WHERE student_ID = ?""", (streak_count, today, student_ID))
            else:
                # First time studying
                streak_count = 1
                cursor.execute('''
                    UPDATE students 
                    SET streak_count = ?, last_study_date = ? 
                    WHERE student_ID = ?''', (streak_count, today, student_ID))
        else:
            print('Student not found.')

        conn.commit()
        conn.close()
        