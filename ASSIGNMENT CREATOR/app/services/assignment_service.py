from app.database import users_col, assignments_col
from bson import ObjectId
from datetime import datetime

# -------------------------
# Get Teacher (from users collection)
# -------------------------
def get_teacher(teacher_id):
    try:
        return users_col.find_one({
            "_id": ObjectId(teacher_id),
            "role": "teacher"
        })
    except:
        return None

# -------------------------
# Extract Teacher Info
# -------------------------
def get_teacher_full_details(teacher_id):
    from app.database import domains_col, bootcamps_col
    teacher = get_teacher(teacher_id)
    if not teacher:
        return None

    domain_ids = [ObjectId(d) if isinstance(d, str) else d for d in teacher.get("teacherDomainIds", [])]
    bootcamp_ids = [ObjectId(b) if isinstance(b, str) else b for b in teacher.get("teacherBootcampIds", [])]

    domains = list(domains_col.find({"_id": {"$in": domain_ids}}))
    bootcamps = list(bootcamps_col.find({"_id": {"$in": bootcamp_ids}}))

    return {
        "teacher_id": str(teacher["_id"]),
        "name": teacher.get("name"),
        "domains": [{"id": str(d["_id"]), "name": d.get("name", d.get("domainName", "Unknown Domain"))} for d in domains],
        "bootcamps": [{"id": str(b["_id"]), "name": b.get("name", b.get("bootcampName", "Unknown Bootcamp"))} for b in bootcamps]
    }

# -------------------------
# Save Assignment
# -------------------------
def save_assignment(data):
    data["createdAt"] = datetime.utcnow()
    data["updatedAt"] = datetime.utcnow()

    result = assignments_col.insert_one(data)
    return str(result.inserted_id)