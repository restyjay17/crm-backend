from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.models.activity_log import ActivityLog

def log_activity(
        db: Session,
        *,
        entity_type: str,
        entity_id,
        action: str,
        description: str = None,
        old_value: dict = None,
        new_value: dict = None,
        performed_by=None
):
    log = ActivityLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        description=description,
        old_value=jsonable_encoder(old_value) if old_value is not None else None,
        new_value=jsonable_encoder(new_value) if new_value is not None else None,
        performed_by=performed_by
    )

    db.add(log)
    db.commit()