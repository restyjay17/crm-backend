from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func, or_, and_, asc, desc
from uuid import UUID
from typing import List, Optional

from app.db.session import get_db
from app.models.client import Client
from app.models.client_contact import ClientContacts
from app.models.requirement import Requirements
from app.models.organization import Organizations
from app.schemas.client import ClientCreate, ClientUpdate, ClientUpdateStatus, ClientResponse, ClientContactResponse, ClientRequirementResponse
from app.core.dependencies import get_current_user, require_role, verify_csrf
from app.core.constants import ADMIN_ROLE, MANAGER_ROLE, SALES_ROLE
from app.services.activity_logger import log_activity


router = APIRouter(
    prefix="/clients", 
    tags=["Clients"]
)


# CREATE
@router.post("/", response_model=ClientResponse)
def create_client(
    payload: ClientCreate, 
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE, SALES_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    client_data = payload.model_dump()
    client_data["created_by"] = current_user["sub"]
    client_data["organization_id"] = current_user["org"]

    client = Client(**client_data)

    try:
        db.add(client)
        db.flush()

        log_activity(
            db,
            entity_type="clients",
            entity_id=client.id,
            action="created",
            description=f"{current_user['name']} created a new client: {client.company_name}",
            performed_by=current_user["sub"],
            new_value=payload.model_dump()
        )
        
        db.commit()
        db.refresh(client)
    except Exception:
        db.rollback()
        raise

    return client


# READ ALL
@router.get("/", response_model=List[ClientResponse])
def get_clients(
    search: Optional[str] = Query(None),
    org: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    sort: Optional[str] = Query("asc"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    query = (
        db.query(
            Client,
            func.count(func.distinct(ClientContacts.id)).label("contacts_count"),
            func.count(func.distinct(Requirements.id)).label("requirements_count"),
        )
        .outerjoin(
            ClientContacts,
            and_(
                ClientContacts.client_id == Client.id, 
                ClientContacts.is_deleted.is_(False)
            )
        )
        .outerjoin(
            Requirements,
            and_(
                Requirements.client_id == Client.id, 
                Requirements.is_deleted.is_(False)
            )
        )
        .join(Organizations, Organizations.id == Client.organization_id)
        .options(selectinload(Client.organization))
    )

    if search:
        keyword = f"%{search}%"

        query = query.filter(
            or_(
                Client.company_name.ilike(keyword),
                Client.industry.ilike(keyword),
                Client.city.ilike(keyword),
                Client.country.ilike(keyword),
                Client.website.ilike(keyword),
            )
        )

    if org:
        query = query.filter(Organizations.slug == org)

    if industry:
        query = query.filter(Client.industry == industry)

    if country:
        query = query.filter(Client.country == country)

    if status:
        query = query.filter(Client.status == status)

    query = query.group_by(Client.id, Client.organization_id)

    if sort == "desc":
        query = query.order_by(desc(Client.company_name))
    else:
        query = query.order_by(asc(Client.company_name))

    clients = query.all()

    response = []

    for client, contacts_count, requirements_count in clients:
        item = ClientResponse.model_validate(client)
        item.contacts_count = contacts_count
        item.requirements_count = requirements_count
        response.append(item)

    return response


# READ ONE
@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: UUID, 
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    result = (
        db.query(
            Client,
            func.count(func.distinct(ClientContacts.id)).label("contacts_count"),
            func.count(func.distinct(Requirements.id)).label("requirements_count"),
        )
        .outerjoin(
            ClientContacts,
            and_(
                ClientContacts.client_id == Client.id, 
                ClientContacts.is_deleted.is_(False)
            )
        )
        .outerjoin(
            Requirements,
            and_(
                Requirements.client_id == Client.id, 
                Requirements.is_deleted.is_(False)
            )
        )
        .options(
            selectinload(Client.organization)
        )
        .group_by(Client.id)
        .filter(Client.id == client_id)
        .first()
    )

    if not result:
        raise HTTPException(status_code=404, detail="Client not found")

    client, contacts_count, requirements_count = result
    
    return {
        **client.__dict__,
        "contacts_count": contacts_count,
        "requirements_count": requirements_count,
    }


# READ CLIENT CONTACTS
@router.get("/{client_id}/contacts", response_model=List[ClientContactResponse])
def get_client_contact(
    client_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    result = (
        db.query(ClientContacts)
        .filter(
            ClientContacts.client_id == client_id,
            ClientContacts.is_deleted.is_(False)
        )
        .all()
    )

    if not result:
        raise HTTPException(status_code=404, detail="Client contacts results not found")

    return result


# READ CLIENT REQUIREMENTS
@router.get("/{client_id}/requirements", response_model=List[ClientRequirementResponse])
def get_client_requirements(
    client_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    result = (
        db.query(Requirements)
        .filter(
            Requirements.client_id == client_id,
            Requirements.is_deleted.is_(False)
        )
        .all()
    )

    if not result:
        raise HTTPException(status_code=404, detail="Client requirements results not found")

    return result


# UPDATE
@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: UUID, 
    payload: ClientUpdate, 
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE, SALES_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    old_data = payload.model_dump(exclude_unset=True)
    before_state = {key: getattr(client, key) for key in old_data.keys()}
    
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(client, key, value)

    db.flush()

    after_state = {key: getattr(client, key) for key in old_data.keys()}
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
                entity_type="clients",
                entity_id=client_id,
                action="updated",
                description=f"{current_user['name']} updated {client.company_name}'s details",
                performed_by=current_user["sub"],
                old_value={k: v[0] for k, v in changes.items()},
                new_value={k: v[1] for k, v in changes.items()}
            )

            db.commit()
            db.refresh(client)
    except Exception:
        db.rollback()
        raise
    
    return client

# UPDATE STATUS
@router.patch("/{client_id}/status", response_model=ClientResponse)
def update_client_status(
    client_id: UUID,
    payload: ClientUpdateStatus,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE)),
    csrf: None = Depends(verify_csrf)
):
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    old_status = client.status

    client.status = payload.status

    db.flush()

    try:
        log_activity(
            db,
            entity_type="clients",
            entity_id=client_id,
            action="updated",
            description=f"{current_user['name']} updated {client.company_name}'s status to {payload.status.replace('_', ' ').title()}.",
            performed_by=current_user["sub"],
            old_value={"status": old_status},
            new_value={"status": payload.status}
        )

        db.commit()
        db.refresh(client)
    except Exception:
        db.rollback()
        raise

    return client


# DELETE
# @router.delete("/{client_id}")
# def delete_client(
#     client_id: UUID, 
#     db: Session = Depends(get_db),
#     current_user=Depends(require_role(ADMIN_ROLE, MANAGER_ROLE))
# ):
#     client = db.query(Client).filter(Client.id == client_id).first()

#     if not client:
#         raise HTTPException(status_code=404, detail="Client not found")

#     db.delete(client)
#     db.commit()
#     return {"message": "Client deleted successfully"}