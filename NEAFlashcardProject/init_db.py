import sqlite3
def init_db():
    conn = sqlite3.connect('data.db')
    conn.execute('PRAGMA foreign_keys = ON') # enables foreign keys
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flashcards (
            flashcard_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            user_ID INTEGER,
            frontCard TEXT,
            backCard TEXT,
            deck_ID INTEGER,
            FOREIGN KEY (deck_ID) REFERENCES decks(deck_ID) ON DELETE CASCADE,
            FOREIGN KEY (user_ID) REFERENCES users(user_ID) ON DELETE CASCADE)''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sr_info (
            sr_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
            flashcard_ID INTEGER,
            rating INTEGER,
            sr_interval FLOAT,
            last_review FLOAT,
            EF FLOAT,
            state INTEGER,
            FOREIGN KEY (flashcard_ID) REFERENCES flashcards(flashcard_ID) ON DELETE CASCADE)''')
    
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS decks (
                deck_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                user_ID INTEGER,
                deckName TEXT,
                FOREIGN KEY (user_ID) REFERENCES users(user_ID) ON DELETE CASCADE)''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz (
            quizdata_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
            user_ID INTEGER, 
            deck_ID INTEGER,
            score FLOAT,
            date  DATETIME,
            FOREIGN KEY (user_ID) REFERENCES users(user_ID) ON DELETE CASCADE,
            FOREIGN KEY (deck_ID) REFERENCES decks(deck_ID) ON DELETE CASCADE)''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            email TEXT,
            password TEXT,
            name TEXT,
            is_student INTEGER)''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            user_ID INTEGER,
            streak_count INTEGER DEFAULT 0,
            last_study_date DATE,
            FOREIGN KEY (user_ID) REFERENCES users(user_ID) ON DELETE CASCADE)''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            teacher_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            user_ID INTEGER,
            FOREIGN KEY (user_ID) REFERENCES users(user_ID) ON DELETE CASCADE)''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            class_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
            classname TEXT,
            teacher_ID INTEGER,
            FOREIGN KEY (teacher_ID) REFERENCES teachers(teacher_ID) ON DELETE CASCADE)''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS class_members (
            class_ID INTEGER,
            user_ID INTEGER,
            PRIMARY KEY (class_ID, user_ID)
            FOREIGN KEY (class_ID) REFERENCES classes(class_ID) ON DELETE CASCADE,
            FOREIGN KEY (user_ID) REFERENCES users(user_ID) ON DELETE CASCADE)''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS homework (
            homework_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            class_id INTEGER,
            deck_id INTEGER,
            user_id INTEGER,
            completed BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
            FOREIGN KEY (deck_id) REFERENCES decks(deck_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE);''')
