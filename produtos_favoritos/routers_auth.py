from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .database import get_db
from .deps import get_current_active_user
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
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Client).filter(Client.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    token = create_access_token(user.email)
    return Token(access_token=token)


@router.get("/me", response_model=ClientRead)
def get_me(current: Client = Depends(get_current_active_user)):
    return current
