import os
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector.constants 
import ClientFlag

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", "5432")),
        client_flags=[ClientFlag.SSL],
        ssl_ca=os.getenv("DB_SSL_CA")  # path to CA cert if your provider gives one
    )

@app.route('/', methods=['GET', 'HEAD'])
def index():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM events ORDER BY date ASC")
    events = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('index.html', events=events)

@app.route('/add', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO events (title, date, description) VALUES (%s, %s, %s)",
            (request.form['title'], request.form['date'], request.form['description'])
        )
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('index'))
    return render_template('add_event.html')

@app.route('/register/<int:event_id>', methods=['GET', 'POST'])
def register_event(event_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM events WHERE id = %s", (event_id,))
    event = cursor.fetchone()

    if request.method == 'POST':
        cursor.execute(
            "INSERT INTO registrations (event_id, name, email) VALUES (%s, %s, %s)",
            (event_id, request.form['name'], request.form['email'])
        )
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('index'))

    cursor.close()
    db.close()
    return render_template('register.html', event=event)

@app.route('/registrations')
def view_registrations():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.name, r.email, e.title AS event_title
        FROM registrations r
        JOIN events e ON r.event_id = e.id
    """)
    registrations = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('registrations.html', registrations=registrations)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

