from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional


class OrganizationBasic(BaseModel):
    id: UUID
    name: str
    slug: str

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: str = "recruiter"
    status: str = "active"
    organization_id: UUID

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    organization_id: Optional[UUID] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    role: str
    status: str
    organization: OrganizationBasic

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class CurrentUser(BaseModel):
    id: UUID
    email: str
    role: str
    organization_id: UUID