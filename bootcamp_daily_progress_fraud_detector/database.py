from pymongo import MongoClient

from config import MONGODB_URL

client = MongoClient(MONGODB_URL)

db = client["test"]

progress = db["progresses"]
fraud_updates = db["fraud_updates"]
users = db["users"]