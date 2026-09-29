import uuid
from sqlalchemy import Column, String, Date, Integer, Numeric, DateTime, ForeignKey, Text, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base

class Candidates(Base):
    __tablename__ = "candidates";

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    fname = Column(String, nullable=False)
    lname = Column(String, nullable=False)
    
    email = Column(String, nullable=False)
    contact = Column(String(30))
    # whatsapp = Column(String(30))

    # date_of_birth = Column(Date)
    gender = Column(String(20))
    nationality = Column(String(100))
    
    # years_of_experience = Column(Numeric(4, 1))
    # relevant_years_of_experience = Column(Numeric(4, 1))
    # notice_period = Column(Integer)

    # current_company = Column(String)
    # current_position = Column(String)
    # current_salary = Column(Numeric(12, 2))
    # expected_salary = Column(Numeric(12, 2))

    # current_location = Column(String)
    # preferred_location = Column(String)
    # passport_number = Column(String)
    # passport_expiry = Column(Date)
    # visa_status = Column(String(50)) # none, visit_visa, employment_visa, cancelled, expired
    # visa_professional_title = Column(String(50))

    # family_details = Column(Text)
    # profile_summary = Column(Text)
    # feedback = Column(Text)

    # linkedin_url = Column(Text)
    # resume_url = Column(Text)

    # source_type = Column(String) # linkedin, naukrigulf, indeed, referral, database, manual
    status = Column(String) # draft, active, inactive, blacklisted, deployed, selected, on_hold

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # connections
    screening = relationship(
        "Screenings",
        back_populates="candidate"
    )

    submission = relationship(
        "Submissions",
        back_populates="candidate"
    )

    visa_processes = relationship(
        "VisaProcesses",
        back_populates="candidate"
    )

    deployments = relationship(
        "Deployments",
        back_populates="candidate"
    )

Index(
    "ix_candidates_entity_created",
    Candidates.fname,
    Candidates.lname,
    Candidates.email,
    Candidates.nationality,
    # Candidates.visa_status,
    # Candidates.years_of_experience,
    # Candidates.current_position,
    Candidates.status
)