from flask import Blueprint, session, render_template, request, redirect, url_for
from flashcards import Flashcard, Deck
from priority_queue import Queue
from users import Student
from sr_algorithm import SR
import sqlite3
import time

study_bp = Blueprint('study', __name__)

@study_bp.route('/', methods=['POST', 'GET'])
def studycards():
    session['user_ID'] = session.get('user_ID', 0)
    user_ID = session['user_ID']

    # get student's name
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM users WHERE user_ID = ?', (user_ID,))
    name = cursor.fetchone()[0]
    session['name'] = name

    # initialise session for index
    if 'index' not in session:
        session['index'] = 0
    index = session['index']

    session['quickstudy'] = False

    # initialise session for front/back of card
    if 'side' not in session:
        session['side'] = 0 # 0 is front of card - 1 is back
    side = session['side']

    # connect and fetch card info from database
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT flashcards.flashcard_ID, flashcards.frontCard, flashcards.backCard, sr_info.sr_interval, sr_info.last_review
        FROM flashcards
        INNER JOIN sr_info ON flashcards.flashcard_ID = sr_info.flashcard_ID
        WHERE user_ID = ? ''', (user_ID,))
    flashcards = cursor.fetchall()
    conn.close()

    # make list of cards due today 
    next_midnight = (int(time.time()//86400)) * 86400 + 86400
    due_cards = []
    for i in range (len(flashcards)):
        time_due = flashcards[i][4] + flashcards[i][3]
        if time_due < next_midnight:
            due_cards.append(flashcards[i])
        elif flashcards[i][4] == 0.0 or flashcards[i][3] == 0.0:
            due_cards.append(flashcards[i])

    # push everything onto priority queue
    q = Queue()
    if len(due_cards) > 0: 
        for i in range(len(due_cards)):
            time_due = due_cards[i][4] + due_cards[i][3]
            q.push(due_cards[i][0], time_due)
        
        if 'next' not in session:
            session['next'] = False

        # find the index of the card in due_cards
        if len(due_cards) >= 1:
            id = q.pop()[0]
            for i in range(len(due_cards)):
                if due_cards[i][0] == id:
                    card_index = i
                    break
                else:
                    card_index = 0
    
            # making a list of front and back cards and ids (from due_cards)
            fronts = [due_cards[i][1] for i in range(len(due_cards))]
            backs = [due_cards[i][2] for i in range(len(due_cards))]
            ids = [due_cards[i][0] for i in range(len(due_cards))]

            
            # check if we've reached the end of the flashcards list
            if index >= len(fronts):
                # reset index to 0
                session['index'] = 0
                index = 0
            
            # show the card at the current index
            if len(due_cards) > 0:
                card = [fronts[card_index], backs[card_index], ids[card_index]]
            else: 
                card = [0,0,0]

            # make card a session so can be accessed in rating method
            if 'card' not in session:
                session['card'] = card
            else:
                session['card'] = card

            return render_template('study.html', flashcards=flashcards, card=card, side=side, name=name)
    else:
        message = 'There are no cards to study today!'
        return render_template('no_due_cards.html', message=message, name=name)

@study_bp.route('/quickstudy', methods=['POST', 'GET'])
def quickstudy():
    session['user_ID'] = session.get('user_ID', 0)
    user_ID = session['user_ID']

    # initialise the index if it doesnt already exist in the session
    if 'index' not in session:
        session['index'] = 0
    index = session['index']

    # initialise session for front/back of card
    if 'side' not in session:
        session['side'] = 0 # 0 is front of card - 1 is back
    side = session['side']

    session['quickstudy'] = True

    # connect and fetch card info from database
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT frontCard, backCard, flashcard_ID
        FROM flashcards
        WHERE user_ID = ? ''', (user_ID,))
    flashcards = cursor.fetchall()
    print(flashcards)
    conn.close()
    
    # reset the quick study mode once every card in list has been studied
    if session['index'] >= len(flashcards):
        session['index'] = 0  
        message = 'You have finished this quick study! Press the button to study again.'
        session['quickstudy'] = False
        return render_template('no_due_cards.html', message=message, name=session['name'])

    else:
        card = flashcards[index]
        return render_template('quickstudy.html', flashcards=flashcards, card=card, side=side, name=session['name'])
    

