from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host=os.getenv("dpg-d2g5af75r7bs73el5mmg-a"),
    user=os.getenv("eventsql_user"),
    password=os.getenv("Oj3IfFstBjoF6zME24n5ORZpLyHRmEnf"),
    database=os.getenv("eventsql"),
    port=os.getenv("5432", 3306)
)
cursor = db.cursor(dictionary=True)

@app.route('/')
def index():
    cursor.execute("SELECT * FROM events ORDER BY date ASC")
    events = cursor.fetchall()
    return render_template('index.html', events=events)

@app.route('/add', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        title = request.form['title']
        date = request.form['date']
        description = request.form['description']
        cursor.execute("INSERT INTO events (title, date, description) VALUES (%s, %s, %s)",
                       (title, date, description))
        db.commit()
        return redirect(url_for('index'))
    return render_template('add_event.html')

@app.route('/register/<int:event_id>', methods=['GET', 'POST'])
def register_event(event_id):
    cursor.execute("SELECT * FROM events WHERE id = %s", (event_id,))
    event = cursor.fetchone()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        cursor.execute("INSERT INTO registrations (event_id, name, email) VALUES (%s, %s, %s)",
                       (event_id, name, email))
        db.commit()
        return redirect(url_for('index'))
    return render_template('register.html', event=event)

@app.route('/registrations')
def view_registrations():
    cursor.execute("""
        SELECT r.name, r.email, e.title AS event_title
        FROM registrations r
        JOIN events e ON r.event_id = e.id
    """)
    registrations = cursor.fetchall()
    return render_template('registrations.html', registrations=registrations)

if __name__ == '__main__':
    app.run(debug=True)
