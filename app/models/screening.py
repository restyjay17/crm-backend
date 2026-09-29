import uuid
from sqlalchemy import Column, String, DateTime, Integer, Numeric, ForeignKey, Text, Boolean, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base

class Screenings(Base):
    __tablename__ = "screenings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"))
    recruiter_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    years_of_experience = Column(Numeric(4, 1))
    relevant_years_of_experience = Column(Numeric(4, 1))
    notice_period = Column(Integer)

    current_company = Column(String)
    current_position = Column(String)
    current_salary = Column(Numeric(12, 2))
    expected_salary = Column(Numeric(12, 2))

    current_location = Column(String)
    preferred_location = Column(String)
    visa_status = Column(String(50)) # none, visit_visa, employment_visa, cancelled, expired
    visa_professional_title = Column(String(50))

    communication_type = Column(String) # call, whatsapp, email, zoom, google meet
    family_details = Column(Text)
    profile_summary = Column(Text)
    feedback = Column(Text)
    # salary_discussion = Column(Text)
    # availability = Column(Text)
    # relocation_interest = Column(Boolean)
    
    resume_url = Column(Text)
    
    technical_assessment = Column(String) # poor, average, good, excellent
    status = Column(String(30), nullable=False, default="pending") # pending, qualified, rejected, follow_up

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    candidate = relationship("Candidates", back_populates="screening")
    recruiter = relationship("User", back_populates="screening")

    # connections
    submission = relationship(
        "Submissions",
        back_populates="screening"
    )

Index(
    "ix_screenings_entity_created",
    Screenings.candidate_id,
    Screenings.current_position,
    Screenings.current_location,
    Screenings.visa_status,
    Screenings.communication_type,
    Screenings.status
)