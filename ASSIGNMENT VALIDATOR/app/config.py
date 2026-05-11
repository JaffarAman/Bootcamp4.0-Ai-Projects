from pymongo import MongoClient
import os
from dotenv import load_dotenv

MONGO_URL = "mongodb+srv://user:uS3er2060@bootcamptracker.roknckd.mongodb.net/"
client = MongoClient(MONGO_URL)

db = client["test"]

users_col = db["users"]
assignments_col = db["assignments"]
submitted_col = db["student_assignments"]
notifications_col = db["notifications"]