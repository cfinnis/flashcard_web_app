import time

class SR():
    def __init__(self, card_id, interval, rating, last_review, EF, state, db):
        self.card_id = card_id
        self.EF = EF
        self.interval = interval # the interval its been since last review which is updated to become the interval until next review
        self.last_review = last_review # date of last review (to the second)
        self.state = state # learning or review card (0 or 1)
        self.rating = rating
        self.db = db
        self.late = False

    def SR_algorithm(self):
        timestamp = time.time()
        # check if this is the first time studying the card
        if self.last_review == 0 and self.interval == 0:
            first_review = True
        else:
            first_review = False

        # If the card was due before the previous midnight then apply late correction
        prev_midnight = (int(time.time()//86400)) * 86400
        time_due = self.last_review + self.interval
        if first_review == False and time_due < prev_midnight:
             self.late = True
             self.lateCorrection()

        # calculate ef
        self.updateEF()
        cursor = self.db.cursor()

        #calculate next interval and update database
        self.nextInterval()
        cursor = self.db.cursor()
        cursor.execute("""
        UPDATE sr_info
        SET sr_interval = ?, last_review = ?, state = ?, EF = ?
        WHERE flashcard_id = ?
        """, (self.interval, timestamp, self.state, self.EF, self.card_id))
        self.db.commit()

    # Generates the next interval for the card based on its state and rating
    # The learning steps are 1m 10m 1d (so 60, 600 and 86400 seconds)
    # If its a learning card and the user rates it lower than before it goes back a step
    def nextInterval(self):
        self.checkState() # first checks card is in the correct state
        if self.state == 0 and self.interval == 0: 
            if self.rating >= 3:
                self.interval = 60
        elif self.state == 0 and self.interval == 60:
            if self.rating >= 3:
                self.interval = 600
            elif self.rating < 3:
                self.interval = 0
        elif self.state == 0 and self.interval == 600:
            if self.rating >= 3:
                self.interval = 86400
            elif self.rating < 3:
                self.interval = 60
        elif self.state == 0 and self.interval == 86400:
            if self.rating >= 3:
                self.state = 1 # 'graduates' to review card
                self.intervalCalc() # performs review interval calculation on card
            elif self.rating < 3:
                self.interval = 600  # goes back a step in the learning state if rates the last step less than 3
        else:
            self.intervalCalc()


    # Calculates the EF and makes sure its between 1.3 and 2.5 (to avoid cards being reviewed too frequently or infrequently)
    def updateEF(self):
        self.EF = self.EF + (0.1 - (5 - self.rating) * (0.08 + (5 - self.rating)*0.02)) # equation used to calc EF in SM2
        if self.EF < 1.3:
            self.EF = 1.3 
        if self.EF > 2.5:
            self.EF = 2.5 

    # Calculates the interval for the current card based on the EF using the equation from SM2
    def intervalCalc(self):
        self.interval = self.interval * self.EF

    # Checks that the card is in the right state given its rating
    # If a card is rated 1 at anytime it becomes a learning card again
    # If a card is rated 5 then it instantly becomes a review card (and interval set to one day)
    def checkState(self):
        if self.state == 1 and self.rating == 1:
            self.state = 0
        elif self.state == 0 and self.rating == 5:
            self.interval = 34560 # This is 86400/2.5 becuase when the interval calc is applied it will produce 86400
            self.state = 1

    # replaces the last interval with the actual amount of time that's passed since last review
    def lateCorrection(self):
        timestamp = time.time()
        self.interval = timestamp - self.last_review