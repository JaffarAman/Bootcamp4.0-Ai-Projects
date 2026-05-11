import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MONGO_DB_URI = os.getenv("MONGO_DB_URI")