from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import os

app = Flask(__name__)

UPLOAD_FOLDER = '/var/www/flaskapp/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Home page
@app.route('/')
def index():
    return render_template('register.html')


# Registration
@app.route('/register', methods=['POST'])
def register():
    data = (
        request.form['username'],
        request.form['password'],
        request.form['firstname'],
        request.form['lastname'],
        request.form['email'],
        request.form['address']
    )

    conn = sqlite3.connect('/var/www/flaskapp/users.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (username, password, firstname, lastname, email, address) VALUES (?, ?, ?, ?, ?, ?)",
        data
    )
    conn.commit()
    conn.close()

    return redirect(url_for('profile', username=data[0]))


# Profile display
@app.route('/profile/<username>')
def profile(username):
    conn = sqlite3.connect('/var/www/flaskapp/users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()

    return render_template('profile.html', user=user)


# Login page
@app.route('/login')
def login():
    return render_template('login.html')


# Re-login
@app.route('/relogin', methods=['POST'])
def relogin():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect('/var/www/flaskapp/users.db')
    c = conn.cursor()
    c.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )
    user = c.fetchone()
    conn.close()

    if user:
        return redirect(url_for('profile', username=username))
    else:
        return "Invalid credentials"


# Upload file
@app.route('/upload/', methods=['POST'])
def upload():
    username = request.form.get('username')
    conn = sqlite3.connect('/var/www/flaskapp/users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    if 'file' not in request.files:
        return "No file selected"

    file = request.files['file']

    if file.filename == '':
        return "No filename"

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    with open(filepath, 'r') as f:
        word_count = len(f.read().split())

    return render_template(
        'profile.html',
        user=user,
        word_count=word_count,
        filename=file.filename
    )


# Download file
@app.route('/download/<filename>')
def download(filename):
    return send_file(
        os.path.join(app.config['UPLOAD_FOLDER'], filename),
        as_attachment=True
    )

