from fastapi import Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.refresh_token import RefreshToken


# token periodic cleanup
def delete_token(db: Session = Depends(get_db)):
    db.query(RefreshToken).filter(
        RefreshToken.expires_at < datetime.now(timezone.utc)
    ).delete()

    db.commit()