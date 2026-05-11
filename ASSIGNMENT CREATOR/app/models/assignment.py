from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AssignmentCreate(BaseModel):
    prompt: str
    teacher_id: str
    domain_id: str
    bootcamp_id: str
    module: str
    deadline: str  # Kept as str to easily handle different iso formats from frontend without strict datetime parsing errors

class AssignmentSave(BaseModel):
    title: str
    description: str
    documentUrl: Optional[str] = ""
    domain: str
    teacher: str
    bootcamp: str
    module: str
    deadline: str
    status: str = "Active"
    requiredLinks: List[str] = []