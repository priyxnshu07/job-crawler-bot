# database_setup.py
import psycopg2
from config import DATABASE_CONFIG

def setup_database():
    """Connects to PostgreSQL and creates the jobs table."""
    conn = None
    try:
        # Establish connection
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()

        # Create the jobs table with PostgreSQL-specific syntax
        # SERIAL is an auto-incrementing integer in PostgreSQL
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

        conn.commit()
        cursor.close()
        print("Database and table created successfully in PostgreSQL.")

    except psycopg2.OperationalError as e:
        print(f"Could not connect to the database: {e}")
        print("Please ensure PostgreSQL is running and the configuration in 'config.py' is correct.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    setup_database()

