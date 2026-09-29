from pydantic import BaseModel, field_validator
from typing import Optional
from uuid import UUID


class SubmissionBasic(BaseModel):
    status: str

    class Config:
        from_attributes = True

class ScreeningBasic(BaseModel):
    visa_status: str
    years_of_experience: int
    status: str

    class Config:
        from_attributes = True
    
class CandidateBase(BaseModel):
    fname: str
    lname: str
    email: str
    contact: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    status: Optional[str] = "draft"

class CandidateCreate(CandidateBase):
    pass

class CandidateUpdate(BaseModel):
    fname: Optional[str] = None
    lname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    contact: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    status: Optional[str] = None

class CandidateResponse(CandidateBase):
    id: UUID
    submission: Optional[SubmissionBasic] = None
    screening: Optional[ScreeningBasic] = None

    class Config:
        from_attributes = True