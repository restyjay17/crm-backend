from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from typing import List

from app.db.session import get_db
from app.models.submission import Submissions
from app.schemas.submission import SubmissionCreate, SubmissionUpdate, SubmissionResponse
from app.core.dependencies import get_current_user, require_role, verify_csrf
from app.core.constants import ADMIN_ROLE, MANAGER_ROLE, RECRUITER_ROLE
from app.services.activity_logger import log_activity


router = APIRouter(
    prefix="/submissions",
    tags=["Submissions"]
)


# CREATE
@router.post("/", response_model=SubmissionResponse)
def create_submission(
    payload: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE, RECRUITER_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    submission = Submissions(**payload.model_dump())
    submission.submitted_by = current_user["sub"]

    try:
        db.add(submission)
        db.flush()

        log_activity(
            db,
            entity_type="submissions",
            entity_id=submission.id,
            action="created",
            performed_by=current_user["sub"],
            new_value=payload.model_dump()
        )

        db.commit()
        db.refresh(submission)
    except Exception:
        db.rollback()
        raise

    return submission


# READ ALL
@router.get("/", response_model=List[SubmissionResponse])
def get_submissions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(Submissions).options(
        joinedload(Submissions.candidate),
        joinedload(Submissions.screening),
        joinedload(Submissions.requirement),
        joinedload(Submissions.clientcontact),
        joinedload(Submissions.submitter)
    ).all()


# READ ONE
@router.get("/{submission_id}", response_model=SubmissionResponse)
def get_submission(
    submission_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    submission = db.query(Submissions).options(
        joinedload(Submissions.candidate),
        joinedload(Submissions.screening),
        joinedload(Submissions.requirement),
        joinedload(Submissions.clientcontact),
        joinedload(Submissions.submitter)
    ).filter(
        Submissions.id == submission_id
    ).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return submission


# UPDATE
@router.put("/{submission_id}", response_model=SubmissionResponse)
def update_submission(
    submission_id: UUID,
    payload: SubmissionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE, RECRUITER_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    submission = db.query(Submissions).filter(Submissions.id == submission_id).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    old_data = payload.model_dump(exclude_unset=True)
    before_state = {key: getattr(submission, key) for key in old_data.keys()}

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(submission, key, value)

    db.flush()

    after_state = {key: getattr(submission, key) for key in old_data.keys()}
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
                entity_type="submissions",
                entity_id=submission_id,
                action="updated",
                performed_by=current_user["sub"],
                old_value={k: v[0] for k, v in changes.items()},
                new_value={k: v[1] for k, v in changes.items()}
            )

            db.commit()
            db.refresh(submission)
    except Exception:
        db.rollback()
        raise

    return submission