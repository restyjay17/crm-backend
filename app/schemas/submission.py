from pydantic import BaseModel, EmailStr
from typing import Optional
from decimal import Decimal
from uuid import UUID


class CandidateBasic(BaseModel):
    id: UUID
    fname: str
    lname: str
    email: EmailStr

    class Config:
        from_attributes = True

class ScreeningBasic(BaseModel):
    candidate: CandidateBasic
    id: UUID
    years_of_experience: Optional[Decimal] = None
    relevant_years_of_experience: Optional[Decimal] = None
    notice_period: Optional[int] = None
    current_company: Optional[str] = None
    current_position: Optional[str] = None
    current_salary: Optional[Decimal] = None
    expected_salary: Optional[Decimal] = None
    current_location: Optional[str] = None
    preferred_location: Optional[str] = None
    visa_status: Optional[str] = None
    visa_professional_title: Optional[str] = None
    communication_type: Optional[str] = None
    family_details: Optional[str] = None
    profile_summary: Optional[str] = None
    feedback: Optional[str] = None
    technical_assessment: Optional[str] = None

    class Config:
        from_attributes = True

class RequirementBasic(BaseModel):
    id: UUID
    title: str
    employment_type: str
    visa_type: str
    job_description: Optional[str] = None

    class Config:
        from_attributes = True

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

class SubmissionCreate(BaseModel):
    candidate_id: UUID
    screening_id: Optional[UUID] = None
    requirement_id: UUID
    client_contact_id: Optional[UUID] = None
    submission_summary: Optional[str] = None
    status: Optional[str] = "draft"

class SubmissionUpdate(BaseModel):
    screening_id: Optional[UUID] = None
    requirement_id: Optional[UUID] = None
    client_contact_id: Optional[UUID] = None
    submission_summary: Optional[str] = None
    status: Optional[str] = None

class SubmissionResponse(BaseModel):
    id: UUID
    submission_summary: Optional[str] = None
    status: Optional[str] = None
    # candidate: CandidateBasic
    screening: Optional[ScreeningBasic] = None
    requirement: RequirementBasic
    client_contact: Optional[ClientContactBasic] = None
    submitter: SubmitterBasic

    class Config:
        from_attributes = True