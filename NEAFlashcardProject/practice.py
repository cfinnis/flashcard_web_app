import sqlite3

# # Connect to the SQLite database
# conn = sqlite3.connect('data.db')
# cursor = conn.cursor()

# # Step 1: Delete the existing quiz table
# cursor.execute('DROP TABLE IF EXISTS quiz')

# # Step 2: Reinitialize the quiz table with the desired schema
# cursor.execute('''
#     CREATE TABLE quiz (
#         quizdata_ID INTEGER PRIMARY KEY AUTOINCREMENT,
#         user_ID INTEGER,
#         deck_ID INTEGER,
#         score INTEGER,
#         date TEXT,
#         FOREIGN KEY (user_ID) REFERENCES users(user_ID),
#         FOREIGN KEY (deck_ID) REFERENCES decks(deck_ID)
#     )
# ''')

# # Commit the changes and close the connection
# conn.commit()
# conn.close()

# # # print("Quiz table has been deleted and reinitialized.")
# conn = sqlite3.connect('data.db')
# cursor = conn.cursor()
# #cursor.execute('DROP TRIGGER IF EXISTS add_student_after_insert;')
# # cursor.execute('DROP TRIGGER IF EXISTS add_teacher_after_insert;')
# # conn.commit()
# # conn.close()
# cursor.execute('ALTER TABLE students ADD COLUMN streak_count INTEGER DEFAULT 0;')
# cursor.execute('ALTER TABLE students ADD COLUMN last_study_date DATE;')
# conn.commit()
# conn.close()

# list = [1]
# list.insert(0,-4)
# print(list)
