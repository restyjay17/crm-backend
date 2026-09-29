import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Index, func
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.database import Base

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    entity_type = Column(String(50), nullable=False) # candidate, requirement, submission
    entity_id = Column(UUID(as_uuid=True), nullable=False)

    action = Column(String(100), nullable=False) # created, updated, status_changed, submitted

    description = Column(Text)

    old_value = Column(JSONB)
    new_value = Column(JSONB)

    performed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

Index(
    "ix_activity_logs_entity_created",
    ActivityLog.entity_type,
    ActivityLog.entity_id,
    ActivityLog.created_at,
)