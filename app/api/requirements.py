from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import or_, and_, asc, desc
from uuid import UUID
from typing import List, Optional
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.requirement import Requirements
from app.models.client import Client
from app.models.candidate import Candidates
from app.models.screening import Screenings
from app.models.submission import Submissions
from app.schemas.requirement import RequirementCreate, RequirementUpdate, RequirementUpdateStatus, RequirementResponse, RequirementCandidateResponse
from app.core.dependencies import get_current_user, require_role, verify_csrf
from app.core.constants import ADMIN_ROLE, MANAGER_ROLE, SALES_ROLE
from app.services.activity_logger import log_activity


router = APIRouter(
    prefix="/requirements",
    tags=["Requirements"]
)


# CREATE
@router.post("/", response_model=RequirementResponse)
def create_requirement(
    payload: RequirementCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE, SALES_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    requirement = Requirements(**payload.model_dump())
    requirement.assigned_to = current_user["sub"]
    requirement.status = "draft"

    try:
        db.add(requirement)
        db.flush()

        client = db.query(Client).filter(
            Client.id == requirement.client_id
        ).first()

        log_activity(
            db,
            entity_type="requirements",
            entity_id=requirement.id,
            action="created",
            description=(
                f"{current_user['name']} added "
                f"{requirement.title} as a new requirement for "
                f"{client.company_name}"
            ),
            performed_by=current_user["sub"],
            new_value=payload.model_dump()
        )

        db.commit()
        db.refresh(requirement)
    except Exception:
        db.rollback()
        raise

    return requirement


# READ ALL
@router.get("/", response_model=List[RequirementResponse])
def get_requirements(
    search: Optional[str] = Query(None),
    client: Optional[str] = Query(None),
    employment_type: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    sort: Optional[str] = Query("asc"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    query = (
        db.query(Requirements)
            .join(Client, Client.id == Requirements.client_id)
            .options(selectinload(Requirements.client))
    )

    if search:
        keyword = f"%{search}%"

        query = query.filter(
            or_(
                Requirements.title.ilike(keyword),
                Requirements.job_description.ilike(keyword)
            )
        )

    if client:
        query = query.filter(Requirements.client_id == client)

    if employment_type:
        query = query.filter(Requirements.employment_type == employment_type)

    if priority:
        query = query.filter(Requirements.priority == priority)

    if status:
        query = query.filter(Requirements.status == status)

    query = query.filter(Requirements.is_deleted.is_(False))

    if sort == "desc":
        query = query.order_by(
            asc(Client.company_name),
            desc(Requirements.title)
        )
    else:
        query = query.order_by(
            asc(Client.company_name),
            asc(Requirements.title)
        )

    requirements = query.all()

    return requirements


# READ ONE
@router.get("/{requirement_id}", response_model=RequirementResponse)
def get_requirement(
    requirement_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    requirement = db.query(Requirements).options(
        joinedload(Requirements.client)
    ).filter(
        Requirements.id == requirement_id,
        Requirements.is_deleted.is_(False)
    ).first()

    if not requirement:
        raise HTTPException(status_code=404, detail="Client requirements not found")
    
    return requirement


# READ REQUIREMENT CANDIDATES
@router.get("/{requirement_id}/candidates", response_model=List[RequirementCandidateResponse])
def get_requirement_candidates(
    requirement_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    result = (
        db.query(
            Submissions.id,
            Submissions.candidate_id,
            Submissions.screening_id,
            Submissions.requirement_id,
            Submissions.status,
            Candidates.fname,
            Candidates.lname,
            Candidates.email,
            Candidates.contact,
            Candidates.gender,
            Candidates.nationality,
            Screenings.current_position,
            Screenings.years_of_experience,
            Screenings.relevant_years_of_experience,
            Screenings.notice_period,
            Screenings.current_salary,
            Screenings.expected_salary,
            Screenings.visa_status,
            Screenings.current_company,
            Screenings.current_location,
            Screenings.preferred_location,
            Screenings.visa_professional_title,
            Screenings.communication_type,
            Screenings.family_details,
            Screenings.profile_summary,
            Screenings.feedback
        )
        .join(
            Submissions,
            Submissions.candidate_id == Candidates.id
        )
        .join(
            Screenings,
            Screenings.id == Submissions.screening_id
        )
        .filter(
            Submissions.requirement_id == requirement_id
        )
        .order_by(
            asc(Candidates.fname)
        )
        .all()
    )

    if not result:
        raise HTTPException(status_code=404, detail="No candidates found")

    return result


# UPDATE
@router.put("/{requirement_id}", response_model=RequirementResponse)
def update_requirement(
    requirement_id: UUID,
    payload: RequirementUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE, SALES_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    requirement = db.query(Requirements).filter(
        Requirements.id == requirement_id,
        Requirements.is_deleted.is_(False)
    ).first()

    if not requirement:
        raise HTTPException(status_code=404, detail="Client requirements not found")
    
    old_data = payload.model_dump(exclude_unset=True)
    before_state = {key: getattr(requirement, key) for key in old_data.keys()}

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(requirement, key, value)

    db.flush()

    after_state = {key: getattr(requirement, key) for key in old_data.keys()}
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
                entity_type="requirements",
                entity_id=requirement_id,
                action="updated",
                description=(
                    f"{current_user['name']} updated the details of {requirement.title} "
                    f"for {requirement.client.company_name}"
                ),
                performed_by=current_user["sub"],
                old_value={k: v[0] for k, v in changes.items()},
                new_value={k: v[1] for k, v in changes.items()}
            )

            db.commit()
            db.refresh(requirement)
    except Exception:
        db.rollback()
        raise

    return requirement


# UPDATE STATUS
@router.patch("/{requirement_id}/status", response_model=RequirementResponse)
def update_requirement_status(
    requirement_id: UUID,
    payload: RequirementUpdateStatus,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE, SALES_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    requirement = db.query(Requirements).filter(
        Requirements.id == requirement_id,
        Requirements.is_deleted.is_(False)
    ).first()

    if not requirement:
        raise HTTPException(status_code=404, detail="Client requirement not found")

    old_status = requirement.status

    requirement.status = payload.status

    db.flush()

    try:
        log_activity(
            db,
            entity_type="requirements",
            entity_id=requirement_id,
            action="updated",
            description=(
                f"{current_user['name']} updated {requirement.title}'s "
                f"status to {payload.status.replace('_', ' ').title()} "
                f"for {requirement.client.company_name}"
            ),
            performed_by=current_user["sub"],
            old_value={"status": old_status},
            new_value={"status": payload.status}
        )

        db.commit()
        db.refresh(requirement)
    except Exception:
        db.rollback()
        raise

    return requirement


# DELETE
@router.delete("/{requirement_id}")
def delete_requirement(
    requirement_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    requirement = db.query(Requirements).filter(
        Requirements.id == requirement_id,
        Requirements.is_deleted.is_(False)
    ).first()

    if not requirement:
        raise HTTPException(status_code=404, detail="Client requirements not found")
    
    snapshot = {
        c.name: getattr(requirement, c.name)
        for c in requirement.__table__.columns
    }

    try:
        requirement.is_deleted = True
        requirement.deleted_at = datetime.now(timezone.utc)

        log_activity(
            db,
            entity_type="requirements",
            entity_id=requirement_id,
            action="deleted",
            performed_by=current_user["sub"],
            new_value=snapshot
        )
        
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {"message": "Client requirements deleted successfully"}