import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

print("Teacher: ", db["users"].find_one({"role": "teacher"}))
print("Bootcamp: ", db["bootcamp"].find_one())
print("Domain: ", db["domains"].find_one())
