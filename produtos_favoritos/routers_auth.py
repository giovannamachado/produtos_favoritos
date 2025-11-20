from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .database import get_db
from .models import Client
from .schemas import ClientCreate, ClientRead, Token
from .security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=ClientRead, status_code=201)
def register(payload: ClientCreate, db: Session = Depends(get_db)):
    existing = db.query(Client).filter(Client.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email já cadastrado")
    client = Client(name=payload.name, email=payload.email,
                    password_hash=hash_password(payload.password), role="user")
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.post("/login", response_model=Token)
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(Client).filter(Client.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    token = create_access_token(user.email)
    return Token(access_token=token)
