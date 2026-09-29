from pydantic import BaseModel, field_validator
from typing import Optional
from decimal import Decimal
from uuid import UUID
import re


def normalize_decimal(v):
    if v is None:
        return v
    
    if isinstance(v, str):
        # remove commas, spaces, currency symbols, etc.
        v = re.sub(r"[,$\s]", "", v)

        if v == "":
            return None
    
    return Decimal(v)


class DecimalNormalizationMixin:
    @field_validator(
        "experience_required",
        "salary_budget_min",
        "salary_budget_max",
        "billing_rate",
        mode="before"
    )
    @classmethod
    def normalize_decimal(cls, v):
        return normalize_decimal(v)
  
class OrganizationBasic(BaseModel):
    id: UUID
    name: str
    slug: str

    class Config:
        from_attributes = True
  
class ClientBasic(BaseModel):
    id: UUID
    company_name: str
    industry: Optional[str] = None
    country: Optional[str] = None
    organization: OrganizationBasic

    class Config:
        from_attributes = True

class SubmissionBasic(BaseModel):
    id: UUID
    candidate_id: UUID
    screening_id: UUID
    requirement_id: UUID

    class Config:
        from_attributes = True

class CandidateBasic(BaseModel):
    fname: str
    lname: str
    email: Optional[str] = None
    contact: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None

    class Config:
        from_attributes = True

class ScreeningBasic(BaseModel):
    current_position: Optional[str] = None
    years_of_experience: Optional[int] = None
    relevant_years_of_experience: Optional[int] = None
    notice_period: Optional[int] = None
    current_salary: Optional[Decimal] = None
    expected_salary: Optional[Decimal] = None
    visa_status: Optional[str] = None
    status: Optional[str] = None
    current_company: Optional[str] = None
    current_location: Optional[str] = None
    preferred_location: Optional[str] = None
    visa_professional_title: Optional[str] = None
    communication_type: Optional[str] = None
    family_details: Optional[str] = None
    profile_summary: Optional[str] = None
    feedback: Optional[str] = None

    class Config:
        from_attributes = True

class RequirementCreate(DecimalNormalizationMixin, BaseModel):
    client_id: UUID
    title: str
    department: Optional[str] = None
    job_description: Optional[str] = None
    employment_type: str
    headcount: Optional[int] = None
    experience_required: Optional[Decimal] = None

    salary_budget_min: Optional[Decimal] = None
    salary_budget_max: Optional[Decimal] = None
    billing_rate: Optional[Decimal] = None

    currency: Optional[str] = None
    location_country: Optional[str] = None
    location_city: Optional[str] = None
    contract_duration: Optional[int] = None
    visa_type: str
    priority: str
    status: Optional[str] = "draft"
    assigned_to: Optional[UUID] = None

class RequirementUpdate(DecimalNormalizationMixin, BaseModel):
    client_id: Optional[UUID] = None
    title: Optional[str] = None
    department: Optional[str] = None
    job_description: Optional[str] = None
    employment_type: Optional[str] = None
    headcount: Optional[int] = None
    experience_required: Optional[Decimal] = None
    salary_budget_min: Optional[Decimal] = None
    salary_budget_max: Optional[Decimal] = None
    billing_rate: Optional[Decimal] = None
    currency: Optional[str] = None
    location_country: Optional[str] = None
    location_city: Optional[str] = None
    contract_duration: Optional[int] = None
    visa_type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[UUID] = None

class RequirementUpdateStatus(BaseModel):
    status: str

class RequirementResponse(DecimalNormalizationMixin, BaseModel):
    id: UUID
    title: str
    department: Optional[str] = None
    job_description: Optional[str] = None
    employment_type: str
    headcount: Optional[int] = None
    experience_required: Optional[Decimal] = None

    salary_budget_min: Optional[Decimal] = None
    salary_budget_max: Optional[Decimal] = None
    billing_rate: Optional[Decimal] = None

    currency: Optional[str] = None
    location_country: Optional[str] = None
    location_city: Optional[str] = None
    contract_duration: Optional[int] = None
    visa_type: str
    priority: str
    status: Optional[str] = None
    assigned_to: Optional[UUID] = None

    client: ClientBasic

    class Config:
        from_attributes = True

class RequirementCandidateResponse(SubmissionBasic, CandidateBasic, ScreeningBasic):
    pass