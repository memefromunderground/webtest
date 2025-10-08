# init_db.py
import os
import mysql.connector
from urllib.parse import urlparse

def init_database():
    """Connects to the database and creates the users table."""
    conn = None
    try:
        # Use Railway's internal variable for deployment
        db_url = os.getenv('MYSQL_URL')
        if not db_url:
            # Fallback to local .env variable for local testing
            db_url = os.getenv('DATABASE_URL')
            if not db_url:
                raise ValueError("No database URL found in environment variables.")

        url = urlparse(db_url)
        conn = mysql.connector.connect(
            host=url.hostname,
            user=url.username,
            password=url.password,
            database=url.path[1:],
            port=url.port
        )
        cursor = conn.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_table_query)
        conn.commit()
        print("✅ Database table 'users' created or verified successfully.")

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    init_database()
