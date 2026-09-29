from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class OrganizationBasic(BaseModel):
    id: UUID
    name: str
    slug: str

    class Config:
        from_attributes = True
    

class ClientCreate(BaseModel):
    company_name: str
    industry: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    website: Optional[str] = None
    billing_currency: Optional[str] = None
    payment_terms: Optional[str] = None
    status: Optional[str] = "active"
    notes: Optional[str] = None
    organization_id: Optional[UUID] = None

class ClientUpdate(BaseModel):
    company_name: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    website: Optional[str] = None
    billing_currency: Optional[str] = None
    payment_terms: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    organization_id: Optional[UUID] = None

class ClientUpdateStatus(BaseModel):
    status: str

class ClientResponse(BaseModel):
    id: UUID
    company_name: str
    industry: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    website: Optional[str] = None
    billing_currency: Optional[str] = None
    payment_terms: Optional[str] = None
    status: Optional[str] = "active"
    notes: Optional[str] = None
    contacts_count: int = 0
    requirements_count: int = 0
    organization: OrganizationBasic

    class Config:
        from_attributes = True

class ClientContactResponse(BaseModel):
    id: UUID
    name: str
    position: Optional[str] = None
    email: str
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True

class ClientRequirementResponse(BaseModel):
    id: UUID
    title: str
    employment_type: str
    location_country: Optional[str] = None
    visa_type: str
    priority: str
    status: Optional[str] = None

    class Config:
        from_attributes = True