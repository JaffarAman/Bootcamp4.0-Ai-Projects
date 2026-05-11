from config import notifications_col

pipeline = [
    {
        "$group": {
            "_id": {
                "studentId": "$studentId",
                "assignmentId": "$assignmentId",
                "type": "$type"
            },
            "ids": {"$push": "$_id"},
            "count": {"$sum": 1}
        }
    },
    {
        "$match": {"count": {"$gt": 1}}
    }
]

duplicates = list(notifications_col.aggregate(pipeline))

for doc in duplicates:
    ids = doc["ids"]
    for _id in ids[1:]:  # keep first, delete rest
        notifications_col.delete_one({"_id": _id})

print("✅ Duplicates cleaned")