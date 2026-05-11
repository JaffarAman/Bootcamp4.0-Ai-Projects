from pydantic import BaseModel, HttpUrl

class SubmissionRequest(BaseModel):
    studentId: str
    assignmentId: str
    link: HttpUrl

class SubmissionResponse(BaseModel):
    success: bool
    message: str
    similarity: float