import os
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash
from urllib.parse import urlparse

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

def get_db_connection():
    # Prioritize Railway's internal service discovery variables for deployment
    if os.getenv('MYSQL_URL'):
        url = urlparse(os.getenv('MYSQL_URL'))
        host = url.hostname
        user = url.username
        password = url.password
        database = url.path[1:]
        port = url.port
    # Fallback to the DATABASE_URL for local development
    else:
        url = urlparse(os.getenv('DATABASE_URL'))
        host = url.hostname
        user = url.username
        password = url.password
        database = url.path[1:]
        port = url.port

    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port
    )

def init_db():
    # ... (rest of your init_db function remains the same)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database initialization error: {e}")

@app.route('/')
def index():
    # ... (rest of your code)
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # ... (rest of your code)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash('Please fill all fields', 'error')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', 
                         (username, hashed_password))
            conn.commit()
            cursor.close()
            conn.close()
            print(f"✅ User {username} registered successfully!")
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError as e:
            print(f"❌ IntegrityError: {e}")
            flash('Username already exists', 'error')
        except mysql.connector.Error as e:
            print(f"❌ MySQL Error: {e}")
            flash('Registration failed - Database error', 'error')
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            flash('Registration failed', 'error')
        
    return render_template('register.html')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    # ... (rest of your code)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')
        except Exception as e:
            flash('Login failed', 'error')
            print(f"Error: {e}")
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # ... (rest of your code)
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/logout')
def logout():
    # ... (rest of your code)
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
