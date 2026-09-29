from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from typing import List

from app.db.session import get_db
from app.models.offer import Offers
from app.schemas.offer import OfferCreate, OfferUpdate, OfferResponse
from app.core.dependencies import get_current_user, require_role, verify_csrf
from app.core.constants import ADMIN_ROLE, MANAGER_ROLE
from app.services.activity_logger import log_activity


router = APIRouter(
    prefix="/offers",
    tags=["Offers"]
)


# CREATE
@router.post("/", response_model=OfferResponse)
def create_offer(
    payload: OfferCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    offer = Offers(**payload.model_dump())
    offer.created_by = current_user["sub"]

    try:
        db.add(offer)
        db.flush()

        log_activity(
            db,
            entity_type="offers",
            entity_id=offer.id,
            action="created",
            performed_by=current_user["sub"],
            new_value=payload.model_dump()
        )

        db.commit()
        db.refresh(offer)
    except Exception:
        db.rollback()
        raise

    return offer


# READ ALL
@router.get("/", response_model=List[OfferResponse])
def get_offers(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(Offers).options(
        joinedload(Offers.submission),
        joinedload(Offers.creator)
    ).all()


# READ ONE
@router.get("/{offer_id}", response_model=OfferResponse)
def get_offer(
    offer_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    offer = db.query(Offers).options(
        joinedload(Offers.submission),
        joinedload(Offers.creator)
    ).filter(
        Offers.id == offer_id
    ).first()

    if not offer:
        raise HTTPException(status_code=404, detail="Candidate offer not found")
    
    return offer


# UPDATE
@router.put("/{offer_id}", response_model=OfferResponse)
def update_offer(
    offer_id: UUID,
    payload: OfferUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    offer = db.query(Offers).filter(Offers.id == offer_id).first()

    if not offer:
        raise HTTPException(status_code=404, detail="Candidate offer not found")
    
    old_data = payload.model_dump(exclude_unset=True)
    before_state = {key: getattr(offer, key) for key in old_data.keys()}

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(offer, key, value)

    db.flush()

    after_state = {key: getattr(offer, key) for key in old_data.keys()}
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
                entity_type="offers",
                entity_id=offer_id,
                action="updated",
                performed_by=current_user["sub"],
                old_value={k: v[0] for k, v in changes.items()},
                new_value={k: v[1] for k, v in changes.items()}
            )

            db.commit()
            db.refresh(offer)
    except Exception:
        db.rollback()
        raise

    return offer