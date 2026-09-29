from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from decimal import Decimal
from datetime import date
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
        "offered_salary",
        mode="before"
    )
    @classmethod
    def normalize_decimal(cls, v):
        return normalize_decimal(v)
    
class CreatorBasic(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr

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
    
class OfferCreate(DecimalNormalizationMixin, BaseModel):
    submission_id: UUID
    offered_salary: Decimal
    currency: Optional[str] = None
    joining_date: date
    offer_letter_url: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = "pending"

class OfferUpdate(DecimalNormalizationMixin, BaseModel):
    submission_id: Optional[UUID] = None
    offered_salary: Optional[Decimal] = None
    currency: Optional[str] = None
    joining_date: Optional[date] = None
    offer_letter_url: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None

class OfferResponse(BaseModel):
    id: UUID
    offered_salary: Decimal
    currency: Optional[str] = None
    joining_date: date
    offer_letter_url: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    creator: CreatorBasic
    submission: SubmissionBasic

    class Config:
        from_attributes = None