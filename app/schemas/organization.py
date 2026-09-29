from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class OrganizationCreate(BaseModel):
    name: str
    slug: str
    status: str = "active"

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    status: Optional[str] = None

class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    status: str