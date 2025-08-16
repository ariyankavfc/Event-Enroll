import os
from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import psycopg2.extras

app = Flask(__name__)

def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dbname=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", "5432")),
        sslmode="require"   # PostgreSQL on Render requires SSL
    )

@app.route('/init-db')
def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            date DATE NOT NULL,
            description TEXT
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id SERIAL PRIMARY KEY,
            event_id INT REFERENCES events(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    return "✅ Database initialized!"

@app.route('/', methods=['GET', 'HEAD'])
def index():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM events ORDER BY date ASC")
    events = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', events=events)

@app.route('/add', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO events (title, date, description) VALUES (%s, %s, %s)",
            (request.form['title'], request.form['date'], request.form['description'])
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_event.html')

@app.route('/register/<int:event_id>', methods=['GET', 'POST'])
def register_event(event_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM events WHERE id = %s", (event_id,))
    event = cur.fetchone()

    if request.method == 'POST':
        cur.execute(
            "INSERT INTO registrations (event_id, name, email) VALUES (%s, %s, %s)",
            (event_id, request.form['name'], request.form['email'])
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))

    cur.close()
    conn.close()
    return render_template('register.html', event=event)

@app.route('/registrations')
def view_registrations():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT r.name, r.email, e.title AS event_title
        FROM registrations r
        JOIN events e ON r.event_id = e.id
    """)
    registrations = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('registrations.html', registrations=registrations)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