@study_bp.route('/nextcard', methods=['POST'])
def nextcard():
    # increment index and save back to session
    session['index'] = session.get('index', 0) + 1
    # sets session to 0 so the front of the next card is shown instead of back
    session['side'] = 0
    return redirect(url_for('study.quickstudy'))

@study_bp.route('/flipcard', methods=['GET', 'POST'])
def flipcard():
    # switch between setting side to front or back (0 or 1)
    session['side'] = session.get('side', 0)
    if session['side'] == 0:
        session['side'] = 1
    else:
        session['side'] = 0

    session['quickstudy'] = session.get('quickstudy', 0)
    if session['quickstudy'] == True:
        return redirect(url_for('study.quickstudy'))
    return redirect(url_for('study.studycards'))

@study_bp.route('/rating', methods=['GET', 'POST'])
def rating():
    session['user_ID'] = session.get('user_ID', 0)
    user_ID = session['user_ID']

    # get student_ID
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT student_ID from students WHERE user_ID = ?', (user_ID,))
    student_ID = cursor.fetchone()[0]

    # update study streak
    student = Student('data.db')
    student.updateStudyStreak(student_ID)

    # get rating from form
    rating = request.form['rating']
    session['card'] = session.get('card', 0)
    id = session['card'][2]

    # use Flashcard class to update the rating
    card = Flashcard(session['card'][0], session['card'][1], 'data.db')
    card.UpdateRating(rating, id)
    
    # get info from database so SR class can be used and algorithm applied to class
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT sr_interval, rating, last_review, EF, state FROM sr_info WHERE flashcard_ID = ?", (id,))
    info = cursor.fetchall()[0]
    db = sqlite3.connect('data.db')
    card_sr = SR(id, info[0], info[1], info[2], info[3], info[4], db)
    card_sr.SR_algorithm()
    conn.close()

    #this moves on to next card when rating is pressed
    session['next'] = True 

    # sets session to 0 so the front of the next card is shown instead of back
    session['side'] = 0
    return redirect(url_for('study.studycards'))

@study_bp.route('/manageflashcards', methods = ['GET', 'POST'])
def manageflashcards():
    session['user_ID'] = session.get('user_ID', 0)
    user_ID = session['user_ID']
    session['name'] = session.get('name', 0)
    name = session['name']
    # fetch info needed for page from database
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT flashcard_ID, frontCard, backCard FROM flashcards WHERE user_ID = ?', (user_ID,))
    flashcards = cursor.fetchall()
    cursor.execute('SELECT deck_ID, deckName FROM decks WHERE user_ID = ?', (user_ID,))
    decks = cursor.fetchall()
    cursor.execute('SELECT is_student FROM users WHERE user_ID = ?', (user_ID,))
    is_student = cursor.fetchone()[0]
    conn.close()
    if is_student == 0:
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT teacher_ID FROM teachers WHERE user_ID = ?', (user_ID,))
        teacher_ID = cursor.fetchall()[0][0]
        cursor.execute('SELECT class_ID, classname FROM classes WHERE teacher_ID = ?', (teacher_ID,))
        classes = cursor.fetchall()
        return render_template('teacher_make_quiz.html', flashcards=flashcards, decks=decks, classes=classes, name=session['name'])
    else:
        return render_template('manage_cards.html', flashcards=flashcards, decks=decks, name=name)

@study_bp.route('/addflashcards', methods=['GET', 'POST'])
def addflashcards():
    # add the new card with data inputted in form to database
    if request.method == 'POST':
        front = request.form['front']
        back = request.form['back']
        deck_ID = request.form['select_deck']
        session['user_ID'] = session.get('user_ID', 0)
        user_ID = session['user_ID']
        newCard = Flashcard(front, back, 'data.db')
        newCard.AddCard(deck_ID, user_ID)
    return redirect(url_for('study.manageflashcards'))

