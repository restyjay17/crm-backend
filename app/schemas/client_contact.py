from pydantic import BaseModel
from typing import Optional
from uuid import UUID


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

class ClientContactCreate(BaseModel):
    client_id: UUID
    name: str
    position: Optional[str] = None
    email: str
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    is_primary: Optional[bool] = False
    status: Optional[str] = "active"

class ClientContactUpdate(BaseModel):
    client_id: Optional[UUID] = None
    name: Optional[str] = None
    position: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    is_primary: Optional[bool] = None
    status: Optional[str] = None

class ClientContactUpdateStatus(BaseModel):
    status: str

class ClientContactResponse(BaseModel):
    id: UUID
    name: str
    position: Optional[str] = None
    email: str
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    is_primary: Optional[bool] = None
    status: Optional[str] = None
    client: ClientBasic

    class Config:
        from_attributes = True