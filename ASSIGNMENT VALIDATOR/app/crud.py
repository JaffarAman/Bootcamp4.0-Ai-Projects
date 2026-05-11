from app.config import users_col, assignments_col, submitted_col
from bson import ObjectId

def get_user(student_id):
    return users_col.find_one({"_id": ObjectId(student_id)})

def get_assignment(assignment_id):
    return assignments_col.find_one({"_id": ObjectId(assignment_id)})

def save_submission(student_id, assignment_id, link, content, similarity):
    submitted_col.insert_one({
        "student": ObjectId(student_id),
        "assignment": ObjectId(assignment_id),
        "link": link,
        "scraped_content": content,
        "similarity": similarity,
        "isSubmit": True
    })