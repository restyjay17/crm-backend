import uuid
from sqlalchemy import Column, String, DateTime, Date, ForeignKey, Text, Boolean, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base

class VisaProcesses(Base):
    __tablename__ = "visa_processes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False)

    country = Column(String)
    visa_type = Column(String(100), nullable=False)
    passport_received = Column(Boolean, default=False)
    medical_completed = Column(Boolean, default=False)
    medical_status = Column(String(30), default="pending") # pending, passed, failed

    visa_applied = Column(Boolean, default=False)
    visa_approved = Column(Boolean, default=False)
    visa_number = Column(String)
    embassy_status = Column(String(50), default="pending") # pending, processing, approved, rejected

    flight_booked = Column(Boolean, default=False)
    flight_detail = Column(Text)
    deployment_date = Column(Date)
    
    status = Column(String(30), default="initiated") # initiated, processing, approved, rejected, deployed

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    candidate = relationship("Candidates", back_populates="visa_processes")
    submission = relationship("Submissions", back_populates="visa_processes")
    creator = relationship("User", back_populates="visa_processes")

Index(
    "ix_visa_processes_entity_created",
    VisaProcesses.candidate_id,
    VisaProcesses.submission_id,
    VisaProcesses.country,
    VisaProcesses.visa_approved,
    VisaProcesses.embassy_status,
    VisaProcesses.status
)