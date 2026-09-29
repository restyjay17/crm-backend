from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from typing import List

from app.db.session import get_db
from app.models.interview import Interviews
from app.schemas.interview import InterviewCreate, InterviewUpdate, InterviewResponse
from app.core.dependencies import get_current_user, require_role, verify_csrf
from app.core.constants import ADMIN_ROLE, MANAGER_ROLE, RECRUITER_ROLE
from app.services.activity_logger import log_activity


router = APIRouter(
    prefix="/interviews",
    tags=["Interviews"]
)


# CREATE
@router.post("/", response_model=InterviewResponse)
def create_interview(
    payload: InterviewCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE, RECRUITER_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    interview = Interviews(**payload.model_dump())
    interview.created_by = current_user["sub"]

    try:
        db.add(interview)
        db.flush()

        log_activity(
            db,
            entity_type="interviews",
            entity_id=interview.id,
            action="created",
            performed_by=current_user["sub"],
            new_value=payload.model_dump()
        )

        db.commit()
        db.refresh(interview)
    except Exception:
        db.rollback()
        raise

    return interview


# READ ALL
@router.get("/", response_model=List[InterviewResponse])
def get_interviews(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(Interviews).options(
        joinedload(Interviews.submission)
    ).all()


# READ ONE
@router.get("/{interview_id}", response_model=InterviewResponse)
def get_interview(
    interview_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    interview = db.query(Interviews).options(
        joinedload(Interviews.submission)
    ).filter(
        Interviews.id == interview_id
    ).first()

    if not interview:
        raise HTTPException(status_code=404, detail="Interview details not found")
    
    return interview


# UPDATE
@router.put("/{interview_id}", response_model=InterviewResponse)
def update_interview(
    interview_id: UUID,
    payload: InterviewUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE, RECRUITER_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    interview = db.query(Interviews).filter(Interviews.id == interview_id).first()

    if not interview:
        raise HTTPException(status_code=404, detail="Interview details not found")
    
    old_data = payload.model_dump(exclude_unset=True)
    before_state = {key: getattr(interview, key) for key in old_data.keys()}

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(interview, key, value)

    db.flush()

    after_state = {key: getattr(interview, key) for key in old_data.keys()}
    changes = {}
    for key in old_data.keys():
        old_val = before_state.get(key)
        new_val = after_state.get(key)

        if old_val != new_val:
            changes[key] = [old_val, new_val]

    try:
        if changes:
            log_activity(
                db,
                entity_type="interviews",
                entity_id=interview_id,
                action="updated",
                performed_by=current_user["sub"],
                old_value={k: v[0] for k, v in changes.items()},
                new_value={k: v[1] for k, v in changes.items()}
            )

            db.commit()
            db.refresh(interview)
    except Exception:
        db.rollback()
        raise

    return interview