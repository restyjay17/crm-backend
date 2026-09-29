import uuid
from sqlalchemy import Column, String, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base

class Organizations(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    slug = Column(String, nullable=False)
    name = Column(String, nullable=False)
    status = Column(String(30), default="active") # active, inactive

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # connections
    client = relationship(
        "Client",
        back_populates="organization"
    )

    user = relationship(
        "User",
        back_populates="organization"
    )

Index(
    "ix_organizations_entity_created",
    Organizations.name,
    Organizations.status
)