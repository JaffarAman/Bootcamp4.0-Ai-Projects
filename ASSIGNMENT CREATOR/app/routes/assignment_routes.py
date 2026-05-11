from fastapi import APIRouter, HTTPException
from app.services.ai_generator import generate_assignment
from app.services.assignment_service import get_teacher, get_teacher_full_details, save_assignment
from app.models.assignment import AssignmentCreate
from app.utils.formatter import extract_title_description
from bson import ObjectId
from datetime import datetime

routes = APIRouter()

@routes.get("/teacher/{teacher_id}/details")
def teacher_details(teacher_id: str):
    details = get_teacher_full_details(teacher_id)
    if not details:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return details

@routes.post("/generate-assignment")
def generate(data: AssignmentCreate):
    details = get_teacher_full_details(data.teacher_id)
    domain_name = next((d["name"] for d in details["domains"] if d["id"] == data.domain_id), "") if details else ""
    bootcamp_name = next((b["name"] for b in details["bootcamps"] if b["id"] == data.bootcamp_id), "") if details else ""
    
    context_prompt = f"Context: This assignment is for a bootcamp '{bootcamp_name}' and domain '{domain_name}'. Module: {data.module}.\n\n" + data.prompt
    ai_response = generate_assignment(context_prompt)

    return {
        "generated_text": ai_response
    }

@routes.post("/submit-assignment")
def submit(data: dict):

    teacher_id = data["teacher_id"]
    domain_id = data["domain_id"]
    bootcamp_id = data["bootcamp_id"]

    teacher = get_teacher(teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    title, description = extract_title_description(data["content"])

    try:
        if isinstance(data.get("deadline"), str):
            deadline_val = datetime.fromisoformat(data["deadline"].replace("Z", "+00:00"))
        else:
            deadline_val = data["deadline"]
    except:
        deadline_val = data.get("deadline")

    assignment_data = {
        "title": title,
        "description": description,
        "documentUrl": data.get("documentUrl", ""),
        "domain": ObjectId(domain_id),
        "teacher": ObjectId(teacher_id),
        "bootcamp": ObjectId(bootcamp_id),
        "module": data["module"],
        "deadline": deadline_val,
        "status": "Active",
        "requiredLinks": data.get("requiredLinks", [])
    }

    assignment_id = save_assignment(assignment_data)

    return {
        "message": "Assignment Created",
        "assignment_id": assignment_id
    }