import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    company_name = Column(String, nullable=False)
    industry = Column(String)
    country = Column(String)
    city = Column(String)
    website = Column(String)

    billing_currency = Column(String)
    payment_terms = Column(String)
    status = Column(String, default="active") # active, inactive, blacklisted, pending_contract
    notes = Column(String)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)

    created_by = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    organization = relationship("Organizations", back_populates="client")

    # connection
    client_contacts = relationship(
        "ClientContacts",
        back_populates="client",
        cascade="all, delete-orphan"
    )

    requirements = relationship(
        "Requirements",
        back_populates="client",
        cascade="all, delete-orphan"
    )

    deployments = relationship(
        "Deployments",
        back_populates="client"
    )

Index(
    "ix_client_entity_created",
    Client.industry,
    Client.country,
    Client.status,
    Client.organization_id,
    Client.created_at
)

Index(
    "ix_client_company_name_trgm",
    Client.company_name,
    postgresql_using="gin",
    postgresql_ops={
        "company_name": "gin_trgm_ops"
    }
)

Index(
    "ix_client_website_trgm",
    Client.website,
    postgresql_using="gin",
    postgresql_ops={
        "website": "gin_trgm_ops"
    }
)