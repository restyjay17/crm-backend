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
        "salary",
        "billing_rate",
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

class RequirementBasic(BaseModel):
    id: UUID
    title: str
    employment_type: str
    visa_type: str
    billing_rate: Optional[Decimal] = None
    location_country: Optional[str] = None
    location_city: Optional[str] = None

    class Config:
        from_attributes = True

class UserBasic(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr

    class Config:
        from_attributes = True

class DeploymentCreate(DecimalNormalizationMixin, BaseModel):
    candidate_id: UUID
    client_id: UUID
    requirement_id: UUID
    salary: Optional[Decimal] = None
    billing_rate: Optional[Decimal] = None
    currency: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    deployment_country: Optional[str] = None
    deployment_city: Optional[str] = None
    accommodation_details: Optional[str] = None
    status: Optional[str] = "active"

class DeploymentUpdate(DecimalNormalizationMixin, BaseModel):
    client_id: Optional[UUID] = None
    requirement_id: Optional[UUID] = None
    salary: Optional[Decimal] = None
    billing_rate: Optional[Decimal] = None
    currency: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    deployment_country: Optional[str] = None
    deployment_city: Optional[str] = None
    accommodation_details: Optional[str] = None
    status: Optional[str] = None

class DeploymentResponse(DecimalNormalizationMixin, BaseModel):
    id: UUID
    salary: Optional[Decimal] = None
    billing_rate: Optional[Decimal] = None
    currency: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    deployment_country: Optional[str] = None
    deployment_city: Optional[str] = None
    accommodation_details: Optional[str] = None
    status: Optional[str] = None
    candidate: CandidateBasic
    client: ClientBasic
    requirement: RequirementBasic
    creator: UserBasic

    class Config:
        from_attributes = True