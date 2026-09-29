from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from typing import List

from app.db.session import get_db
from app.models.visa_process import VisaProcesses
from app.schemas.visa_process import VisaProcessCreate, VisaProcessUpdate, VisaProcessResponse
from app.core.dependencies import get_current_user, require_role, verify_csrf
from app.core.constants import ADMIN_ROLE, MANAGER_ROLE, OPERATIONS_ROLE
from app.services.activity_logger import log_activity


router = APIRouter(
    prefix="/visa_processes",
    tags=["Visa Processes"]
)


# CREATE
@router.post("/", response_model=VisaProcessResponse)
def create_visa_process(
    payload: VisaProcessCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE, OPERATIONS_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    visaprocess = VisaProcesses(**payload.model_dump())
    visaprocess.created_by = current_user["sub"]

    try:
        db.add(visaprocess)
        db.flush()

        log_activity(
            db,
            entity_type="visa_processes",
            entity_id=visaprocess.id,
            action="created",
            performed_by=current_user["sub"],
            new_value=payload.model_dump()
        )

        db.commit()
        db.refresh(visaprocess)
    except Exception:
        db.rollback()
        raise

    return visaprocess


# READ ALL
@router.get("/", response_model=List[VisaProcessResponse])
def get_visa_processes(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(VisaProcesses).options(
        joinedload(VisaProcesses.candidate),
        joinedload(VisaProcesses.submission),
        joinedload(VisaProcesses.creator)
    ).all()


# READ ONE
@router.get("/{visa_process_id}", response_model=VisaProcessResponse)
def get_visa_process(
    visa_process_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    visaprocess = db.query(VisaProcesses).options(
        joinedload(VisaProcesses.candidate),
        joinedload(VisaProcesses.submission),
        joinedload(VisaProcesses.creator)
    ).filter(
        VisaProcesses.id == visa_process_id
    ).first()

    if not visaprocess:
        raise HTTPException(status_code=404, detail="Visa processing details not found")
    
    return visaprocess


# UPDATE
@router.put("/{visa_process_id}", response_model=VisaProcessResponse)
def update_visa_process(
    visa_process_id: UUID,
    payload: VisaProcessUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE, OPERATIONS_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    visaprocess = db.query(VisaProcesses).filter(VisaProcesses.id == visa_process_id).first()

    if not visaprocess:
        raise HTTPException(status_code=404, detail="Visa process details not found")
    
    old_data = payload.model_dump(exclude_unset=True)
    before_state = {key: getattr(visaprocess, key) for key in old_data.keys()}

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(visaprocess, key, value)

    db.flush()

    after_state = {key: getattr(visaprocess, key) for key in old_data.keys()}
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
                entity_type="visa_processes",
                entity_id=visa_process_id,
                action="updated",
                old_value={k: v[0] for k, v in changes.items()},
                new_value={k: v[1] for k, v in changes.items()}
            )

            db.commit()
            db.refresh(visaprocess)
    except Exception:
        db.rollback()
        raise

    return visaprocess