from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime


class CandidateBasic(BaseModel):
    id: UUID
    fname: str
    lname: str
    email: EmailStr

    class Config:
        from_attributes = True

class RequirementBasic(BaseModel):
    id: UUID
    title: str
    employment_type: str
    visa_type: str
    job_description: Optional[str] = None

class SubmitterBasic(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr

    class Config:
        from_attributes = True

class ClientContactBasic(BaseModel):
    id: UUID
    name: str
    position: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None

    class Config:
        from_attributes = True

class SubmissionBasic(BaseModel):
    id: UUID
    submission_summary: Optional[str] = None
    candidate: CandidateBasic
    requirement: RequirementBasic
    client_contact: Optional[ClientContactBasic] = None
    submitter: SubmitterBasic

    class Config:
        from_attributes = True

class InterviewCreate(BaseModel):
    submission_id: UUID
    interviewer_name: str
    interview_type: str
    scheduled_at: Optional[datetime] = None
    feedback: Optional[str] = None
    status: Optional[str] = "scheduled"

class InterviewUpdate(BaseModel):
    submission_id: Optional[UUID] = None
    interviewer_name: Optional[str] = None
    interview_type: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    feedback: Optional[str] = None
    status: Optional[str] = None

class InterviewResponse(BaseModel):
    id: UUID
    interviewer_name: str
    interview_type: str
    scheduled_at: Optional[datetime] = None
    feedback: Optional[str] = None
    status: Optional[str] = None
    submission: SubmissionBasic

    class Config:
        from_attributes = True