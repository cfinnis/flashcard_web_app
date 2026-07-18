from flask import Blueprint, session, render_template, request, redirect, url_for, Response
from flashcards import Quiz
from charts import create_chart, create_barchart
import random
import sqlite3

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/quiz', methods = ['GET', 'POST'])
def quiz():
    session['user_ID'] = session.get('user_ID', 0)
    user_ID = session['user_ID']

    # fetch info needed for page from database
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT deck_ID, deckName FROM decks WHERE user_ID = ?', (user_ID,))
    decks = cursor.fetchall()
    conn.close()

    if request.method == 'POST':
        deck_ID = request.form.get('deck_id')
        if 'deck' not in session:
            session['deck'] = deck_ID
        session['deck'] = deck_ID

        if 'q_id' not in session:
            session['q_id'] = 0
        session['q_id'] = 0
        
        return redirect(url_for('quiz.doquiz'))
    return render_template('quiz.html', decks=decks, name=session['name'])

@quiz_bp.route('/doquiz', methods=['GET', 'POST'])
def doquiz():
    session['deck'] = session.get('deck', 0)
    deck_id = session['deck']

    # get info from database
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT flashcards.flashcard_ID, flashcards.frontCard, flashcards.backCard, decks.deckName
    FROM decks
    INNER JOIN flashcards ON decks.deck_ID=flashcards.deck_ID
    WHERE decks.deck_ID = ? ''', (deck_id,))
    quiz = cursor.fetchall()
    conn.close() 

    # can only make a quiz if the deck has at least 4 cards in it
    if len(quiz) >= 4:
        if 'quiz_length' not in session:
            session['quiz_length'] = len(quiz)

        session['q_id'] = session.get('q_id', 0)
        q_id = session['q_id']

        # generate three distinct random numbers (that also are not the same as q_ID of current question)
        random1 = random.randint(0,len(quiz)-1)
        random2 = random.randint(0,len(quiz)-1)
        random3 = random.randint(0,len(quiz)-1)
        while random1 == q_id or random2 == q_id or random3 == q_id or random1 == random2 or random1 == random3 or random2 == random3:
            random1 = random.randint(0,len(quiz)-1)
            random2 = random.randint(0,len(quiz)-1)
            random3 = random.randint(0,len(quiz)-1)
        
        # add current card info to a quiz data list
        quiz_data = []
        quiz_data.append((quiz[q_id][1], quiz[q_id][2], quiz[q_id][0]))

        # putting the answers in a random order so the correct answer doesnt always come up in the first box
        ans1 = (quiz[q_id][2], quiz[q_id][0])
        ans2 = (quiz[random1][2], quiz[random1][0])
        ans3 = (quiz[random2][2], quiz[random2][0])
        ans4 = (quiz[random3][2], quiz[random3][0])
        rand1 = random.randint(0,3)
        rand2 = random.randint(0,3)
        rand3 = random.randint(0,3)
        rand4 = random.randint(0,3)
        while rand1 == rand2 or rand1 == rand3 or rand1 == rand4 or rand2 == rand3 or rand2 == rand4 or rand3 == rand4:
            rand1 = random.randint(0,3)
            rand2 = random.randint(0,3)
            rand3 = random.randint(0,3)
            rand4 = random.randint(0,3)

        # puts answers in random order in list
        answers = [None] * 4
        answers[rand1] = ans1
        answers[rand2] = ans2
        answers[rand3] = ans3
        answers[rand4] = ans4

        # get just the question (front card)
        current_question = quiz_data[0]

        if 'current_q' not in session:
            current_question = quiz_data[0]
        session['current_q'] = quiz_data[0]
    
        return render_template('doquiz.html', quiz=quiz, current_question=current_question, answers=answers, name=session['name'])
    
    # if the deck isnt big enough to make a quiz
    elif len(quiz) < 4 and len(quiz) > 0:
        message = 'This deck is too small to make a quiz! Add some more cards so you can get started...'
        return render_template('no_quiz.html', message=message, name=session['name'])
    
    # if the deck is empty a quiz cannot be made
    elif len(quiz) == 0:
        message = 'This deck is empty! Add some cards so you can complete a quiz...'
        return render_template('no_quiz.html', message=message, name=session['name'])
    

@quiz_bp.route('/answer', methods=['GET', 'POST'])
def answers():
    # set score to 0 if at start of quiz
    if 'score' not in session or session['q_id'] == 0:
        session['score'] = 0
    score = session['score']

    # get answer from form
    ans = request.form.get('answer')
    session['current_q'] = session.get('current_q', 0)
    current = session['current_q']
    
    # if answer equals the back card of the current question then its correct
    if int(ans) == int(current[2]):
        message = 'Well Done! You got it right!'
        score += 1
    else:
        correct = str(current[1])
        message = 'Incorrect. The correct answer was: '+correct
    session['score'] = score
    return render_template('answer_screen.html', message=message, name=session['name'])

@quiz_bp.route('/nextquiz', methods=['GET', 'POST'])
def nextquiz():
    # get info from form and sessions
    next = str(request.form['next'])
    session['q_id'] = session.get('q_id', 0)

    session['user_ID'] = session.get('user_ID', 0)
    user_ID = session['user_ID']

    session['deck'] = session.get('deck', 0)
    deck_id = session['deck']
    
    # check whether this deck is a homework
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT homework_ID, deck_ID FROM homework WHERE user_ID = ?', (user_ID,))
    homeworks = cursor.fetchall()
    conn.close()

    if len(homeworks) == 0:
        homework = False
        
    for i in range(len(homeworks)):
        if str(homeworks[i][1]) == str(deck_id):
            homework = True
        else:
            homework = False

    if next == 'next':
        # if not at end of quiz, increment q_id
        session['quiz_length'] = session.get('quiz_length', 0)
        if session['q_id'] < session['quiz_length'] - 1:
            session['q_id'] += 1
        else:
            # if at end of quiz, generate score as percentage and add to database
            session['score'] = session.get('score', 0)
            session['deck'] = session.get('deck', 0)
            deck_ID = session['deck']
            percent = session['score']/session['quiz_length'] * 100
            quiz_entry = Quiz(percent, deck_ID, 'data.db')
            quiz_entry.AddScore(user_ID)
            message = 'You finished the quiz! Your final score is: '+str(session['score'])+'/'+str(session['quiz_length'])
            if homework == True:
                completed = 1
                conn = sqlite3.connect('data.db')
                cursor = conn.cursor()
                cursor.execute('UPDATE homework SET completed = ? WHERE deck_id = ? AND user_ID = ?', (completed, deck_id, user_ID))
                conn.commit()
                conn.close()
            return render_template('quiz_end.html', message=message, name=session['name'])
    return redirect(url_for('quiz.doquiz'))

@quiz_bp.route('/backtoquizzes', methods=['POST', 'GET'])    
def back_to_quizzes():
    return redirect(url_for('quiz.quiz'))

@quiz_bp.route('/statsbutton', methods=['POST', 'GET'])
def stats_button():
    return redirect(url_for('quiz.quiz_stats'))

@quiz_bp.route('/quizstats', methods=['POST', 'GET'])
def quiz_stats():
    session['deck'] = session.get('deck', 0)
    deck_ID = session['deck']
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT MAX(score)
        FROM quiz
        WHERE deck_ID = ?''', (deck_ID,))
    highscore_tuple = cursor.fetchall()
    highscore = highscore_tuple[0][0]
    if highscore == None:
        message = "You haven't completed this quiz yet so there are no stats to see."
        return render_template('nostats.html', message=message, name=session['name'])

    cursor.execute('''
        SELECT COUNT(quizdata_ID)
        FROM quiz
        WHERE deck_ID = ?''', (deck_ID,))
    count = cursor.fetchall()[0][0]
    conn.close()

    return render_template('quizstats.html', highscore=highscore, count=count, name=session['name'])

