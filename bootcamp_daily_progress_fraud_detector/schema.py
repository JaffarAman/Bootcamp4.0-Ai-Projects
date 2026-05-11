from pydantic import BaseModel
from datetime import datetime
from pydantic import BaseModel
from datetime import datetime

class TodayUpdate(BaseModel):
    student_id: str
    bootcamp_id: str

    yesterdayWork: str
    todayPlan: str | None = None
    blockers: str | None = None
    githubLink: str | None = None
    hoursWorked: int | None = None
    needMentor: bool | None = False

    grade: str | None = ""
    mentor: str | None = None
    feedback: str | None = ""

    date: datetime | None = None