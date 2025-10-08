import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from contextlib import contextmanager
import sys

# --- Configuration ---
app = Flask(__name__)

# Use environment variables for secure, deployable configuration
app.config['MYSQL_HOST'] = os.environ.get('DB_HOST')
app.config['MYSQL_USER'] = os.environ.get('DB_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('DB_PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('DB_NAME')
app.config['MYSQL_PORT'] = int(os.environ.get('DB_PORT', 3306))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key') # Crucial for sessions

mysql = MySQL(app)

# Helper for secure cursor usage and connection handling
@contextmanager
def get_db_cursor(commit=False):
    """Provides a transactional cursor for database operations."""
    try:
        cur = mysql.connection.cursor()
        yield cur
        if commit:
            mysql.connection.commit()
    except Exception as e:
        # Log and handle MySQL connection or query errors
        print(f"Database Error: {e}", file=sys.stderr)
        flash(f"A database error occurred: {e}. Please check the server logs.", 'danger')
        if commit:
            mysql.connection.rollback()
        raise # Re-raise to allow error handling in routes
    finally:
        if 'cur' in locals():
            cur.close()

def init_db():
    """Initializes the required 'users' table in the database."""
    print("Attempting to initialize database tables...")
    try:
        with get_db_cursor(commit=True) as cursor:
            # Create the users table if it does not exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL
                )
            """)
            print("Database table 'users' initialized successfully.")
    except Exception as e:
        print(f"FAILED to initialize database: {e}", file=sys.stderr)
        sys.exit(1) # Exit if critical setup fails

# --- Routes ---

@app.route('/')
def index():
    """Redirects authenticated users to the dashboard, otherwise to login."""
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        if not username or not password:
            flash('Please fill out all fields.', 'warning')
            return redirect(url_for('register'))

        try:
            with get_db_cursor(commit=True) as cursor:
                # Check if user already exists
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                account = cursor.fetchone()

                if account:
                    flash('Account already exists!', 'danger')
                else:
                    # Insert new user
                    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
                    flash('You have successfully registered! Please log in.', 'success')
                    return redirect(url_for('login'))

        except Exception as e:
            # Error handling is managed by the get_db_cursor context manager
            return render_template('register.html')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            with get_db_cursor() as cursor:
                # Fetch user by username
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                account = cursor.fetchone()

            if account and check_password_hash(account[2], password): # account[2] is the hashed password column
                # Create session data
                session['loggedin'] = True
                session['id'] = account[0]
                session['username'] = account[1]
                flash(f'Welcome, {session["username"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Incorrect username/password!', 'danger')
        
        except Exception as e:
            # Error handling is managed by the get_db_cursor context manager
            return render_template('login.html')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Protected route for logged-in users."""
    if 'loggedin' in session:
        return render_template('dashboard.html', username=session['username'])
    
    # User is not logged in
    flash('Please log in to access the dashboard.', 'info')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    """Logs out the user by clearing the session."""
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# --- Main Execution ---

if __name__ == '__main__':
    # Check for a specific command-line argument to initialize the DB.
    # This is a safe way to run setup commands in a deployed environment like Railway Shell.
    if len(sys.argv) > 1 and sys.argv[1] == 'init':
        init_db()
    else:
        # Standard run: 0.0.0.0 is crucial for Docker containers to listen to external traffic
        app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))
