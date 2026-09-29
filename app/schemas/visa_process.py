from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import date


class CandidateBasic(BaseModel):
    id: UUID
    fname: str
    lname: str
    email: EmailStr

    class Config:
        from_attributes = True

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


class UserBasic(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr

    class Config:
        from_attributes = True

class VisaProcessCreate(BaseModel):
    candidate_id: UUID
    submission_id: UUID
    country: Optional[str] = None
    visa_type: str
    passport_received: Optional[bool] = False
    medical_completed: Optional[bool] = False
    medical_status: Optional[str] = "pending"
    visa_applied: Optional[bool] = False
    visa_approved: Optional[bool] = False
    visa_number: Optional[str] = None
    embassy_status: Optional[str] = "pending"
    flight_booked: Optional[bool] = False
    flight_detail: Optional[str] = None
    deployment_date: Optional[date] = None
    status: Optional[str] = "initiated"

class VisaProcessUpdate(BaseModel):
    country: Optional[str] = None
    visa_type: Optional[str] = None
    passport_received: Optional[bool] = None
    medical_completed: Optional[bool] = None
    medical_status: Optional[str] = None
    visa_applied: Optional[bool] = None
    visa_approved: Optional[bool] = None
    visa_number: Optional[str] = None
    embassy_status: Optional[str] = None
    flight_booked: Optional[bool] = None
    flight_detail: Optional[str] = None
    depployment_date: Optional[date] = None
    status: Optional[str] = None

class VisaProcessResponse(BaseModel):
    id: UUID
    country: Optional[str] = None
    visa_type: Optional[str] = None
    passport_received: Optional[bool] = None
    medical_completed: Optional[bool] = None
    medical_status: Optional[str] = None
    visa_applied: Optional[bool] = None
    visa_approved: Optional[bool] = None
    visa_number: Optional[str] = None
    embassy_status: Optional[str] = None
    flight_booked: Optional[bool] = None
    flight_detail: Optional[str] = None
    depployment_date: Optional[date] = None
    status: Optional[str] = None
    candidate: CandidateBasic
    submission: SubmissionBasic
    creator: UserBasic

    class Config:
        from_attributes = True