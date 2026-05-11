import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Create Tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            type TEXT NOT NULL CHECK(type IN ('sale', 'expense')),
            amount NUMERIC(15, 2) NOT NULL CHECK(amount > 0),
            category_id INTEGER REFERENCES categories(id),
            note TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Initialize categories
        INSERT INTO categories (name) VALUES
            ('electricity'), ('rent'), ('salaries'), ('supplies'),
            ('food'), ('transport'), ('marketing'), ('other'),
            ('product_sale'), ('service_sale')
        ON CONFLICT (name) DO NOTHING;
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("[OK] PostgreSQL Database initialized.")

if __name__ == "__main__":
    init_db()
