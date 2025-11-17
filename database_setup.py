# database_setup.py
import psycopg2
from config import DATABASE_CONFIG

def setup_database():
    """Connects to PostgreSQL and creates/updates tables."""
    conn = None
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()

        # --- jobs table ---
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            jobId SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            company TEXT,
            location TEXT,
            description TEXT,
            apply_link TEXT UNIQUE NOT NULL
        );
        ''')
        print("Table 'jobs' is ready.")

        # --- users table ---
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
        ''')
        print("Table 'users' is ready.")
        
        # --- NEW: Add 'skills' column to users table ---
        # We use 'ADD COLUMN IF NOT EXISTS' so this is safe to run
        # even if the column already exists.
        # TEXT[] is a PostgreSQL-specific type for an array of strings.
        try:
            cursor.execute('''
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS skills TEXT[];
            ''')
            print("Column 'skills' in 'users' table is ready.")
        except psycopg2.Error as e:
            print(f"Error adding 'skills' column: {e}")
            conn.rollback() # Rollback the transaction on error
        
        # --- NEW: Add 'email_alerts_enabled' column to users table ---
        try:
            cursor.execute('''
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS email_alerts_enabled BOOLEAN DEFAULT FALSE;
            ''')
            print("Column 'email_alerts_enabled' in 'users' table is ready.")
        except psycopg2.Error as e:
            print(f"Error adding 'email_alerts_enabled' column: {e}")
            conn.rollback()
        
        # --- NEW: Add 'last_email_check' column to users table ---
        try:
            cursor.execute('''
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS last_email_check TIMESTAMP;
            ''')
            print("Column 'last_email_check' in 'users' table is ready.")
        except psycopg2.Error as e:
            print(f"Error adding 'last_email_check' column: {e}")
            conn.rollback()
        
        # --- NEW: Add email configuration columns to users table ---
        try:
            cursor.execute('''
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS email_smtp_server TEXT,
                ADD COLUMN IF NOT EXISTS email_smtp_port INTEGER,
                ADD COLUMN IF NOT EXISTS email_username TEXT,
                ADD COLUMN IF NOT EXISTS email_password TEXT;
            ''')
            print("Email configuration columns in 'users' table are ready.")
        except psycopg2.Error as e:
            print(f"Error adding email configuration columns: {e}")
            conn.rollback()
        
        # --- NEW: Add 'preferred_location' column to users table ---
        try:
            cursor.execute('''
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS preferred_location TEXT;
            ''')
            print("Column 'preferred_location' in 'users' table is ready.")
        except psycopg2.Error as e:
            print(f"Error adding 'preferred_location' column: {e}")
            conn.rollback()


        conn.commit()
        cursor.close()
        print("Database and tables created/updated successfully in PostgreSQL.")

    except psycopg2.OperationalError as e:
        print(f"Could not connect to the database: {e}")
        print("Please ensure PostgreSQL is running and the configuration in 'config.py' is correct.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    setup_database()

