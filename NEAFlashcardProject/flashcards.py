import sqlite3
import datetime

class Flashcard():
    def __init__(self, front, back, db):
        self.front = front
        self.back = back
        self.db = db

    def AddCard(self, deck_ID, user_ID):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        #creating a trigger so when a card is added to the flashcards table, it's also entered into the sr_info table
        cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS add_sr_info
        AFTER INSERT ON flashcards
        FOR EACH ROW
        BEGIN
            INSERT INTO sr_info (flashcard_ID, rating, sr_interval, last_review, EF, state)
            VALUES (NEW.flashcard_ID, 0, 0, 0.0, 2.5, 0);
        END;
        ''')
        cursor.execute('''
        INSERT INTO flashcards (user_ID, deck_ID, frontCard, backCard) VALUES (?,?,?,?)''', (user_ID, deck_ID, self.front, self.back))

        conn.commit()
        cursor.close()
        conn.close()

    def EditCard(self, newFront, newBack, id):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE flashcards 
            SET frontCard = (?), backCard = (?) 
            WHERE flashcard_ID = (?)''',
            (newFront, newBack, id))
        conn.commit()
        cursor.close()
        conn.close()

    def DeleteCard(self, id):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        #creating another trigger so if a card is deleted from the flashcards table, it's also deleted from the sr_info table
        cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS delete_sr_info
        AFTER DELETE ON flashcards
        FOR EACH ROW
        BEGIN
            DELETE FROM sr_info WHERE flashcard_ID = OLD.flashcard_ID;
        END;''')
        cursor.execute('DELETE FROM flashcards WHERE flashcard_ID = (?)', id)
        conn.commit()
        cursor.close()
        conn.close()
    
    def MoveCard(self, deck_ID, card_ID, user_ID):
        #this method deletes the card and then creates a new one with the new deck
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM flashcards WHERE flashcard_ID = ?', (card_ID,))
        conn.commit()
        cursor.close()
        conn.close()
        self.AddCard(deck_ID, user_ID)

    def UpdateRating(self, rating, id):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE sr_info
            SET rating = (?)
            WHERE flashcard_ID = (?)''',
            (rating, id))
        conn.commit()
        cursor.close()
        conn.close()
    
    
class Deck():
    def __init__(self, deckname, db):
        self.name = deckname
        self.db = db
        self.id = id

    def AddDeck(self, user_ID):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        
        cursor.execute('INSERT INTO decks (user_ID, deckName) VALUES (?, ?)', (user_ID, self.name))
        cursor.execute('SELECT deck_ID FROM decks WHERE deckName = (?)', (self.name,))
        self.id = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
    
    def DeleteDeck(self, deck_ID):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM flashcards WHERE deck_ID = (?)', [deck_ID])
        cursor.execute('DELETE FROM decks WHERE deck_ID = (?)', [deck_ID])
        conn.commit()
        cursor.close()
        conn.close()
    

class Quiz():
    def __init__(self, percent, deck_ID, db):
        self.score = percent
        self.deck_ID = deck_ID
        self.db = db

    def AddScore(self, user_ID):
        date = datetime.datetime.now()
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO quiz (user_ID, deck_ID, score, date) VALUES (?,?,?,?)''', (user_ID, self.deck_ID, self.score, date))
        conn.commit()
        cursor.close()
        conn.close()

    def Highscore(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('''
        SELECT MAX(score)
        FROM quiz
        WHERE deck_ID = ? ''', (self.deck_ID,))
        highscore = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
        return highscore