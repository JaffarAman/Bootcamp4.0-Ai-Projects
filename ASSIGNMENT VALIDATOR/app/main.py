from fastapi import FastAPI, HTTPException
from app.models import SubmissionRequest
from app.crud import get_user, get_assignment
from app.services.validator import validate_submission
from app.config import assignments_col, submitted_col, users_col, notifications_col
from bson import ObjectId
from datetime import datetime

app = FastAPI(title="Bootcamp Smart Validator")

# 🔹 DOMAIN MAP
DOMAIN_MAP = {
    "69c538969d2f7dcce6f2df26": "AI",
    "69c538969d2f7dcce6f2df24": "Web",
    "69c2304ccfe658657f11a4fd": "UI/UX"
}

# 🔹 SERIALIZER (FIX ObjectId ERROR)
def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc

def serialize_list(docs):
    return [serialize_doc(doc) for doc in docs]


# =========================================================
# 🚀 SUBMIT ASSIGNMENT (UPDATED)
# =========================================================
@app.post("/submit")
def submit(data: SubmissionRequest):

    student_id = ObjectId(data.studentId)
    assignment_id = ObjectId(data.assignmentId)

    user = get_user(data.studentId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    assignment = get_assignment(data.assignmentId)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # ✅ 1. Duplicate submission check
    existing = submitted_col.find_one({
        "student": student_id,
        "assignment": assignment_id
    })

    if existing:
        raise HTTPException(status_code=400, detail="Assignment already submitted")

    # ✅ 2. Deadline check
    if datetime.utcnow() > assignment["deadline"]:
        raise HTTPException(status_code=400, detail="Deadline passed")

    # ✅ 3. Validation (your existing logic)
    success, message, similarity = validate_submission(
        user,
        assignment,
        str(data.link)
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    # ✅ 4. Save submission ONLY if valid
    submitted_col.insert_one({
        "student": student_id,
        "assignment": assignment_id,
        "link": str(data.link),
        "similarity": similarity,
        "isSubmit": True,
        "submittedAt": datetime.utcnow()
    })

    return {
        "success": True,
        "message": "Assignment submitted successfully",
        "similarity": similarity
    }


# =========================================================
# 🚀 STUDENT DASHBOARD (MISS + NOTIFICATIONS) 🔥
# =========================================================
@app.get("/student-dashboard/{student_id}")
def student_dashboard(student_id: str):

    try:
        student_obj_id = ObjectId(student_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid student ID")

    user = users_col.find_one({"_id": student_obj_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    current_time = datetime.utcnow()

    assignments = list(assignments_col.find({
        "domain": user["domainId"]
    }))

    missed_assignments = []

    for assignment in assignments:

        # only active assignments
        if assignment.get("status") != "Active":
            continue

        # 🔥 DEADLINE PASSED
        if assignment["deadline"] < current_time:

            submission = submitted_col.find_one({
                "student": student_obj_id,
                "assignment": assignment["_id"]
            })

            if not submission:

                # ✅ CHECK EXISTING NOTIFICATION (STRICT)
                existing_notification = notifications_col.find_one({
                    "studentId": str(student_obj_id),
                    "assignmentId": str(assignment["_id"]),
                    "type": "deadline_passed"
                })

                # ✅ CREATE ONLY ONCE
                if not existing_notification:
                    try:
                        notifications_col.insert_one({
                            "studentId": str(student_obj_id),
                            "studentName": user["name"],
                            "assignmentId": str(assignment["_id"]),
                            "assignmentName": assignment["title"],
                            "type": "deadline_passed",
                            "message": f"Assignment '{assignment['title']}' deadline has passed and you did not submit it.",
                            "deadline": assignment["deadline"],
                            "createdAt": datetime.utcnow()
                        })
                    except:
                        pass  # ignore duplicate error from unique index

                # ✅ MISSED ASSIGNMENTS STRUCTURED
                missed_assignments.append({
                    "assignmentId": str(assignment["_id"]),
                    "title": assignment["title"],
                    "deadline": assignment["deadline"]
                })

        # 🔥 DEADLINE NOT PASSED (OPTIONAL REMINDER)
        elif assignment["deadline"] > current_time:

            submission = submitted_col.find_one({
                "student": student_obj_id,
                "assignment": assignment["_id"]
            })

            if not submission:

                existing_notification = notifications_col.find_one({
                    "studentId": str(student_obj_id),
                    "assignmentId": str(assignment["_id"]),
                    "type": "deadline_pending"
                })

                if not existing_notification:
                    try:
                        notifications_col.insert_one({
                            "studentId": str(student_obj_id),
                            "studentName": user["name"],
                            "assignmentId": str(assignment["_id"]),
                            "assignmentName": assignment["title"],
                            "type": "deadline_pending",
                            "message": f"You have not submitted '{assignment['title']}' yet. Deadline: {assignment['deadline']}",
                            "deadline": assignment["deadline"],
                            "createdAt": datetime.utcnow()
                        })
                    except:
                        pass

    # ✅ REMOVE DUPLICATES FROM RESPONSE (AGGREGATION)
    notifications_cursor = notifications_col.find(
    {
        "studentId": str(student_obj_id),
        "type": "deadline_passed"
    }
).sort("deadline", -1).limit(3)   # 🔥 TOP 3

    notifications = list(notifications_cursor)

    return {
        "student": user["name"],
        "missed_assignments": missed_assignments,
        "notifications": serialize_list(notifications)
    }

# =========================================================
# (UNCHANGED APIs BELOW - just serialization fix if needed)
# =========================================================

@app.get("/student-progress/{student_id}")
def student_progress(student_id: str):

    student_id_obj = ObjectId(student_id)

    user = users_col.find_one({"_id": student_id_obj})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    domain_name = DOMAIN_MAP.get(str(user["domainId"]), "Unknown")

    assignments = list(assignments_col.find({
        "domain": user["domainId"]
    }))

    total_assignments = len(assignments)

    submitted = list(submitted_col.find({
        "student": student_id_obj,
        "isSubmit": True
    }))

    submitted_count = len(submitted)
    missed_count = total_assignments - submitted_count

    return {
        "student": user["name"],
        "domain": domain_name,
        "total_assignments": total_assignments,
        "submitted": submitted_count,
        "missed": missed_count
    }


@app.get("/missed-students/{assignment_id}")
def missed_students(assignment_id: str):

    assignment = assignments_col.find_one({"_id": ObjectId(assignment_id)})

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if assignment["deadline"] > datetime.utcnow():
        return {"message": "Deadline not passed yet"}

    students = list(users_col.find({
        "domainId": assignment["domain"]
    }))

    submitted = list(submitted_col.find({
        "assignment": ObjectId(assignment_id),
        "isSubmit": True
    }))

    submitted_ids = [s["student"] for s in submitted]

    missing_students = [
        {
            "studentId": str(s["_id"]),
            "name": s["name"],
            "email": s["email"]
        }
        for s in students
        if s["_id"] not in submitted_ids
    ]

    return {
        "assignment": assignment["title"],
        "missing_count": len(missing_students),
        "missing_students": missing_students
    }


@app.get("/assignment-status")
def assignment_status():

    assignments = list(assignments_col.find({}))
    result = []

    for assignment in assignments:

        domain_name = DOMAIN_MAP.get(str(assignment["domain"]), "Unknown")

        total_students = users_col.count_documents({
            "domainId": assignment["domain"]
        })

        submitted = submitted_col.count_documents({
            "assignment": assignment["_id"],
            "isSubmit": True
        })

        result.append({
            "assignment": assignment["title"],
            "domain": domain_name,
            "total_students": total_students,
            "submitted": submitted,
            "missing": total_students - submitted
        })

    return result