from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse
)

from app.core.security import hash_password
from app.core.dependencies import require_role, verify_csrf
from app.core.constants import ADMIN_ROLE
from app.services.activity_logger import log_activity

router = APIRouter(
    prefix="/user",
    tags=["User"]
)


# CREATE
@router.post("/", response_model=UserResponse)
def register(
    payload: UserCreate, 
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    existing = (
        db.query(User).filter(User.email == payload.email).first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        status=payload.status,
        organization_id=payload.organization_id
    )

    try:
        db.add(user)
        db.flush()

        user_value = {
            "email": payload.email,
            "full_name": payload.full_name,
            "hashed_password": hash_password(payload.password),
            "role": payload.role,
            "status": payload.status,
            "organization_id": payload.organization_id
        }

        log_activity(
            db,
            entity_type="users",
            entity_id=user.id,
            action="created",
            performed_by=current_user["sub"],
            new_value=user_value
        )

        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise

    return user


# READ ALL
@router.get("/", response_model=List[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE))
):
    return db.query(User).all()


# READ ONE
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE))
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


# UPDATE
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    old_data = payload.model_dump(exclude_unset=True)
    before_state = {key: getattr(user, key) for key in old_data.keys()}
    
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, key, value)

    db.flush()

    after_state = {key: getattr(user, key) for key in old_data.keys()}
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
                entity_type="users",
                entity_id=user_id,
                action="updated",
                performed_by=current_user["sub"],
                old_value={k: v[0] for k, v in changes.items()},
                new_value={k: v[1] for k, v in changes.items()}
            )

        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise

    return user