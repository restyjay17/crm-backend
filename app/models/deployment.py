import uuid
from sqlalchemy import Column, String, DateTime, Date, Numeric, Text, ForeignKey, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base

class Deployments(Base):
    __tablename__ = "deployments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    requirement_id = Column(UUID(as_uuid=True), ForeignKey("requirements.id"), nullable=False)

    salary = Column(Numeric(12, 2))
    billing_rate = Column(Numeric(12, 2))
    currency = Column(String(50))

    start_date = Column(Date)
    end_date = Column(Date)
    deployment_country = Column(String)
    deployment_city = Column(String)
    accommodation_details = Column(Text)

    status = Column(String(30), default="active") # active, completed, terminated, absconded, resigned, on_leave

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    candidate = relationship("Candidates", back_populates="deployments")
    client = relationship("Client", back_populates="deployments")
    requirement = relationship("Requirements", back_populates="deployments")
    creator = relationship("User", back_populates="deployments")

Index(
    "ix_deployments_entity_created",
    Deployments.candidate_id,
    Deployments.client_id,
    Deployments.requirement_id,
    Deployments.deployment_country,
    Deployments.status
)