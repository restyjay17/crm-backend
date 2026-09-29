from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from typing import List

from app.db.session import get_db
from app.models.deployment import Deployments
from app.schemas.deployment import DeploymentCreate, DeploymentUpdate, DeploymentResponse
from app.core.dependencies import get_current_user, require_role, verify_csrf
from app.core.constants import ADMIN_ROLE, MANAGER_ROLE, OPERATIONS_ROLE
from app.services.activity_logger import log_activity


router = APIRouter(
    prefix="/deployments",
    tags=["Deployments"]
)

def get_deployment_data(db: Session, deployment_id: UUID):
    return (
        db.query(Deployments)
        .options(
            joinedload(Deployments.candidate),
            joinedload(Deployments.client),
            joinedload(Deployments.requirement),
            joinedload(Deployments.creator),
        )
        .filter(Deployments.id == deployment_id)
        .first()
    )


# CREATE
@router.post("/", response_model=DeploymentResponse)
def create_deployment(
    payload: DeploymentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE, OPERATIONS_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    deployment = Deployments(**payload.model_dump())
    deployment.created_by = current_user["sub"]

    try:
        db.add(deployment)
        db.flush()

        log_activity(
            db,
            entity_type="deployments",
            entity_id=deployment.id,
            action="created",
            performed_by=current_user["sub"],
            new_value=payload.model_dump()
        )

        db.commit()
        db.refresh(deployment)
    except Exception:
        db.rollback()
        raise

    return deployment


# READ ALL
@router.get("/", response_model=List[DeploymentResponse])
def get_deployments(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(Deployments).options(
        joinedload(Deployments.candidate),
        joinedload(Deployments.client),
        joinedload(Deployments.requirement),
        joinedload(Deployments.creator)
    ).all()


# READ ONE
@router.get("/{deployment_id}", response_model=DeploymentResponse)
def get_deployment(
    deployment_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    deployment = get_deployment_data(db, deployment_id)

    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment details not found")
    
    return deployment


# UPDATE
@router.put("/{deployment_id}", response_model=DeploymentResponse)
def update_deployment(
    deployment_id: UUID,
    payload: DeploymentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE, OPERATIONS_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    deployment = get_deployment_data(db, deployment_id)

    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment details not found")
    
    old_data = payload.model_dump(exclude_unset=True)
    before_state = {key: getattr(deployment, key) for key in old_data.keys()}

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(deployment, key, value)

    db.flush()

    after_state = {key: getattr(deployment, key) for key in old_data.keys()}
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
                entity_type="deployments",
                entity_id=deployment_id,
                action="updated",
                performed_by=current_user["sub"],
                old_value={k: v[0] for k, v in changes.items()},
                new_value={k: v[1] for k, v in changes.items()}
            )

            db.commit()
            db.refresh(deployment)
    except Exception:
        db.rollback()
        raise

    return deployment