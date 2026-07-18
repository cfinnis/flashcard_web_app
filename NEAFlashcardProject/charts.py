from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sqlite3
from datetime import datetime

def create_barchart(deck_ID):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT strftime('%Y-%W', date) AS week, AVG(score) AS avg_score
    FROM quiz
    WHERE deck_ID = ?''', (deck_ID,))
    data = cursor.fetchall()
    conn.close()

    x_data = [row[0].split('-')[1] for row in data]
    y_data = [row[1] for row in data]

    plt.figure(figsize=(4, 3))
    plt.bar(x_data, y_data, label='Weekly Average Scores')

    plt.xlabel('Week')
    plt.ylabel('Average Score (%)')
    plt.legend()
    
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf.getvalue()  # Returns the binary content of the image


def create_chart(deck_ID):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT date, score 
    FROM quiz
    WHERE deck_ID = ?''', (deck_ID,))
    data = cursor.fetchall()
    conn.close()

    # changes i made to fix the dates, however made the graph presentation not work
    # x_data = [datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f') for row in data]
    # x_data = [dt.date() for dt in x_data]

    x_data = [row[0] for row in data]
    y_data = [row[1] for row in data]
    plt.figure(figsize=(4, 3))
    plt.plot(x_data, y_data, label='Progress Line')

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))  # Show month and day
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))    # Set interval between ticks

    plt.xlabel('Date')
    plt.ylabel('Score (%)')
    plt.legend()
    
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf.getvalue()  # Returns the binary content of the image
