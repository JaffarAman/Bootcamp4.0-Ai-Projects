from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# ✅ Correct collections
users_col = db["users"]
domains_col = db["domains"]
bootcamps_col = db["bootcamps"]
assignments_col = db["assignments"]