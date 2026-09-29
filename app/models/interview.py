import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base

class Interviews(Base):
    __tablename__ = "interviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    submission_id = Column(UUID(as_uuid=True), ForeignKey("submissions.id"))

    interviewer_name = Column(String, nullable=False)
    interview_type = Column(String(50), nullable=False) # hr, technical, managerial, client, final

    scheduled_at = Column(DateTime(timezone=True))
    feedback = Column(Text)
    status = Column(String(30), nullable=False, default="scheduled") #scheduled, completed, cancelled, no_show, selected, rejected

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    submission = relationship("Submissions", back_populates="interview")

Index(
    "ix_interviews_entity_created",
    Interviews.submission_id,
    Interviews.interview_type,
    Interviews.scheduled_at,
    Interviews.status
)