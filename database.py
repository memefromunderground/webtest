import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE'),
        port=os.getenv('MYSQL_PORT', 3306)
    )

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()

def create_user(username, email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO users (username, email, password) VALUES (%s, %s, %s)',
            (username, email, password)
        )
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_user_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    return user