from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.db.session import get_db
from app.models.organization import Organizations
from app.schemas.organization import OrganizationCreate, OrganizationUpdate, OrganizationResponse
from app.core.dependencies import get_current_user, require_role, verify_csrf
from app.core.constants import ADMIN_ROLE
from app.services.activity_logger import log_activity


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"]
)


# CREATE
@router.post("/", response_model=OrganizationResponse)
def create_organization(
    payload: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    organization = Organizations(**payload.model_dump())

    try:
        db.add(organization)
        db.flush()

        log_activity(
            db,
            entity_type="organizations",
            entity_id=organization.id,
            action="created",
            performed_by=current_user["sub"],
            new_value=payload.model_dump()
        )

        db.commit()
        db.refresh(organization)
    except Exception:
        db.rollback()
        raise

    return organization


# READ ALL
@router.get("/", response_model=List[OrganizationResponse])
def get_organizations(
    db: Session = Depends(get_db),
    curren_user=Depends(get_current_user)
):
    return db.query(Organizations).all()


# READ ONE
@router.get("/{organization_id}", response_model=OrganizationResponse)
def get_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    organization = db.query(Organizations).filter(Organizations.id == organization_id).first()

    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return organization


# UPDATE
@router.put("/{organization_id}", response_model=OrganizationResponse)
def update_organization(
    organization_id: UUID,
    payload: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    organization = db.query(Organizations).filter(Organizations.id == organization_id).first()

    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    old_data = payload.model_dump(exclude_unset=True)
    before_state = {key: getattr(organization, key) for key in old_data.keys()}

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(organization, key, value)

    db.flush()

    after_state = {key: getattr(organization, key) for key in old_data.keys()}
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
                entity_type="organizations",
                entity_id=organization_id,
                action="updated",
                old_value={k: v[0] for k, v in changes.items()},
                new_value={k: v[1] for k, v in changes.items()}
            )

            db.commit()
            db.refresh(organization)
    except Exception:
        db.rollback()
        raise

    return organization