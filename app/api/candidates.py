from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from sqlalchemy.sql import over
from uuid import UUID
from typing import List, Optional

from app.db.session import get_db
from app.models.candidate import Candidates
from app.models.submission import Submissions
from app.models.screening import Screenings
from app.schemas.candidate import CandidateCreate, CandidateUpdate, CandidateResponse
from app.core.dependencies import get_current_user, require_role, verify_csrf
from app.core.constants import ADMIN_ROLE, MANAGER_ROLE, RECRUITER_ROLE
from app.services.activity_logger import log_activity


router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"]
)


# CREATE
@router.post("/", response_model=CandidateResponse)
def create_candidate(
    payload: CandidateCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE, RECRUITER_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    check = db.query(Candidates).filter(Candidates.email == payload.email).first()

    if check:
        return check
    
    candidate = Candidates(**payload.model_dump())

    try:
        db.add(candidate)
        db.flush()

        log_activity(
            db,
            entity_type="candidates",
            entity_id=candidate.id,
            action="created",
            description=(
                f"{current_user} added a new candidate for "
                f""
            ),
            performed_by=current_user["sub"],
            new_value=payload.model_dump()
        )

        db.commit()
        db.refresh(candidate)
    except Exception:
        db.rollback()
        raise

    return candidate


# READ ALL
@router.get("/", response_model=List[CandidateResponse])
def get_candidates(
    search: Optional[str] = Query(None),
    visa_status: Optional[str] = Query(None),
    nationality: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):    
    ranked_submissions = (
        db.query(
            Submissions.id.label("submission_id"),
            Submissions.candidate_id.label("candidate_id"),
            func.row_number()
            .over(
                partition_by=Submissions.candidate_id,
                order_by=[
                    Submissions.submitted_at.desc(),
                    Submissions.id.desc(),
                ],
            )
            .label("rn"),
        )
        .filter(Submissions.status != "draft")
        .subquery()
    )
    
    query = (
        db.query(Candidates, Submissions, Screenings)
        .outerjoin(
            ranked_submissions,
            (ranked_submissions.c.candidate_id == Candidates.id)
            & (ranked_submissions.c.rn == 1),
        )
        .outerjoin(
            Submissions,
            Submissions.id == ranked_submissions.c.submission_id,
        )
        .outerjoin(
            Screenings,
            Screenings.id == Submissions.screening_id,
        )
    )

    if search:
        keyword = f"%{search}%"

        query = query.filter(
            or_(
                Candidates.fname.ilike(keyword),
                Candidates.lname.ilike(keyword),
                Candidates.email.ilike(keyword)
            )
        )

    if visa_status:
        query = query.filter(Screenings.visa_status == visa_status)

    if nationality:
        query = query.filter(Candidates.nationality == nationality)

    if status:
        query = query.filter(Candidates.status == status)

    query = query.filter(Candidates.status != "draft")

    if sort == "desc":
        query = query.order_by(
            Candidates.fname.desc(),
            Candidates.id.desc(),
        )
    else:
        query = query.order_by(
            Candidates.fname.asc(),
            Candidates.id.asc(),
        )

    results = query.all()
    
    return [
        CandidateResponse(
            id=candidate.id,
            fname=candidate.fname,
            lname=candidate.lname,
            email=candidate.email,
            contact=candidate.contact,
            gender=candidate.gender,
            nationality=candidate.nationality,
            status=candidate.status,
            submission=submission,
            screening=screening,
        )
        for candidate, submission, screening in results
    ]


# READ ONE
@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(
    candidate_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    candidate = db.query(Candidates).filter(Candidates.id == candidate_id).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return candidate


# UPDATE
@router.put("/{candidate_id}", response_model=CandidateResponse)
def update_candidate(
    candidate_id: UUID,
    payload: CandidateUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE, RECRUITER_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    candidate = db.query(Candidates).filter(Candidates.id == candidate_id).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    old_data = payload.model_dump(exclude_unset=True)
    before_state = {key: getattr(candidate, key) for key in old_data.keys()}

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(candidate, key, value)

    db.flush()

    after_state = {key: getattr(candidate, key) for key in old_data.keys()}
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
                entity_type="candidates",
                entity_id=candidate_id,
                action="updated",
                performed_by=current_user["sub"],
                old_value={k: v[0] for k, v in changes.items()},
                new_value={k: v[1] for k, v in changes.items()}
            )

            db.commit()
            db.refresh(candidate)
    except Exception:
        db.rollback()
        raise

    return candidate