from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib
from database import init_db, create_user, get_user_by_username
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Initialize database
def initialize_database():
    init_db()

# Hash password (in real apps, use proper hashing like bcrypt)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def home():
    if 'username' in session:
        return f'Hello {session["username"]}! <a href="/logout">Logout</a>'
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if get_user_by_username(username):
            flash('Username already exists!')
            return render_template('register.html')
        
        hashed_password = hash_password(password)
        if create_user(username, email, hashed_password):
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        else:
            flash('Registration failed!')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = get_user_by_username(username)
        if user and user['password'] == hash_password(password):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials!')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)