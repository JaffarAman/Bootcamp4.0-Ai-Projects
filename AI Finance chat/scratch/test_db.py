import psycopg2
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='backend/.env')
DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("DONE: PostgreSQL connection successful!")
    conn.close()
except Exception as e:
    print(f"FAILED: PostgreSQL connection failed: {e}")
