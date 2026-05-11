from config import GROQ_API_KEY, MONGO_DB_URI
from pymongo import MongoClient

client = MongoClient(MONGO_DB_URI)

db = client["test"]

quiz_collection = db["aiquizprompts"]
ai_quiz_collection = db["aigeneratedquizzes"]

