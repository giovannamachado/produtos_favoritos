from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .database import get_db
from .deps import get_current_active_user, get_current_admin
from .models import Client
from .schemas import ClientRead, ClientUpdate

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


@router.patch("/me", response_model=ClientRead)
def update_me(payload: ClientUpdate, db: Session = Depends(get_db), current: Client = Depends(get_current_active_user)):
    if payload.name is not None:
        current.name = payload.name
    db.commit()
    db.refresh(current)
    return current


@router.delete("/{client_id}", status_code=204)
def delete_client(client_id: int, db: Session = Depends(get_db), _: Client = Depends(get_current_admin)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    db.delete(client)
    db.commit()
    return None
