# Flashcard Learning Web Application

A full-stack flashcard learning application built in Python using Flask
and SQLite as my A-level Computer Science project.

The application combines active recall with a custom spaced-repetition
scheduler and supports separate student and teacher workflows.

<img width="1266" height="772" alt="image" src="https://github.com/user-attachments/assets/b6c08566-bbe1-4e35-a1dd-143c20e68afa" />
<img width="1298" height="698" alt="image" src="https://github.com/user-attachments/assets/04cab126-7c82-427b-8303-191fbfdc5b15" />


## Key Features

- Custom spaced-repetition scheduling based on card difficulty and review history
- Student and teacher account types with authentication
- Flashcard and deck creation, editing and deletion
- Quiz generation with progress statistics
- Study streak tracking
- Teacher-created classes and homework assignments
- Student homework completion and teacher progress monitoring

## Technologies

**Python · Flask · SQLite · HTML · CSS · Jinja · bcrypt · Matplotlib**

### Spaced Repetition Algorithm
I implemented a custom spaced repetition algorithm inspired by Anki and SuperMemo 2 which I researched in order to reach a method that would give the best results for my end users.

This works by cards moving between learning and review states based on user ratings.
New cards progress through short learning intervals before graduating
to review, where future intervals are calculated using the card's
previous interval and ease factor.

The scheduler also accounts for overdue reviews and uses a priority
queue to present cards according to when they are due.

### Application Architecture

This project is built using Flask and separates its functionality
across different Python modules and Flask Blueprints.

The main application handles authentication and account management,
while different components manage student study functionality, teacher
functionality and quizzes. Jinja templates are used to render the
HTML interface, with SQLite providing persistent storage.

The application also uses object-oriented programming to represent
the main entities in the system. `Student` and `Teacher` inherit from
a common `User` class, while separate classes handle flashcards,
decks, quizzes, spaced repetition and the priority queue.

<img width="1544" height="1066" alt="image" src="https://github.com/user-attachments/assets/2a904161-606d-44e4-bd10-2769c2f343dd" />


### Database Design

The application uses a relational SQLite database to store users,
students, teachers, decks, flashcards, spaced-repetition state,
classes, homework and quiz results.

I used foreign keys and linking tables to model relationships such as
students belonging to multiple classes. Cascading deletes maintain
referential integrity when parent records are removed.

<img width="1380" height="632" alt="image" src="https://github.com/user-attachments/assets/efac2c17-8fa9-4e29-a94a-acb8097135bd" />


### Authentication

User authentication is implemented using Flask sessions and `bcrypt`.

Passwords are hashed with `bcrypt` before being stored in the database
and are verified against the stored hash during login. Once authenticated,
the user's ID is stored in a Flask session so that their account can be
accessed across different routes.

Student and teacher accounts are stored separately while sharing common
user information through the underlying user model.

The Flask secret key is supplied through an environment variable rather
than being stored in the source code.

## Testing

The application was manually tested against each of the functional
requirements defined during development.

Testing also identified limitations in the application, including an
issue with date aggregation in the quiz-progress visualisation, which
is documented under Future Improvements

## Limitations & Future Improvements

This project was completed under A-level coursework time constraints.
Areas I would improve in a future version include:

- improving responsive layouts for large numbers of cards/classes
- strengthening input validation
- correcting date aggregation in the quiz-progress visualisation
- moving from a local SQLite deployment to a hosted database/application

## Running Locally

1. Clone the repository:

```bash
git clone <repository-url>
cd <repository-folder>
```

2. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install the required dependencies:

```bash
python -m pip install -r requirements.txt
```

Set a Flask secret key:

```bash
export SECRET_KEY="your-secret-key"
```

Run the application:

```bash
python main.py
```

The application will then be available at the local address displayed
by Flask, typically `http://127.0.0.1:5000`.

## Screenshots
<img width="626" height="756" alt="image" src="https://github.com/user-attachments/assets/93d6412e-4160-4528-a46b-a2b408b45e1d" />
<img width="1470" height="746" alt="image" src="https://github.com/user-attachments/assets/aba70ad8-6181-4ab4-8433-217d971c0fcf" />
<img width="786" height="602" alt="image" src="https://github.com/user-attachments/assets/6b66e2c5-bc9f-4f6b-8367-126f5680bc1a" />
<img width="1260" height="618" alt="image" src="https://github.com/user-attachments/assets/175bfa5e-597c-4682-a47c-4e5c949bf9d6" />



