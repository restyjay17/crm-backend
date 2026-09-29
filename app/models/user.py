import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=False)

    hashed_password = Column(String, nullable=False)

    role = Column(String, default="recruiter") # recruiter, sales, operations, finance, manager, admin
    status = Column(String, default="active") # active, inactive, suspended
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization = relationship("Organizations", back_populates="user")

    # connections
    screening = relationship(
        "Screenings",
        back_populates="recruiter"
    )

    submission = relationship(
        "Submissions",
        back_populates="submitter"
    )

    offer = relationship(
        "Offers",
        back_populates="creator"
    )

    visa_processes = relationship(
        "VisaProcesses",
        back_populates="creator"
    )

    deployments = relationship(
        "Deployments",
        back_populates="creator"
    )

Index(
    "ix_user_entity_created",
    User.email,
    User.role,
    User.status,
    User.organization_id
)