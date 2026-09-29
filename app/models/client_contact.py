import uuid
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base

class ClientContacts(Base):
    __tablename__ = "client_contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"))

    name = Column(String, nullable=False)
    position = Column(String)
    email = Column(String)
    phone = Column(String)
    whatsapp = Column(String)

    is_primary = Column(Boolean, default=False)
    status = Column(String, default="active") # active, inactive

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    client = relationship("Client", back_populates="client_contacts")

    # connections
    submission = relationship(
        "Submissions",
        back_populates="clientcontact"
    )

Index(
    "ix_client_contacts_entity_created",
    ClientContacts.client_id,
    ClientContacts.status,
    ClientContacts.is_deleted,
)