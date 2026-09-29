import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Numeric, Boolean, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base

class Requirements(Base):
    __tablename__ = "requirements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)

    title = Column(String, nullable=False)
    department = Column(String)
    job_description = Column(Text)
    employment_type = Column(String(100), nullable=False) # full_time, contract, remote, part_time, outsourcing

    headcount = Column(Integer, default=1)
    experience_required = Column(Numeric(4, 1))
    salary_budget_min = Column(Numeric(12, 2))
    salary_budget_max = Column(Numeric(12, 2))
    billing_rate = Column(Numeric(12, 2)) # what the client pays the company
    currency = Column(String(15))

    location_country = Column(String)
    location_city = Column(String)
    contract_duration = Column(Integer)

    visa_type = Column(String(100), nullable=False)
    priority = Column(String(50), nullable=False) # low, medium, high, urgent
    status = Column(String(30), default="draft") # draft, open, sourcing, submitted, interviewing, offered, closed, cancelled, on_hold

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationship
    client = relationship("Client", back_populates="requirements")

    # connections
    submission = relationship(
        "Submissions",
        back_populates="requirement"
    )

    deployments = relationship(
        "Deployments",
        back_populates="requirement"
    )

Index(
    "ix_requirements_entity_created",
    Requirements.client_id,
    Requirements.title,
    Requirements.employment_type,
    Requirements.salary_budget_min,
    Requirements.salary_budget_max,
    Requirements.location_country,
    Requirements.visa_type,
    Requirements.priority,
    Requirements.status,
    Requirements.created_by,
    Requirements.assigned_to,
    Requirements.created_at,
    Requirements.is_deleted,
)