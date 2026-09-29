from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from typing import List

from app.db.session import get_db
from app.models.screening import Screenings
from app.schemas.screening import ScreeningCreate, ScreeningUpdate, ScreeningResponse
from app.core.dependencies import require_role, verify_csrf
from app.core.constants import ADMIN_ROLE, MANAGER_ROLE, RECRUITER_ROLE
from app.services.activity_logger import log_activity


router = APIRouter(
    prefix="/screenings",
    tags=["Screenings"]
)


# CREATE
@router.post("/", response_model=ScreeningResponse)
def create_screening(
    payload: ScreeningCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE, RECRUITER_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    screening = Screenings(**payload.model_dump())
    screening.recruiter_id = current_user["sub"]

    try:
        db.add(screening)
        db.flush()

        log_activity(
            db,
            entity_type="screenings",
            entity_id=screening.id,
            action="created",
            performed_by=current_user["sub"],
            new_value=payload.model_dump()
        )

        db.commit()
        db.refresh(screening)
    except Exception:
        db.rollback()
        raise

    return screening


# READ ALL
@router.get("/", response_model=List[ScreeningResponse])
def get_screenings(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE, RECRUITER_ROLE))
):
    return db.query(Screenings).options(
        joinedload(Screenings.candidate),
        joinedload(Screenings.recruiter)
    ).all()


# READ ONE
@router.get("/{screening_id}", response_model=ScreeningResponse)
def get_screening(
    screening_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE, RECRUITER_ROLE))
):
    screening = db.query(Screenings).options(
        joinedload(Screenings.candidate),
        joinedload(Screenings.recruiter)
    ).filter(
        Screenings.id == screening_id
    ).first()

    if not screening:
        raise HTTPException(status_code=404, detail="Candidate screening details not found")
    
    return screening


# UPDATE
@router.put("/{screening_id}", response_model=ScreeningResponse)
def update_screening(
    screening_id: UUID,
    payload: ScreeningUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE, RECRUITER_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    screening = db.query(Screenings).filter(Screenings.id == screening_id).first()

    if not screening:
        raise HTTPException(status_code=404, detail="Candidate screening details not found")
    
    old_data = payload.model_dump(exclude_unset=True)
    before_state = {key: getattr(screening, key) for key in old_data.keys()}

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(screening, key, value)

    db.flush()

    after_state = {key: getattr(screening, key) for key in old_data.keys()}
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
                entity_type="screenings",
                entity_id=screening_id,
                action="updated",
                performed_by=current_user["sub"],
                old_value={k: v[0] for k, v in changes.items()},
                new_value={k: v[1] for k, v in changes.items()}
            )

            db.commit()
            db.refresh(screening)
    except Exception:
        db.rollback()
        raise

    return screening