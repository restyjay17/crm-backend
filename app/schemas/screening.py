from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from decimal import Decimal
from uuid import UUID
import re


def normalize_decimal(v):
    if v is None:
        return v
    
    if isinstance(v, str):
        v = re.sub(r"[,$\s]", "", v)
        if v == "":
            return None
        
    return Decimal(v)


class DecimalNormalizationMixin:
    @field_validator(
        "years_of_experience",
        "relevant_years_of_experience",
        "current_salary",
        "expected_salary",
        mode="before"
    )
    @classmethod
    def normalize_decimal(cls, v):
        return normalize_decimal(v)


class CandidateBasic(BaseModel):
    id: UUID
    fname: str
    lname: str
    email: EmailStr

    class Config:
        from_attributes = True

class RecruiterBasic(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr

    class Config:
        from_attributes = True

class ScreeningCreate(DecimalNormalizationMixin, BaseModel):
    candidate_id: UUID
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
    communication_type: str
    family_details: Optional[str] = None
    profile_summary: Optional[str] = None
    feedback: Optional[str] = None
    technical_assessment: Optional[str] = None
    status: Optional[str] = "pending"

class ScreeningUpdate(BaseModel):
    candidate_id: Optional[UUID] = None
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
    communication_type: str
    family_details: Optional[str] = None
    profile_summary: Optional[str] = None
    feedback: Optional[str] = None
    technical_assessment: Optional[str] = None
    status: Optional[str] = None

class ScreeningResponse(BaseModel):
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
    communication_type: str
    family_details: Optional[str] = None
    profile_summary: Optional[str] = None
    feedback: Optional[str] = None
    technical_assessment: Optional[str] = None
    status: Optional[str] = None
    candidate: CandidateBasic
    recruiter: RecruiterBasic

    class Config:
        from_attributes = True