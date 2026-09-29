from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import or_, asc, desc
from uuid import UUID
from typing import List, Optional
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.client_contact import ClientContacts
from app.models.client import Client
from app.schemas.client_contact import ClientContactCreate, ClientContactUpdate, ClientContactUpdateStatus, ClientContactResponse
from app.core.dependencies import require_role, verify_csrf
from app.core.constants import ADMIN_ROLE, MANAGER_ROLE, SALES_ROLE
from app.services.activity_logger import log_activity

router = APIRouter(
    prefix="/client_contacts",
    tags=["Client Contacts"]
)


# CREATE
@router.post("/", response_model=ClientContactResponse)
def create_client_contact(
    payload: ClientContactCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE, SALES_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    client_contact = ClientContacts(**payload.model_dump())

    try:
        db.add(client_contact)
        db.flush()

        client = db.query(Client).filter(
            Client.id == client_contact.client_id
        ).first()

        log_activity(
            db,
            entity_type="client_contacts",
            entity_id=client_contact.id,
            action="created",
            description=(
                f"{current_user['name']} added "
                f"{client_contact.name} as a contact for "
                f"{client.company_name}"
            ),
            performed_by=current_user["sub"],
            new_value=payload.model_dump()
        )

        db.commit()
        db.refresh(client_contact)
    except Exception:
        db.rollback()
        raise
    
    return client_contact


# READ ALL
@router.get("/", response_model=List[ClientContactResponse])
def get_client_contact(
    search: Optional[str] = Query(None),
    client: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    sort: Optional[str] = Query("asc"),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE, SALES_ROLE))
):
    query = (
        db.query(ClientContacts)
            .join(Client, Client.id == ClientContacts.client_id)
            .options(selectinload(ClientContacts.client))
    )

    if search:
        keyword = f"%{search}%"

        query = query.filter(
            or_(
                ClientContacts.name.ilike(keyword),
                ClientContacts.position.ilike(keyword),
                ClientContacts.email.ilike(keyword)
            )
        )

    if client:
        query = query.filter(ClientContacts.client_id == client)

    if status:
        query = query.filter(ClientContacts.status == status)

    query = query.filter(ClientContacts.is_deleted.is_(False))

    if sort == "desc":
        query = query.order_by(
            asc(Client.company_name),
            desc(ClientContacts.name)
        )
    else:
        query = query.order_by(
            asc(Client.company_name),
            asc(ClientContacts.name)
        )

    clientcontacts = query.all()

    return clientcontacts


# READ ONE
@router.get("/{client_contact_id}", response_model=ClientContactResponse)
def get_client_contact(
    client_contact_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE, SALES_ROLE))
):
    client_contact = db.query(ClientContacts).options(
        joinedload(ClientContacts.client)
    ).filter(
        ClientContacts.id == client_contact_id,
        ClientContacts.is_deleted.is_(False)
    ).first()

    if not client_contact:
        raise HTTPException(status_code=404, detail="Client contact not found")
    
    return client_contact


# UPDATE
@router.put("/{client_contact_id}", response_model=ClientContactResponse)
def update_client_contact(
    client_contact_id: UUID,
    payload: ClientContactUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE, SALES_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    client_contact = db.query(ClientContacts).filter(
        ClientContacts.id == client_contact_id,
        ClientContacts.is_deleted.is_(False)
    ).first()

    if not client_contact:
        raise HTTPException(status_code=404, detail="Client contact not found")
    
    old_data = payload.model_dump(exclude_unset=True)
    before_state = {key: getattr(client_contact, key) for key in old_data.keys()}

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(client_contact, key, value)

    db.flush()

    after_state = {key: getattr(client_contact, key) for key in old_data.keys()}
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
                entity_type="client_contacts",
                entity_id=client_contact_id,
                action="updated",
                description=(
                    f"{current_user['name']} updated {client_contact.name}'s "
                    f"contact details for {client_contact.client.company_name}"
                ),
                performed_by=current_user["sub"],
                old_value={k: v[0] for k, v in changes.items()},
                new_value={k: v[1] for k, v in changes.items()}
            )

            db.commit()
            db.refresh(client_contact)
    except Exception:
        db.rollback()
        raise

    return client_contact


# UPDATE STATUS
@router.patch("/{client_contact_id}/status", response_model=ClientContactResponse)
def update_client_contact_status(
    client_contact_id: UUID,
    payload: ClientContactUpdateStatus,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE, SALES_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    client_contact = db.query(ClientContacts).filter(
        ClientContacts.id == client_contact_id,
        ClientContacts.is_deleted.is_(False)
    ).first()

    if not client_contact:
        raise HTTPException(status_code=404, detail="Client contact not found")

    old_status = client_contact.status

    client_contact.status = payload.status

    db.flush()

    try:
        log_activity(
            db,
            entity_type="client_contacts",
            entity_id=client_contact_id,
            action="updated",
            description=(
                f"{current_user['name']} updated {client_contact.name}'s "
                f"status to {payload.status.replace('_', ' ').title()} "
                f"for {client_contact.client.company_name}"
            ),
            performed_by=current_user["sub"],
            old_value={"status": old_status},
            new_value={"status": payload.status}
        )

        db.commit()
        db.refresh(client_contact)
    except Exception:
        db.rollback()
        raise

    return client_contact


# DELETE
@router.delete("/{client_contact_id}")
def delete_client_contact(
    client_contact_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    client_contact = db.query(ClientContacts).filter(
        ClientContacts.id == client_contact_id,
        ClientContacts.is_deleted.is_(False)
    ).first()

    if not client_contact:
        raise HTTPException(status_code=404, detail="Client contact not found")
    
    snapshot = {
        c.name: getattr(client_contact, c.name)
        for c in client_contact.__table__.columns
    }

    try:
        client_contact.is_deleted = True
        client_contact.deleted_at = datetime.now(timezone.utc)

        log_activity(
            db,
            entity_type="client_contacts",
            entity_id=client_contact_id,
            action="deleted",
            performed_by=current_user["sub"],
            new_value=snapshot
        )

        db.commit()
    except Exception:
        db.rollback()
        raise
    
    return {"message": "Client contact deleted successfully"}