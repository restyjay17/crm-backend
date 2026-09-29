import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base

class Submissions(Base):
    __tablename__ = "submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    screening_id = Column(UUID(as_uuid=True), ForeignKey("screenings.id"))
    requirement_id = Column(UUID(as_uuid=True), ForeignKey("requirements.id"), nullable=False)
    submitted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    client_contact_id = Column(UUID(as_uuid=True), ForeignKey("client_contacts.id"))

    submission_summary = Column(Text)

    status = Column(String(30), nullable=False, default="draf") # draft, submitted, shortlisted, interview_scheduled, interviewed, rejected, selected, offered, joined

    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    candidate = relationship("Candidates", back_populates="submission")
    screening = relationship("Screenings", back_populates="submission")
    requirement = relationship("Requirements", back_populates="submission")
    submitter = relationship("User", back_populates="submission")
    clientcontact = relationship("ClientContacts", back_populates="submission")


    # connections
    interview = relationship(
        "Interviews",
        back_populates="submission"
    )

    offer = relationship(
        "Offers",
        back_populates="submission"
    )

    visa_processes = relationship(
        "VisaProcesses",
        back_populates="submission"
    )

Index(
    "ix_submissions_entity_created",
    Submissions.candidate_id,
    Submissions.screening_id,
    Submissions.requirement_id,
    Submissions.submitted_by,
    Submissions.client_contact_id,
    Submissions.status
)