from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base

class RefreshToken(Base):
    __tablename__ = "refresh_token"

    token_hash = Column(String, unique=True, nullable=False, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    revoked = Column(Boolean, nullable=False, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User")

Index(
    "ix_refresh_token_entity_created",
    RefreshToken.token_hash,
    RefreshToken.user_id,
    RefreshToken.revoked,
)