@quiz_bp.route('/chart')
def chart():
    session['deck'] = session.get('deck', 0)
    deck_ID = session['deck']
    img = create_chart(deck_ID)
    return Response(img, mimetype='image/png')

@quiz_bp.route('/barchart')
def barchart():
    session['deck'] = session.get('deck', 0)
    deck_ID = session['deck']
    img = create_barchart(deck_ID)
    return Response(img, mimetype='image/png')

@quiz_bp.route('/homework', methods=['POST', 'GET'])
def homework():
    # get id of current student logged in
    session['user_ID'] = session.get('user_ID', 0)
    user_ID = session['user_ID']

    # find which of this student's classes have set homework from the homework table
    completed = 0
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT hw.deck_ID, d.deckName
        FROM homework hw
        INNER JOIN decks d ON d.deck_ID = hw.deck_ID
        WHERE hw.user_ID = ? AND hw.completed = ?''', (user_ID, completed))
    homework_decks = cursor.fetchall()

    # checks if list is empty
    if not homework_decks:
        message = 'You have no homework today!'
        return render_template('no_homework.html', message=message, name=session['name'])
    else:
        decks = homework_decks
        return render_template('homework.html', decks=decks, name=session['name'])
  
@quiz_bp.route('/homeworkprogress', methods=['POST', 'GET'])
def homeworkprogress():

    session['user_ID'] = session.get('user_ID', 0)
    user_ID = session['user_ID']

    # list of set decks
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
                   SELECT decks.deck_ID, decks.deckName, classes.classname 
                   FROM decks 
                   INNER JOIN teachers ON decks.user_ID = teachers.user_ID
                   INNER JOIN classes ON teachers.teacher_ID = classes.teacher_ID
                   WHERE decks.user_ID = ?''', (user_ID,))
    decks = cursor.fetchall()

    return render_template('homework_progress.html', decks = decks, name=session['name'])

@quiz_bp.route('/homeworkdeck', methods=['GET', 'POST'])
def homeworkdeck():
    deck_ID = int(request.form.get('deck_id'))

    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT deckName FROM decks WHERE deck_ID = ?', (deck_ID,))
    deckname = cursor.fetchone()[0]
    cursor.execute('''
        SELECT hw.user_ID, users.name, hw.deck_ID, COALESCE(q.score, NULL) AS score
        FROM homework hw
        LEFT JOIN quiz q ON q.deck_ID = hw.deck_ID AND q.user_ID = hw.user_ID
        LEFT JOIN users ON hw.user_ID = users.user_ID
        WHERE hw.deck_ID = ?''', (deck_ID,))

    stats = cursor.fetchall() # coalesce(q.score, NULL) will return NULL if q.score is NUll (which python will convert to NONE)
    scores = []
    for i in range(len(stats)):
        if stats[i][3] != None:
            stat = str(stats[i][3]) + '%'
            scores.append((stats[i][1],stat))
        else:
            scores.append((stats[i][1],'Incomplete'))
    return render_template('homework_stats.html', deckname=deckname, scores=scores, name=session['name'])
