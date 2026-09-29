import uuid
from sqlalchemy import Column, String, DateTime, Text, Numeric, Date, ForeignKey, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base

class Offers(Base):
    __tablename__ = "offers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    submission_id = Column(UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False)

    offered_salary = Column(Numeric(12, 1))
    currency = Column(String(50))
    joining_date = Column(Date)
    offer_letter_url = Column(Text)
    notes = Column(Text)

    status = Column(String(30), nullable=False, default="pending") # pending, accepted, rejected, withdrawn

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    submission = relationship("Submissions", back_populates="offer")
    creator = relationship("User", back_populates="offer")

Index(
    "ix_offers_entity_created",
    Offers.submission_id,
    Offers.joining_date,
    Offers.status,
    Offers.created_by
)