from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .database import get_db
from .deps import get_current_active_user, get_current_admin
from .models import Client
from .schemas import ClientCreate, ClientRead, ClientUpdate
from .security import hash_password

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("/", response_model=list[ClientRead])
def list_clients(db: Session = Depends(get_db), _: Client = Depends(get_current_admin)):
    return db.query(Client).all()


@router.get("/{client_id}", response_model=ClientRead)
def get_client(client_id: int, db: Session = Depends(get_db), _: Client = Depends(get_current_admin)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return client


@router.post("/", response_model=ClientRead, status_code=201)
def create_client(payload: ClientCreate, role: str = "user", db: Session = Depends(get_db), _: Client = Depends(get_current_admin)):
    existing = db.query(Client).filter(Client.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email já cadastrado")
    if role not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Role inválida")
    client = Client(name=payload.name, email=payload.email,
                    password_hash=hash_password(payload.password), role=role)
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.patch("/me", response_model=ClientRead)
def update_me(payload: ClientUpdate, db: Session = Depends(get_db), current: Client = Depends(get_current_active_user)):
    if payload.name is not None:
        current.name = payload.name
    db.commit()
    db.refresh(current)
    return current


@router.patch("/{client_id}", response_model=ClientRead)
def update_client(client_id: int, payload: ClientUpdate, db: Session = Depends(get_db), _: Client = Depends(get_current_admin)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    if payload.name is not None:
        client.name = payload.name
    db.commit()
    db.refresh(client)
    return client


@router.delete("/{client_id}", status_code=204)
def delete_client(client_id: int, db: Session = Depends(get_db), _: Client = Depends(get_current_admin)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    db.delete(client)
    db.commit()
    return None
