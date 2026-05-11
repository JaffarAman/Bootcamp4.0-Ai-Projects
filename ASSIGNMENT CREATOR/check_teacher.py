import os
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

teacher_id = "69c63b9436adc54470ff7709"
teacher = db["users"].find_one({"_id": ObjectId(teacher_id)})
print(f"Teacher {teacher_id}: {teacher}")

# If not found, find any teacher
if not teacher:
    any_teacher = db["users"].find_one({"role": "teacher"})
    if any_teacher:
        print(f"Found alternative teacher ID: {any_teacher['_id']}")