@study_bp.route('/deleteflashcards', methods = ['POST', 'GET'])
def deleteflashcards():
    # get list of the ids of the checked cards
    checked_cards = request.form.getlist("check")
    for i in range(0, len(checked_cards)):
        checked_cards[i] = int(checked_cards[i])
    
    # get info from database
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT flashcard_ID, frontCard, backCard FROM flashcards')
    flashcards = cursor.fetchall()
    cursor.close()
    conn.close()

    # need a seperate list just of all ids
    ids = []
    for i in range(len(flashcards)):
        ids.append(flashcards[i][0]) #list of just all ids
    i = 0

    # check to see if the id of the checked card is in the database then delete from db
    for card in checked_cards:
        if card in ids:
            card_to_delete = Flashcard(flashcards[i][1], flashcards[i][2], 'data.db')
            card_to_delete.DeleteCard([card])
            i += 1
    return redirect(url_for('study.manageflashcards'))

@study_bp.route('/editflashcards', methods=['GET', 'POST'])
def editflashcards():
    id = request.form.get("flashcard_id")
    newfront = request.form['front']
    newback = request.form['back']
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT frontCard, backCard FROM flashcards WHERE flashcard_ID = (?)", (id,))
    card = cursor.fetchall()
    card_to_update = Flashcard(card[0][0], card[0][1], 'data.db')
    card_to_update.EditCard(newfront, newback, id)
    return redirect(url_for('study.manageflashcards'))

@study_bp.route('/adddeck', methods=['GET', 'POST'])
def adddeck():
    # get info from form then add deck to database
    if request.method == 'POST':
        deckname = str(request.form['deck'])
        session['user_ID'] = session.get('user_ID', 0)
        user_ID = session['user_ID']
        newDeck = Deck(deckname, 'data.db')
        newDeck.AddDeck(user_ID)
    return redirect(url_for('study.manageflashcards'))

@study_bp.route('/deletedeck', methods=['GET','POST'])
def deletedeck():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    # get info from form and database so class can be created then deck is deleted
    if request.method == 'POST':
        deck_ID = request.form['delete_deck'] # id of selected deck
        cursor.execute('SELECT deckName FROM decks WHERE deck_ID = (?)', [deck_ID])
        deckname = cursor.fetchall() #gets deckname so an object can be made
        newDeck = Deck(deckname, 'data.db')
        newDeck.DeleteDeck(deck_ID)
    conn.close()
    return redirect(url_for('study.manageflashcards'))

@study_bp.route('/moveflashcards', methods=['GET', 'POST'])
def moveflashcards():
    if request.method == 'POST':
        # retrieve ID of card and ID of deck to move the card to
        deck_ID = request.form['move_deck']
        card_ID = request.form['move_card']

        session['user_ID'] = session.get('user_ID', 0)
        user_ID = session['user_ID']
        
        # get the front and back of card to make flashcard object
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT frontCard, backCard FROM flashcards WHERE flashcard_ID = ?', (card_ID,))
        card = cursor.fetchone()
        conn.close()
        front = card[0]
        back = card[1]

        # make flashcard object and move card to new deck
        move_card = Flashcard(front, back,'data.db')
        move_card.MoveCard(deck_ID, card_ID, user_ID)
        
    return redirect(url_for('study.manageflashcards'))


@study_bp.route('/setdeck', methods=['POST', 'GET'])
def setdeck():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    # creates list of user_IDs and names of students in selected class
    class_ID = request.form['class']
    cursor.execute('''
        SELECT u.user_ID, u.name
        FROM class_members cm
        INNER JOIN users u ON cm.user_ID = u.user_ID
        WHERE cm.class_ID = ?''', (class_ID,))
    class_members = cursor.fetchall()

    # the deck that the teacher wants to set
    deck_ID = request.form['deck']

    # create entry in homework table for each student in list
    for student in class_members:
        cursor.execute('INSERT INTO homework (class_ID, deck_ID, user_ID) VALUES(?,?,?)', (class_ID, deck_ID, student[0]))
        conn.commit()

    conn.close()
    return redirect(url_for('study.manageflashcards'))
